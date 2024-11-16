import threading
from django.shortcuts import render
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
import json
import pyttsx3
from .models import SearchQuery
from transformers import GPT2LMHeadModel, GPT2Tokenizer
import torch
from googleapiclient.discovery import build
import logging

logger = logging.getLogger(__name__)

# Initialize GPT-2 model and tokenizer
model_name = 'gpt2'
tokenizer = GPT2Tokenizer.from_pretrained(model_name)
model = GPT2LMHeadModel.from_pretrained(model_name)
model.config.pad_token_id = model.config.eos_token_id 

# Google Search API 
api_key = 'AIzaSyD9vvGIXueQKfg0jinIWrO05VT7_ApXGag'
cse_id = 'd418baac4dcc34ace'

def say(text):
    engine = pyttsx3.init()
    engine.say(text)
    engine.runAndWait()

def handle_edge_cases(response):
    if len(response.split()) < 5:  # If the response is too short
        return "Sorry, I couldn't find a detailed answer. Could you please rephrase the question?"
    return response

# Google Search function with results for both text and images
def google_search(query, search_type="text"):
    service = build("customsearch", "v1", developerKey=api_key)
    try:
        if search_type == "image":
            # Perform an image search
            result = service.cse().list(q=query, cx=cse_id, searchType="image", num=1).execute()
            search_results = result.get('items', [])
            if not search_results:
                return None
            image_url = search_results[0].get('link')  # Return image URL only
            return {"image_url": image_url}
        else:
            # Perform a regular text search
            result = service.cse().list(q=query, cx=cse_id, num=1).execute()
            search_results = result.get('items', [])
            if not search_results:
                return None
            snippet = search_results[0].get('snippet', 'No text available')  # Return text snippet
            return {"text_result": snippet}
    except Exception as e:
        return None

# Function to generate response using GPT-2
def generate_gpt2_response(query):
    # Check if the query exists in the database
    cached_query = SearchQuery.objects.filter(query=query).first()
    if cached_query:
        return cached_query.result, None  # Return cached result and no image

    # Tokenize the query input and create the attention mask
    input_ids = tokenizer.encode(query, return_tensors='pt')
    attention_mask = torch.ones(input_ids.shape, dtype=torch.long)  # Attention mask (1 for valid tokens)
    # Generate a response using GPT-2
    output = model.generate(
        input_ids, 
        max_length=240,  
        num_return_sequences=1, 
        no_repeat_ngram_size=2, 
        attention_mask=attention_mask, 
        pad_token_id=model.config.pad_token_id,
        do_sample=False  # Deterministic generation
    )
    
    response = tokenizer.decode(output[0], skip_special_tokens=True)
    # Handle edge cases (e.g: short or unclear responses)
    response = handle_edge_cases(response)
    # Save the query and result in the database for future reference
    SearchQuery.objects.create(query=query, result=response)
    return response, None  # Return GPT-2 response without an image

# Main view to render the Jarvis assistant template
def jarvis(request):
    return render(request, 'index.html')  # Renders your template (index.html)

# View to handle general queries using GPT-2 and Google Search
@csrf_exempt
def search(request):
    if request.method == "POST":
        try:
            data = json.loads(request.body)
            query = data.get('query', '').strip().lower()  # Convert to lowercase for consistency
            say(query)
            logger.debug(f"Received query: {query}")

            if not query:
                return JsonResponse({"success": False, "result": "Search query cannot be empty."})

            # Function to speak the text asynchronously
            def speak_async(text):
                threading.Thread(target=say, args=(text,)).start()

            # If the query requests an image, perform an image-only search
            if "image" in query or "photo" in query or "pic" in query:
                image_data = google_search(query, search_type="image")  # Use the modified image search function
                if image_data:
                    speak_async(image_data['image_url'])
                    return JsonResponse({"success": True, "image_url": image_data['image_url']})
                else:
                    speak_async("No image found.")
                    return JsonResponse({"success": False, "result": "No image found."})

            # Otherwise, perform the GPT-2 response or Google text search as before
            gpt2_response, _ = generate_gpt2_response(query)
            google_text_data = google_search(query, search_type="text")  # Optional: Fallback text search for non-image queries
            # Combine Google text result and GPT-2 response
            result_text = google_text_data.get('text_result', '') + "\n" + gpt2_response if google_text_data else gpt2_response
            
            # Speak the result asynchronously
            speak_async(result_text)
            
            # Return the generated result
            return JsonResponse({"success": True, "result": result_text})
        except json.JSONDecodeError:
            return JsonResponse({"success": False, "result": "Invalid JSON input."})
        except Exception as e:
            return JsonResponse({"success": False, "result": f"An error occurred: {str(e)}"})

    return JsonResponse({"success": False, "result": "Invalid request method."})

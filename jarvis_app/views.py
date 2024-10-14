from django.shortcuts import render
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
import json
import pyttsx3
from .models import SearchQuery  # Import the SearchQuery model
from transformers import GPT2LMHeadModel, GPT2Tokenizer
import torch
from googleapiclient.discovery import build

# Initialize GPT-2 model and tokenizer
model_name = 'gpt2'
tokenizer = GPT2Tokenizer.from_pretrained(model_name)
model = GPT2LMHeadModel.from_pretrained(model_name)

# Ensure that the pad_token_id is set to eos_token_id for open-ended generation
model.config.pad_token_id = model.config.eos_token_id

# Google Search API initialization
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
def google_search(query):
    service = build("customsearch", "v1", developerKey=api_key)
    
    try:
        result = service.cse().list(q=query, cx=cse_id, num=3).execute()
        search_results = result.get('items', [])
        
        if not search_results:
            return "No results found."
        
        # Extract text and images from search results
        answer = search_results[0].get('snippet', 'Sorry, no detailed answer found.')
        image_url = None
        for item in search_results:
            if 'pagemap' in item and 'cse_image' in item['pagemap']:
                image_url = item['pagemap']['cse_image'][0]['src']
                break
        
        return answer, image_url
    
    except Exception as e:
        return f"Error during Google search: {str(e)}", None

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
        max_length=240,  # Increase the response length
        num_return_sequences=1, 
        no_repeat_ngram_size=2, 
        temperature=0.7, 
        attention_mask=attention_mask,  
        pad_token_id=model.config.pad_token_id  # Use eos_token_id for padding
    )

    response = tokenizer.decode(output[0], skip_special_tokens=True)

    # Handle edge cases (e.g., short or unclear responses)
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
            data = json.loads(request.body)  # Parse JSON from the request body
            say(data)
            query = data.get('query', '').strip()  # Get the query from the POST data and remove extra spaces

            if not query:
                return JsonResponse({"success": False, "result": "Search query cannot be empty."})

            # First, attempt to generate a response using GPT-2
            gpt2_response, _ = generate_gpt2_response(query)
            
            # If GPT-2 doesn't return a good result, fallback to Google Search for detailed answers
            google_text, image_url = google_search(query)
            if google_text:
                result_text = google_text + "\n" + gpt2_response
            else:
                result_text = gpt2_response
            
            # If there is an image, include it in the response
            result_data = {"success": True, "result": result_text}
            if image_url:
                result_data["image_url"] = image_url

            say(result_text)  # Call the say function to speak the result

            return JsonResponse(result_data)

        except json.JSONDecodeError:
            return JsonResponse({"success": False, "result": "Invalid JSON input."})
        except Exception as e:
            return JsonResponse({"success": False, "result": f"An error occurred: {str(e)}"})

    return JsonResponse({"success": False, "result": "Invalid request method."})

from django.shortcuts import render
from django.http import JsonResponse
from googleapiclient.discovery import build
from django.views.decorators.csrf import csrf_exempt
import json
import pyttsx3
from .models import SearchQuery  # Import the SearchQuery model
from transformers import GPT2LMHeadModel, GPT2Tokenizer
import torch
# Initialize the text-to-speech engine
def jarvis(request):
    return render(request, 'index.html')  # Renders your template (index.html)

def say(text):
    engine = pyttsx3.init()
    engine.say(text)
    engine.runAndWait()

# Google Search API function with caching
def google_search(query):
    # Check if the query exists in the database
    cached_query = SearchQuery.objects.filter(query=query).first()
    if cached_query:
        return cached_query.result  # Return the cached result

    # Replace with your actual API key and CSE ID
    api_key = 'AIzaSyD9vvGIXueQKfg0jinIWrO05VT7_ApXGag'
    cse_id = 'd418baac4dcc34ace'

    try:
        service = build("customsearch", "v1", developerKey=api_key)
        result = service.cse().list(q=query, cx=cse_id, num=3).execute()

        search_results = result.get('items', [])
        if not search_results:
            answer = "No results found."
        else:
            # Get the first snippet or relevant answer from the search results
            answer = search_results[0].get('snippet', 'Sorry, I could not find an answer.')

        # Save the query and result in the database
        SearchQuery.objects.create(query=query, result=answer)

        return answer

    except Exception as e:
        return f"Error during Google search: {str(e)}"

# View to handle general queries using Google Search
@csrf_exempt
def search(request):
    if request.method == "POST":
        try:
            data = json.loads(request.body)# Parse JSON from the request body
            say(data)
            query = data.get('query', '').strip()  # Get the query from the POST data and remove extra spaces

            if not query:
                return JsonResponse({"success": False, "result": "Search query cannot be empty."})

            result = google_search(query)  # Perform the Google search
            say(result)  # Call the say function to speak the result
            return JsonResponse({"success": True, "result": result})

        except json.JSONDecodeError:
            return JsonResponse({"success": False, "result": "Invalid JSON input."})
        except Exception as e:
            return JsonResponse({"success": False, "result": f"An error occurred: {str(e)}"})

    return JsonResponse({"success": False, "result": "Invalid request method."})


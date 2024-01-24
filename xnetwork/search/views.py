import json
import os
import sys
import uuid
import openai
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from django.contrib.auth.models import User

from .models import Query, ChatSession
from .serializers import QueryTextSerializer, ChatSessionSerializer
from .utils import extract_search_criteria, can_generate_query
import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Use environment variables
openai.api_key = os.getenv('OPENAI_API_KEY')

# Get the directory of your current file
current_file_dir = os.path.dirname(__file__)

# Calculate the path to the 'ml-model' directory
ml_model_dir = os.path.join(current_file_dir, '../../ml-model/model-training')
ml_inference_dir = os.path.join(current_file_dir, '../../ml-model/model-inference')

# Add the 'ml-model' directory to sys.path
sys.path.append(ml_model_dir)
sys.path.append(ml_inference_dir)

from load_model import search_index
from inference import rank_movies
from .faiss_singleton import FaissIndex
from .search_rtr_singleton import SearchRTR, FeatureStore
from .elasticsearch_singleton import ElasticsearchIndex, search_results_es


class ChatSessionViewSet(viewsets.GenericViewSet):
    serializer_class = ChatSessionSerializer

    @action(detail=False, methods=['post'], url_path='chat')
    def chat(self, request):
        session_id = request.data.get('session_id')
        user_message = request.data.get('conversation_history')
        max_tokens = request.data.get('max_tokens', 150)  # You can adjust the default value as needed

        # Handle anonymous users by assigning to a default user or skipping the user association
        if request.user.is_authenticated:
            user = request.user
        else:
            user = User.objects.get(
                username='jason0')  # Or assign to a default user, like User.objects.get(username='default')

        # Retrieve or create a chat session
        if not session_id:
            # If no session_id provided, create a new session with a system message
            session_id = str(uuid.uuid4())  # Generate a new session_id
            messages = [
                {"role": "system", "content": "You are a helpful assistant specializing in movie searches."}
            ]
            chat_session = ChatSession.objects.create(user=user, session_id=session_id,
                                                      conversation_history=json.dumps(messages))
        else:
            # If session_id is provided, retrieve the existing session
            chat_session, created = ChatSession.objects.get_or_create(user=user, session_id=session_id)
            messages = json.loads(chat_session.conversation_history) if chat_session.conversation_history else []

        if user_message:
            # Add user message to conversation history
            user_message = "Briefly respond: " + user_message
            messages.append({"role": "user", "content": user_message})
            print("DEBUG messages: ")
            print(messages)
            # Get response from OpenAI
            response = openai.ChatCompletion.create(
                model="gpt-3.5-turbo",
                messages=messages,
                temperature=0,
                max_tokens=max_tokens,
            )

            gpt_message = response['choices'][0]['message']['content']
            messages.append({"role": "assistant", "content": gpt_message})
            assistant_response = {'reply': gpt_message}

            # Update conversation history in the database
            chat_session.conversation_history = json.dumps(messages)
            chat_session.save()

            # Extract movie search criteria from the conversation
            is_query, query_text = extract_search_criteria(user_message, openai)

            assistant_response['searching_for'] = None
            assistant_response['ranked_results'] = None
            if is_query and query_text is not None:  # determine if the criteria are sufficient
                ranked_results = self.search_lean_tile_internal(request, query_text)

                assistant_response['searching_for'] = query_text
                # Append additional info to assistant_response
                assistant_response['ranked_results'] = ranked_results

            # Return the response
            return Response(assistant_response, status=status.HTTP_200_OK)

        else:
            # Handle empty user message
            return Response({"error": "The message content cannot be empty."}, status=status.HTTP_400_BAD_REQUEST)

    def search_lean_tile_internal(self, request, query_text):
        if request.user.is_authenticated:
            user = request.user
        else:
            user = User.objects.get(username='jason0')
        print(f"DEBUG: search_lean_tile_internal query_text: {query_text}")
        # Extract user info from the request
        user_id = user.id
        top_k = request.data.get("top_k", 60)  # Default to 10 if not provided
        print(f"user_id: {user_id}")
        print(f"top_k: {top_k}")

        # Use the query_text generated by the chatbot to perform the search
        es = ElasticsearchIndex.get_instance()
        relevance_weight = 2.0
        index_name = "movies_index"

        results = search_results_es(query_text, es, index_name, top_k)
        if len(results) == 0:
            print("Nothing from Elasticsearch")
            print(f'query: {query_text}')
            return []
        loaded_model = SearchRTR.get_instance()
        feature_store = FeatureStore.get_instance()

        movie_ids = [result[1] for result in results]
        print("DEBUG: movie_ids")
        print(movie_ids)

        sorted_movies_with_scores = rank_movies(loaded_model, user_id, query_text, movie_ids, relevance_weight,
                                                feature_store)

        # Return the search results
        return sorted_movies_with_scores


class SearchAPIViewSet(viewsets.GenericViewSet):
    serializer_class = QueryTextSerializer

    # Override get_queryset
    def get_queryset(self):
        return Query.objects.none()

    @action(detail=False, methods=['post'], url_path='product-search-es')
    def search_via_es(self, request, *args, **kwargs):
        query = request.data.get("query_text")
        top_k = request.data.get("top_k")
        es = ElasticsearchIndex.get_instance()
        index_name = "movies_index"

        result = search_results_es(query, es, index_name, top_k)
        print("DEBUG result: ", result)
        print(result)
        return Response(result, status=200)

    @action(detail=False, methods=['post'], url_path='product-search')
    def search_lean_tile(self, request, *args, **kwargs):
        query = request.data.get("query_text")
        user_id = request.data.get("user")
        top_k = request.data.get("top_k")
        es = ElasticsearchIndex.get_instance()

        # Config params
        index_name = "movies_index"
        relevance_weight = 2.0

        results = search_results_es(query, es, index_name, top_k)
        # print("DEBUG result: ", results)
        # print(results)
        loaded_model = SearchRTR.get_instance()
        feature_store = FeatureStore.get_instance()

        movie_ids = [result[1] for result in results]
        # print("DEBUG movie_ids: ")
        # print(movie_ids)

        # print(f'user_id: {user_id}; query: {query}')

        sorted_movies_with_scores = rank_movies(loaded_model, user_id, query, movie_ids, relevance_weight,
                                                feature_store)
        print("DEBUG to print results")
        for movie_id, score, title, image_url, genres in sorted_movies_with_scores:
            print(f"Movie ID: {movie_id}, Predicted Score: {score}, Title: {title}, Url: {image_url}, Genres: {genres}")

        return Response(sorted_movies_with_scores, status=200)

    @action(detail=False, methods=['post'], url_path='product-search-faiss')
    def search_via_faiss(self, request, *args, **kwargs):
        query = request.data.get("query_text")
        top_k = request.data.get("top_k")
        print("DEBUG query, top_k: ")
        print(query)
        print(top_k)
        faiss_index, tokenizer, encoder, index_to_id = FaissIndex.get_instance()

        result = search_index(query, top_k, faiss_index, index_to_id, tokenizer, encoder)
        print("DEBUG result: ", result)
        print(result)
        return Response(result, status=200)

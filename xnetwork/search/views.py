from rest_framework import viewsets
from rest_framework.decorators import action
from .serializers import QueryTextSerializer
from .models import Query
from .ml_module import search_algorithm  # Import your ML module
from rest_framework.response import Response
import os, sys

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

        sorted_movies_with_scores = rank_movies(loaded_model, user_id, query, movie_ids, relevance_weight, feature_store)
        print("DEBUG to print results")
        for movie_id, score, title, image_url in sorted_movies_with_scores:
            print(f"Movie ID: {movie_id}, Predicted Score: {score}, Title: {title}, Url: {image_url}")

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

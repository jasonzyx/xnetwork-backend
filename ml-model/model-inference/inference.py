from transformers import DistilBertTokenizer, DistilBertModel
import torch
from feast import FeatureStore
import numpy as np
import pandas as pd
import torch.nn as nn

# Use DistilBert tokenizer and model
tokenizer = DistilBertTokenizer.from_pretrained('distilbert-base-uncased')
encoder = DistilBertModel.from_pretrained('distilbert-base-uncased')


def get_bert_embedding(text):
    inputs = tokenizer(text, return_tensors='pt', padding=True, truncation=True)
    outputs = encoder(**inputs)
    return outputs.last_hidden_state.mean(dim=1)


class MLP(nn.Module):
    def __init__(self, input_size):
        super(MLP, self).__init__()
        self.layers = nn.Sequential(
            nn.Linear(input_size, 128),
            nn.ReLU(),
            nn.Linear(128, 64),
            nn.ReLU(),
            nn.Linear(64, 1)
        )

    def forward(self, x):
        return self.layers(x)


def combine_features(query_emb, user_features, movie_emb):
    user_avg, user_std = user_features['avg_rating'][0], \
        user_features['rating_stddev'][0]
    combined = np.concatenate([query_emb, [user_avg, user_std], movie_emb])
    return combined


def prepare_features(userId, query, movieId, path):
    # Fetch features for user and movie
    store = FeatureStore(repo_path=path)
    user_features = store.get_online_features(
        features=["user_stats_view:avg_rating", "user_stats_view:rating_stddev"],
        entity_rows=[{"userId": userId}]
    ).to_dict()

    movie_features = store.get_online_features(
        features=["movies_view:title"],
        entity_rows=[{"movieId": movieId}]
    ).to_dict()

    # Extract movie title (replace with Feast if movie title is also a feature)
    movie_title = movie_features['title'][0]

    # Get embeddings
    query_emb = get_bert_embedding(query).detach().numpy().flatten()
    movie_emb = get_bert_embedding(movie_title).detach().numpy().flatten()

    # Combine features
    feature_vector = combine_features(query_emb, user_features, movie_emb)
    feature_tensor = torch.tensor(np.array([feature_vector]), dtype=torch.float32)

    return feature_tensor


def predict_score(model, userId, query, movieId, path):
    model.eval()
    with torch.no_grad():
        input_features = prepare_features(userId, query, movieId, path)
        output = model(input_features)
        predicted_score = output.item()
    return predicted_score


def batch_fetch_movie_features(movie_ids, store):
    # Fetch both 'title' and 'image_url' features
    movie_features = store.get_online_features(
        features=["movies_view:title", "movies_view:image", "movies_view:genres"],  # Include 'image_url' feature
        entity_rows=[{"movieId": movie_id} for movie_id in movie_ids]
    ).to_dict()

    # Return a dictionary with movie IDs as keys and both features as values
    return {
        movie_id: {
            'title': movie_features['title'][i],
            'image': movie_features['image'][i],
            'genres': movie_features['genres'][i]
        } for i, movie_id in enumerate(movie_ids)
    }


def get_feature_store(feature_store_path):
    return FeatureStore(repo_path=feature_store_path)


def rank_movies(model, user_id, query, movie_ids, relevance_weight, store):
    # Batch fetch movie features
    movie_info = batch_fetch_movie_features(movie_ids, store)
    user_features = store.get_online_features(
        features=["user_stats_view:avg_rating", "user_stats_view:rating_stddev"],
        entity_rows=[{"userId": user_id}]
    ).to_dict()
    # Predict scores for each movie
    movie_scores = []
    for movie_id in movie_ids:
        movie_title = movie_info[movie_id]['title']
        image = movie_info[movie_id]['image']
        genres = movie_info[movie_id]['genres']
        query_emb = get_bert_embedding(query).detach().numpy().flatten()
        movie_emb = get_bert_embedding(movie_title).detach().numpy().flatten()
        query_movie_dot_product = np.dot(query_emb, movie_emb)
        feature_vector = combine_features(query_emb, user_features, movie_emb)
        feature_tensor = torch.tensor(np.array([feature_vector]), dtype=torch.float32)

        model.eval()
        with torch.no_grad():
            output = model(feature_tensor)
            predicted_score = output.item()

        if image is not None:
            movie_scores.append((movie_id, predicted_score + relevance_weight * query_movie_dot_product, movie_title,
                                 image, genres))

    # Sort movies by score in descending order
    sorted_movies = sorted(movie_scores, key=lambda x: x[1], reverse=True)
    return sorted_movies


# [Model initialization and loading code stays the same]
def load_rtr_model(model_path='../model-artifacts/mlp_model.pth'):
    input_size = 768 * 2 + 2  # Example size: 2 * BERT embeddings + user avg and stddev
    loaded_model = MLP(input_size)
    # Load the model's state dictionary
    loaded_model.load_state_dict(torch.load(model_path))
    # Set the model to evaluation mode
    loaded_model.eval()
    return loaded_model

# used for testing the scripts locally
# def test_rtr():
#     # Example usage
#     user_id = 100
#     query = "toy story"
#     movie_ids = [1, 2, 3, 4]  # Replace with your list of movie IDs
#     relevance_weight = 2.0
#     feature_store_path = "../feast-feature-store/main_pangolin/feature_repo"
#     loaded_model = load_rtr_model()
#     store = get_feature_store(feature_store_path)
#     sorted_movies_with_scores = rank_movies(loaded_model, user_id, query, movie_ids, relevance_weight,
#                                             store)
#
#     print(f"query: {query}")
#     for movie_id, score, title in sorted_movies_with_scores:
#         print(f"Movie ID: {movie_id}, Predicted Score: {score}, Title: {title}")
#
# test_rtr()

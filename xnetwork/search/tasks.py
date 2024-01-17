from celery import shared_task
import os, sys
from .faiss_singleton import FaissIndex


# Get the directory of your current file
current_file_dir = os.path.dirname(__file__)

# Calculate the path to the 'ml-model' directory
ml_model_dir = os.path.join(current_file_dir, '../../ml-model/model-training')
# Add the 'ml-model' directory to sys.path
sys.path.append(ml_model_dir)
from load_model import search_index

@shared_task
def async_search(query, top_k):
    faiss_index, tokenizer, encoder, index_to_id = FaissIndex.get_instance()
    print("DEBUG index_to_id[1]: ")
    print(index_to_id[1])
    return search_index(query, top_k, faiss_index, index_to_id, tokenizer, encoder)
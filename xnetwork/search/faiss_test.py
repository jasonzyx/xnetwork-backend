import os
import sys


def main():
    # Get the directory of your current file
    current_file_dir = os.path.dirname(__file__)

    # Calculate the path to the 'ml-model' directory
    ml_model_dir = os.path.join(current_file_dir, '../../ml-model/model-training')
    # Add the 'ml-model' directory to sys.path
    sys.path.append(ml_model_dir)
    from load_model import search_index, load_models

    # Load models
    PATH_PREFIX = "../../ml-model/model-artifacts"  # Adjust the path as necessary
    faiss_index, tokenizer, encoder, index_to_id = load_models(PATH_PREFIX)
    results = search_index("toy", 10, faiss_index, index_to_id, tokenizer, encoder)
    results2 = search_index("story", 10, faiss_index, index_to_id, tokenizer, encoder)

    print("DEBUG: results: ")
    print(results)
    print(results2)
    return results


if __name__ == "__main__":
    main()

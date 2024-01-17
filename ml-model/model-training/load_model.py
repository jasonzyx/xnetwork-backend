from transformers import BertTokenizer, BertModel
import faiss
import numpy as np
import pickle


def load_models(path_prefix):
    print("load_models DEBUG: ")
    print(path_prefix)
    faiss_index = faiss.read_index(f"{path_prefix}/faiss_index.idx")
    tokenizer = BertTokenizer.from_pretrained(f"{path_prefix}/bert_model")
    encoder = BertModel.from_pretrained(f"{path_prefix}/bert_model")

    with open(f"{path_prefix}/index_to_id.pickle", 'rb') as handle:
        index_to_id = pickle.load(handle)

    print(index_to_id[0])
    return faiss_index, tokenizer, encoder, index_to_id


def search_index(query, k, faiss_index, index_to_id, tokenizer, encoder):
    query_embedding = encode_query(query, tokenizer, encoder)
    print(f"DEBUG: calling faiss_index with {k}...")
    print(f"DEBUG: query_embedding dimension...")
    print(query_embedding.shape)
    distances, indices = faiss_index.search(query_embedding, k)
    print(f"DEBUG: done calling faiss_index with {k}!")

    # Retrieve movie IDs for the indices
    return [(index_to_id[idx], distances[0][i]) for i, idx in enumerate(indices[0])]


def encode_titles_batch(titles, tokenizer, encoder, batch_size=32):
    all_embeddings = []

    for i in range(0, len(titles), batch_size):
        batch = titles[i:i + batch_size]
        inputs = tokenizer(batch, padding=True, truncation=True, return_tensors="pt", max_length=128)
        outputs = encoder(**inputs)
        embeddings = outputs.last_hidden_state.mean(dim=1).detach().numpy()
        all_embeddings.append(embeddings)

        print(f"Processed batch {i // batch_size + 1}/{len(titles) // batch_size + 1}")

    # Concatenate all batches
    all_embeddings = np.vstack(all_embeddings)
    return all_embeddings


def encode_query(query, tokenizer, encoder):
    print(f"DEBUG: encoding query: {query}...")
    inputs = tokenizer(query, padding=True, truncation=True, return_tensors="pt", max_length=128)
    outputs = encoder(**inputs)
    embeddings = outputs.last_hidden_state.mean(dim=1).detach().numpy()
    print(f"DEBUG: done encoding query: {query}")

    return embeddings
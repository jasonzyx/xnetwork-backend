from elasticsearch import Elasticsearch


class ElasticsearchIndex:
    _instance = None

    @classmethod
    def get_instance(cls):
        # Connect to Elasticsearch with HTTP (not HTTPS)
        es = Elasticsearch(
            ['http://localhost:9200']  # Use HTTP instead of HTTPS
        )

        # Define the index name
        index_name = 'movies_index'
        if cls._instance is None:
            cls._instance = es
        return cls._instance


def search_results_es(query_text, es, index_name, top_k):
    query = {
        "multi_match": {
            "query": query_text,
            "fields": ["title^2", "genres^0.5"]
        }
    }
    results = es.search(index=index_name, query=query, size=top_k)
    return [(hit['_source'].get('title'), hit['_source'].get('movieId'), hit['_source'].get('genres')) for hit in results['hits']['hits']]

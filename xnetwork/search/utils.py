import openai
import json


def extract_search_criteria(user_input, openai):
    """
    Extracts movie search criteria from the user's input.

    :param user_input: The user's message as a string.
    :param openai: openai client.
    :return: Dictionary with extracted information.
    """
    prompt = f"""
             Extract movie search query text from the following user input: '{user_input}',
             following the below requirement: 
             - Please output in English only and do not use languages other than English， regardless of the input language
             - Output in JSON format with 'query_text' and 'is_query', where 'is_query' indicates whether the user_input can 
             be formulated into a movie search query, and 'query_text' is the text used for movie engine search and needs
             to be in English, regardless of the input language.
             - If the input is a genre or a movie title, for the 'query_text' field of the output, 
             keep it as is except for correcting any typos.
             - If user input is an actor/actress name or something else, output relevant movie names only.
             - Please only output movie names or genres, no other words or descriptions.

             Example 1:
             user_input = "recommend a movie from Leonardo DiCaprio"
             output = {{ "query_text": "titanic", "is_query": True }}
             
             Example 4:
             user_input = "Leonardo DiCaprio"
             output = {{ "query_text": None, "is_query": False }}
             
             Example 5:
             user_input = "泰坦尼克号"
             output = {{ "query_text": titanic, "is_query": True }}

             Example 2:
             user_input = "adventre"
             output = {{ "query_text": "adventure", "is_query": True }}

             Example 3:
             user_input = "recommend a movie for a family of four for Saturday night"
             output = {{ "query_text": None, "is_query": False }}
             
             
             """

    print(prompt)

    model = "gpt-3.5-turbo"

    response = openai.ChatCompletion.create(
        model=model,
        messages=[{"role": "system", "content": prompt}],
        temperature=0,
    )

    extracted_info = response.get('choices', [])[0].get('message', {'content': ''})['content'].strip()
    parsed_json = json.loads(extracted_info)

    # Accessing elements
    query_text = parsed_json["query_text"]
    is_query = parsed_json["is_query"]

    return is_query, query_text


def can_generate_query(movie_search_info):
    return True

import openai


def extract_search_criteria(user_input, openai):
    """
    Extracts movie search criteria from the user's input.

    :param user_input: The user's message as a string.
    :param openai: openai client.
    :return: Dictionary with extracted information.
    """
    prompt = f"""
             Extract movie search query text from the following user input: '{user_input}'，following the below requirement: 
             - if the input is a genres, or the input is a movie title, do not process and output it as is except for 
             correcting the typo if any
             - if user input is an actor/actress name or something else, output relevant movie names only.
             - please output English only and don't use languages other than English, 
             - please only output movie names or genres，no other words or description
             """

    print(prompt)

    model = "gpt-3.5-turbo"

    response = openai.ChatCompletion.create(
        model=model,
        messages=[{"role": "system", "content": prompt}],
        temperature=0,
    )

    extracted_info = response.get('choices', [])[0].get('message', {'content': ''})['content'].strip()
    print("DEBUG: extracted_info")
    print(extracted_info)

    # Assuming the model returns a comma-separated list of key-value pairs
    # criteria = {}
    # for item in extracted_info.split(','):
    #     key_value = item.split(':')
    #     if len(key_value) == 2:
    #         criteria[key_value[0].strip()] = key_value[1].strip()

    return extracted_info


def generate_query_text(movie_search_info):
    """
    Generates a search query based on the accumulated movie search criteria.

    :param movie_search_info: Dictionary containing the search criteria.
    :return: A query string.
    """
    return movie_search_info
    # query_parts = []
    # for key, value in movie_search_info.items():
    #     # query_parts.append(f"{key}:{value}")
    #     query_parts.append(value)
    # return " ".join(query_parts)


def can_generate_query(movie_search_info):
    return True

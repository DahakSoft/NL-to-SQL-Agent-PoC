#
# agent.py
#
# A Proof-of-Concept AI agent that converts natural language questions
# into executable SQL SELECT statements using the Google Gemini API.
#

import os
import sys
import json
import requests

# --- CONFIGURATION ---
# The API key is read from an environment variable for security.
# To run this script, use the following command:
# API_KEY="your_api_key_here" python3 agent.py "your question here"
API_KEY = os.environ.get("API_KEY")
# MODEL_NAME = "gemini-2.5-pro"
MODEL_NAME = "gemini-2.5-flash"
API_URL = f"https://generativelanguage.googleapis.com/v1beta/models/{MODEL_NAME}:generateContent?key={API_KEY}"


# --------------------


def read_file_content(filepath: str) -> str:
    """
    Reads and returns the content of a specified file.
    Exits the script if the file is not found.

    Args:
        filepath: The path to the file.

    Returns:
        The content of the file as a string.
    """
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            return f.read()
    except FileNotFoundError:
        print(f"ERROR: Schema file not found at: {filepath}", file=sys.stderr)
        sys.exit(1)


def build_prompt(user_question: str, db_schema: str) -> dict:
    """
    Constructs the full prompt payload for the Gemini API.

    This function creates a structured conversation that includes a system directive,
    the database schema, and the user's question to guide the model's output.

    Args:
        user_question: The user's question in natural language.
        db_schema: A string containing the database schema (e.g., CREATE TABLE statements).

    Returns:
        A dictionary representing the JSON payload for the API request.
    """

    system_prompt = f"""
Your task is to act as an expert NL-to-SQL agent.
You will be given a user's question and a database schema.
You must convert the user's question into a valid, executable SQL SELECT statement for the MySQL standard.

This is the database schema you will be working with:
--- SCHEMA START ---
{db_schema}
--- SCHEMA END ---

You must adhere to the following rules:
1. ONLY output the SQL query.
2. Do not include any explanations, comments, or conversational text in your response.
3. Do not format the output with triple backticks (```). Return only the raw SQL text.
4. If the user's question cannot be answered using the provided schema, output the single word: ERROR.
"""

    # We use a few-shot approach by providing the system prompt as the first
    # message in the conversation history, followed by the actual user question.
    contents = [
        {
            "role": "user",
            "parts": [{"text": system_prompt}]
        },
        {
            "role": "model",
            "parts": [{"text": "Understood. Awaiting user question."}]
        },
        {
            "role": "user",
            "parts": [{"text": user_question}]
        }
    ]
    return {"contents": contents}


def generate_sql(prompt: dict) -> str:
    """
    Sends the request to the Google Gemini API and returns the generated SQL.

    Args:
        prompt: The JSON payload containing the conversation history and prompt.

    Returns:
        The generated SQL query as a string, or an error message.
    """

    headers = {
        'Content-Type': 'application/json',
        'User-Agent': 'NL-to-SQL-Agent-PoC/1.0'
    }

    try:
        response = requests.post(API_URL, headers=headers, data=json.dumps(prompt))

        # Raise an exception for HTTP error codes (4xx or 5xx)
        response.raise_for_status()

        response_json = response.json()

        # Safely access the generated text from the response
        if 'candidates' in response_json and len(response_json['candidates']) > 0:
            content = response_json['candidates'][0]['content']['parts'][0]['text']
            return content.strip()
        else:
            # Handle cases where the response is valid but unexpected (e.g., safety blocks)
            print(f"WARNING: Received an unexpected response structure: {response_json}", file=sys.stderr)
            return "ERROR: Invalid response structure from API"

    except requests.exceptions.HTTPError as http_err:
        print(f"HTTP ERROR: {http_err}", file=sys.stderr)
        print(f"Response Details: {http_err.response.text}", file=sys.stderr)
        return "ERROR: The API request failed with an HTTP error"
    except Exception as e:
        print(f"An unexpected error occurred: {e}", file=sys.stderr)
        return "ERROR: An unexpected error occurred during the API call"


def main():
    """
    The main execution function for the script.

    It validates inputs, orchestrates the API call, and prints the final result.
    """

    # 1. Validate that the API key is set
    if not API_KEY:
        print("ERROR: The API_KEY environment variable is not set.", file=sys.stderr)
        print("Usage: API_KEY=\"your_key\" python3 agent.py \"your question\"", file=sys.stderr)
        sys.exit(1)

    # 2. Validate that a user question was provided
    if len(sys.argv) < 2:
        print("ERROR: No user question provided.", file=sys.stderr)
        print("Example: python3 agent.py \"show me all products in the electronics category\"", file=sys.stderr)
        sys.exit(1)

    # The user's question is passed as the first argument after the script name.
    # We join all arguments after the script name to handle questions with spaces.
    user_question = " ".join(sys.argv[1:])

    # 3. Read the database schema
    db_schema = read_file_content("schema.sql")

    print("--- Input Data ---")
    print(f"User Question: {user_question}\n")

    # 4. Build the prompt and generate the SQL
    prompt = build_prompt(user_question, db_schema)
    generated_sql = generate_sql(prompt)

    print("--- Output ---")
    print("Generated SQL:")
    print(generated_sql)


# Standard Python entry point guard
if __name__ == "__main__":
    main()
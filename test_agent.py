# File: test_agent.py
# Unit tests for the NL-to-SQL agent.

import unittest
from unittest.mock import patch, Mock
import os

# We need to import the functions we want to test from our agent script.
# Make sure the file is named 'agent.py' for this to work.
from agent import build_prompt, generate_sql


class TestAgent(unittest.TestCase):

    def setUp(self):
        """This method is called before each test function."""
        self.db_schema = """
                         CREATE TABLE products \
                         ( \
                             id    INT PRIMARY KEY, \
                             name  VARCHAR(255)   NOT NULL, \
                             price DECIMAL(10, 2) NOT NULL
                         ); \
                         """
        # Set a dummy API key for testing purposes
        os.environ['API_KEY'] = 'dummy_api_key_for_testing'

    def test_build_prompt_structure(self):
        """Tests if the build_prompt function creates the correct JSON structure."""
        print("\nRunning: test_build_prompt_structure")

        user_question = "show me all products"
        prompt = build_prompt(user_question, self.db_schema)

        # Check if the main key 'contents' exists
        self.assertIn('contents', prompt)

        # Check if there are 3 parts in the conversation (system, model, user)
        self.assertEqual(len(prompt['contents']), 3)

        # Check if the user's question is correctly placed in the last message
        last_message = prompt['contents'][-1]
        self.assertEqual(last_message['role'], 'user')
        self.assertEqual(last_message['parts'][0]['text'], user_question)
        print("OK")

    # The @patch decorator temporarily replaces 'requests.post' with a mock object.
    # This allows us to test the 'generate_sql' function WITHOUT making a real API call.
    @patch('agent.requests.post')
    def test_generate_sql_success(self, mock_post):
        """Tests the generate_sql function for a successful API call scenario."""
        print("\nRunning: test_generate_sql_success")

        # Configure the mock response that the fake 'requests.post' will return
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "candidates": [
                {
                    "content": {
                        "parts": [
                            {"text": "SELECT * FROM products;"}
                        ]
                    }
                }
            ]
        }
        # This function will be called when response.raise_for_status() is executed.
        # Since it does nothing, it simulates a successful (2xx) status code.
        mock_response.raise_for_status.return_value = None
        mock_post.return_value = mock_response

        prompt = {"contents": []}  # The content doesn't matter here, as we are mocking the call
        result = generate_sql(prompt)

        # Check if the function correctly extracted the SQL from the mock response
        self.assertEqual(result, "SELECT * FROM products;")
        print("OK")

    @patch('agent.requests.post')
    def test_generate_sql_http_error(self, mock_post):
        """Tests how generate_sql handles an HTTP error from the API."""
        print("\nRunning: test_generate_sql_http_error")

        # Configure the mock response to simulate an error (e.g., 400 Bad Request)
        mock_response = Mock()
        mock_response.status_code = 400

        # We need to configure the .response attribute for the exception object
        from requests.exceptions import HTTPError
        http_error = HTTPError("400 Client Error")
        http_error.response = Mock()
        http_error.response.text = "Mocked error details from API"
        mock_response.raise_for_status.side_effect = http_error

        mock_post.return_value = mock_response
        prompt = {"contents": []}
        result = generate_sql(prompt)

        # Check if the function returned the expected error message
        self.assertTrue(result.startswith("ERROR: The API request failed"))
        print("OK")


# This makes the script runnable from the command line
if __name__ == '__main__':
    unittest.main()
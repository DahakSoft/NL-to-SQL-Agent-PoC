# Natural Language to SQL Agent (Proof of Concept)

A functional proof-of-concept for an AI agent that converts natural language questions into executable SQL SELECT statements using the Google Gemini API.

This project serves as a demonstration of building a reliable, logic-driven application around a Large Language Model (LLM) to perform a structured data task.

---

## Features

- **Natural Language Input**: Accepts a user's question in plain language.
- **Schema-Aware Generation**: The agent is provided with a database schema to generate contextually correct queries.
- **Structured Output**: Designed to output only a raw, executable SQL query, making it suitable for programmatic use.
- **Error Handling**: Gracefully handles API errors and returns clear messages.
- **Tested Logic**: Includes unit tests to verify core functionality, such as prompt construction and response parsing.

---

## How It Works

The architecture is straightforward:

1.  **Input**: The script takes a natural language question as a command-line argument.
2.  **Schema Loading**: It reads a `schema.sql` file to understand the target database structure.
3.  **Prompt Engineering**: It constructs a detailed prompt for the Gemini API, including the schema, a system directive, and the user's question. This uses a "few-shot" approach to guide the model.
4.  **API Call**: It sends the request to the Google Gemini API.
5.  **Output**: It prints the generated SQL query to the standard output.

---

## Getting Started

### Prerequisites

- Python 3.8+
- The `requests` library (`pip install requests`)

### Installation

1.  Clone the repository:
    ```bash
    git clone https://github.com/DahakSoft/NL-to-SQL-Agent-PoC.git
    cd NL-to-SQL-Agent-PoC
    ```

### Running the Agent

The script requires a Google Gemini API key to be passed as an environment variable.

Execute the script from your terminal:

```bash
API_KEY="YOUR_GEMINI_API_KEY" python3 agent.py "YOUR_QUESTION_HERE"
```
Example Usage:
```Bash
API_KEY="AIza..." python3 agent.py "show me all products that cost more than 500"
```

**Example Output:**
```Bash
--- Input Data ---
User Question: show me all products that cost more than 500
--- Output ---
Generated SQL:
SELECT * FROM products WHERE price > 500;
```
---

## Testing

The project includes a suite of unit tests to ensure the core logic is working correctly. To run the tests, execute the following command from the project's root directory:

```bash
python3 -m unittest test_agent.py
```
---

## About the Author

This proof-of-concept was developed by **Robert Mieńko** as a demonstration of building robust, AI-powered data tools.

For more information or to discuss a potential project, please visit [**dahaksoft.pl**](https://www.dahaksoft.pl).
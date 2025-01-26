from dotenv import load_dotenv
import streamlit as st
import os
import sqlite3
import google.generativeai as genai

# Set page config as the first Streamlit command
# st.set_page_config(page_title="Gemini SQL Query Retriever", layout="wide")

# Load environment variables from .env file
load_dotenv()  # Load all environment variables from .env

# Configure the API key
genai.configure(api_key=os.getenv("GOOGLE_API_KEYS"))

# Function to load Google Gemini model and provide the query response
def get_gemini_response(question, prompt):
    try:
        model = genai.GenerativeModel('gemini-pro')
        response = model.generate_content([prompt[0], question])  # Using a single prompt; multiple prompts can be used if needed
        if response and response.text:
            return response.text.strip()
        else:
            raise ValueError("Empty response from the model")
    except Exception as e:
        st.error(f"Error in generating response: {e}")
        return ""

# Function to retrieve query from the SQLite database
def read_sql_query(sql, db):
    try:
        conn = sqlite3.connect(db)
        cur = conn.cursor()
        cur.execute(sql)
        rows = cur.fetchall()
        conn.close()
        return rows
    except sqlite3.Error as e:
        st.error(f"SQLite error: {e}")
        return []
    except Exception as e:
        st.error(f"Error: {e}")
        return []

# Defining the prompt to make the application more efficient
prompt = [
    """
    You are an expert in converting English questions into SQL queries!
    The SQL database is named `STUDENT` and has the following columns: `NAME`, `CLASS`, and `SECTION`.

    Examples:
    1. Question: "How many entries of records are present?"
       SQL Query: SELECT COUNT(*) FROM STUDENT;

    2. Question: "How many students study in the Data Science class?"
       SQL Query: SELECT * FROM STUDENT WHERE CLASS = 'Data Science';

    Important Notes:
    - Do not include backticks or triple backticks (` ``` `) around the query.
    - Do not include the word "SQL" in the output.
    """
]

# Streamlit app setup
st.header("Gemini App to Retrieve SQL Data")

question = st.text_input("Ask your question here:", key="input")

if st.button("Submit"):
    with st.spinner("Processing..."):
        response = get_gemini_response(question, prompt)
        if response:
            st.text(f"Generated SQL Query: {response}")  # Show the generated query
            rows = read_sql_query(response, "student.db")
            
            if rows:
                st.subheader("Query Results")
                st.table(rows)  # Display the rows in a table format
            else:
                st.error("No data found or an error occurred.")
        else:
            st.error("Failed to generate a valid SQL query.")

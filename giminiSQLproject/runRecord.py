from dotenv import load_dotenv
import streamlit as st
import os
import sqlite3

# Set page config as the first Streamlit command
st.set_page_config(page_title="Student Data Entry", layout="wide")

# Load environment variables from .env file
load_dotenv()

# Initialize database connection
def get_db_connection():
    conn = sqlite3.connect("student.db")
    return conn

# Function to check if a student ID already exists in the database or session state
def student_id_exists(student_id):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('SELECT COUNT(*) FROM STUDENT WHERE STUDENT_ID = ?', (student_id,))
    count_db = cursor.fetchone()[0]
    conn.close()
    
    count_session = sum(1 for record in st.session_state.get('records', []) if record['student_id'] == student_id)
    
    return count_db > 0 or count_session > 0

# Function to insert a new student record into the session state
def add_student_record(student_id, name, cls, section, marks):
    if 'records' not in st.session_state:
        st.session_state['records'] = []
    st.session_state['records'].append({'student_id': student_id, 'name': name, 'class': cls, 'section': section, 'marks': marks})

# Function to submit all session records to the database
def submit_to_database():
    conn = get_db_connection()
    cursor = conn.cursor()
    records = st.session_state.get('records', [])
    for record in records:
        cursor.execute('INSERT INTO STUDENT (STUDENT_ID, NAME, CLASS, SECTION, MARKS) VALUES (?, ?, ?, ?, ?)', 
                       (record['student_id'], record['name'], record['class'], record['section'], record['marks']))
    conn.commit()
    conn.close()
    st.session_state['records'] = []
    st.success("All records added to the database successfully!")

# Function to delete a specific student record in session state
def delete_student_record(index):
    del st.session_state['records'][index]
    st.query_params()  # Refresh the page

# Streamlit app
def streamlit_app():
    st.header("Student Data Entry Application")

    # Input fields for data entry
    col1, col2, col3, col4, col5 = st.columns(5)

    with col1:
        student_id = st.text_input("Student ID", key="student_id_input")

    with col2:
        name = st.text_input("Name", key="name_input")

    with col3:
        cls = st.text_input("Class", key="class_input")

    with col4:
        section = st.text_input("Section", key="section_input")

    with col5:
        marks = st.number_input("Marks", min_value=0, max_value=100, step=1, key="marks_input")

    # Button to add data to session state
    if st.button("Add Record"):
        if student_id and name and cls and section and marks:
            if student_id_exists(student_id):
                st.warning(f"Student ID {student_id} already exists. Please use a different Student ID.")
            else:
                add_student_record(student_id, name, cls, section, marks)
                st.success("Record added successfully!")
            # Reset input boxes using callback
            # clear_inputs()

    # Display all records added in the current session
    if 'records' in st.session_state and st.session_state['records']:
        st.subheader("Current Session Records")
        for idx, record in enumerate(st.session_state['records']):
            cols = st.columns(6)
            cols[0].write(record['student_id'])
            cols[1].write(record['name'])
            cols[2].write(record['class'])
            cols[3].write(record['section'])
            cols[4].write(record['marks'])
            if cols[5].button("Delete", key=f"delete_{idx}"):
                delete_student_record(idx)

    # Function to edit a specific student record in session state
    def edit_student_record(index, student_id, name, cls, section, marks):
        st.session_state['records'][index] = {'student_id': student_id, 'name': name, 'class': cls, 'section': section, 'marks': marks}

    # Dropdown to select which record to edit
    if 'records' in st.session_state and st.session_state['records']:
        record_to_edit = st.selectbox("Select record to edit", options=[""] + list(range(len(st.session_state['records']))), format_func=lambda x: st.session_state['records'][x]['student_id'] if x != "" else "")
        
        if record_to_edit != "":
            record = st.session_state['records'][record_to_edit]
            col1, col2, col3, col4, col5 = st.columns(5)

            with col1:
                new_student_id = st.text_input("Student ID", value=record['student_id'], key=f"edit_student_id_{record_to_edit}")

            with col2:
                new_name = st.text_input("Name", value=record['name'], key=f"edit_name_{record_to_edit}")

            with col3:
                new_cls = st.text_input("Class", value=record['class'], key=f"edit_class_{record_to_edit}")

            with col4:
                new_section = st.text_input("Section", value=record['section'], key=f"edit_section_{record_to_edit}")

            with col5:
                new_marks = st.number_input("Marks", min_value=0, max_value=100, step=1, value=record['marks'], key=f"edit_marks_{record_to_edit}")

            if st.button("Update Record"):
                edit_student_record(record_to_edit, new_student_id, new_name, new_cls, new_section, new_marks)
                st.success("Record updated successfully!")

    # Final submit button to save all records to the database
    if st.button("Submit All to Database"):
        submit_to_database()

# Call the function to run the app
if __name__ == "__main__":
    streamlit_app()

'''
Main entry point for streamlit app.
'''
from st_pages import Page, show_pages
import streamlit as st

# Specify what pages should be shown in the sidebar, and what their titles
# and icons should be
# show_pages(
#     [
#         Page("scholarship_app/pages/home.py", "Home"),
#         Page("scholarship_app/pages/scholarship_management.py", "Scholarship Management"),
#         Page("scholarship_app/pages/login.py", "Log In"),
#         Page("scholarship_app/pages/download.py", "Download File"),
#         Page("scholarship_app/pages/student_metrics.py", "Student Metrics"),
#         Page("scholarship_app/pages/import.py", "Import Data"),
#         Page("scholarship_app/pages/export.py", "Export Data"),
#     ]
# )
st.write('hello')
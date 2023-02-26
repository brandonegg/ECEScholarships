
'''
Render view for import data page
'''
import streamlit as st
from utils.html import centered_text

st.title("Import Data")
st.write("Add files to be imported. Multiple files can be selected and the application will attempt to merge them.")
form = st.form(key="import_data_form")
files = form.file_uploader('Data Sources:')
form.markdown(centered_text('<em>supports both excel and csv format</em>'), unsafe_allow_html=True)

submit = form.form_submit_button('Import')

if submit:
    # Handle imported files.
    print(submit)
    print(files)
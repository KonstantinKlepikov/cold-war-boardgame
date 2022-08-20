import streamlit as st
import requests


st.set_page_config(page_title='Dashboard', layout="wide")

# main
st.title('Make request to backend')

if st.button('Get response'):
    r = requests.get('http://backend:8000/')
    st.text(r.text)

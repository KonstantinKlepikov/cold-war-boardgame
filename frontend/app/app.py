import streamlit as st
import requests, os
from urllib.parse import urljoin


API_ROOT = os.environ.get('API_ROOT')
if not API_ROOT:
    raise RuntimeError('Api root uri not set')


st.set_page_config(page_title='Dashboard', layout="wide")

# main
st.title('Make request to backend')

if st.button('Get response'):
    r = requests.get(urljoin(API_ROOT, '/'))
    st.text(r.text)

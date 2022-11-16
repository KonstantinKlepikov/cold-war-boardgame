import streamlit as st
import requests, os


API_ROOT = os.environ.get('API_ROOT')
if not API_ROOT:
    raise RuntimeError('Api root uri not set')

API_VERSION: str = "api/v1"


st.set_page_config(page_title='Dashboard', layout="wide")


# main
clear_all = st.empty()
with clear_all.container():
    access_token = None

    with st.form("login_form"):
        st.write('Login to get game data.')
        login = st.text_input(label='login:')
        password = st.text_input(label='password:')
        submit = st.form_submit_button(label='login')

        if submit:
            url = os.path.join(API_ROOT, API_VERSION, 'user/login')
            r = requests.post(
                url,
                headers = {
                    'accept': 'application/json',
                    'Content-Type': 'application/x-www-form-urlencoded',
                        },
                data={"username": f"{login}", "password": f"{password}"}
                )

            if r.status_code == 200:
                access_token=r.json()['access_token']
                clear_all.empty()

            elif r.status_code == 400:
                st.text(r.json()['detail'])

            else:
                st.text(r.text)

if access_token:
    st.balloons()
    st.write(f'{access_token=}')
    logout = st.button(f'{login} logout')
    if logout:
        access_token = None

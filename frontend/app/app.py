import streamlit as st
import requests, os


API_ROOT = os.environ.get('API_ROOT')
if not API_ROOT:
    raise RuntimeError('Api root uri not set')

API_VERSION: str = "api/v1"


st.set_page_config(page_title='Dashboard', layout="wide")

main = st.empty()
left, right = st.columns([3, 1])

with main.container():

    with left:
        st.write('me')

    with right:

        st.markdown(f"Login: **{st.session_state.get('login', 'not logged')}**")

        if st.session_state.get('access_token') is None:

            with st.form("login_form"):
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
                        st.session_state['login'] = login
                        st.session_state['access_token'] = r.json()['access_token']
                        main.empty()

                    elif r.status_code == 400:
                        st.text(r.json()['detail'])

                    else:
                        st.text(r.text)

        if st.session_state.get('access_token'):

            logout = st.button(f"logout")
            if logout:
                st.session_state['access_token'] = None

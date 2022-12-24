import streamlit as st
import requests, os
import streamlit_nested_layout
from typing import Dict
from requests import Response
from streamlit.delta_generator import DeltaGenerator


API_ROOT = os.environ.get('API_ROOT')
if not API_ROOT:
    raise RuntimeError('Api root uri not set')

API_VERSION: str = "api/v1"


st.set_page_config(page_title='Dashboard', layout="wide")


def write_error(r: Response) -> None:
    """Write error from response

    Args:
        r (Response): response object
    """
    st.write(r.json()['detail'])
    st.stop()


def get_current_data() -> None:
    """Request for current data
    """
    token = st.session_state.get('access_token')
    url = os.path.join(API_ROOT, API_VERSION, 'game/data/current')
    r = requests.post(
        url,
        headers={
            'Authorization': f'Bearer {token}'
                }
            )
    if r.status_code == 200:
        st.session_state['current'] = r.json()
    else:
        write_error(r)

@st.cache
def get_static_data() -> None:
    """Request for static data
    """
    url = os.path.join(API_ROOT, API_VERSION, 'game/data/static')
    r = requests.get(url)
    if r.status_code == 200:
        st.session_state['static'] = r.json()
    else:
        write_error(r)

@st.cache
def get_static_objectives() -> Dict[str, dict]:
    """Get dict of objectives cards

    Returns:
        Dict[str, dict]: objective mapping
    """
    return {card['name']: card for card in st.session_state['static']['objective_cards']}

def show_current_data() -> None:
    """Display important game data in right side
    """
    current = st.session_state['current']
    st.subheader("Current game")
    st.markdown(f"turn: **{current['game_steps']['game_turn']}**")
    st.markdown(f"step: **{current['game_steps']['turn_phase']}**")
    st.markdown(f"is_game_end: **{current['game_steps']['is_game_end']}**")
    st.markdown(f"player faction: **{current['players'][0]['faction']}**")
    st.markdown(f"player priority: **{current['players'][0]['has_priority']}**")
    st.markdown("---")

def show_objectives():
    """Display objective deck and mission card
    """
    current = st.session_state['current']['game_decks']
    st.subheader("Objective deck")
    st.markdown(f"Deck len: **{current['objective_deck']['deck_len']}**")

    with st.expander("Objectives pile"):
        if current['objective_deck']['pile']:
            for card in current['objective_deck']['pile']:
                st.caption(card)
        else:
            st.caption('empty')

    st.markdown(f"Mission card: **{current['mission_card']}**")
    if current['mission_card'] is not None:
        with st.expander("Mission card data"):
            st.caption(get_static_objectives()[current['mission_card']])

    st.markdown("---")

def show_groups():
    """Display group deck
    """
    current = st.session_state['current']['game_decks']['group_deck']
    st.subheader("Group deck")
    st.markdown(f"Deck len: **{current['deck_len']}**")

    with st.expander("Groups pile"):
        if current['pile']:
            for card in current['pile']:
                st.caption(card)
        else:
            st.caption('empty')

    st.markdown("---")

def start_new_game() -> None:
    """Start new game
    """
    token = st.session_state.get('access_token')
    url = os.path.join(API_ROOT, API_VERSION, 'game/create')
    r = requests.post(
        url,
        headers={
            'Authorization': f'Bearer {token}'
                }
            )
    if r.status_code != 201:
        write_error(r)


def log_in(holder: DeltaGenerator) -> None:
    """Right side log in scenario

    Args:
        holder (DeltaGenerator): holder for change and clear displayed data
    """
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
                st.session_state['access_token'] = r.json()['access_token']
                st.session_state['login'] = login
                holder.empty()
            else:
                write_error(r)

def autorized() -> None:
    """Right side autorized scenario
    """
    st.caption('Login as:')
    st.header(f"**{st.session_state['login']}**")
    col1, col2, col3 = st.columns([1, 1, 1])
    with col1:
        load_game = st.button("load game")
    with col2:
        new_game = st.button("new game")
    with col3:
        logout = st.button("logout")
    st.markdown("---")

    if load_game:
        get_current_data()

    if new_game:
        start_new_game()
        get_current_data()

    if logout:
        st.session_state['access_token'] = None
        st.session_state['login'] = None
        st.session_state['current'] = None
        st.experimental_rerun()


def choose_side(holder: DeltaGenerator) -> None:
    """Choise side scenario

    Args:
        holder (DeltaGenerator): holder for change and clear displayed data
    """
    st.subheader("Choose your side")
    choice = st.radio(
        label='Choose your side:',
        options=['cia', 'kgb'],
        horizontal=True,
        label_visibility='collapsed'
            )
    push = st.button("choose")
    st.markdown("---")

    if push and choice:
        token = st.session_state.get('access_token')
        url = os.path.join(API_ROOT, API_VERSION, f'game/preset/faction?q={choice}')
        r = requests.patch(
            url,
            headers={
                'Authorization': f'Bearer {token}'
                    }
                )
        if r.status_code == 200:
            get_current_data()
            holder.empty()
        else:
            write_error(r)

def main():

    left, right = st.columns([3, 1])

    with left:
        st.header("Opponent")
        st.markdown("---")
        st.markdown("---")
        st.header("Player")

    with right:

        holder1 = st.empty()
        with holder1.container():
            if st.session_state.get('access_token') is None:
                log_in(holder1)

        if st.session_state.get('access_token'):
            get_static_data()
            autorized()

            if st.session_state.get('current') is not None \
                    and st.session_state['current']['players'][0]['faction'] is None:
                holder2 = st.empty()
                with holder2.container():
                    choose_side(holder2)

            if st.session_state.get('current'):
                show_current_data()
                show_objectives()
                show_groups()


if __name__ == '__main__':
    main()

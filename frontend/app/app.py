import streamlit as st
import requests, os, time
import streamlit_nested_layout
from typing import Dict, Literal
from requests import Response
from streamlit.delta_generator import DeltaGenerator


API_ROOT = os.environ.get('API_ROOT')
if not API_ROOT:
    raise RuntimeError('Api root uri not set')

API_VERSION: str = "api/v1"


st.set_page_config(page_title='Dashboard', layout="wide")


def show_api_error(r: Response) -> None:
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
        show_api_error(r)


@st.cache
def get_static_data() -> None:
    """Request for static data
    """
    url = os.path.join(API_ROOT, API_VERSION, 'game/data/static')
    r = requests.get(url)
    if r.status_code == 200:
        st.session_state['static'] = r.json()
    else:
        show_api_error(r)


def show_current_data() -> None:
    """Display important game data in right side
    """
    current = st.session_state['current']
    st.subheader("Current game")

    if current['steps']['is_game_ends'] == True:
        st.caption("this game is end")

    if current['players']['player']['faction'] is None:

        st.markdown(f"turn: -")
        st.markdown(f"phase: -")
        st.markdown(f"player faction: -")
        st.markdown(f"balance: -")

    elif current['players']['player']['has_balance'] is None:
        st.caption('Push next phase button')
        st.markdown(f"turn: -")
        st.markdown(f"phase: -")
        st.markdown(f"player faction: **{current['players']['player']['faction']}**")
        st.markdown(f"balance: -")

    else:
        st.markdown(f"turn: **{current['steps']['game_turn']}**")
        st.markdown(f"phase: **{current['steps']['turn_phase']}**")
        st.markdown(f"player faction: **{current['players']['player']['faction']}**")
        priority = current['players']['player']['has_balance']
        if priority == True:
            p = 'player'
        elif priority == False:
            p = 'opponent'
        st.markdown(f"balance: **{p}**")

    st.markdown("---")


def show_objectives():
    """Display objective deck and mission card
    """
    current = st.session_state['current']['decks']['objectives']
    st.subheader("Objective deck")
    st.markdown(f"in deck now **{len(current['deck'])}** cards")

    with st.expander("Objectives pile"):
        if current['pile']:
            for card in current['pile']:
                st.caption(card)
        else:
            st.caption('empty')

    mission = current['mission'] if current['mission'] is not None else '-'
    st.markdown(f"Mission card: **{mission}**")
    with st.expander("Mission card data"):
        if current['mission'] is None:
            st.caption('empty')
        else:
            m = st.session_state['static']['objectives'][current['mission']]
            st.caption(f"population: {m['population']}")
            st.caption(f"stability: {m['stability']}")
            st.caption(f"bias icons: {', '.join(m['bias_icons'])}")
            st.caption(f"victory points: {m['victory_points']}")
            st.caption(f"special ability: {m['special_ability']}")

    st.markdown("---")


def show_groups():
    """Display group deck
    """
    current = st.session_state['current']['decks']['groups']
    st.subheader("Group deck")
    st.markdown(f"in deck now **{len(current['deck'])}** cards")

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
        show_api_error(r)


def show_log_in(holder: DeltaGenerator) -> None:
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
                show_api_error(r)


def show_autorized() -> None:
    """Right side autorized scenario
    """
    st.caption('Login as:')
    st.header(f"**{st.session_state['login']}**")
    col1, col2, col3, _ = st.columns([1, 1, 1, 1])
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


def show_choose_side(holder: DeltaGenerator) -> None:
    """Choise side scenario

    Args:
        holder (DeltaGenerator): holder for change and clear displayed data
    """
    st.subheader("Choose your faction")
    choice = st.radio(
        label='Choose your faction:',
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
            show_api_error(r)


def show_coin(holder: DeltaGenerator, text: str) -> None:
    """Show image picture

    args:
        holder (DeltaGenerator): holder for change and clear displayed data
    """
    holder.text(
    f"""
    {text}

    ------>  +====+  <------
    ------>  |(::)|  <------
    ------>  | )( |  <------
    ------>  |(..)|  <------
    ------>  +====+  <------

    """
            )


def next_step(
    step: Literal['turn', 'phase'],
    holder: DeltaGenerator
        ) -> None:
    """Get next phase or turn

    Args:
        step (str): typo of next
        holder (DeltaGenerator): holder for change and clear displayed data
    """
    token = st.session_state.get('access_token')
    url = os.path.join(API_ROOT, API_VERSION, f'game/next_{step}')
    r = requests.patch(
        url,
        headers={
            'Authorization': f'Bearer {token}'
                }
            )
    if r.status_code == 200:
        if step == 'turn':
            text = "-> go to next turn"
        else:
            if st.session_state['current']['steps']['turn_phase'] is None:
                text = "-> set priority and mission card"
            else:
                text = "-> go to the next phase"
        show_coin(holder, text)
        time.sleep(2)
        holder.empty()
        get_current_data()
        if st.session_state['current']['steps']['turn_phase'] is None:
            next_step('phase', holder)
    else:
        show_api_error(r)


def show_next(holder: DeltaGenerator):
    """Show next turn/phase scenario
    """
    col1, col2, _ = st.columns([1, 1, 2])

    phase = st.session_state['current']['steps']['turn_phase']
    faction = st.session_state['current']['players']['player']['faction']

    p = False if phase != 'detente' and faction is not None else True
    t = False if phase == 'detente' else True

    with col1:
        st.button(
            'next phase',
            disabled=p,
            on_click=next_step,
            args=('phase', holder)
                )
    with col2:
        st.button(
            'next turn',
            disabled=t,
            on_click=next_step,
            args=('turn', holder)
                )


def show_special_cards_of_opponent():

    buttons = zip(
        st.columns([1, 1, 1, 1, 1, 1]),
        st.session_state['static']['objectives_ablilities']
            )

    for b in buttons:  # FIXME: fixme - here is another abilities
        with b[0]:
            if b[1] in st.session_state['current']['players']['opponent']['awaiting_abilities']:
                st.write(b[1])
            else:
                st.caption(b[1])


def show_special_cards_of_player():

    buttons = zip(
        st.columns([1, 1, 1, 1, 1, 1]),
        st.session_state['static']['objectives_ablilities']
            )

    for b in buttons:  # FIXME: fixme - here is another abilities
        with b[0]:
            p = False if b[1] in st.session_state['current']['players']['player']['awaiting_abilities'] else True
            st.button(b[1], disabled=p)


def main():

    get_static_data()

    left, right = st.columns([3, 1], gap='medium')

    with left:
        st.header("Opponent")
        if st.session_state.get('current') is not None:
            show_special_cards_of_opponent()
        st.markdown("---")
        st.markdown("---")
        st.header("Player")
        if st.session_state.get('current') is not None:
            show_special_cards_of_player()

    with right:

        holder1 = st.empty()
        with holder1.container():
            if st.session_state.get('access_token') is None:
                show_log_in(holder1)

        if st.session_state.get('access_token'):
            show_autorized()

            if st.session_state.get('current') is not None \
                    and st.session_state['current']['players']['player']['faction'] is None:
                holder2 = st.empty()
                with holder2.container():
                    show_choose_side(holder2)

            if st.session_state.get('current') is not None:
                holder3 = st.empty()
                show_current_data()
                show_objectives()
                show_groups()
                show_next(holder3)


if __name__ == '__main__':
    main()

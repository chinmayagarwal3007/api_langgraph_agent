import streamlit as st
from api_client import APIClient

st.set_page_config(page_title="API Copilot", layout="wide")

# ---------------- STATE ---------------- #

if "client" not in st.session_state:
    st.session_state.client = APIClient()

if "logged_in" not in st.session_state:
    st.session_state.logged_in = False

if "current_session" not in st.session_state:
    st.session_state.current_session = None

if "username" not in st.session_state:
    st.session_state.username = None

client = st.session_state.client

# ---------------- AUTH UI ---------------- #

def auth_ui():
    st.title("🔐 API Copilot Login")

    tab1, tab2 = st.tabs(["Login", "Signup"])

    with tab1:
        username = st.text_input("Username")
        password = st.text_input("Password", type="password")

        if st.button("Login"):
            res = client.login(username, password)
            if res.status_code == 200:
                st.session_state.logged_in = True
                st.session_state.username = username
                st.rerun()
            else:
                st.error(res.text)

    with tab2:
        username = st.text_input("New Username")
        password = st.text_input("New Password", type="password")

        if st.button("Signup"):
            res = client.signup(username, password)
            if res.status_code == 200:
                st.success("Signup successful")
            else:
                st.error(res.text)

# ---------------- HELPER ---------------- #

def get_session_title(session_id):
    """
    Session title = first user message up to 100 chars.
    """
    res = client.get_messages(session_id)

    if res.status_code != 200:
        return f"Session {session_id}"

    messages = res.json()

    for m in messages:
        if m["role"] == "user":
            return (m["content"][:10]+"........") if len(m["content"]) > 10 else m["content"]

    return f"Session {session_id}"


# ---------------- CHAT UI ---------------- #

def chat_ui():

    # ===== SIDEBAR ===== #

    with st.sidebar:

        st.title("💬 Sessions")

        # Logged in user display
        st.markdown(f"👤 **{st.session_state.username}**")

        if st.button("🚪 Sign out"):
            st.session_state.clear()
            st.rerun()

        st.divider()

        # Create new chat
        if st.button("➕ New Chat"):
            res = client.create_session()
            if res.status_code == 200:
                st.session_state.current_session = res.json()["session_id"]
                st.rerun()

        # Load sessions
        sessions_res = client.get_sessions()

        if sessions_res.status_code == 200:
            sessions = sessions_res.json()

            for idx, s in enumerate(sessions):

                session_id = s["id"]
                title = get_session_title(session_id)

                col1, col2 = st.columns([5,1])

                # Open session
                with col1:
                    if st.button(
                        title,
                        key=f"open_{session_id}",
                        use_container_width=True
                    ):
                        st.session_state.current_session = session_id
                        st.rerun()

                # Delete session
                with col2:
                    if st.button("🗑️", key=f"delete_{session_id}"):

                        client.delete_session(session_id)

                        # Auto select next session
                        remaining = [
                            x for x in sessions if x["id"] != session_id
                        ]

                        if remaining:
                            st.session_state.current_session = remaining[0]["id"]
                        else:
                            st.session_state.current_session = None

                        st.rerun()

    # ===== MAIN CHAT ===== #

    st.title("🚀 API Copilot")

    session_id = st.session_state.current_session

    if not session_id:
        st.info("Create or select a chat session.")
        return

    # Load messages
    messages_res = client.get_messages(session_id)

    if messages_res.status_code == 200:
        messages = messages_res.json()

        for msg in messages:
            with st.chat_message(msg["role"]):
                st.markdown(msg["content"])

    # Chat input
    if prompt := st.chat_input("Ask something..."):

        with st.chat_message("user"):
            st.markdown(prompt)

        res = client.send_message(session_id, prompt)

        if res.status_code == 200:
            reply = res.json()["response"]

            with st.chat_message("assistant"):
                st.markdown(reply)

        else:
            st.error(res.text)

        st.rerun()


# ---------------- ROUTER ---------------- #

if not st.session_state.logged_in:
    auth_ui()
else:
    chat_ui()
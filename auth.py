import streamlit as st


def initialize_session():
    if "logged_in" not in st.session_state:
        st.session_state.logged_in = False

    if "user" not in st.session_state:
        st.session_state.user = None


def authenticate_user(job_id, password, employees):
    if not job_id or not password:
        return None

    job_id = job_id.strip()

    for employee in employees:
        if employee.get("job_id") == job_id and employee.get("password") == password:
            return employee

    return None


def user_has_access(user, required_access):
    if not user:
        return False

    user_access = user.get("access", [])
    return required_access in user_access or "admin" in user_access


def require_access(required_access):
    initialize_session()

    if not st.session_state.logged_in or not st.session_state.user:
        st.warning("Please log in to access this page.")
        st.stop()

    if not user_has_access(st.session_state.user, required_access):
        st.error("You do not have permission to access this page.")
        st.stop()


def require_any_access(required_access_list):
    initialize_session()

    if not st.session_state.logged_in or not st.session_state.user:
        st.warning("Please log in to access this page.")
        st.stop()

    if not any(user_has_access(st.session_state.user, role) for role in required_access_list):
        st.error("You do not have permission to access this page.")
        st.stop()


def logout():
    st.session_state.logged_in = False
    st.session_state.user = None
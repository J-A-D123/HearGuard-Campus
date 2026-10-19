import streamlit as st


PROFILE_KEY = "hearguard_shared_profile"

DEFAULT_PROFILE = {
    "hours": 2.0,
    "volume": "中等",
    "environment": "安静室内",
    "breaks": "有时",
}


def save_profile(hours, volume, environment, breaks):
    """保存当前会话的聆听行为输入。"""

    st.session_state[PROFILE_KEY] = {
        "hours": float(hours),
        "volume": str(volume),
        "environment": str(environment),
        "breaks": str(breaks),
    }


def get_profile():
    """读取已保存的聆听行为输入。"""

    saved = st.session_state.get(PROFILE_KEY)

    if not isinstance(saved, dict):
        return DEFAULT_PROFILE.copy()

    return {
        key: saved.get(key, default)
        for key, default in DEFAULT_PROFILE.items()
    }


def has_profile():
    """判断用户是否保存过聆听行为输入。"""

    return PROFILE_KEY in st.session_state


def clear_profile():
    """清除当前会话保存的个人行为输入。"""

    st.session_state.pop(PROFILE_KEY, None)
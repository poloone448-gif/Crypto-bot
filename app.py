import streamlit as st

# ── Login System ──
USERS = {
    "admin": "admin123",
    "customer1": "pass123",
}

def login():
    st.set_page_config(page_title="Crypto Bot", page_icon="🤖")
    st.title("🤖 Crypto Trading Bot")
    st.subheader("Login")
    username = st.text_input("Username")
    password = st.text_input("Password", type="password")
    if st.button("Login"):
        if username in USERS and USERS[username] == password:
            st.session_state.logged_in = True
            st.session_state.user = username
            st.rerun()
        else:
            st.error("❌ Wrong username or password!")

def dashboard():
    st.set_page_config(page_title="Crypto Bot", page_icon="🤖")
    st.title(f"🤖 Welcome {st.session_state.user}!")
    st.success("✅ Bot Connected")
    
    col1, col2 = st.columns(2)
    with col1:
        symbol = st.selectbox("Select Pair", ["XRP/USDT", "BTC/USDT", "ETH/USDT"])
    with col2:
        balance = st.number_input("Balance (USDT)", value=1000.0)
    
    if st.button("🚀 Run Bot Analysis"):
        with st.spinner("Analyzing market..."):
            st.info("Bot is running... (paste your bot logic here)")
    
    if st.button("🚪 Logout"):
        st.session_state.logged_in = False
        st.rerun()

if "logged_in" not in st.session_state:
    st.session_state.logged_in = False

if st.session_state.logged_in:
    dashboard()
else:
    login()

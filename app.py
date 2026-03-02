import streamlit as st
import pandas as pd
from i18n import get_text
from engine import process_balance, get_sample_data

# Page configuration
st.set_page_config(page_title="SYSCOHADA Clôture", layout="wide", page_icon="📑")

# Initialize language session state
if 'lang' not in st.session_state:
    st.session_state.lang = 'fr'

# Sidebar
with st.sidebar:
    st.title(get_text(st.session_state.lang, "sidebar_header"))
    lang_choice = st.selectbox(
        get_text(st.session_state.lang, "select_lang"),
        options=["fr", "en", "ru", "zh"],
        format_func=lambda x: {"fr": "Français 🇫🇷", "en": "English 🇬🇧", "ru": "Русский 🇷🇺", "zh": "中文 🇨🇳"}[x],
        index=["fr", "en", "ru", "zh"].index(st.session_state.lang)
    )
    if lang_choice != st.session_state.lang:
        st.session_state.lang = lang_choice
        st.rerun()

    st.divider()
    st.subheader(get_text(st.session_state.lang, "upload_section"))
    use_sample = st.checkbox(get_text(st.session_state.lang, "sample_data"), value=True)
    uploaded_file = st.file_uploader(get_text(st.session_state.lang, "upload_btn"), type=["csv", "xlsx"])

# Data loading
df = None
if use_sample:
    df = get_sample_data()
elif uploaded_file:
    if uploaded_file.name.endswith('.csv'):
        df = pd.read_csv(uploaded_file)
    else:
        df = pd.read_excel(uploaded_file)

# Main Content
st.title(get_text(st.session_state.lang, "title"))

if df is not None:
    results = process_balance(df)
    
    # Dashboard Tabs
    tab1, tab2, tab3 = st.tabs([
        get_text(st.session_state.lang, "dashboard"),
        get_text(st.session_state.lang, "statements"),
        get_text(st.session_state.lang, "indicators")
    ])
    
    with tab1:
        st.subheader(f"{get_text(st.session_state.lang, 'dashboard')} 📊")
        
        col1, col2, col3, col4 = st.columns(4)
        col1.metric(get_text(st.session_state.lang, "revenue"), f"{results['revenue']:,.0f} FCFA", "📈")
        col2.metric(get_text(st.session_state.lang, "net_profit"), f"{results['net_profit']:,.0f} FCFA", "💰")
        col3.metric(get_text(st.session_state.lang, "working_capital"), f"{results['working_capital']:,.0f} FCFA", "🏗️")
        col4.metric("Cash 🏦", f"{results['cash']:,.0f} FCFA", "🌊")
        
        # Alerts Seciton
        st.divider()
        st.subheader("Alertes & Notifications 🔔")
        
        if results['cash'] < 5000:
            st.error(f"{get_text(st.session_state.lang, 'alert_low_liquidity')} 🔥")
        else:
            st.success("Liquidité sous contrôle ✅")
            
        if results['net_profit'] > 10000:
            st.balloons()
            st.info(f"{get_text(st.session_state.lang, 'alert_good_profit')} 🏆")
            
        st.area_chart(pd.DataFrame({
            "Month": ["Jan", "Feb", "Mar", "Apr", "May", "Jun"],
            "Revenue": [results['revenue']*0.8, results['revenue']*0.9, results['revenue'], results['revenue']*1.1, results['revenue']*1.05, results['revenue']]
        }).set_index("Month"))

    with tab2:
        st.subheader(get_text(st.session_state.lang, "statements"))
        exp1 = st.expander(get_text(st.session_state.lang, "bilan"))
        with exp1:
            st.write("--- ACTIF ---")
            st.write(f"Immobilisations: {results['fixed_assets']:,.0f}")
            st.write(f"Actif Circulant: {results['current_assets']:,.0f}")
            st.write("--- PASSIF ---")
            st.write(f"Capitaux Propres & Dettes LMT: {results['equity_debt']:,.0f}")
            
        exp2 = st.expander(get_text(st.session_state.lang, "resultat"))
        with exp2:
            st.write(f"Produits (7): {results['revenue']:,.0f}")
            st.write(f"Charges (6): {results['expenses']:,.0f}")
            st.write(f"RÉSULTAT NET: {results['net_profit']:,.0f}")

    with tab3:
        st.subheader(get_text(st.session_state.lang, "indicators"))
        st.write(f"⚡ {get_text(st.session_state.lang, 'solvency')}: {results['equity_debt']/max(1, results['fixed_assets']):.2f}")
        st.progress(min(1.0, results['net_profit']/max(1, results['revenue'])))
        st.write(f"🎭 Rentabilité: {(results['net_profit']/max(1, results['revenue'])*100):.1f}%")

else:
    st.info(get_text(st.session_state.lang, "no_data"))
    st.image("https://illustrations.popsy.co/amber/accounting.svg", width=400)

st.sidebar.markdown("---")
st.sidebar.info("Expert SYSCOHADA v1.0 🧠")

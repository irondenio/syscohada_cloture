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
        col3.metric(get_text(st.session_state.lang, "ebitda"), f"{results['ebitda']:,.0f} FCFA", "⚡")
        col4.metric(get_text(st.session_state.lang, "working_capital"), f"{results['working_capital']:,.0f} FCFA", "🏗️")
        
        # Alerts Seciton
        st.divider()
        st.subheader(get_text(st.session_state.lang, "industrial_alerts"))
        
        alert_col1, alert_col2 = st.columns(2)
        with alert_col1:
            if results['cash'] < 50000000:
                st.error(f"{get_text(st.session_state.lang, 'alert_low_liquidity')} 🔥")
            else:
                st.success("Liquidité sous contrôle ✅")
            
            if results['net_profit'] > 50000000:
                st.balloons()
                st.info(f"{get_text(st.session_state.lang, 'alert_good_profit')} 🏆")
        
        with alert_col2:
            if results['maintenance_costs'] > results['revenue'] * 0.05:
                st.warning(get_text(st.session_state.lang, "maintenance_alert"))
            
            debt_ratio = results['debt'] / max(1, results['equity'])
            if debt_ratio > 0.5:
                st.warning(f"{get_text(st.session_state.lang, 'excess_debt')} (Ratio: {debt_ratio:.2f})")

        st.line_chart(pd.DataFrame({
            "Month": ["Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"],
            "EBITDA": [results['ebitda']*r for r in [0.9, 0.95, 1.0, 1.1, 1.2, 1.15, 1.1, 1.25, 1.3, 1.2, 1.1, 1.0]],
            "Net Profit": [results['net_profit']*r for r in [0.8, 0.85, 1.0, 1.05, 1.1, 1.05, 1.0, 1.15, 1.2, 1.1, 1.0, 0.9]]
        }).set_index("Month"))

    with tab2:
        st.subheader(get_text(st.session_state.lang, "statements"))
        exp1 = st.expander(get_text(st.session_state.lang, "bilan"))
        with exp1:
            bil_col1, bil_col2 = st.columns(2)
            with bil_col1:
                st.write("--- ACTIF ---")
                st.write(f"Immobilisations: {results['fixed_assets']:,.0f}")
                st.write(f"Stocks: {results['inventory']:,.0f}")
                st.write(f"Trésorerie: {results['cash']:,.0f}")
                st.write(f"TOTAL ACTIF: {results['total_assets']:,.0f}")
            with bil_col2:
                st.write("--- PASSIF ---")
                st.write(f"Capitaux Propres: {results['equity']:,.0f}")
                st.write(f"Dettes LMT: {results['debt']:,.0f}")
                st.write(f"RÉSULTAT NET: {results['net_profit']:,.0f}")
            
        exp2 = st.expander(get_text(st.session_state.lang, "resultat"))
        with exp2:
            st.write(f"CA (Produits 70): {results['revenue']:,.0f}")
            st.write(f"EBITDA: {results['ebitda']:,.0f}")
            st.write(f"Amortissements (68): {results['ebitda'] - results['ebit']:,.0f}")
            st.write(f"RÉSULTAT NET: {results['net_profit']:,.0f}")

    with tab3:
        st.subheader(get_text(st.session_state.lang, "indicators"))
        ind_col1, ind_col2 = st.columns(2)
        with ind_col1:
            st.write(f"⚡ {get_text(st.session_state.lang, 'op_margin')}: {(results['ebit']/max(1, results['revenue'])*100):.1f}%")
            st.progress(min(1.0, results['ebit']/max(1, results['revenue'])))
            
            st.write(f"🎭 {get_text(st.session_state.lang, 'debt_equity')}: {(results['debt']/max(1, results['equity'])):.2f}")
            st.progress(min(1.0, results['debt']/max(1, results['equity'])))
        
        with ind_col2:
            st.write(f"⚙️ {get_text(st.session_state.lang, 'asset_turnover')}: {(results['revenue']/max(1, results['total_assets'])):.2f}")
            st.progress(min(1.0, results['revenue']/max(1, results['total_assets'])))

else:
    st.info(get_text(st.session_state.lang, "no_data"))
    st.image("https://illustrations.popsy.co/amber/accounting.svg", width=400)

st.sidebar.markdown("---")
st.sidebar.info("Expert SYSCOHADA v1.0 🧠")

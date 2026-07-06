import streamlit as st
import sys, os
sys.path.insert(0, os.path.dirname(__file__))

from utils.database import init_db
from utils.styles import CSS
from pages import (dashboard, produits, ventes, compte_resultat,
                   bilan, flux_tresorerie, ratios, rapport_global)
from pages.operations import show_achats, show_depenses, show_stock

st.set_page_config(
    page_title="Cosmética Manager",
    page_icon="💄",
    layout="wide",
    initial_sidebar_state="expanded",
)

init_db()
st.markdown(CSS, unsafe_allow_html=True)

# ── SIDEBAR ───────────────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown("""
    <div class="logo-area">
        <span class="logo-icon">💄</span>
        <div class="logo-title">Cosmética Manager</div>
        <div class="logo-sub">Gestion · Stock · Finance</div>
    </div>
    <hr style="margin:.7rem 0;border-color:rgba(167,139,250,.2)">
    """, unsafe_allow_html=True)

    st.markdown('<div style="font-size:.68rem;color:#a78bfa;font-weight:700;padding:0 .5rem .4rem;letter-spacing:.08em;text-transform:uppercase">Opérations</div>', unsafe_allow_html=True)
    menu = st.radio("nav", [
        "📊  Tableau de bord",
        "📦  Produits",
        "🛒  Ventes",
        "🏭  Achats",
        "💸  Dépenses",
        "🏪  Stock",
    ], label_visibility="collapsed")

    st.markdown('<hr style="margin:.7rem 0;border-color:rgba(167,139,250,.2)">', unsafe_allow_html=True)
    st.markdown('<div style="font-size:.68rem;color:#a78bfa;font-weight:700;padding:0 .5rem .4rem;letter-spacing:.08em;text-transform:uppercase">États financiers</div>', unsafe_allow_html=True)
    menu_fin = st.radio("fin", [
        "📈  Compte de résultat",
        "⚖️  Bilan",
        "💧  Flux de trésorerie",
        "📐  Ratios financiers",
        "📋  Rapport global",
    ], label_visibility="collapsed")

    st.markdown('<hr style="margin:.7rem 0;border-color:rgba(167,139,250,.2)">', unsafe_allow_html=True)
    st.markdown("""
    <div style="padding:0 .5rem;font-size:.72rem;color:#c4b5fd;line-height:1.9">
        🔒 Données 100% locales<br>
        📦 SQLite embarqué<br>
        📱 Aucun internet requis
    </div>""", unsafe_allow_html=True)

# ── ROUTING ───────────────────────────────────────────────────────────────────
# Détecter quel menu a changé en dernier
if "last_menu" not in st.session_state:
    st.session_state["last_menu"] = menu
    st.session_state["last_fin"]  = menu_fin
    st.session_state["active"]    = "ops"

if menu != st.session_state.get("last_menu"):
    st.session_state["active"] = "ops"
    st.session_state["last_menu"] = menu
if menu_fin != st.session_state.get("last_fin"):
    st.session_state["active"] = "fin"
    st.session_state["last_fin"] = menu_fin

active = st.session_state.get("active", "ops")

if active == "ops":
    page = menu.split("  ", 1)[-1].strip()
    if page == "Tableau de bord":   dashboard.show()
    elif page == "Produits":        produits.show()
    elif page == "Ventes":          ventes.show()
    elif page == "Achats":          show_achats()
    elif page == "Dépenses":        show_depenses()
    elif page == "Stock":           show_stock()
else:
    page = menu_fin.split("  ", 1)[-1].strip()
    if page == "Compte de résultat":    compte_resultat.show()
    elif page == "Bilan":               bilan.show()
    elif page == "Flux de trésorerie":  flux_tresorerie.show()
    elif page == "Ratios financiers":   ratios.show()
    elif page == "Rapport global":      rapport_global.show()

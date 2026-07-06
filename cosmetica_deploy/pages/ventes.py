import streamlit as st
import pandas as pd
from datetime import date
import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))
from utils.database import get_produits, add_vente, get_ventes, delete_vente
from utils.styles import page_header, section_title, fmt

VILLES    = ["Yaoundé","Douala","Bafoussam","Garoua","Maroua","Bertoua","Autre"]
CANAUX    = ["Facebook","Client récurrent","Référence","Livraison directe","Autre"]
PAIEMENTS = ["Cash","Orange Money","MTN Mobile Money","À la livraison","Autre"]


def show():
    st.markdown(page_header("🛒 Ventes", "Saisissez chaque vente avec ses détails"), unsafe_allow_html=True)
    tab1, tab2 = st.tabs(["  ➕ Nouvelle vente  ", "  📋 Historique  "])
    produits = get_produits()
    prod_dict = {p["nom"]: p for p in produits}

    with tab1:
        if not produits:
            st.markdown('<div class="alert-warning">⚠️ Ajoutez d\'abord des produits.</div>', unsafe_allow_html=True)
            return
        with st.form("form_vente", clear_on_submit=True):
            c1, c2, c3 = st.columns(3)
            with c1:
                date_v   = st.date_input("Date *", date.today())
                prod_nom = st.selectbox("Produit *", list(prod_dict.keys()))
                quantite = st.number_input("Quantité *", min_value=0.1, value=1.0, step=1.0)
            with c2:
                p = prod_dict.get(prod_nom, {})
                prix     = st.number_input("Prix unitaire (FCFA)", min_value=0.0, value=float(p.get("prix_vente",0)), step=100.0)
                remise   = st.number_input("Remise unitaire (FCFA)", min_value=0.0, value=0.0, step=100.0)
                ville    = st.selectbox("Ville *", VILLES)
            with c3:
                canal    = st.selectbox("Canal", CANAUX)
                paiement = st.selectbox("Paiement", PAIEMENTS)
                livraison   = st.number_input("Frais livraison (FCFA)", min_value=0.0, value=0.0, step=100.0)
                commission  = st.number_input("Commission livreur (FCFA)", min_value=0.0, value=0.0, step=100.0)
            notes = st.text_input("Notes")

            ca_p    = (prix-remise)*quantite
            cout_p  = p.get("cout_unitaire",0)*quantite
            benef_p = ca_p - cout_p - livraison - commission
            cc1, cc2, cc3 = st.columns(3)
            cc1.metric("CA cette vente", fmt(ca_p))
            cc2.metric("Coût produit", fmt(cout_p))
            cc3.metric("Bénéfice estimé", fmt(benef_p))

            stock_dispo = p.get("stock_actuel", 0)
            if quantite > stock_dispo:
                st.markdown(f'<div class="alert-danger">⚠️ Stock insuffisant : {stock_dispo} {p.get("unite","u")} disponible(s).</div>', unsafe_allow_html=True)

            if st.form_submit_button("💾 Enregistrer la vente", use_container_width=True):
                if quantite > stock_dispo:
                    st.markdown('<div class="alert-danger">❌ Stock insuffisant.</div>', unsafe_allow_html=True)
                elif prix <= 0:
                    st.markdown('<div class="alert-danger">❌ Prix invalide.</div>', unsafe_allow_html=True)
                else:
                    add_vente({"date":str(date_v),"produit_id":p["id"],"quantite":quantite,
                                "prix_unitaire":prix,"remise":remise,"ville":ville,"canal":canal,
                                "mode_paiement":paiement,"livraison":livraison,
                                "commission":commission,"notes":notes})
                    st.markdown(f'<div class="alert-success">✅ Vente enregistrée — CA : <strong>{fmt(ca_p)}</strong> | Bénéfice : <strong>{fmt(benef_p)}</strong></div>', unsafe_allow_html=True)
                    st.rerun()

    with tab2:
        cc1, cc2 = st.columns(2)
        with cc1: d1 = st.date_input("Du", date.today().replace(day=1), key="v_d1")
        with cc2: d2 = st.date_input("Au", date.today(), key="v_d2")
        ventes = get_ventes(str(d1), str(d2))
        if not ventes:
            st.info("Aucune vente sur cette période.")
            return
        df = pd.DataFrame(ventes)
        df["CA"] = (df["prix_unitaire"]-df["remise"])*df["quantite"]
        c1,c2,c3,c4 = st.columns(4)
        c1.metric("Ventes", len(ventes))
        c2.metric("CA total", fmt(df["CA"].sum()))
        c3.metric("Qté totale", int(df["quantite"].sum()))
        c4.metric("CA moyen/vente", fmt(df["CA"].mean()))
        show_df = df[["date","produit_nom","quantite","prix_unitaire","remise","ville","canal","mode_paiement"]].copy()
        show_df.columns = ["Date","Produit","Qté","Prix","Remise","Ville","Canal","Paiement"]
        st.dataframe(show_df, use_container_width=True, hide_index=True)
        st.markdown(section_title("Annuler une vente"), unsafe_allow_html=True)
        ids = {f"#{v['id']} — {v['date']} — {v['produit_nom']}": v["id"] for v in ventes}
        sel = st.selectbox("Vente à annuler", list(ids.keys()))
        if st.button("🗑️ Annuler", key="del_vente"):
            delete_vente(ids[sel]); st.rerun()

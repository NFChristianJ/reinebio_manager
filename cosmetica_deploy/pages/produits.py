import streamlit as st
import pandas as pd
from datetime import date
import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))
from utils.database import get_produits, add_produit, update_produit, delete_produit
from utils.styles import page_header, section_title, fmt


def show():
    st.markdown(page_header("📦 Catalogue produits", "Gérez vos produits, prix, coûts et marges"), unsafe_allow_html=True)
    tab1, tab2 = st.tabs(["  📋 Liste  ", "  ➕ Ajouter / Modifier  "])

    with tab1:
        produits = get_produits(actif_only=False)
        if not produits:
            st.info("Aucun produit enregistré.")
            return
        df = pd.DataFrame(produits)
        df["Marge %"] = ((df["prix_vente"]-df["cout_unitaire"])/df["prix_vente"]*100).round(1)
        df["Statut"]  = df["actif"].apply(lambda x: "✅ Actif" if x else "❌ Inactif")

        c1, c2 = st.columns(2)
        with c1:
            cat_f = st.selectbox("Catégorie", ["Toutes"] + sorted(df["categorie"].dropna().unique().tolist()))
        with c2:
            typ_f = st.selectbox("Type", ["Tous","achat_revente","production"])

        if cat_f != "Toutes": df = df[df["categorie"]==cat_f]
        if typ_f != "Tous":   df = df[df["type"]==typ_f]

        show_df = df[["nom","categorie","type","prix_vente","cout_unitaire","Marge %","stock_actuel","unite","Statut"]].copy()
        show_df.columns = ["Produit","Catégorie","Type","Prix vente","Coût unit.","Marge %","Stock","Unité","Statut"]
        show_df["Prix vente"] = df["prix_vente"].apply(lambda x: f"{x:,.0f}")
        show_df["Coût unit."] = df["cout_unitaire"].apply(lambda x: f"{x:,.0f}")
        st.dataframe(show_df, use_container_width=True, hide_index=True)

        st.markdown(section_title("Désactiver un produit"), unsafe_allow_html=True)
        opts = {p["nom"]: p["id"] for p in produits if p["actif"]}
        if opts:
            sel = st.selectbox("Produit à désactiver", list(opts.keys()))
            if st.button("🗑️ Désactiver", key="del_prod"):
                delete_produit(opts[sel]); st.rerun()

    with tab2:
        produits_all = get_produits(actif_only=False)
        mode = st.radio("Mode", ["Nouveau produit","Modifier un produit existant"], horizontal=True)
        d = {"nom":"","categorie":"Crèmes","type":"achat_revente","prix_vente":0.0,
             "cout_unitaire":0.0,"unite":"unité","stock_actuel":0.0,"stock_min":5.0}
        pid = None

        if mode == "Modifier un produit existant" and produits_all:
            opts = {p["nom"]: p for p in produits_all}
            sel  = st.selectbox("Sélectionner", list(opts.keys()))
            p    = opts[sel]; pid = p["id"]
            d    = {k: p[k] for k in d}

        CATS = ["Crèmes","Sirops","Comprimés","Gélules","Thés","Suppositoires","Autre"]
        with st.form("form_prod", clear_on_submit=(mode=="Nouveau produit")):
            c1, c2 = st.columns(2)
            with c1:
                nom       = st.text_input("Nom *", value=d["nom"])
                categorie = st.selectbox("Catégorie", CATS, index=CATS.index(d["categorie"]) if d["categorie"] in CATS else 0)
                type_p    = st.selectbox("Type", ["achat_revente","production"], index=0 if d["type"]=="achat_revente" else 1,
                                          format_func=lambda x: "Achat & revente" if x=="achat_revente" else "Produit fabriqué")
                unite     = st.text_input("Unité", value=d["unite"])
            with c2:
                prix      = st.number_input("Prix de vente (FCFA) *", min_value=0.0, value=float(d["prix_vente"]), step=100.0)
                cout      = st.number_input("Coût unitaire (FCFA) *", min_value=0.0, value=float(d["cout_unitaire"]), step=100.0)
                stock_act = st.number_input("Stock actuel", min_value=0.0, value=float(d["stock_actuel"]), step=1.0)
                stock_min = st.number_input("Seuil alerte", min_value=0.0, value=float(d["stock_min"]), step=1.0)

            if prix > 0 and cout > 0:
                marge = (prix-cout)/prix*100
                st.markdown(f'<div class="alert-success">Marge : <strong>{marge:.1f}%</strong> — Bénéfice unit. : <strong>{fmt(prix-cout)}</strong></div>', unsafe_allow_html=True)

            if st.form_submit_button("💾 Enregistrer", use_container_width=True):
                if not nom or prix <= 0:
                    st.markdown('<div class="alert-danger">❌ Remplissez le nom et le prix.</div>', unsafe_allow_html=True)
                else:
                    data = {"nom":nom,"categorie":categorie,"type":type_p,"prix_vente":prix,
                            "cout_unitaire":cout,"unite":unite,"stock_actuel":stock_act,"stock_min":stock_min}
                    if pid: update_produit(pid, data)
                    else:   add_produit(data)
                    st.markdown('<div class="alert-success">✅ Produit enregistré.</div>', unsafe_allow_html=True)
                    st.rerun()

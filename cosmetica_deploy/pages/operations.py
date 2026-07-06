import streamlit as st
import pandas as pd
import plotly.express as px
from datetime import date
import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))
from utils.database import (get_produits, add_achat, get_achats, delete_achat,
                              add_depense, get_depenses, delete_depense,
                              update_produit)
from utils.styles import page_header, section_title, info_box, fmt

CATS_DEP = {
    "Publicité":      ["Facebook Ads","Instagram","WhatsApp","Autre pub"],
    "Transport":      ["Livraison Yaoundé","Livraison Douala","Expédition","Transport achat"],
    "Charges fixes":  ["Téléphone","Internet","Emballages","Électricité","Loyer bureau"],
    "Personnel":      ["Salaire livreur","Commission","Autre personnel"],
    "Autre":          ["Imprévu","Frais bancaires","Autre"],
}


# ── ACHATS ────────────────────────────────────────────────────────────────────
def show_achats():
    st.markdown(page_header("🏭 Achats & approvisionnements", "Entrées de stock et fournisseurs"), unsafe_allow_html=True)
    tab1, tab2 = st.tabs(["  ➕ Nouvel achat  ", "  📋 Historique  "])
    produits  = get_produits()
    prod_dict = {p["nom"]: p for p in produits}

    with tab1:
        with st.form("form_achat", clear_on_submit=True):
            type_a = st.radio("Type", ["produit_fini","matiere_premiere"], horizontal=True,
                               format_func=lambda x: "Produit fini" if x=="produit_fini" else "Matière première")
            c1, c2, c3 = st.columns(3)
            with c1:
                date_a = st.date_input("Date *", date.today())
                if type_a == "produit_fini" and produits:
                    prod_sel = st.selectbox("Produit *", list(prod_dict.keys()))
                    mat_nom  = None
                else:
                    mat_nom  = st.text_input("Matière première *", placeholder="ex: Huile de coco")
                    prod_sel = None
                quantite = st.number_input("Quantité *", min_value=0.1, value=1.0, step=1.0)
            with c2:
                prix_u    = st.number_input("Prix unitaire (FCFA) *", min_value=0.0, step=100.0)
                transport = st.number_input("Frais transport (FCFA)", min_value=0.0, step=100.0)
                fournisseur = st.text_input("Fournisseur")
            with c3:
                mode_p = st.selectbox("Paiement", ["Cash","Mobile Money","Crédit"])
                notes  = st.text_area("Notes", height=80)

            total = quantite*prix_u + transport
            st.metric("Total achat", fmt(total))

            if st.form_submit_button("💾 Enregistrer", use_container_width=True):
                if quantite <= 0 or prix_u <= 0:
                    st.markdown('<div class="alert-danger">❌ Quantité et prix requis.</div>', unsafe_allow_html=True)
                else:
                    pid = prod_dict[prod_sel]["id"] if type_a=="produit_fini" and prod_sel else None
                    add_achat({"date":str(date_a),"type_achat":type_a,"produit_id":pid,
                                "matiere_nom":mat_nom,"quantite":quantite,"prix_unitaire":prix_u,
                                "fournisseur":fournisseur,"frais_transport":transport,
                                "mode_paiement":mode_p,"notes":notes or ""})
                    st.markdown(f'<div class="alert-success">✅ Achat enregistré — Total : <strong>{fmt(total)}</strong></div>', unsafe_allow_html=True)
                    st.rerun()

    with tab2:
        cc1, cc2 = st.columns(2)
        with cc1: d1 = st.date_input("Du", date.today().replace(day=1), key="a_d1")
        with cc2: d2 = st.date_input("Au", date.today(), key="a_d2")
        achats = get_achats(str(d1), str(d2))
        if not achats:
            st.info("Aucun achat sur cette période.")
            return
        df = pd.DataFrame(achats)
        df["Total"] = df["quantite"]*df["prix_unitaire"] + df["frais_transport"]
        c1,c2,c3 = st.columns(3)
        c1.metric("Achats", len(achats))
        c2.metric("Total décaissé", fmt(df["Total"].sum()))
        c3.metric("Dont transport", fmt(df["frais_transport"].sum()))
        show_df = df[["date","type_achat","produit_nom","quantite","prix_unitaire","fournisseur","Total"]].copy()
        show_df.columns = ["Date","Type","Produit","Qté","Prix unit.","Fournisseur","Total"]
        st.dataframe(show_df, use_container_width=True, hide_index=True)
        ids = {f"#{a['id']} — {a['date']} — {a.get('produit_nom','Mat.')}": a["id"] for a in achats}
        sel = st.selectbox("Supprimer", list(ids.keys()))
        if st.button("🗑️ Supprimer", key="del_achat"):
            delete_achat(ids[sel]); st.rerun()


# ── DÉPENSES ─────────────────────────────────────────────────────────────────
def show_depenses():
    st.markdown(page_header("💸 Dépenses & charges", "Publicité, transport, charges fixes et autres"), unsafe_allow_html=True)
    tab1, tab2 = st.tabs(["  ➕ Nouvelle dépense  ", "  📋 Historique & analyse  "])

    with tab1:
        with st.form("form_dep", clear_on_submit=True):
            c1, c2, c3 = st.columns(3)
            with c1:
                date_d  = st.date_input("Date *", date.today())
                cat     = st.selectbox("Catégorie *", list(CATS_DEP.keys()))
            with c2:
                sous_cat = st.selectbox("Sous-catégorie", CATS_DEP.get(cat, ["Autre"]))
                montant  = st.number_input("Montant (FCFA) *", min_value=0.0, step=100.0)
            with c3:
                ville = st.selectbox("Ville", ["Yaoundé","Douala","Autre","N/A"])
                desc  = st.text_input("Description")
            if st.form_submit_button("💾 Enregistrer", use_container_width=True):
                if montant <= 0:
                    st.markdown('<div class="alert-danger">❌ Montant invalide.</div>', unsafe_allow_html=True)
                else:
                    add_depense({"date":str(date_d),"categorie":cat,"sous_categorie":sous_cat,
                                  "montant":montant,"description":desc,"ville":ville})
                    st.markdown(f'<div class="alert-success">✅ Dépense enregistrée : <strong>{fmt(montant)}</strong> — {cat}</div>', unsafe_allow_html=True)
                    st.rerun()

    with tab2:
        cc1, cc2 = st.columns(2)
        with cc1: d1 = st.date_input("Du", date.today().replace(day=1), key="dep_d1")
        with cc2: d2 = st.date_input("Au", date.today(), key="dep_d2")
        depenses = get_depenses(str(d1), str(d2))
        if not depenses:
            st.info("Aucune dépense sur cette période.")
            return
        df = pd.DataFrame(depenses)
        c1,c2,c3 = st.columns(3)
        c1.metric("Total", fmt(df["montant"].sum()))
        c2.metric("Publicité", fmt(df[df["categorie"]=="Publicité"]["montant"].sum()))
        c3.metric("Transport", fmt(df[df["categorie"]=="Transport"]["montant"].sum()))
        cat_sum = df.groupby("categorie")["montant"].sum().reset_index()
        fig = px.pie(cat_sum, values="montant", names="categorie", hole=0.4,
                     color_discrete_sequence=["#7c3aed","#db2777","#0891b2","#059669","#d97706"])
        fig.update_layout(paper_bgcolor="rgba(0,0,0,0)", margin=dict(t=20,b=10), height=240,
                           legend=dict(orientation="h",y=-0.15))
        st.plotly_chart(fig, use_container_width=True, config={"displayModeBar":False})
        show_df = df[["date","categorie","sous_categorie","montant","description","ville"]].copy()
        show_df.columns = ["Date","Catégorie","Sous-cat.","Montant","Description","Ville"]
        show_df["Montant"] = df["montant"].apply(lambda x: f"{x:,.0f}")
        st.dataframe(show_df, use_container_width=True, hide_index=True)
        ids = {f"#{d['id']} — {d['date']} — {d['categorie']} ({d['montant']:,.0f})": d["id"] for d in depenses}
        sel = st.selectbox("Supprimer", list(ids.keys()))
        if st.button("🗑️ Supprimer", key="del_dep"):
            delete_depense(ids[sel]); st.rerun()


# ── STOCK ─────────────────────────────────────────────────────────────────────
def show_stock():
    st.markdown(page_header("🏪 Stock", "Niveaux, alertes, valeur et ajustements"), unsafe_allow_html=True)
    produits = get_produits(actif_only=True)
    if not produits:
        st.info("Aucun produit actif.")
        return
    df = pd.DataFrame(produits)
    df["Valeur"] = df["stock_actuel"]*df["cout_unitaire"]
    df["Statut"] = df.apply(lambda r: "🔴 Rupture" if r["stock_actuel"]==0 else ("🟡 Bas" if r["stock_actuel"]<=r["stock_min"] else "🟢 OK"), axis=1)

    c1,c2,c3,c4 = st.columns(4)
    c1.metric("Produits actifs", len(produits))
    c2.metric("Valeur totale stock", fmt(df["Valeur"].sum()))
    c3.metric("En alerte", len(df[df["stock_actuel"]<=df["stock_min"]]))
    c4.metric("En rupture", len(df[df["stock_actuel"]==0]))

    alertes = df[df["stock_actuel"]<=df["stock_min"]]
    if not alertes.empty:
        st.markdown(f'<div class="alert-danger">🔴 À réapprovisionner : {", ".join(alertes["nom"].tolist())}</div>', unsafe_allow_html=True)

    fig = px.bar(df.sort_values("stock_actuel"), x="stock_actuel", y="nom", orientation="h",
                 color="Statut", color_discrete_map={"🔴 Rupture":"#ef4444","🟡 Bas":"#f59e0b","🟢 OK":"#059669"},
                 text="stock_actuel")
    fig.update_layout(paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
                       margin=dict(t=10,b=10), height=290,
                       xaxis_title="Quantité", yaxis_title="",
                       legend=dict(orientation="h",y=1.1))
    fig.update_traces(texttemplate="%{text:.0f}", textposition="outside")
    st.plotly_chart(fig, use_container_width=True, config={"displayModeBar":False})

    show_df = df[["nom","categorie","stock_actuel","stock_min","unite","Valeur","Statut"]].copy()
    show_df.columns = ["Produit","Catégorie","Stock","Seuil","Unité","Valeur (FCFA)","Statut"]
    show_df["Valeur (FCFA)"] = df["Valeur"].apply(lambda x: f"{x:,.0f}")
    st.dataframe(show_df, use_container_width=True, hide_index=True)

    st.markdown(section_title("Ajustement manuel"), unsafe_allow_html=True)
    prod_dict = {p["nom"]: p for p in produits}
    with st.form("form_stock"):
        c1,c2,c3 = st.columns(3)
        with c1: sel = st.selectbox("Produit", list(prod_dict.keys()))
        with c2: nouveau = st.number_input("Nouveau stock réel", min_value=0.0, step=1.0,
                                            value=float(prod_dict[sel]["stock_actuel"]))
        with c3: raison = st.text_input("Raison (inventaire, perte…)")
        if st.form_submit_button("✅ Appliquer", use_container_width=True):
            p = prod_dict[sel]
            update_produit(p["id"], {**p, "stock_actuel": nouveau})
            st.markdown(f'<div class="alert-success">✅ Stock <strong>{sel}</strong> → <strong>{nouveau:.0f} {p["unite"]}</strong></div>', unsafe_allow_html=True)
            st.rerun()

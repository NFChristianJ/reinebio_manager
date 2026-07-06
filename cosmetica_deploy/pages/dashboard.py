import streamlit as st
import plotly.express as px
import plotly.graph_objects as go
import pandas as pd
from datetime import date, timedelta
import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))
from utils.database import (get_ventes_par_produit, get_ventes_par_ville,
                              get_ventes, get_depenses, get_stock_alerte)
from utils.styles import kpi_card, page_header, section_title, fmt, fmt_pct, info_box

PAL = ["#7c3aed","#db2777","#0891b2","#059669","#d97706","#dc2626"]


def get_kpis_simple(d1, d2):
    ventes = get_ventes(d1, d2)
    depenses = get_depenses(d1, d2)
    ca = sum((v["prix_unitaire"]-v["remise"])*v["quantite"] for v in ventes)
    cout = sum(v["cout_unitaire"]*v["quantite"] for v in ventes)
    pub = sum(d["montant"] for d in depenses if d["categorie"]=="Publicité")
    transport = sum(v["livraison"]+v["commission"] for v in ventes)
    autres = sum(d["montant"] for d in depenses)
    benef = ca - cout - transport - autres
    return {"ca":ca,"cout":cout,"pub":pub,"transport":transport,"autres":autres,
            "benef":benef,"marge":(benef/ca*100) if ca else 0,"nb":len(ventes)}


def show():
    st.markdown(page_header("📊 Tableau de bord", "Vue d'ensemble en temps réel"), unsafe_allow_html=True)

    # Période
    c1, c2, c3 = st.columns([2,2,3])
    with c1:
        p = st.selectbox("Période", ["7 jours","30 jours","Ce mois","3 mois","Cette année","Personnalisé"],
                          label_visibility="collapsed")
    today = date.today()
    if p=="7 jours":     d1,d2 = today-timedelta(7), today
    elif p=="30 jours":  d1,d2 = today-timedelta(30), today
    elif p=="Ce mois":   d1,d2 = today.replace(day=1), today
    elif p=="3 mois":    d1,d2 = today-timedelta(90), today
    elif p=="Cette année":d1,d2 = today.replace(month=1,day=1), today
    else:
        with c2: d1 = st.date_input("Du", today-timedelta(30), label_visibility="collapsed")
        with c3: d2 = st.date_input("Au", today, label_visibility="collapsed")

    d1s,d2s = str(d1),str(d2)
    kpis      = get_kpis_simple(d1s, d2s)
    par_prod  = get_ventes_par_produit(d1s, d2s)
    par_ville = get_ventes_par_ville(d1s, d2s)
    alertes   = get_stock_alerte()

    # KPI Cards
    c1,c2,c3,c4 = st.columns(4)
    with c1: st.markdown(kpi_card("Chiffre d'affaires", fmt(kpis["ca"]), f"{kpis['nb']} ventes"), unsafe_allow_html=True)
    with c2: st.markdown(kpi_card("Bénéfice net", fmt(kpis["benef"]), f"Marge {fmt_pct(kpis['marge'])}", "green" if kpis["benef"]>=0 else "red"), unsafe_allow_html=True)
    with c3: st.markdown(kpi_card("Publicité dépensée", fmt(kpis["pub"]), f"{fmt(kpis['pub']/kpis['nb'])} / vente" if kpis["nb"] else "", "orange"), unsafe_allow_html=True)
    with c4: st.markdown(kpi_card("Coût produits", fmt(kpis["cout"]), f"Transport : {fmt(kpis['transport'])}", "cyan"), unsafe_allow_html=True)

    if alertes:
        st.markdown(f'<div class="alert-warning">⚠️ <strong>{len(alertes)} produit(s) en stock bas :</strong> {", ".join(a["nom"] for a in alertes)}</div>', unsafe_allow_html=True)

    # Charts
    col_g1, col_g2 = st.columns([3,2])
    with col_g1:
        st.markdown(section_title("Répartition des charges"), unsafe_allow_html=True)
        charges = {"Coût produits":kpis["cout"],"Pub":kpis["pub"],"Transport ventes":kpis["transport"],"Autres":kpis["autres"]}
        charges = {k:v for k,v in charges.items() if v>0}
        if charges:
            fig = go.Figure(go.Pie(labels=list(charges.keys()), values=list(charges.values()),
                                    hole=0.52, marker_colors=PAL, textfont_size=11, textinfo="percent+label"))
            fig.update_layout(paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
                               margin=dict(t=20,b=10,l=0,r=0), height=270, showlegend=False)
            st.plotly_chart(fig, use_container_width=True, config={"displayModeBar":False})
        else:
            st.info("Aucune charge sur la période.")

    with col_g2:
        st.markdown(section_title("CA par ville"), unsafe_allow_html=True)
        if par_ville:
            vdf = pd.DataFrame([{"Ville":k,"CA":v["ca"]} for k,v in par_ville.items()])
            fig2 = px.bar(vdf, x="Ville", y="CA", color="Ville",
                          color_discrete_sequence=PAL, text_auto=".2s")
            fig2.update_layout(paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
                                margin=dict(t=10,b=10,l=0,r=0), height=270,
                                showlegend=False, yaxis_title="FCFA", xaxis_title="")
            st.plotly_chart(fig2, use_container_width=True, config={"displayModeBar":False})
        else:
            st.info("Aucune vente sur la période.")

    # Par produit
    if par_prod:
        st.markdown(section_title("Performance par produit"), unsafe_allow_html=True)
        pdata = []
        for nom, v in par_prod.items():
            m = (v["benefice"]/v["ca"]*100) if v["ca"] else 0
            pdata.append({"Produit":nom, "CA":v["ca"], "Bénéfice":v["benefice"], "Marge %":round(m,1), "Qté":v["qte"]})
        pdf = pd.DataFrame(pdata).sort_values("CA", ascending=False)

        fig3 = go.Figure()
        fig3.add_trace(go.Bar(name="CA", x=pdf["Produit"], y=pdf["CA"], marker_color="#7c3aed"))
        fig3.add_trace(go.Bar(name="Bénéfice", x=pdf["Produit"], y=pdf["Bénéfice"], marker_color="#059669"))
        fig3.update_layout(paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
                            margin=dict(t=10,b=10), height=280, barmode="group",
                            legend=dict(orientation="h",y=1.1),
                            yaxis_title="FCFA", xaxis_title="")
        st.plotly_chart(fig3, use_container_width=True, config={"displayModeBar":False})

    # Dernières ventes
    st.markdown(section_title("Dernières ventes"), unsafe_allow_html=True)
    ventes = get_ventes(d1s, d2s)
    if ventes:
        df = pd.DataFrame(ventes[:12])[["date","produit_nom","quantite","prix_unitaire","ville","mode_paiement"]]
        df.columns = ["Date","Produit","Qté","Prix unit.","Ville","Paiement"]
        st.dataframe(df, use_container_width=True, hide_index=True)
    else:
        st.info("Aucune vente sur cette période.")

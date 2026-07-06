import streamlit as st
import plotly.graph_objects as go
from datetime import date, timedelta
import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))
from utils.database import compute_flux_tresorerie, add_encaissement, add_decaissement, get_encaissements, get_decaissements
from utils.styles import page_header, section_title, info_box, fmt
from utils.exports import export_flux_pdf

INFOS = {
    "exploitation": ("Flux d'exploitation",
        "L'argent généré (ou consommé) par l'activité principale : ventes, achats de marchandises, charges. "
        "C'est le flux le plus important — une entreprise saine doit avoir un flux d'exploitation positif.",
        "Flux exploit. = Encaissements clients − Achats − Charges − IS payé"),
    "investissement": ("Flux d'investissement",
        "Les mouvements liés aux acquisitions ou cessions d'actifs durables (machines, matériels). "
        "Un flux négatif signifie que vous investissez — c'est souvent bon signe à moyen terme.",
        "Flux invest. = Cessions − Acquisitions d'immobilisations"),
    "financement": ("Flux de financement",
        "Les mouvements liés aux emprunts et remboursements. Un emprunt apporte du cash (positif), "
        "un remboursement le réduit (négatif).",
        "Flux financement = Emprunts − Remboursements − Dividendes"),
    "variation": ("Variation de trésorerie",
        "La somme des trois flux. Si positive, votre trésorerie a augmenté sur la période. "
        "Si négative, vous avez consommé plus de cash que vous n'en avez généré.",
        "Variation = Flux exploit. + Flux invest. + Flux financement"),
}


def show():
    st.markdown(page_header("💧 Tableau des flux de trésorerie",
                             "Où va l'argent ? D'où vient-il ? La vérité sur votre cash."), unsafe_allow_html=True)

    tab_tableau, tab_saisie = st.tabs(["  📊 Tableau des flux  ", "  ➕ Saisir encaissements / décaissements  "])

    with tab_tableau:
        col_p, col_d1, col_d2 = st.columns([2, 2, 2])
        with col_p:
            p = st.selectbox("Période", ["Ce mois", "Mois dernier", "Trimestre", "Cette année", "Personnalisé"], key="flux_p")
        today = date.today()
        if p == "Ce mois":      d1, d2 = today.replace(day=1), today
        elif p == "Mois dernier":
            first = today.replace(day=1); d2 = first - timedelta(1); d1 = d2.replace(day=1)
        elif p == "Trimestre":  q = (today.month-1)//3; d1 = date(today.year, q*3+1, 1); d2 = today
        elif p == "Cette année":d1, d2 = today.replace(month=1, day=1), today
        else:
            with col_d1: d1 = st.date_input("Du", today.replace(day=1), key="flux_d1")
            with col_d2: d2 = st.date_input("Au", today, key="flux_d2")

        d1s, d2s = str(d1), str(d2)
        flux = compute_flux_tresorerie(d1s, d2s)
        label = f"{d1s} → {d2s}"

        mode_peda = st.toggle("📚 Mode pédagogique", value=True, key="flux_peda")

        def info(key):
            if mode_peda:
                titre, expl, formule = INFOS[key]
                st.markdown(f'<div class="info-box blue"><strong>{titre}</strong><br>{expl}<br><em>📐 {formule}</em></div>',
                            unsafe_allow_html=True)

        def flux_row(label, val, style=""):
            sign = "+" if val >= 0 else ""
            color = "#059669" if val >= 0 else "#dc2626"
            bg = "#f0fdf4" if val >= 0 else "#fef2f2"
            weight = "700" if style == "total" else "400"
            border = "2px solid #e5e7eb" if style == "total" else "1px solid #f3f4f6"
            st.markdown(f"""
            <div style="display:flex;justify-content:space-between;align-items:center;
                        padding:.4rem .8rem;border-radius:7px;margin:.15rem 0;
                        background:{'#f3f4f6' if style=='header' else (bg if style=='total' else 'white')};
                        border:{border};font-weight:{weight}">
                <span style="color:{'#1e1b4b' if style in ('header','total') else '#374151'}">{label}</span>
                <span style="color:{color if style!='header' else '#1e1b4b'};font-weight:{weight}">{sign}{fmt(abs(val))}</span>
            </div>""", unsafe_allow_html=True)

        # ── I. EXPLOITATION ──────────────────────────────────────────────────
        st.markdown(section_title("I. Flux d'exploitation"), unsafe_allow_html=True)
        info("exploitation")
        flux_row("Encaissements clients", flux["encaiss_clients"])
        flux_row("(-) Achats fournisseurs", -flux["cout_achats"])
        flux_row("(-) Charges d'exploitation", -flux["cout_depenses"])
        flux_row("(-) Livraisons & commissions", -flux["cout_livraison"])
        flux_row("(-) IS payé", -flux["is_paye"])
        flux_row("→ FLUX D'EXPLOITATION", flux["flux_exploitation"], "total")

        # ── II. INVESTISSEMENT ───────────────────────────────────────────────
        st.markdown(section_title("II. Flux d'investissement"), unsafe_allow_html=True)
        info("investissement")
        flux_row("(-) Acquisitions d'immobilisations", -flux["acquisitions"])
        flux_row("(+) Cessions d'actifs", flux["cessions"])
        flux_row("→ FLUX D'INVESTISSEMENT", flux["flux_investissement"], "total")

        # ── III. FINANCEMENT ─────────────────────────────────────────────────
        st.markdown(section_title("III. Flux de financement"), unsafe_allow_html=True)
        info("financement")
        flux_row("(+) Emprunts nouveaux", flux["emprunts_nouveaux"])
        flux_row("(-) Remboursements", -flux["remboursements"])
        flux_row("(-) Dividendes", -flux["dividendes"])
        flux_row("→ FLUX DE FINANCEMENT", flux["flux_financement"], "total")

        # ── SYNTHÈSE ─────────────────────────────────────────────────────────
        st.markdown(section_title("Synthèse de trésorerie"), unsafe_allow_html=True)
        info("variation")

        c1, c2, c3 = st.columns(3)
        c1.metric("Trésorerie initiale", fmt(flux["tresorerie_init"]))
        c2.metric("Variation", fmt(flux["variation_tresorerie"]),
                  delta=f"{'+' if flux['variation_tresorerie'] >= 0 else ''}{flux['variation_tresorerie']:,.0f}")
        c3.metric("Trésorerie finale", fmt(flux["tresorerie_finale"]))

        # Graphique en barres
        categories = ["Exploitation", "Investissement", "Financement"]
        valeurs = [flux["flux_exploitation"], flux["flux_investissement"], flux["flux_financement"]]
        couleurs = ["#059669" if v >= 0 else "#dc2626" for v in valeurs]

        fig = go.Figure(go.Bar(
            x=categories, y=valeurs, marker_color=couleurs,
            text=[f"{'+' if v>=0 else ''}{v:,.0f}" for v in valeurs],
            textposition="outside", textfont_size=11,
        ))
        fig.add_hline(y=0, line_color="#6b7280", line_width=1)
        fig.update_layout(paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
                           margin=dict(t=30, b=10), height=260,
                           yaxis_title="FCFA", showlegend=False)
        st.plotly_chart(fig, use_container_width=True, config={"displayModeBar": False})

        # Export
        st.markdown(section_title("Exporter"), unsafe_allow_html=True)
        pdf_buf = export_flux_pdf(flux, label)
        st.download_button("⬇️ Télécharger les flux de trésorerie (PDF)",
                            data=pdf_buf, file_name=f"flux_tresorerie_{d1s}_{d2s}.pdf",
                            mime="application/pdf", use_container_width=True)

    with tab_saisie:
        st.markdown(info_box(
            "Saisissez ici les mouvements de trésorerie réels : encaissements reçus (Orange Money, MTN, cash) "
            "et décaissements effectués. Ces données alimentent le tableau des flux.",
            "purple"), unsafe_allow_html=True)

        col_enc, col_dec = st.columns(2)

        with col_enc:
            st.markdown(section_title("➕ Encaissement"), unsafe_allow_html=True)
            with st.form("form_enc", clear_on_submit=True):
                date_e = st.date_input("Date", date.today(), key="enc_date")
                montant_e = st.number_input("Montant (FCFA)", min_value=0.0, step=500.0)
                mode_e = st.selectbox("Mode", ["Cash", "Orange Money", "MTN Mobile Money", "Virement", "Autre"])
                desc_e = st.text_input("Description")
                if st.form_submit_button("💾 Enregistrer", use_container_width=True):
                    if montant_e > 0:
                        add_encaissement({"date": str(date_e), "montant": montant_e,
                                           "mode": mode_e, "description": desc_e})
                        st.markdown('<div class="alert-success">✅ Encaissement enregistré.</div>', unsafe_allow_html=True)
                        st.rerun()

            encs = get_encaissements()
            if encs:
                import pandas as pd
                df = pd.DataFrame(encs[:10])[["date", "montant", "mode", "description"]]
                df.columns = ["Date", "Montant", "Mode", "Description"]
                st.dataframe(df, use_container_width=True, hide_index=True)

        with col_dec:
            st.markdown(section_title("➖ Décaissement"), unsafe_allow_html=True)
            with st.form("form_dec", clear_on_submit=True):
                date_d = st.date_input("Date", date.today(), key="dec_date")
                montant_d = st.number_input("Montant (FCFA)", min_value=0.0, step=500.0)
                cat_d = st.selectbox("Catégorie", ["Achat marchandise", "Charge exploitation",
                                                    "Remboursement emprunt", "Investissement",
                                                    "IS payé", "Autre"])
                desc_d = st.text_input("Description", key="dec_desc")
                if st.form_submit_button("💾 Enregistrer", use_container_width=True):
                    if montant_d > 0:
                        add_decaissement({"date": str(date_d), "montant": montant_d,
                                           "categorie": cat_d, "description": desc_d})
                        st.markdown('<div class="alert-success">✅ Décaissement enregistré.</div>', unsafe_allow_html=True)
                        st.rerun()

            decs = get_decaissements()
            if decs:
                import pandas as pd
                df = pd.DataFrame(decs[:10])[["date", "montant", "categorie", "description"]]
                df.columns = ["Date", "Montant", "Catégorie", "Description"]
                st.dataframe(df, use_container_width=True, hide_index=True)

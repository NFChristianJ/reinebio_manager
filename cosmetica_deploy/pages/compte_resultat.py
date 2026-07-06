import streamlit as st
import plotly.graph_objects as go
from datetime import date, timedelta
import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))
from utils.database import compute_compte_resultat
from utils.styles import page_header, section_title, info_box, cr_row, fmt, fmt_pct
from utils.exports import export_compte_resultat_pdf

INFOS = {
    "ca": ("Chiffre d'affaires (CA)",
           "La somme totale de ce que vous avez encaissé (ou facturé) sur vos ventes. C'est le point de départ de toute analyse.",
           "CA = Σ (Prix unitaire − Remise) × Quantité vendue"),
    "cmv": ("Coût des marchandises vendues (CMV)",
            "Ce que vous avez réellement dépensé pour produire ou acheter les produits que vous avez vendus. Comprend le coût d'achat et les frais de transport liés aux ventes.",
            "CMV = Coût unitaire × Quantité + Transport ventes"),
    "marge_brute": ("Marge brute",
                    "Ce qu'il reste après avoir soustrait le coût des produits. C'est votre première marge — elle mesure si votre activité de vente est rentable avant les frais généraux.",
                    "Marge brute = CA − CMV"),
    "ebitda": ("EBITDA (Excédent brut d'exploitation)",
               "Ce qu'il reste après toutes les charges opérationnelles (pub, transport, personnel, charges fixes). C'est la capacité brute de l'entreprise à générer de la trésorerie.",
               "EBITDA = Marge brute − Charges d'exploitation"),
    "dap": ("Dotations aux amortissements et provisions (DAP)",
            "La perte de valeur annuelle de vos équipements et matériels (téléphone, machine, véhicule…). Ce n'est pas une sortie de cash — c'est une charge comptable qui réduit le résultat.",
            "DAP = Valeur d'acquisition × Taux d'amortissement / 100"),
    "ebit": ("EBIT — Résultat opérationnel",
             "Le bénéfice réel de l'activité, après amortissements. C'est le cœur de la rentabilité opérationnelle de l'entreprise.",
             "EBIT = EBITDA − DAP"),
    "rf": ("Résultat financier",
           "L'impact des emprunts et dettes financières. Si vous avez des crédits en cours, les intérêts viennent réduire votre résultat ici.",
           "Résultat financier = Produits financiers − Charges d'intérêts"),
    "rcai": ("Résultat courant avant impôt (RCAI)",
             "La rentabilité totale de l'entreprise dans son activité normale (opérationnelle + financière) avant impôts.",
             "RCAI = EBIT + Résultat financier"),
    "re": ("Résultat exceptionnel",
           "Les gains ou pertes qui sortent du fonctionnement normal : vente d'un bien, indemnité, amende… Ce n'est pas récurrent.",
           "Résultat exceptionnel = Produits exceptionnels − Charges exceptionnelles"),
    "rai": ("Résultat avant impôt (RAI)",
            "La somme du résultat courant et du résultat exceptionnel. C'est la base sur laquelle l'impôt est calculé.",
            "RAI = RCAI + Résultat exceptionnel"),
    "is": ("Impôt sur les sociétés (IS)",
           "La part du résultat que vous devez reverser à l'État. Au Cameroun, le taux standard de l'IS est de 30% du bénéfice.",
           "IS = RAI × Taux IS (30%)"),
    "rn": ("Résultat net",
           "C'est LE chiffre final — ce que l'entreprise a réellement gagné après tout. C'est ce qui peut être distribué ou réinvesti.",
           "Résultat net = RAI − IS"),
    "marges": ("Marges — Marge opérationnelle & Marge nette",
               "La marge opérationnelle mesure l'efficacité de l'activité. La marge nette mesure ce que vous gardez vraiment sur chaque franc de vente.",
               "Marge opérationnelle = EBIT / CA × 100 | Marge nette = RN / CA × 100"),
}


def _periode_label(d1, d2):
    return f"{d1} → {d2}"


def show():
    st.markdown(page_header("📈 Compte de résultat", "Du chiffre d'affaires au bénéfice net, ligne par ligne"), unsafe_allow_html=True)

    # Filtre période
    col_p, col_d1, col_d2 = st.columns([2,2,2])
    with col_p:
        p = st.selectbox("Période", ["Ce mois","Mois dernier","Trimestre","Cette année","Personnalisé"],
                          key="cr_periode")
    today = date.today()
    if p=="Ce mois":
        d1,d2 = today.replace(day=1), today
    elif p=="Mois dernier":
        first = today.replace(day=1); d2 = first-timedelta(1); d1 = d2.replace(day=1)
    elif p=="Trimestre":
        q=(today.month-1)//3; d1=date(today.year,q*3+1,1); d2=today
    elif p=="Cette année":
        d1,d2 = today.replace(month=1,day=1), today
    else:
        with col_d1: d1 = st.date_input("Du", today.replace(day=1), key="cr_d1")
        with col_d2: d2 = st.date_input("Au", today, key="cr_d2")

    d1s,d2s = str(d1),str(d2)
    label = _periode_label(d1s, d2s)

    cr = compute_compte_resultat(d1s, d2s)

    # Mode pédagogique
    mode_peda = st.toggle("📚 Mode pédagogique — afficher les explications", value=True)

    st.markdown("<br>", unsafe_allow_html=True)

    def show_info(key):
        if mode_peda and key in INFOS:
            titre, expl, formule = INFOS[key]
            st.markdown(f'<div class="info-box purple"><strong>{titre}</strong><br>{expl}<br><em>📐 {formule}</em></div>', unsafe_allow_html=True)

    # ── BLOC CA ──────────────────────────────────────────────────────────────
    st.markdown(section_title("1. Revenus"), unsafe_allow_html=True)
    show_info("ca")
    st.markdown(cr_row("(+) Chiffre d'affaires", fmt(cr["ca"]), "header"), unsafe_allow_html=True)
    st.markdown(f'<div style="font-size:.78rem;color:#6b7280;padding:.2rem .7rem">{cr["nb_ventes"]} ventes · {cr["nb_jours"]} jours · Pub/vente : {fmt(cr["pub_par_vente"])}</div>', unsafe_allow_html=True)

    # ── BLOC CMV ─────────────────────────────────────────────────────────────
    st.markdown(section_title("2. Coût des marchandises vendues"), unsafe_allow_html=True)
    show_info("cmv")
    st.markdown(cr_row("(-) Coût d'achat des produits", fmt(cr["cmv"]), "indent", True), unsafe_allow_html=True)
    st.markdown(cr_row("(-) Transport & commissions livreurs", fmt(cr["transport_ventes"]), "indent", True), unsafe_allow_html=True)
    st.markdown(cr_row("= Coût total marchandises vendues", fmt(cr["cmv_total"]), "subtotal"), unsafe_allow_html=True)

    # ── MARGE BRUTE ──────────────────────────────────────────────────────────
    st.markdown(section_title("3. Marge brute"), unsafe_allow_html=True)
    show_info("marge_brute")
    color_mb = "green" if cr["marge_brute"]>=0 else "red"
    st.markdown(cr_row(f"= MARGE BRUTE ({fmt_pct(cr['marge_brute_pct'])})", fmt(cr["marge_brute"]), color_mb), unsafe_allow_html=True)

    # ── CHARGES EXPLOITATION ─────────────────────────────────────────────────
    st.markdown(section_title("4. Charges d'exploitation"), unsafe_allow_html=True)
    st.markdown(cr_row("(-) Publicité (Facebook Ads, etc.)", fmt(cr["pub"]), "indent", True), unsafe_allow_html=True)
    st.markdown(cr_row("(-) Transport & livraisons (charges)", fmt(cr["transport"]), "indent", True), unsafe_allow_html=True)
    st.markdown(cr_row("(-) Personnel & commissions", fmt(cr["personnel"]), "indent", True), unsafe_allow_html=True)
    st.markdown(cr_row("(-) Charges fixes (téléphone, internet…)", fmt(cr["fixes"]), "indent", True), unsafe_allow_html=True)
    st.markdown(cr_row("(-) Autres charges", fmt(cr["autres_charges"]), "indent", True), unsafe_allow_html=True)
    st.markdown(cr_row("= Total charges d'exploitation", fmt(cr["total_charges_exploitation"]), "subtotal"), unsafe_allow_html=True)

    # ── EBITDA ───────────────────────────────────────────────────────────────
    st.markdown(section_title("5. EBITDA"), unsafe_allow_html=True)
    show_info("ebitda")
    st.markdown(cr_row(f"= EBITDA ({fmt_pct(cr['ebitda_pct'])})", fmt(cr["ebitda"]), "subtotal"), unsafe_allow_html=True)

    # ── DAP + EBIT ───────────────────────────────────────────────────────────
    st.markdown(section_title("6. Amortissements → EBIT"), unsafe_allow_html=True)
    show_info("dap")
    st.markdown(cr_row("(-) Dotations aux amortissements (DAP)", fmt(cr["dap"]), "indent", True), unsafe_allow_html=True)
    show_info("ebit")
    st.markdown(cr_row(f"= EBIT — Résultat opérationnel ({fmt_pct(cr['marge_oper_pct'])})", fmt(cr["ebit"]), "subtotal"), unsafe_allow_html=True)

    # ── RÉSULTAT FINANCIER ───────────────────────────────────────────────────
    st.markdown(section_title("7. Résultat financier"), unsafe_allow_html=True)
    show_info("rf")
    st.markdown(cr_row("(-) Charges d'intérêts (emprunts)", fmt(cr["charges_interets"]), "indent", True), unsafe_allow_html=True)
    st.markdown(cr_row("= Résultat financier", fmt(cr["resultat_financier"]), "indent"), unsafe_allow_html=True)

    show_info("rcai")
    st.markdown(cr_row("= Résultat courant avant impôt (RCAI)", fmt(cr["rcai"]), "subtotal"), unsafe_allow_html=True)

    # ── RÉSULTAT EXCEPTIONNEL ────────────────────────────────────────────────
    st.markdown(section_title("8. Résultat exceptionnel"), unsafe_allow_html=True)
    show_info("re")
    st.markdown(cr_row("Résultat exceptionnel", fmt(cr["resultat_exceptionnel"]), "indent"), unsafe_allow_html=True)

    show_info("rai")
    st.markdown(cr_row("= Résultat avant impôt (RAI)", fmt(cr["rai"]), "subtotal"), unsafe_allow_html=True)

    # ── IS ───────────────────────────────────────────────────────────────────
    st.markdown(section_title("9. Impôt sur les sociétés (IS)"), unsafe_allow_html=True)
    show_info("is")
    st.markdown(cr_row(f"(-) IS ({cr['taux_is']:.0f}%)", fmt(cr["is_du"]), "indent", True), unsafe_allow_html=True)

    # ── RÉSULTAT NET ─────────────────────────────────────────────────────────
    st.markdown(section_title("10. Résultat net"), unsafe_allow_html=True)
    show_info("rn")
    st.markdown(cr_row(f"= RÉSULTAT NET", fmt(cr["resultat_net"]), "total"), unsafe_allow_html=True)

    # ── MARGES ───────────────────────────────────────────────────────────────
    st.markdown(section_title("Ratios de marge"), unsafe_allow_html=True)
    show_info("marges")
    c1,c2,c3,c4 = st.columns(4)
    c1.metric("Marge brute", fmt_pct(cr["marge_brute_pct"]))
    c2.metric("Marge EBITDA", fmt_pct(cr["ebitda_pct"]))
    c3.metric("Marge opérationnelle", fmt_pct(cr["marge_oper_pct"]))
    c4.metric("Marge nette", fmt_pct(cr["marge_nette_pct"]))

    # Waterfall chart
    st.markdown(section_title("Décomposition visuelle"), unsafe_allow_html=True)
    fig = go.Figure(go.Waterfall(
        measure=["relative","relative","relative","relative","relative","relative","total"],
        x=["CA","- CMV","- Charges","- DAP","+ Rés.Fin.","- IS","Résultat net"],
        y=[cr["ca"], -cr["cmv_total"], -cr["total_charges_exploitation"],
           -cr["dap"], cr["resultat_financier"], -cr["is_du"], cr["resultat_net"]],
        connector={"line":{"color":"#e5e7eb"}},
        increasing={"marker":{"color":"#059669"}},
        decreasing={"marker":{"color":"#dc2626"}},
        totals={"marker":{"color":"#7c3aed"}},
        texttemplate="%{y:,.0f}", textposition="outside",
    ))
    fig.update_layout(paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
                       margin=dict(t=10,b=10,l=10,r=10), height=300,
                       yaxis_title="FCFA", showlegend=False)
    st.plotly_chart(fig, use_container_width=True, config={"displayModeBar":False})

    # Export
    st.markdown(section_title("Exporter"), unsafe_allow_html=True)
    pdf_buf = export_compte_resultat_pdf(cr, label)
    st.download_button("⬇️ Télécharger le compte de résultat (PDF)",
                        data=pdf_buf, file_name=f"compte_resultat_{d1s}_{d2s}.pdf",
                        mime="application/pdf", use_container_width=True)

import streamlit as st
import plotly.graph_objects as go
from datetime import date, timedelta
import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))
from utils.database import compute_bilan, compute_compte_resultat, compute_ratios
from utils.styles import page_header, section_title, fmt, fmt_pct, fmt_x
from utils.exports import export_ratios_pdf

RATIOS_META = {
    "roe": {
        "nom": "ROE — Rentabilité des capitaux propres",
        "formule": "Résultat net ÷ Capitaux propres × 100",
        "description": (
            "Le ROE mesure combien l'entreprise génère de bénéfice pour chaque franc investi par les associés. "
            "Un ROE de 15% signifie que pour 100 FCFA investis, l'entreprise génère 15 FCFA de bénéfice net."
        ),
        "norme": "Bon : > 10% | Excellent : > 20% | Insuffisant : < 5%",
        "seuil_bon": 10, "seuil_ok": 5, "unite": "%",
    },
    "roa": {
        "nom": "ROA — Rentabilité des actifs",
        "formule": "Résultat net ÷ Total actif × 100",
        "description": (
            "Le ROA mesure l'efficacité avec laquelle l'entreprise utilise tous ses actifs (stocks, équipements, trésorerie) "
            "pour générer du bénéfice. Plus il est élevé, plus les actifs sont bien exploités."
        ),
        "norme": "Bon : > 5% | Acceptable : > 2% | Faible : < 2%",
        "seuil_bon": 5, "seuil_ok": 2, "unite": "%",
    },
    "endettement": {
        "nom": "Ratio d'endettement",
        "formule": "Dettes totales ÷ Capitaux propres",
        "description": (
            "Mesure le niveau de risque financier. Un ratio de 0,5x signifie que les dettes représentent "
            "la moitié des capitaux propres. Au-delà de 1x, l'entreprise doit plus à ses créanciers qu'elle ne possède."
        ),
        "norme": "Excellent : < 0,3x | Acceptable : 0,3–1x | Risqué : > 1x",
        "seuil_bon": 0.3, "seuil_ok": 1.0, "unite": "x", "inverse": True,
    },
    "liquidite": {
        "nom": "Ratio de liquidité générale",
        "formule": "Actif circulant ÷ Dettes court terme",
        "description": (
            "Mesure la capacité de l'entreprise à rembourser ses dettes à court terme avec ses actifs circulants "
            "(stocks + créances + trésorerie). Un ratio > 1 signifie que vous pouvez couvrir vos dettes immédiates."
        ),
        "norme": "Bon : > 1,5x | Minimum : > 1x | Danger : < 1x",
        "seuil_bon": 1.5, "seuil_ok": 1.0, "unite": "x",
    },
    "fr": {
        "nom": "Fonds de roulement (FR)",
        "formule": "Capitaux permanents − Actif immobilisé",
        "description": (
            "Le fonds de roulement est la réserve de financement disponible pour couvrir le cycle d'exploitation "
            "(achats, stocks, ventes). Un FR positif est indispensable — il signifie que vos ressources durables "
            "financent vos actifs durables ET qu'il reste de la marge."
        ),
        "norme": "Positif = sain | Négatif = structure fragile",
        "seuil_bon": 1, "seuil_ok": 0, "unite": "FCFA",
    },
    "bfr": {
        "nom": "Besoin en fonds de roulement (BFR)",
        "formule": "Stocks + Créances clients − Dettes d'exploitation",
        "description": (
            "Le BFR est le montant que vous devez financer en permanence pour que votre activité tourne. "
            "Un BFR élevé signifie que vous immobilisez beaucoup d'argent dans les stocks et les créances. "
            "L'idéal est de le garder le plus bas possible."
        ),
        "norme": "Faible = bien | Élevé = surveiller | Négatif = très bon (fournisseurs financent)",
        "seuil_bon": 0, "seuil_ok": 500000, "unite": "FCFA", "inverse": True,
    },
    "tresorerie_nette": {
        "nom": "Trésorerie nette",
        "formule": "Fonds de roulement − BFR",
        "description": (
            "C'est la position de trésorerie structurelle. Positive = vous avez plus de cash disponible "
            "que nécessaire pour financer le cycle. Négative = vous êtes en tension de trésorerie et devez "
            "emprunter pour fonctionner."
        ),
        "norme": "Positif = sain | Négatif = tension de trésorerie",
        "seuil_bon": 1, "seuil_ok": 0, "unite": "FCFA",
    },
}


def signal_color(key, value):
    meta = RATIOS_META.get(key, {})
    seuil_bon = meta.get("seuil_bon", 0)
    seuil_ok  = meta.get("seuil_ok", 0)
    inverse   = meta.get("inverse", False)
    if not inverse:
        if value >= seuil_bon: return "good", "🟢 Bon"
        if value >= seuil_ok:  return "warn", "🟡 Acceptable"
        return "bad", "🔴 À améliorer"
    else:
        if value <= seuil_bon: return "good", "🟢 Bon"
        if value <= seuil_ok:  return "warn", "🟡 Acceptable"
        return "bad", "🔴 Risqué"


def render_ratio_card(key, value, meta, mode_peda):
    sig_cls, sig_txt = signal_color(key, value)

    if meta["unite"] == "%":
        val_str = f"{value:.1f}%"
    elif meta["unite"] == "x":
        val_str = f"{value:.2f}x" if value < 999 else "∞"
    else:
        val_str = fmt(value)

    st.markdown(f"""
    <div class="ratio-card">
        <div class="ratio-name">{meta["nom"]}</div>
        <div style="display:flex;align-items:baseline;gap:.7rem">
            <div class="ratio-value">{val_str}</div>
            <div class="ratio-signal {sig_cls}">{sig_txt}</div>
        </div>
        <div class="ratio-formula">📐 {meta["formule"]}</div>
        {'<div class="ratio-desc">' + meta["description"] + '<br><em style="color:#6d28d9">Norme : ' + meta["norme"] + '</em></div>' if mode_peda else ''}
    </div>""", unsafe_allow_html=True)


def show():
    st.markdown(page_header("📐 Ratios financiers",
                             "Les indicateurs clés pour piloter la santé de votre entreprise"), unsafe_allow_html=True)

    col_p, col_d = st.columns([3, 2])
    with col_p:
        annee = st.selectbox("Exercice", [str(date.today().year), str(date.today().year - 1)], key="ratios_annee")
    d1s = f"{annee}-01-01"
    d2s = str(date.today()) if annee == str(date.today().year) else f"{annee}-12-31"

    mode_peda = st.toggle("📚 Mode pédagogique — afficher les explications", value=True, key="ratios_peda")

    bilan  = compute_bilan(d2s)
    cr     = compute_compte_resultat(d1s, d2s)
    ratios = compute_ratios(bilan, cr)
    label  = f"Exercice {annee}"

    # Vue synthétique rapide
    c1, c2, c3, c4 = st.columns(4)
    c1.metric("ROE", f"{ratios['roe']:.1f}%", help="Rentabilité capitaux propres")
    c2.metric("ROA", f"{ratios['roa']:.1f}%", help="Rentabilité des actifs")
    c3.metric("Endettement", f"{ratios['ratio_endettement']:.2f}x", help="Dettes / Capitaux propres")
    c4.metric("Liquidité", f"{min(ratios['liquidite_generale'],99):.2f}x", help="Actif circ. / Dettes CT")

    st.markdown("<br>", unsafe_allow_html=True)

    # ── RENTABILITÉ ───────────────────────────────────────────────────────────
    st.markdown(section_title("Ratios de rentabilité"), unsafe_allow_html=True)
    col_r1, col_r2 = st.columns(2)
    with col_r1:
        render_ratio_card("roe", ratios["roe"], RATIOS_META["roe"], mode_peda)
    with col_r2:
        render_ratio_card("roa", ratios["roa"], RATIOS_META["roa"], mode_peda)

    # Graphique radar rentabilité vs normes
    fig_radar = go.Figure(go.Scatterpolar(
        r=[min(ratios["roe"], 30), min(ratios["roa"], 15),
           max(0, 20 - ratios["ratio_endettement"]*10),
           min(ratios["liquidite_generale"] if ratios["liquidite_generale"] < 999 else 3, 3) * 5,
           min(max(ratios["fonds_roulement"] / 100000, 0), 10)],
        theta=["ROE", "ROA", "Solvabilité", "Liquidité", "Fonds de roulement"],
        fill="toself",
        name="Votre entreprise",
        line_color="#7c3aed", fillcolor="rgba(124,58,237,0.2)",
    ))
    fig_radar.add_trace(go.Scatterpolar(
        r=[10, 5, 10, 7.5, 5],
        theta=["ROE", "ROA", "Solvabilité", "Liquidité", "Fonds de roulement"],
        fill="toself", name="Norme minimale",
        line_color="#d97706", fillcolor="rgba(217,119,6,0.1)",
        line_dash="dash",
    ))
    fig_radar.update_layout(
        polar=dict(radialaxis=dict(visible=True, range=[0, 15])),
        paper_bgcolor="rgba(0,0,0,0)", height=320,
        margin=dict(t=30, b=10),
        legend=dict(orientation="h", y=-0.1),
        showlegend=True,
    )
    st.plotly_chart(fig_radar, use_container_width=True, config={"displayModeBar": False})

    # ── SOLVABILITÉ / ENDETTEMENT ─────────────────────────────────────────────
    st.markdown(section_title("Ratio d'endettement"), unsafe_allow_html=True)
    render_ratio_card("endettement", ratios["ratio_endettement"], RATIOS_META["endettement"], mode_peda)

    # ── LIQUIDITÉ ─────────────────────────────────────────────────────────────
    st.markdown(section_title("Ratio de liquidité générale"), unsafe_allow_html=True)
    liq_val = min(ratios["liquidite_generale"], 999)
    render_ratio_card("liquidite", liq_val, RATIOS_META["liquidite"], mode_peda)

    # ── FONDS DE ROULEMENT & BFR ──────────────────────────────────────────────
    st.markdown(section_title("Fonds de roulement, BFR et Trésorerie nette"), unsafe_allow_html=True)

    col_f1, col_f2, col_f3 = st.columns(3)
    with col_f1:
        render_ratio_card("fr", ratios["fonds_roulement"], RATIOS_META["fr"], mode_peda)
    with col_f2:
        render_ratio_card("bfr", ratios["bfr"], RATIOS_META["bfr"], mode_peda)
    with col_f3:
        render_ratio_card("tresorerie_nette", ratios["tresorerie_nette"], RATIOS_META["tresorerie_nette"], mode_peda)

    # Schéma FR / BFR / TN
    if mode_peda:
        st.markdown(f"""
        <div class="info-box purple">
        <strong>🔗 La relation FR → BFR → Trésorerie nette</strong><br>
        Le fonds de roulement ({fmt(ratios["fonds_roulement"])}) est votre «&nbsp;matelas&nbsp;» de financement.<br>
        Il finance le BFR ({fmt(ratios["bfr"])}) — ce que votre cycle opérationnel consomme.<br>
        Ce qu'il reste = Trésorerie nette ({fmt(ratios["tresorerie_nette"])}).
        <br><em>📐 FR − BFR = Trésorerie nette</em>
        </div>""", unsafe_allow_html=True)

    # Export
    st.markdown(section_title("Exporter"), unsafe_allow_html=True)
    pdf_buf = export_ratios_pdf(ratios, label)
    st.download_button("⬇️ Télécharger les ratios financiers (PDF)",
                        data=pdf_buf, file_name=f"ratios_{annee}.pdf",
                        mime="application/pdf", use_container_width=True)

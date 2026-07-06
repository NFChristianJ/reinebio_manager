import streamlit as st
import plotly.graph_objects as go
from datetime import date, timedelta
import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))
from utils.database import (compute_compte_resultat, compute_bilan, compute_flux_tresorerie,
                              compute_ratios, get_ventes, get_achats, get_depenses,
                              get_ventes_par_produit, get_ventes_par_ville)
from utils.styles import page_header, section_title, info_box, fmt, fmt_pct
from utils.exports import export_rapport_global_pdf, export_global_excel


def _periode(p, today):
    if p == "Semaine en cours":
        d1 = today - timedelta(days=today.weekday()); d2 = today
        label = f"Semaine du {d1.strftime('%d/%m')} au {d2.strftime('%d/%m/%Y')}"
    elif p == "Semaine dernière":
        d1 = today - timedelta(days=today.weekday()+7); d2 = d1 + timedelta(6)
        label = f"Semaine du {d1.strftime('%d/%m')} au {d2.strftime('%d/%m/%Y')}"
    elif p == "Mois en cours":
        d1 = today.replace(day=1); d2 = today; label = today.strftime("%B %Y")
    elif p == "Mois dernier":
        first = today.replace(day=1); d2 = first - timedelta(1); d1 = d2.replace(day=1)
        label = d1.strftime("%B %Y")
    elif p == "Trimestre en cours":
        q = (today.month-1)//3; d1 = date(today.year, q*3+1, 1); d2 = today
        label = f"T{q+1} {today.year}"
    elif p == "Cette année":
        d1 = today.replace(month=1, day=1); d2 = today; label = str(today.year)
    return d1, d2, label


def show():
    st.markdown(page_header("📋 Rapport financier global",
                             "Bilan + Compte de résultat + Flux + Ratios — tout en un seul document"), unsafe_allow_html=True)

    # Sélection période
    col_t, col_d1, col_d2 = st.columns([2, 2, 2])
    with col_t:
        type_p = st.selectbox("Type de rapport", [
            "Semaine en cours", "Semaine dernière",
            "Mois en cours", "Mois dernier",
            "Trimestre en cours", "Cette année", "Personnalisé"
        ])

    today = date.today()
    if type_p != "Personnalisé":
        d1, d2, label = _periode(type_p, today)
    else:
        with col_d1: d1 = st.date_input("Du", today.replace(day=1), key="rg_d1")
        with col_d2: d2 = st.date_input("Au", today, key="rg_d2")
        label = f"{d1} → {d2}"

    d1s, d2s = str(d1), str(d2)

    if st.button("🔄 Générer le rapport complet", type="primary", use_container_width=True):
        st.session_state["rg_ok"]    = True
        st.session_state["rg_d1"]   = d1s
        st.session_state["rg_d2"]   = d2s
        st.session_state["rg_label"]= label

    if not st.session_state.get("rg_ok"):
        st.markdown(info_box(
            "Sélectionnez une période puis cliquez sur « Générer le rapport complet ». "
            "Le rapport intègre les 4 états financiers et tous les ratios, avec export PDF et Excel.", "blue"),
            unsafe_allow_html=True)
        return

    d1s   = st.session_state["rg_d1"]
    d2s   = st.session_state["rg_d2"]
    label = st.session_state["rg_label"]

    # ── Calculs ───────────────────────────────────────────────────────────────
    with st.spinner("Calcul des états financiers…"):
        cr        = compute_compte_resultat(d1s, d2s)
        bilan     = compute_bilan(d2s)
        flux      = compute_flux_tresorerie(d1s, d2s)
        ratios    = compute_ratios(bilan, cr)
        ventes    = get_ventes(d1s, d2s)
        achats    = get_achats(d1s, d2s)
        depenses  = get_depenses(d1s, d2s)
        par_prod  = get_ventes_par_produit(d1s, d2s)
        par_ville = get_ventes_par_ville(d1s, d2s)

    st.markdown(f"## 📊 Rapport — {label}")

    # ── RÉSUMÉ EXÉCUTIF ───────────────────────────────────────────────────────
    st.markdown(section_title("Résumé exécutif"), unsafe_allow_html=True)
    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Chiffre d'affaires", fmt(cr["ca"]))
    c2.metric("Bénéfice net", fmt(cr["resultat_net"]),
              delta=f"Marge {cr['marge_nette_pct']:.1f}%")
    c3.metric("Flux de tréso.", fmt(flux["variation_tresorerie"]))
    c4.metric("ROE", f"{ratios['roe']:.1f}%")

    c5, c6, c7, c8 = st.columns(4)
    c5.metric("Marge brute", fmt_pct(cr["marge_brute_pct"]))
    c6.metric("EBITDA", fmt(cr["ebitda"]))
    c7.metric("Total actif", fmt(bilan["total_actif"]))
    c8.metric("Fonds de roulement", fmt(ratios["fonds_roulement"]))

    # ── I. COMPTE DE RÉSULTAT (résumé) ────────────────────────────────────────
    st.markdown(section_title("I. Compte de résultat"), unsafe_allow_html=True)
    lignes = [
        ("(+) Chiffre d'affaires",          cr["ca"],               False),
        ("(-) Coût marchandises vendues",    cr["cmv_total"],        True),
        ("= Marge brute",                   cr["marge_brute"],      False),
        ("(-) Charges d'exploitation",       cr["total_charges_exploitation"], True),
        ("= EBITDA",                        cr["ebitda"],           False),
        ("(-) Amortissements (DAP)",         cr["dap"],              True),
        ("= EBIT",                          cr["ebit"],             False),
        ("Résultat financier",              cr["resultat_financier"],False),
        ("= Résultat avant impôt",          cr["rai"],              False),
        (f"(-) IS ({cr['taux_is']:.0f}%)",  cr["is_du"],            True),
        ("= RÉSULTAT NET",                  cr["resultat_net"],     False),
    ]
    for libelle, val, is_charge in lignes:
        is_total = libelle.startswith("=")
        bg = "#ede9fe" if is_total else "white"
        fw = "700" if is_total else "400"
        color = "#dc2626" if is_charge else ("#059669" if val >= 0 else "#dc2626")
        pref = "-" if is_charge else ("+" if val > 0 else "")
        st.markdown(f"""
        <div style="display:flex;justify-content:space-between;padding:.35rem .7rem;
                    background:{bg};border-radius:6px;margin:.1rem 0;font-weight:{fw};font-size:.87rem">
            <span style="color:#1e1b4b">{libelle}</span>
            <span style="color:{color}">{pref}{fmt(abs(val))}</span>
        </div>""", unsafe_allow_html=True)

    # ── II. BILAN (résumé) ────────────────────────────────────────────────────
    st.markdown(section_title("II. Bilan"), unsafe_allow_html=True)
    col_ba, col_bp = st.columns(2)
    with col_ba:
        st.markdown("**ACTIF**")
        items_a = [
            ("Immobilisations nettes", bilan["valeur_nette_immos"]),
            ("Stocks", bilan["valeur_stock"]),
            ("Créances", bilan["creances_clients"]),
            ("Trésorerie", bilan["tresorerie"]),
            ("**TOTAL ACTIF**", bilan["total_actif"]),
        ]
        for lib, val in items_a:
            bold = "700" if lib.startswith("**") else "400"
            clean = lib.replace("**","")
            st.markdown(f'<div style="display:flex;justify-content:space-between;padding:.28rem .5rem;font-size:.85rem;font-weight:{bold};border-bottom:1px solid #f3f4f6"><span>{clean}</span><span>{fmt(val)}</span></div>', unsafe_allow_html=True)
    with col_bp:
        st.markdown("**PASSIF**")
        items_p = [
            ("Capitaux propres", bilan["total_capitaux_propres"]),
            ("Dettes financières", bilan["total_dettes_financieres"]),
            ("Dettes d'exploitation", bilan["total_dettes_exploit"]),
            ("**TOTAL PASSIF**", bilan["total_passif"]),
        ]
        for lib, val in items_p:
            bold = "700" if lib.startswith("**") else "400"
            clean = lib.replace("**","")
            st.markdown(f'<div style="display:flex;justify-content:space-between;padding:.28rem .5rem;font-size:.85rem;font-weight:{bold};border-bottom:1px solid #f3f4f6"><span>{clean}</span><span>{fmt(val)}</span></div>', unsafe_allow_html=True)

    # ── III. FLUX (résumé) ────────────────────────────────────────────────────
    st.markdown(section_title("III. Tableau des flux de trésorerie"), unsafe_allow_html=True)
    flux_items = [
        ("→ Flux d'exploitation",    flux["flux_exploitation"]),
        ("→ Flux d'investissement",  flux["flux_investissement"]),
        ("→ Flux de financement",    flux["flux_financement"]),
        ("= Variation de trésorerie",flux["variation_tresorerie"]),
        ("Trésorerie initiale",      flux["tresorerie_init"]),
        ("Trésorerie finale",        flux["tresorerie_finale"]),
    ]
    for lib, val in flux_items:
        is_total = lib.startswith("=") or lib == "Trésorerie finale"
        color = "#059669" if val >= 0 else "#dc2626"
        bg = "#f0fdf4" if (val >= 0 and is_total) else ("#fef2f2" if (val < 0 and is_total) else "white")
        st.markdown(f"""
        <div style="display:flex;justify-content:space-between;padding:.35rem .7rem;
                    background:{bg};border-radius:6px;margin:.1rem 0;font-size:.87rem;
                    font-weight:{'700' if is_total else '400'}">
            <span>{lib}</span>
            <span style="color:{color}">{'+' if val>=0 else ''}{fmt(val)}</span>
        </div>""", unsafe_allow_html=True)

    # ── IV. RATIOS ────────────────────────────────────────────────────────────
    st.markdown(section_title("IV. Ratios financiers"), unsafe_allow_html=True)

    def signal(val, seuil_bon, seuil_ok, inverse=False):
        if not inverse:
            if val >= seuil_bon: return "🟢"
            if val >= seuil_ok:  return "🟡"
            return "🔴"
        else:
            if val <= seuil_bon: return "🟢"
            if val <= seuil_ok:  return "🟡"
            return "🔴"

    ratios_display = [
        ("ROE", f"{ratios['roe']:.1f}%", signal(ratios["roe"],10,5), "Rentabilité capitaux propres"),
        ("ROA", f"{ratios['roa']:.1f}%", signal(ratios["roa"],5,2),  "Rentabilité des actifs"),
        ("Endettement", f"{ratios['ratio_endettement']:.2f}x", signal(ratios["ratio_endettement"],0.3,1,True), "Dettes/CP"),
        ("Liquidité gén.", f"{min(ratios['liquidite_generale'],99):.2f}x", signal(ratios["liquidite_generale"],1.5,1), "Actif circ./Dettes CT"),
        ("Fonds de roulement", fmt(ratios["fonds_roulement"]), signal(ratios["fonds_roulement"],1,0), "Cap.perm − Actif immo"),
        ("BFR", fmt(ratios["bfr"]), signal(ratios["bfr"],0,500000,True), "Stock+Créances−Dettes expl."),
        ("Trésorerie nette", fmt(ratios["tresorerie_nette"]), signal(ratios["tresorerie_nette"],1,0), "FR − BFR"),
    ]

    cols = st.columns(4)
    for i, (nom, val, sig, desc) in enumerate(ratios_display):
        with cols[i % 4]:
            st.markdown(f"""
            <div style="background:white;border-radius:10px;padding:.8rem 1rem;margin-bottom:.6rem;
                        box-shadow:0 1px 6px rgba(0,0,0,.07);text-align:center">
                <div style="font-size:.7rem;color:#6b7280;font-weight:700;text-transform:uppercase">{nom}</div>
                <div style="font-size:1.2rem;font-weight:800;color:#1e1b4b;margin:.2rem 0">{val}</div>
                <div style="font-size:1.1rem">{sig}</div>
                <div style="font-size:.68rem;color:#9ca3af">{desc}</div>
            </div>""", unsafe_allow_html=True)

    # ── GRAPHIQUE WATERFALL ───────────────────────────────────────────────────
    st.markdown(section_title("Du CA au Résultat net"), unsafe_allow_html=True)
    fig = go.Figure(go.Waterfall(
        measure=["relative","relative","relative","relative","relative","relative","total"],
        x=["CA","− CMV","− Charges","− DAP","± Fin.","− IS","Résultat net"],
        y=[cr["ca"], -cr["cmv_total"], -cr["total_charges_exploitation"],
           -cr["dap"], cr["resultat_financier"], -cr["is_du"], cr["resultat_net"]],
        connector={"line":{"color":"#e5e7eb"}},
        increasing={"marker":{"color":"#059669"}},
        decreasing={"marker":{"color":"#dc2626"}},
        totals={"marker":{"color":"#7c3aed"}},
        texttemplate="%{y:,.0f}", textposition="outside",
    ))
    fig.update_layout(paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
                       margin=dict(t=20,b=10), height=300,
                       yaxis_title="FCFA", showlegend=False)
    st.plotly_chart(fig, use_container_width=True, config={"displayModeBar":False})

    # ── EXPORTS ───────────────────────────────────────────────────────────────
    st.markdown(section_title("📥 Exporter le rapport complet"), unsafe_allow_html=True)
    st.markdown(info_box("Le PDF contient les 4 états financiers complets + ratios commentés. L'Excel contient un onglet par état.", "purple"), unsafe_allow_html=True)

    col_e1, col_e2 = st.columns(2)
    with col_e1:
        pdf_buf = export_rapport_global_pdf(cr, bilan, flux, ratios, label, par_prod, par_ville)
        st.download_button("⬇️ Rapport complet (PDF)", data=pdf_buf,
                            file_name=f"rapport_financier_{d1s}_{d2s}.pdf",
                            mime="application/pdf", use_container_width=True)
    with col_e2:
        excel_buf = export_global_excel(cr, bilan, flux, ratios, label,
                                         ventes, achats, depenses, par_prod, par_ville)
        st.download_button("⬇️ Rapport complet (Excel)", data=excel_buf,
                            file_name=f"rapport_financier_{d1s}_{d2s}.xlsx",
                            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                            use_container_width=True)

    # Exports individuels
    st.markdown(section_title("📄 Exports individuels"), unsafe_allow_html=True)
    from utils.exports import export_compte_resultat_pdf, export_bilan_pdf, export_flux_pdf, export_ratios_pdf
    col_i1, col_i2, col_i3, col_i4 = st.columns(4)
    with col_i1:
        buf = export_compte_resultat_pdf(cr, label)
        st.download_button("📈 Compte de résultat", data=buf,
                            file_name=f"compte_resultat_{d1s}_{d2s}.pdf",
                            mime="application/pdf", use_container_width=True)
    with col_i2:
        buf = export_bilan_pdf(bilan, d2s)
        st.download_button("⚖️ Bilan", data=buf,
                            file_name=f"bilan_{d2s}.pdf",
                            mime="application/pdf", use_container_width=True)
    with col_i3:
        buf = export_flux_pdf(flux, label)
        st.download_button("💧 Flux de tréso.", data=buf,
                            file_name=f"flux_{d1s}_{d2s}.pdf",
                            mime="application/pdf", use_container_width=True)
    with col_i4:
        buf = export_ratios_pdf(ratios, label)
        st.download_button("📐 Ratios", data=buf,
                            file_name=f"ratios_{d1s}_{d2s}.pdf",
                            mime="application/pdf", use_container_width=True)

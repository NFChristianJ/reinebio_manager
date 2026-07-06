import io, pandas as pd
from reportlab.lib.pagesizes import A4
from reportlab.lib import colors
from reportlab.lib.styles import ParagraphStyle
from reportlab.lib.units import cm
from reportlab.platypus import (SimpleDocTemplate, Table, TableStyle,
                                 Paragraph, Spacer, HRFlowable, PageBreak)
from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_RIGHT

# Palette
V   = colors.HexColor("#6d28d9")
VL  = colors.HexColor("#ede9fe")
R   = colors.HexColor("#be185d")
C   = colors.HexColor("#0891b2")
G   = colors.HexColor("#059669")
O   = colors.HexColor("#d97706")
GR  = colors.HexColor("#6b7280")
W   = colors.white
BK  = colors.HexColor("#1e1b4b")
ERR = colors.HexColor("#dc2626")


def _style(name, **kw):
    base = {"fontName":"Helvetica","fontSize":9,"leading":13,"textColor":BK}
    base.update(kw)
    return ParagraphStyle(name, **base)

T_TITLE   = _style("tt", fontSize=20, fontName="Helvetica-Bold", textColor=V, alignment=TA_CENTER, spaceAfter=4)
T_PERIOD  = _style("tp", fontSize=9,  textColor=GR, alignment=TA_CENTER, spaceAfter=14)
T_SECTION = _style("ts", fontSize=12, fontName="Helvetica-Bold", textColor=V, spaceBefore=14, spaceAfter=6)
T_BODY    = _style("tb", fontSize=8.5, leading=13)
T_FOOTER  = _style("tf", fontSize=7, textColor=GR, alignment=TA_CENTER, spaceBefore=6)
T_NOTE    = _style("tn", fontSize=7.5, textColor=colors.HexColor("#4b5563"), leading=11, spaceBefore=3)


def _table(data, col_widths, header_bg=V, alt=None):
    t = Table(data, colWidths=col_widths)
    alt_color = alt or colors.HexColor("#f5f3ff")
    style = [
        ("BACKGROUND",  (0,0),(-1,0), header_bg),
        ("TEXTCOLOR",   (0,0),(-1,0), W),
        ("FONTNAME",    (0,0),(-1,0), "Helvetica-Bold"),
        ("FONTSIZE",    (0,0),(-1,-1), 8.5),
        ("ROWBACKGROUNDS",(0,1),(-1,-1),[W, alt_color]),
        ("GRID",        (0,0),(-1,-1), 0.25, colors.HexColor("#e5e7eb")),
        ("ALIGN",       (1,0),(-1,-1), "RIGHT"),
        ("VALIGN",      (0,0),(-1,-1), "MIDDLE"),
        ("PADDING",     (0,0),(-1,-1), 5),
    ]
    t.setStyle(TableStyle(style))
    return t


def _kpi_table(kpis_list):
    """kpis_list = [(label, value), ...]"""
    data = [["Indicateur","Valeur"]] + [[k,v] for k,v in kpis_list]
    t = Table(data, colWidths=[10*cm, 6*cm])
    style = [
        ("BACKGROUND", (0,0),(-1,0), V),
        ("TEXTCOLOR",  (0,0),(-1,0), W),
        ("FONTNAME",   (0,0),(-1,0), "Helvetica-Bold"),
        ("FONTSIZE",   (0,0),(-1,-1), 9),
        ("ROWBACKGROUNDS",(0,1),(-1,-1),[W, VL]),
        ("GRID",(0,0),(-1,-1),0.3, colors.HexColor("#e5e7eb")),
        ("ALIGN",(1,0),(1,-1),"RIGHT"),
        ("PADDING",(0,0),(-1,-1),5),
    ]
    t.setStyle(TableStyle(style)); return t


# ── RAPPORT COMPLET ───────────────────────────────────────────────────────────
def export_rapport_global_pdf(cr, bilan, flux, ratios, periode, par_produit, par_ville):
    buf = io.BytesIO()
    doc = SimpleDocTemplate(buf, pagesize=A4,
                             topMargin=1.5*cm, bottomMargin=1.5*cm,
                             leftMargin=1.8*cm, rightMargin=1.8*cm)
    story = []

    def HR(): return HRFlowable(width="100%", thickness=1, color=V, spaceAfter=10)
    def SP(h=0.3): return Spacer(1, h*cm)

    # ── Couverture ────────────────────────────────────────────────────────
    story += [SP(2), Paragraph("RAPPORT FINANCIER COMPLET", T_TITLE),
              Paragraph(f"Période : {periode}", T_PERIOD), HR()]

    # KPIs résumé
    story.append(Paragraph("Résultats clés", T_SECTION))
    story.append(_kpi_table([
        ("Chiffre d'affaires",      f"{cr['ca']:,.0f} FCFA"),
        ("Marge brute",             f"{cr['marge_brute']:,.0f} FCFA ({cr['marge_brute_pct']:.1f}%)"),
        ("EBITDA",                  f"{cr['ebitda']:,.0f} FCFA ({cr['ebitda_pct']:.1f}%)"),
        ("Résultat net",            f"{cr['resultat_net']:,.0f} FCFA"),
        ("Marge nette",             f"{cr['marge_nette_pct']:.1f}%"),
        ("Total actif",             f"{bilan['total_actif']:,.0f} FCFA"),
        ("Capitaux propres",        f"{bilan['total_capitaux_propres']:,.0f} FCFA"),
        ("ROE",                     f"{ratios['roe']:.1f}%"),
        ("ROA",                     f"{ratios['roa']:.1f}%"),
        ("Fonds de roulement",      f"{ratios['fonds_roulement']:,.0f} FCFA"),
    ]))
    story.append(PageBreak())

    # ── I. Compte de résultat ─────────────────────────────────────────────
    story.append(Paragraph("I. COMPTE DE RÉSULTAT", T_SECTION))
    story.append(HR())
    cr_rows = [
        ["Ligne","Montant (FCFA)","Note"],
        ["(+) Chiffre d'affaires",               f"{cr['ca']:,.0f}",   "Ventes nettes de remises"],
        ["(-) Coût des marchandises vendues",      f"-{cr['cmv_total']:,.0f}", "Coût achat + transport"],
        ["= MARGE BRUTE",                          f"{cr['marge_brute']:,.0f}", f"{cr['marge_brute_pct']:.1f}% du CA"],
        ["(-) Publicité",                          f"-{cr['pub']:,.0f}",  "Facebook Ads et autres"],
        ["(-) Transport & livraisons",             f"-{cr['transport']:,.0f}", ""],
        ["(-) Personnel",                          f"-{cr['personnel']:,.0f}", ""],
        ["(-) Charges fixes",                      f"-{cr['fixes']:,.0f}", "Téléphone, internet…"],
        ["(-) Autres charges",                     f"-{cr['autres_charges']:,.0f}", ""],
        ["= EBITDA",                               f"{cr['ebitda']:,.0f}", f"{cr['ebitda_pct']:.1f}% du CA"],
        ["(-) Dotations amortissements (DAP)",     f"-{cr['dap']:,.0f}", "Perte de valeur immobilisations"],
        ["= EBIT (Résultat opérationnel)",         f"{cr['ebit']:,.0f}", f"Marge oper. {cr['marge_oper_pct']:.1f}%"],
        ["Résultat financier",                     f"{cr['resultat_financier']:,.0f}", "Charges d'intérêts"],
        ["= Résultat courant avant impôt (RCAI)",  f"{cr['rcai']:,.0f}", ""],
        ["Résultat exceptionnel",                  f"{cr['resultat_exceptionnel']:,.0f}", "Hors activité normale"],
        ["= Résultat avant impôt (RAI)",           f"{cr['rai']:,.0f}", ""],
        [f"(-) Impôt sur les sociétés ({cr['taux_is']:.0f}%)", f"-{cr['is_du']:,.0f}", "IS dû"],
        ["= RÉSULTAT NET",                         f"{cr['resultat_net']:,.0f}", f"Marge nette {cr['marge_nette_pct']:.1f}%"],
    ]
    t = Table(cr_rows, colWidths=[7.5*cm, 4*cm, 5*cm])
    t.setStyle(TableStyle([
        ("BACKGROUND", (0,0),(-1,0), V), ("TEXTCOLOR",(0,0),(-1,0),W),
        ("FONTNAME",(0,0),(-1,0),"Helvetica-Bold"),
        ("FONTSIZE",(0,0),(-1,-1),8),
        ("ROWBACKGROUNDS",(0,1),(-1,-1),[W, VL]),
        ("GRID",(0,0),(-1,-1),0.25,colors.HexColor("#e5e7eb")),
        ("FONTNAME",(0,3),(0,3),"Helvetica-Bold"), ("BACKGROUND",(0,3),(-1,3),colors.HexColor("#f0fdf4")),
        ("FONTNAME",(0,9),(0,9),"Helvetica-Bold"), ("BACKGROUND",(0,9),(-1,9),colors.HexColor("#f0fdf4")),
        ("FONTNAME",(0,11),(0,11),"Helvetica-Bold"),
        ("FONTNAME",(0,-1),(0,-1),"Helvetica-Bold"), ("BACKGROUND",(0,-1),(-1,-1),VL),
        ("TEXTCOLOR",(0,-1),(-1,-1),V),
        ("ALIGN",(1,0),(1,-1),"RIGHT"), ("PADDING",(0,0),(-1,-1),5),
    ]))
    story.append(t); story.append(PageBreak())

    # ── II. Bilan ─────────────────────────────────────────────────────────
    story.append(Paragraph("II. BILAN", T_SECTION)); story.append(HR())
    bilan_data = [
        ["ACTIF","Montant (FCFA)", "PASSIF","Montant (FCFA)"],
        ["Actif immobilisé","","Capitaux propres",""],
        [f"  Immos brutes", f"{bilan['valeur_brute_immos']:,.0f}", f"  Capital social", f"{bilan['capital_social']:,.0f}"],
        [f"  (-) Amortissements", f"-{bilan['amort_cumulees']:,.0f}", f"  Réserves & report", f"{bilan['reserve_legale']+bilan['report_nouveau']:,.0f}"],
        [f"  Immos nettes", f"{bilan['valeur_nette_immos']:,.0f}", f"  Résultat net", f"{bilan['resultat_net_exercice']:,.0f}"],
        ["Actif circulant","","Dettes financières",""],
        [f"  Stocks", f"{bilan['valeur_stock']:,.0f}", f"  Emprunts & dettes LT", f"{bilan['total_dettes_financieres']:,.0f}"],
        [f"  Créances clients", f"{bilan['creances_clients']:,.0f}", "Dettes d'exploitation",""],
        [f"  Trésorerie", f"{bilan['tresorerie']:,.0f}", f"  Dettes fournisseurs", f"{bilan['dettes_fournisseurs']:,.0f}"],
        ["","","  IS à payer", f"{bilan['dettes_etat']:,.0f}"],
        ["TOTAL ACTIF", f"{bilan['total_actif']:,.0f}", "TOTAL PASSIF", f"{bilan['total_passif']:,.0f}"],
    ]
    tb = Table(bilan_data, colWidths=[5.5*cm, 3.2*cm, 5.5*cm, 3.2*cm])
    tb.setStyle(TableStyle([
        ("BACKGROUND",(0,0),(-1,0),V), ("TEXTCOLOR",(0,0),(-1,0),W),
        ("FONTNAME",(0,0),(-1,0),"Helvetica-Bold"),
        ("FONTSIZE",(0,0),(-1,-1),8.5),
        ("ROWBACKGROUNDS",(0,1),(-1,-1),[W, VL]),
        ("GRID",(0,0),(-1,-1),0.25,colors.HexColor("#e5e7eb")),
        ("FONTNAME",(0,-1),(-1,-1),"Helvetica-Bold"),
        ("BACKGROUND",(0,-1),(-1,-1),colors.HexColor("#ede9fe")),
        ("ALIGN",(1,0),(1,-1),"RIGHT"), ("ALIGN",(3,0),(3,-1),"RIGHT"),
        ("PADDING",(0,0),(-1,-1),5),
    ]))
    story.append(tb); story.append(SP())

    # ── III. Flux de trésorerie ────────────────────────────────────────────
    story.append(Paragraph("III. TABLEAU DES FLUX DE TRÉSORERIE", T_SECTION)); story.append(HR())
    flux_data = [
        ["Catégorie", "Libellé","Montant (FCFA)"],
        ["EXPLOITATION","Encaissements clients", f"+{flux['encaiss_clients']:,.0f}"],
        ["","Achats fournisseurs",        f"-{flux['cout_achats']:,.0f}"],
        ["","Charges d'exploitation",     f"-{flux['cout_depenses']:,.0f}"],
        ["","Livraisons & commissions",   f"-{flux['cout_livraison']:,.0f}"],
        ["","IS payé",                    f"-{flux['is_paye']:,.0f}"],
        ["","FLUX EXPLOITATION",          f"{flux['flux_exploitation']:,.0f}"],
        ["INVESTISSEMENT","Acquisitions immobilisations", f"-{flux['acquisitions']:,.0f}"],
        ["","Cessions",                   f"+{flux['cessions']:,.0f}"],
        ["","FLUX INVESTISSEMENT",        f"{flux['flux_investissement']:,.0f}"],
        ["FINANCEMENT","Emprunts nouveaux",          f"+{flux['emprunts_nouveaux']:,.0f}"],
        ["","Remboursements",             f"-{flux['remboursements']:,.0f}"],
        ["","FLUX FINANCEMENT",           f"{flux['flux_financement']:,.0f}"],
        ["SYNTHÈSE","Variation de trésorerie",   f"{flux['variation_tresorerie']:,.0f}"],
        ["","Trésorerie initiale",        f"{flux['tresorerie_init']:,.0f}"],
        ["","TRÉSORERIE FINALE",          f"{flux['tresorerie_finale']:,.0f}"],
    ]
    tf = Table(flux_data, colWidths=[3.5*cm, 7*cm, 4*cm])
    tf.setStyle(TableStyle([
        ("BACKGROUND",(0,0),(-1,0),V), ("TEXTCOLOR",(0,0),(-1,0),W),
        ("FONTNAME",(0,0),(-1,0),"Helvetica-Bold"),
        ("FONTSIZE",(0,0),(-1,-1),8.5),
        ("ROWBACKGROUNDS",(0,1),(-1,-1),[W, VL]),
        ("GRID",(0,0),(-1,-1),0.25,colors.HexColor("#e5e7eb")),
        ("ALIGN",(2,0),(2,-1),"RIGHT"),
        ("FONTNAME",(0,6),(2,6),"Helvetica-Bold"),
        ("FONTNAME",(0,9),(2,9),"Helvetica-Bold"),
        ("FONTNAME",(0,12),(2,12),"Helvetica-Bold"),
        ("FONTNAME",(0,15),(2,15),"Helvetica-Bold"),
        ("BACKGROUND",(0,15),(-1,15),VL),
        ("PADDING",(0,0),(-1,-1),5),
    ]))
    story.append(tf); story.append(PageBreak())

    # ── IV. Ratios financiers ─────────────────────────────────────────────
    story.append(Paragraph("IV. RATIOS FINANCIERS", T_SECTION)); story.append(HR())
    ratios_data = [
        ["Ratio","Valeur","Formule","Interprétation"],
        ["ROE", f"{ratios['roe']:.1f}%", "Résultat net / Capitaux propres",
         "Rentabilité pour les associés. Bon si > 10%."],
        ["ROA", f"{ratios['roa']:.1f}%", "Résultat net / Total actif",
         "Efficacité des actifs. Bon si > 5%."],
        ["Ratio d'endettement", f"{ratios['ratio_endettement']:.2f}x",
         "Dettes totales / Capitaux propres",
         "Risque financier. Acceptable si < 1."],
        ["Liquidité générale", f"{min(ratios['liquidite_generale'],999):.2f}x" if ratios['liquidite_generale'] != float('inf') else "∞",
         "Actif circulant / Dettes CT",
         "Capacité à payer les dettes CT. Bon si > 1."],
        ["Fonds de roulement", f"{ratios['fonds_roulement']:,.0f} FCFA",
         "Cap. permanents − Actif immobilisé",
         "Marge de sécurité. Positif = sain."],
        ["BFR", f"{ratios['bfr']:,.0f} FCFA",
         "Stocks + Créances − Dettes exploit.",
         "Besoin de financement du cycle. Gérer si élevé."],
        ["Trésorerie nette", f"{ratios['tresorerie_nette']:,.0f} FCFA",
         "Fonds de roulement − BFR",
         "Position de trésorerie réelle."],
    ]
    tr = Table(ratios_data, colWidths=[3.8*cm, 2.5*cm, 5*cm, 5.2*cm])
    tr.setStyle(TableStyle([
        ("BACKGROUND",(0,0),(-1,0),V), ("TEXTCOLOR",(0,0),(-1,0),W),
        ("FONTNAME",(0,0),(-1,0),"Helvetica-Bold"),
        ("FONTSIZE",(0,0),(-1,-1),8),
        ("ROWBACKGROUNDS",(0,1),(-1,-1),[W, VL]),
        ("GRID",(0,0),(-1,-1),0.25,colors.HexColor("#e5e7eb")),
        ("ALIGN",(1,0),(1,-1),"CENTER"),
        ("FONTNAME",(0,1),(-1,-1),"Helvetica"),
        ("VALIGN",(0,0),(-1,-1),"TOP"),
        ("PADDING",(0,0),(-1,-1),5),
    ]))
    story.append(tr)

    # ── V. Performance produits & villes ──────────────────────────────────
    if par_produit:
        story.append(Paragraph("V. PERFORMANCE PAR PRODUIT", T_SECTION)); story.append(HR())
        prows = [["Produit","CA (FCFA)","Coût","Bénéfice","Marge %","Qté"]]
        for nom, v in sorted(par_produit.items(), key=lambda x:-x[1]["ca"]):
            m = (v["benefice"]/v["ca"]*100) if v["ca"] else 0
            prows.append([nom, f"{v['ca']:,.0f}", f"{v['cout']:,.0f}",
                          f"{v['benefice']:,.0f}", f"{m:.1f}%", str(int(v["qte"]))])
        story.append(_table(prows, [5*cm, 3*cm, 2.8*cm, 3*cm, 2*cm, 1.7*cm], header_bg=R))

    story.append(SP(0.5))
    story.append(HRFlowable(width="100%", thickness=0.5, color=GR))
    story.append(Paragraph("Rapport généré automatiquement par Cosmética Manager", T_FOOTER))

    doc.build(story)
    buf.seek(0)
    return buf


# ── EXPORTS INDIVIDUELS ───────────────────────────────────────────────────────
def export_compte_resultat_pdf(cr, periode):
    buf = io.BytesIO()
    doc = SimpleDocTemplate(buf, pagesize=A4,
                             topMargin=1.5*cm, bottomMargin=1.5*cm,
                             leftMargin=1.8*cm, rightMargin=1.8*cm)
    story = [
        Paragraph("COMPTE DE RÉSULTAT", _style("t", fontSize=18, fontName="Helvetica-Bold", textColor=V, alignment=TA_CENTER, spaceAfter=4)),
        Paragraph(f"Période : {periode}", _style("p", fontSize=9, textColor=GR, alignment=TA_CENTER, spaceAfter=14)),
        HRFlowable(width="100%", thickness=1.5, color=V, spaceAfter=16),
    ]
    rows = [["Ligne","Montant (FCFA)"],
        ["(+) Chiffre d'affaires",          f"{cr['ca']:,.0f}"],
        ["(-) Coût des marchandises vendues",f"-{cr['cmv_total']:,.0f}"],
        ["= Marge brute",                    f"{cr['marge_brute']:,.0f} ({cr['marge_brute_pct']:.1f}%)"],
        ["(-) Publicité",                    f"-{cr['pub']:,.0f}"],
        ["(-) Transport",                    f"-{cr['transport']:,.0f}"],
        ["(-) Personnel",                    f"-{cr['personnel']:,.0f}"],
        ["(-) Charges fixes",                f"-{cr['fixes']:,.0f}"],
        ["(-) Autres charges",               f"-{cr['autres_charges']:,.0f}"],
        ["= EBITDA",                         f"{cr['ebitda']:,.0f} ({cr['ebitda_pct']:.1f}%)"],
        ["(-) DAP",                          f"-{cr['dap']:,.0f}"],
        ["= EBIT",                           f"{cr['ebit']:,.0f}"],
        ["Résultat financier",               f"{cr['resultat_financier']:,.0f}"],
        ["= RCAI",                           f"{cr['rcai']:,.0f}"],
        ["Résultat exceptionnel",            f"{cr['resultat_exceptionnel']:,.0f}"],
        ["= RAI",                            f"{cr['rai']:,.0f}"],
        [f"(-) IS ({cr['taux_is']:.0f}%)",  f"-{cr['is_du']:,.0f}"],
        ["= RÉSULTAT NET",                   f"{cr['resultat_net']:,.0f}"],
    ]
    story.append(_table(rows, [12*cm, 5*cm]))
    doc.build(story); buf.seek(0); return buf


def export_bilan_pdf(bilan, periode):
    buf = io.BytesIO()
    doc = SimpleDocTemplate(buf, pagesize=A4, topMargin=1.5*cm, bottomMargin=1.5*cm,
                             leftMargin=1.8*cm, rightMargin=1.8*cm)
    story = [
        Paragraph("BILAN", _style("t", fontSize=18, fontName="Helvetica-Bold", textColor=V, alignment=TA_CENTER)),
        Paragraph(f"Au {periode}", _style("p", fontSize=9, textColor=GR, alignment=TA_CENTER, spaceAfter=14)),
        HRFlowable(width="100%", thickness=1.5, color=V, spaceAfter=16),
    ]
    rows = [
        ["ACTIF","Montant","PASSIF","Montant"],
        ["Immobilisations nettes", f"{bilan['valeur_nette_immos']:,.0f}", "Capital social", f"{bilan['capital_social']:,.0f}"],
        ["Stock", f"{bilan['valeur_stock']:,.0f}", "Réserves", f"{bilan['reserve_legale']:,.0f}"],
        ["Créances", f"{bilan['creances_clients']:,.0f}", "Résultat net", f"{bilan['resultat_net_exercice']:,.0f}"],
        ["Trésorerie", f"{bilan['tresorerie']:,.0f}", "Dettes financières", f"{bilan['total_dettes_financieres']:,.0f}"],
        ["","","Dettes exploit.", f"{bilan['total_dettes_exploit']:,.0f}"],
        ["TOTAL ACTIF", f"{bilan['total_actif']:,.0f}", "TOTAL PASSIF", f"{bilan['total_passif']:,.0f}"],
    ]
    story.append(_table(rows, [5.5*cm, 3*cm, 5.5*cm, 3*cm]))
    doc.build(story); buf.seek(0); return buf


def export_flux_pdf(flux, periode):
    buf = io.BytesIO()
    doc = SimpleDocTemplate(buf, pagesize=A4, topMargin=1.5*cm, bottomMargin=1.5*cm,
                             leftMargin=1.8*cm, rightMargin=1.8*cm)
    story = [
        Paragraph("TABLEAU DES FLUX DE TRÉSORERIE", _style("t", fontSize=16, fontName="Helvetica-Bold", textColor=V, alignment=TA_CENTER)),
        Paragraph(f"Période : {periode}", _style("p", fontSize=9, textColor=GR, alignment=TA_CENTER, spaceAfter=14)),
        HRFlowable(width="100%", thickness=1.5, color=V, spaceAfter=16),
    ]
    rows = [["Libellé","Montant (FCFA)"],
        ["I. FLUX D'EXPLOITATION",""],
        ["  Encaissements clients", f"+{flux['encaiss_clients']:,.0f}"],
        ["  Achats fournisseurs",   f"-{flux['cout_achats']:,.0f}"],
        ["  Charges d'exploitation",f"-{flux['cout_depenses']:,.0f}"],
        ["  IS payé",               f"-{flux['is_paye']:,.0f}"],
        ["  → Flux d'exploitation", f"{flux['flux_exploitation']:,.0f}"],
        ["II. FLUX D'INVESTISSEMENT",""],
        ["  Acquisitions",          f"-{flux['acquisitions']:,.0f}"],
        ["  Cessions",              f"+{flux['cessions']:,.0f}"],
        ["  → Flux d'investissement",f"{flux['flux_investissement']:,.0f}"],
        ["III. FLUX DE FINANCEMENT",""],
        ["  Emprunts",              f"+{flux['emprunts_nouveaux']:,.0f}"],
        ["  Remboursements",        f"-{flux['remboursements']:,.0f}"],
        ["  → Flux de financement", f"{flux['flux_financement']:,.0f}"],
        ["VARIATION TRÉSORERIE",    f"{flux['variation_tresorerie']:,.0f}"],
        ["Trésorerie initiale",     f"{flux['tresorerie_init']:,.0f}"],
        ["TRÉSORERIE FINALE",       f"{flux['tresorerie_finale']:,.0f}"],
    ]
    story.append(_table(rows, [11*cm, 5*cm]))
    doc.build(story); buf.seek(0); return buf


def export_ratios_pdf(ratios, periode):
    buf = io.BytesIO()
    doc = SimpleDocTemplate(buf, pagesize=A4, topMargin=1.5*cm, bottomMargin=1.5*cm,
                             leftMargin=1.8*cm, rightMargin=1.8*cm)
    story = [
        Paragraph("RATIOS FINANCIERS", _style("t", fontSize=18, fontName="Helvetica-Bold", textColor=V, alignment=TA_CENTER)),
        Paragraph(f"Période : {periode}", _style("p", fontSize=9, textColor=GR, alignment=TA_CENTER, spaceAfter=14)),
        HRFlowable(width="100%", thickness=1.5, color=V, spaceAfter=16),
    ]
    rows = [["Ratio","Valeur","Formule","Interprétation"],
        ["ROE", f"{ratios['roe']:.1f}%", "RN / CP", "> 10% = bon"],
        ["ROA", f"{ratios['roa']:.1f}%", "RN / Actif total", "> 5% = bon"],
        ["Endettement", f"{ratios['ratio_endettement']:.2f}x", "Dettes / CP", "< 1 = acceptable"],
        ["Liquidité gén.", f"{min(ratios['liquidite_generale'],999):.2f}x" if ratios['liquidite_generale']!=float('inf') else "∞",
         "Actif circ. / Dettes CT", "> 1 = sain"],
        ["Fonds de roulement", f"{ratios['fonds_roulement']:,.0f}", "Cap.perm − Actif immo", "> 0 = sain"],
        ["BFR", f"{ratios['bfr']:,.0f}", "Stock+Créances−Dettes", "Surveiller si élevé"],
        ["Trésorerie nette", f"{ratios['tresorerie_nette']:,.0f}", "FR − BFR", "> 0 = sain"],
    ]
    story.append(_table(rows, [3.5*cm, 2.8*cm, 4.5*cm, 5.7*cm]))
    doc.build(story); buf.seek(0); return buf


# ── EXCEL GLOBAL ──────────────────────────────────────────────────────────────
def export_global_excel(cr, bilan, flux, ratios, periode, ventes, achats, depenses, par_produit, par_ville):
    buf = io.BytesIO()
    with pd.ExcelWriter(buf, engine="openpyxl") as writer:
        # Compte de résultat
        cr_df = pd.DataFrame([
            {"Ligne":"Chiffre d'affaires","Valeur":cr["ca"]},
            {"Ligne":"(-) CMV total","Valeur":-cr["cmv_total"]},
            {"Ligne":"= Marge brute","Valeur":cr["marge_brute"]},
            {"Ligne":"Marge brute %","Valeur":f"{cr['marge_brute_pct']:.1f}%"},
            {"Ligne":"(-) Publicité","Valeur":-cr["pub"]},
            {"Ligne":"(-) Transport","Valeur":-cr["transport"]},
            {"Ligne":"(-) Personnel","Valeur":-cr["personnel"]},
            {"Ligne":"(-) Charges fixes","Valeur":-cr["fixes"]},
            {"Ligne":"(-) Autres charges","Valeur":-cr["autres_charges"]},
            {"Ligne":"= EBITDA","Valeur":cr["ebitda"]},
            {"Ligne":"EBITDA %","Valeur":f"{cr['ebitda_pct']:.1f}%"},
            {"Ligne":"(-) DAP","Valeur":-cr["dap"]},
            {"Ligne":"= EBIT","Valeur":cr["ebit"]},
            {"Ligne":"Résultat financier","Valeur":cr["resultat_financier"]},
            {"Ligne":"= RCAI","Valeur":cr["rcai"]},
            {"Ligne":"Résultat exceptionnel","Valeur":cr["resultat_exceptionnel"]},
            {"Ligne":"= RAI","Valeur":cr["rai"]},
            {"Ligne":f"(-) IS ({cr['taux_is']:.0f}%)","Valeur":-cr["is_du"]},
            {"Ligne":"= Résultat net","Valeur":cr["resultat_net"]},
            {"Ligne":"Marge nette %","Valeur":f"{cr['marge_nette_pct']:.1f}%"},
        ])
        cr_df.to_excel(writer, sheet_name="Compte de résultat", index=False)

        # Bilan
        bilan_df = pd.DataFrame([
            {"Poste":"ACTIF","Valeur":""},
            {"Poste":"Immobilisations brutes","Valeur":bilan["valeur_brute_immos"]},
            {"Poste":"(-) Amortissements","Valeur":-bilan["amort_cumulees"]},
            {"Poste":"Immobilisations nettes","Valeur":bilan["valeur_nette_immos"]},
            {"Poste":"Stocks","Valeur":bilan["valeur_stock"]},
            {"Poste":"Créances clients","Valeur":bilan["creances_clients"]},
            {"Poste":"Trésorerie","Valeur":bilan["tresorerie"]},
            {"Poste":"TOTAL ACTIF","Valeur":bilan["total_actif"]},
            {"Poste":"","Valeur":""},
            {"Poste":"PASSIF","Valeur":""},
            {"Poste":"Capital social","Valeur":bilan["capital_social"]},
            {"Poste":"Réserves","Valeur":bilan["reserve_legale"]},
            {"Poste":"Report à nouveau","Valeur":bilan["report_nouveau"]},
            {"Poste":"Résultat net","Valeur":bilan["resultat_net_exercice"]},
            {"Poste":"TOTAL CAPITAUX PROPRES","Valeur":bilan["total_capitaux_propres"]},
            {"Poste":"Dettes financières","Valeur":bilan["total_dettes_financieres"]},
            {"Poste":"Dettes fournisseurs","Valeur":bilan["dettes_fournisseurs"]},
            {"Poste":"IS à payer","Valeur":bilan["dettes_etat"]},
            {"Poste":"TOTAL PASSIF","Valeur":bilan["total_passif"]},
        ])
        bilan_df.to_excel(writer, sheet_name="Bilan", index=False)

        # Flux trésorerie
        flux_df = pd.DataFrame([
            {"Libellé":"I. FLUX D'EXPLOITATION","Montant":""},
            {"Libellé":"Encaissements clients","Montant":flux["encaiss_clients"]},
            {"Libellé":"Achats fournisseurs","Montant":-flux["cout_achats"]},
            {"Libellé":"Charges exploitation","Montant":-flux["cout_depenses"]},
            {"Libellé":"IS payé","Montant":-flux["is_paye"]},
            {"Libellé":"→ FLUX EXPLOITATION","Montant":flux["flux_exploitation"]},
            {"Libellé":"","Montant":""},
            {"Libellé":"II. FLUX D'INVESTISSEMENT","Montant":""},
            {"Libellé":"Acquisitions","Montant":-flux["acquisitions"]},
            {"Libellé":"→ FLUX INVESTISSEMENT","Montant":flux["flux_investissement"]},
            {"Libellé":"","Montant":""},
            {"Libellé":"III. FLUX DE FINANCEMENT","Montant":""},
            {"Libellé":"Remboursements","Montant":-flux["remboursements"]},
            {"Libellé":"→ FLUX FINANCEMENT","Montant":flux["flux_financement"]},
            {"Libellé":"","Montant":""},
            {"Libellé":"VARIATION TRÉSORERIE","Montant":flux["variation_tresorerie"]},
            {"Libellé":"Trésorerie initiale","Montant":flux["tresorerie_init"]},
            {"Libellé":"TRÉSORERIE FINALE","Montant":flux["tresorerie_finale"]},
        ])
        flux_df.to_excel(writer, sheet_name="Flux trésorerie", index=False)

        # Ratios
        ratios_df = pd.DataFrame([
            {"Ratio":"ROE","Valeur":f"{ratios['roe']:.1f}%","Formule":"RN / CP","Norme":"> 10%"},
            {"Ratio":"ROA","Valeur":f"{ratios['roa']:.1f}%","Formule":"RN / Actif total","Norme":"> 5%"},
            {"Ratio":"Endettement","Valeur":f"{ratios['ratio_endettement']:.2f}x","Formule":"Dettes / CP","Norme":"< 1"},
            {"Ratio":"Liquidité générale","Valeur":f"{ratios['liquidite_generale']:.2f}x" if ratios['liquidite_generale']!=float('inf') else "∞","Formule":"AC / Dettes CT","Norme":"> 1"},
            {"Ratio":"Fonds de roulement","Valeur":f"{ratios['fonds_roulement']:,.0f}","Formule":"Cap.perm − AI","Norme":"> 0"},
            {"Ratio":"BFR","Valeur":f"{ratios['bfr']:,.0f}","Formule":"Stock+Créances−DE","Norme":"Surveiller"},
            {"Ratio":"Trésorerie nette","Valeur":f"{ratios['tresorerie_nette']:,.0f}","Formule":"FR − BFR","Norme":"> 0"},
        ])
        ratios_df.to_excel(writer, sheet_name="Ratios financiers", index=False)

        # Détail ventes
        if ventes:
            df_v = pd.DataFrame(ventes)
            cols = ["date","produit_nom","quantite","prix_unitaire","remise","ville","canal","mode_paiement"]
            df_v[[c for c in cols if c in df_v.columns]].to_excel(writer, sheet_name="Ventes", index=False)

        # Par produit
        if par_produit:
            rows = []
            for nom, v in par_produit.items():
                m = (v["benefice"]/v["ca"]*100) if v["ca"] else 0
                rows.append({"Produit":nom,"CA":v["ca"],"Coût":v["cout"],"Bénéfice":v["benefice"],"Marge%":round(m,1),"Qté":v["qte"]})
            pd.DataFrame(rows).to_excel(writer, sheet_name="Par Produit", index=False)

        # Par ville
        if par_ville:
            rows = [{"Ville":k,"CA":v["ca"],"Qté":v["qte"]} for k,v in par_ville.items()]
            pd.DataFrame(rows).to_excel(writer, sheet_name="Par Ville", index=False)

    buf.seek(0); return buf

import streamlit as st
from datetime import date
import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))
from utils.database import compute_bilan, get_immobilisations, get_dettes, add_immobilisation, add_dette, delete_immobilisation, delete_dette, get_param, set_param
from utils.styles import page_header, section_title, info_box, fmt
from utils.exports import export_bilan_pdf

INFOS_ACTIF = {
    "immo": ("Actif immobilisé",
             "Ce sont les biens durables que l'entreprise possède et qui servent à son activité sur plusieurs années : matériels, équipements, véhicules. On les amortit progressivement.",
             "Valeur nette = Valeur d'achat − Amortissements cumulés"),
    "stock": ("Stocks (Actif circulant)",
              "La valeur au coût de tous les produits que vous avez en réserve et qui n'ont pas encore été vendus. C'est de l'argent immobilisé.",
              "Valeur stock = Σ (Stock actuel × Coût unitaire)"),
    "creances": ("Créances clients",
                 "L'argent que vos clients vous doivent mais n'ont pas encore payé. Dans votre cas (paiement à la livraison), ce montant est généralement faible.",
                 "Créances = Ventes facturées non encore encaissées"),
    "tresorerie": ("Trésorerie",
                   "L'argent disponible immédiatement : en caisse ou en compte (Orange Money, MTN MoMo). C'est votre liquidité immédiate.",
                   "Trésorerie = Solde initial + Encaissements − Décaissements"),
}
INFOS_PASSIF = {
    "cp": ("Capitaux propres",
           "Ce que l'entreprise possède en propre : l'argent apporté par les associés (capital social), les bénéfices accumulés et non distribués (réserves), et le résultat de l'exercice en cours.",
           "CP = Capital social + Réserves + Report à nouveau + Résultat net"),
    "df": ("Dettes financières",
           "Les emprunts et crédits contractés auprès de banques ou particuliers pour financer l'activité. Ils doivent être remboursés avec intérêts.",
           "Dettes financières = Σ montants restants des emprunts"),
    "de": ("Dettes d'exploitation",
           "Ce que vous devez à vos fournisseurs (dettes fournisseurs) et à l'État (IS à payer, TVA…). Ce sont des dettes nées du fonctionnement normal.",
           "Dettes exploit. = Dettes fournisseurs + IS dû + Autres dettes"),
}


def show():
    st.markdown(page_header("⚖️ Bilan", "Photographie du patrimoine de l'entreprise à une date donnée"), unsafe_allow_html=True)

    tab_bilan, tab_immos, tab_dettes, tab_capital = st.tabs([
        "  📊 Bilan  ", "  🏗️ Immobilisations  ", "  💳 Dettes financières  ", "  💰 Capitaux & paramètres  "
    ])

    with tab_bilan:
        d2 = st.date_input("Au (date de clôture)", date.today(), key="bilan_date")
        mode_peda = st.toggle("📚 Mode pédagogique", value=True, key="bilan_peda")

        bilan = compute_bilan(str(d2))

        # Équilibre
        if bilan["equilibre"]:
            st.markdown('<div class="alert-success">✅ Bilan équilibré : Total Actif = Total Passif</div>', unsafe_allow_html=True)
        else:
            diff = abs(bilan["total_actif"] - bilan["total_passif"])
            st.markdown(f'<div class="alert-warning">⚠️ Écart de {fmt(diff)} — vérifiez vos saisies.</div>', unsafe_allow_html=True)

        col_a, col_p = st.columns(2)

        def info(key, dico):
            if mode_peda and key in dico:
                titre, expl, formule = dico[key]
                st.markdown(f'<div class="info-box blue"><strong>{titre}</strong><br>{expl}<br><em>📐 {formule}</em></div>', unsafe_allow_html=True)

        with col_a:
            st.markdown(section_title("ACTIF"), unsafe_allow_html=True)

            # Actif immobilisé
            st.markdown('<div class="bilan-section">', unsafe_allow_html=True)
            st.markdown('<div class="bilan-header">🏗️ Actif immobilisé</div>', unsafe_allow_html=True)
            info("immo", INFOS_ACTIF)
            st.markdown(f'<div class="bilan-row"><span>Immobilisations brutes</span><span>{fmt(bilan["valeur_brute_immos"])}</span></div>', unsafe_allow_html=True)
            st.markdown(f'<div class="bilan-row"><span>(-) Amortissements cumulés</span><span style="color:#dc2626">−{fmt(bilan["amort_cumulees"])}</span></div>', unsafe_allow_html=True)
            st.markdown(f'<div class="bilan-total"><span>Immobilisations nettes</span><span>{fmt(bilan["valeur_nette_immos"])}</span></div>', unsafe_allow_html=True)
            st.markdown('</div>', unsafe_allow_html=True)

            # Actif circulant
            st.markdown('<div class="bilan-section">', unsafe_allow_html=True)
            st.markdown('<div class="bilan-header">🔄 Actif circulant</div>', unsafe_allow_html=True)
            info("stock", INFOS_ACTIF)
            st.markdown(f'<div class="bilan-row"><span>📦 Stocks (au coût)</span><span>{fmt(bilan["valeur_stock"])}</span></div>', unsafe_allow_html=True)
            info("creances", INFOS_ACTIF)
            st.markdown(f'<div class="bilan-row"><span>📄 Créances clients</span><span>{fmt(bilan["creances_clients"])}</span></div>', unsafe_allow_html=True)
            info("tresorerie", INFOS_ACTIF)
            st.markdown(f'<div class="bilan-row"><span>💵 Trésorerie</span><span>{fmt(bilan["tresorerie"])}</span></div>', unsafe_allow_html=True)
            st.markdown(f'<div class="bilan-total"><span>Total actif circulant</span><span>{fmt(bilan["total_actif_circulant"])}</span></div>', unsafe_allow_html=True)
            st.markdown('</div>', unsafe_allow_html=True)

            st.markdown(f'<div style="background:linear-gradient(90deg,#6d28d9,#be185d);color:white;border-radius:10px;padding:.8rem 1.2rem;display:flex;justify-content:space-between;font-weight:800;font-size:.97rem;margin-top:.5rem"><span>TOTAL ACTIF</span><span>{fmt(bilan["total_actif"])}</span></div>', unsafe_allow_html=True)

        with col_p:
            st.markdown(section_title("PASSIF"), unsafe_allow_html=True)

            # Capitaux propres
            st.markdown('<div class="bilan-section">', unsafe_allow_html=True)
            st.markdown('<div class="bilan-header">🏦 Capitaux propres</div>', unsafe_allow_html=True)
            info("cp", INFOS_PASSIF)
            st.markdown(f'<div class="bilan-row"><span>Capital social</span><span>{fmt(bilan["capital_social"])}</span></div>', unsafe_allow_html=True)
            st.markdown(f'<div class="bilan-row"><span>Réserve légale</span><span>{fmt(bilan["reserve_legale"])}</span></div>', unsafe_allow_html=True)
            st.markdown(f'<div class="bilan-row"><span>Report à nouveau</span><span>{fmt(bilan["report_nouveau"])}</span></div>', unsafe_allow_html=True)
            st.markdown(f'<div class="bilan-row"><span>Apports divers</span><span>{fmt(bilan["apports_divers"])}</span></div>', unsafe_allow_html=True)
            st.markdown(f'<div class="bilan-row"><span>Résultat net de l\'exercice</span><span style="color:#059669">{fmt(bilan["resultat_net_exercice"])}</span></div>', unsafe_allow_html=True)
            st.markdown(f'<div class="bilan-total"><span>Total capitaux propres</span><span>{fmt(bilan["total_capitaux_propres"])}</span></div>', unsafe_allow_html=True)
            st.markdown('</div>', unsafe_allow_html=True)

            # Dettes financières
            st.markdown('<div class="bilan-section">', unsafe_allow_html=True)
            st.markdown('<div class="bilan-header">💳 Dettes financières</div>', unsafe_allow_html=True)
            info("df", INFOS_PASSIF)
            st.markdown(f'<div class="bilan-row"><span>Emprunts & crédits</span><span>{fmt(bilan["total_dettes_financieres"])}</span></div>', unsafe_allow_html=True)
            st.markdown(f'<div class="bilan-total"><span>Total dettes financières</span><span>{fmt(bilan["total_dettes_financieres"])}</span></div>', unsafe_allow_html=True)
            st.markdown('</div>', unsafe_allow_html=True)

            # Dettes exploitation
            st.markdown('<div class="bilan-section">', unsafe_allow_html=True)
            st.markdown('<div class="bilan-header">📋 Dettes d\'exploitation</div>', unsafe_allow_html=True)
            info("de", INFOS_PASSIF)
            st.markdown(f'<div class="bilan-row"><span>Dettes fournisseurs</span><span>{fmt(bilan["dettes_fournisseurs"])}</span></div>', unsafe_allow_html=True)
            st.markdown(f'<div class="bilan-row"><span>IS à payer</span><span>{fmt(bilan["dettes_etat"])}</span></div>', unsafe_allow_html=True)
            st.markdown(f'<div class="bilan-total"><span>Total dettes exploit.</span><span>{fmt(bilan["total_dettes_exploit"])}</span></div>', unsafe_allow_html=True)
            st.markdown('</div>', unsafe_allow_html=True)

            st.markdown(f'<div style="background:linear-gradient(90deg,#be185d,#6d28d9);color:white;border-radius:10px;padding:.8rem 1.2rem;display:flex;justify-content:space-between;font-weight:800;font-size:.97rem;margin-top:.5rem"><span>TOTAL PASSIF</span><span>{fmt(bilan["total_passif"])}</span></div>', unsafe_allow_html=True)

        # Export
        st.markdown(section_title("Exporter"), unsafe_allow_html=True)
        pdf_buf = export_bilan_pdf(bilan, str(d2))
        st.download_button("⬇️ Télécharger le bilan (PDF)", data=pdf_buf,
                            file_name=f"bilan_{d2}.pdf", mime="application/pdf",
                            use_container_width=True)

    # ── IMMOBILISATIONS ───────────────────────────────────────────────────────
    with tab_immos:
        st.markdown(section_title("Ajouter une immobilisation"), unsafe_allow_html=True)
        st.markdown(info_box("Une immobilisation est un bien durable (> 1 an) utilisé pour l'activité : équipement, machine, véhicule, téléphone professionnel. On l'amortit progressivement sur sa durée de vie utile.", "blue"), unsafe_allow_html=True)

        with st.form("form_immo", clear_on_submit=True):
            c1,c2,c3 = st.columns(3)
            with c1:
                date_acq = st.date_input("Date d'acquisition", date.today())
                libelle  = st.text_input("Libellé *", placeholder="ex: Mixeur industriel")
                categorie= st.selectbox("Catégorie", ["Matériel","Équipement","Véhicule","Informatique","Autre"])
            with c2:
                valeur   = st.number_input("Valeur d'acquisition (FCFA) *", min_value=0.0, step=1000.0)
                duree    = st.number_input("Durée d'amortissement (ans)", min_value=1, max_value=20, value=5)
            with c3:
                taux     = round(100/duree, 2) if duree else 20.0
                st.metric("Taux d'amortissement", f"{taux:.1f}%/an")
                amort_annuel = valeur * taux / 100
                st.metric("Amortissement annuel", fmt(amort_annuel))
                notes    = st.text_input("Notes")

            from datetime import datetime
            annees_ecoulees = (date.today() - date_acq).days / 365 if date_acq else 0
            amort_cumule    = min(amort_annuel * annees_ecoulees, valeur)
            valeur_nette    = max(valeur - amort_cumule, 0)

            if st.form_submit_button("💾 Ajouter l'immobilisation", use_container_width=True):
                if not libelle or valeur <= 0:
                    st.markdown('<div class="alert-danger">❌ Remplissez le libellé et la valeur.</div>', unsafe_allow_html=True)
                else:
                    add_immobilisation({"date_acquisition":str(date_acq),"libelle":libelle,
                                         "categorie":categorie,"valeur_acquisition":valeur,
                                         "duree_amortissement":duree,"taux_amortissement":taux,
                                         "valeur_nette":valeur_nette,"notes":notes})
                    st.markdown('<div class="alert-success">✅ Immobilisation enregistrée.</div>', unsafe_allow_html=True)
                    st.rerun()

        immos = get_immobilisations()
        if immos:
            st.markdown(section_title("Liste des immobilisations"), unsafe_allow_html=True)
            import pandas as pd
            df = pd.DataFrame(immos)[["date_acquisition","libelle","categorie","valeur_acquisition","taux_amortissement","valeur_nette"]]
            df.columns = ["Date","Libellé","Catégorie","Valeur achat","Taux %","Valeur nette"]
            st.dataframe(df, use_container_width=True, hide_index=True)
            ids = {f"#{i['id']} — {i['libelle']}": i["id"] for i in immos}
            sel = st.selectbox("Supprimer", list(ids.keys()), key="del_immo_sel")
            if st.button("🗑️ Supprimer", key="del_immo"):
                delete_immobilisation(ids[sel]); st.rerun()

    # ── DETTES ────────────────────────────────────────────────────────────────
    with tab_dettes:
        st.markdown(section_title("Ajouter un emprunt / crédit"), unsafe_allow_html=True)
        st.markdown(info_box("Les dettes financières regroupent les emprunts bancaires, crédits fournisseurs et apports remboursables. Elles figurent au passif et réduisent votre autonomie financière.", "amber"), unsafe_allow_html=True)

        with st.form("form_dette", clear_on_submit=True):
            c1,c2,c3 = st.columns(3)
            with c1:
                date_debut = st.date_input("Date de début", date.today())
                libelle_d  = st.text_input("Libellé *", placeholder="ex: Crédit fournisseur MTN")
                creancier  = st.text_input("Créancier", placeholder="ex: BICEC, particulier…")
            with c2:
                montant_init = st.number_input("Montant initial (FCFA) *", min_value=0.0, step=1000.0)
                montant_rest = st.number_input("Montant restant dû (FCFA) *", min_value=0.0, step=1000.0)
            with c3:
                taux_int = st.number_input("Taux d'intérêt annuel (%)", min_value=0.0, max_value=100.0, value=0.0, step=0.5)
                duree_m  = st.number_input("Durée (mois)", min_value=1, max_value=360, value=12)

            if taux_int > 0 and montant_rest > 0:
                interet_annuel = montant_rest * taux_int / 100
                st.metric("Intérêts annuels estimés", fmt(interet_annuel))

            if st.form_submit_button("💾 Enregistrer l'emprunt", use_container_width=True):
                if not libelle_d or montant_init <= 0:
                    st.markdown('<div class="alert-danger">❌ Remplissez le libellé et le montant.</div>', unsafe_allow_html=True)
                else:
                    add_dette({"date_debut":str(date_debut),"libelle":libelle_d,
                                "montant_initial":montant_init,"montant_restant":montant_rest,
                                "taux_interet":taux_int,"duree_mois":duree_m,"creancier":creancier})
                    st.markdown('<div class="alert-success">✅ Emprunt enregistré.</div>', unsafe_allow_html=True)
                    st.rerun()

        dettes = get_dettes()
        if dettes:
            st.markdown(section_title("Dettes en cours"), unsafe_allow_html=True)
            import pandas as pd
            df = pd.DataFrame(dettes)[["date_debut","libelle","creancier","montant_initial","montant_restant","taux_interet","duree_mois"]]
            df.columns = ["Date","Libellé","Créancier","Montant init.","Restant dû","Taux %","Durée (mois)"]
            st.dataframe(df, use_container_width=True, hide_index=True)
            ids = {f"#{d['id']} — {d['libelle']} ({fmt(d['montant_restant'])})": d["id"] for d in dettes}
            sel = st.selectbox("Solder / supprimer", list(ids.keys()), key="del_dette_sel")
            if st.button("🗑️ Solder cette dette", key="del_dette"):
                delete_dette(ids[sel]); st.rerun()

    # ── CAPITAUX & PARAMÈTRES ─────────────────────────────────────────────────
    with tab_capital:
        st.markdown(section_title("Paramètres de l'entreprise"), unsafe_allow_html=True)
        st.markdown(info_box("Ces paramètres alimentent directement le bilan et le calcul de l'IS. Renseignez-les une seule fois au démarrage.", "purple"), unsafe_allow_html=True)

        with st.form("form_params"):
            c1,c2 = st.columns(2)
            with c1:
                capital     = st.number_input("Capital social (FCFA)", min_value=0.0, value=get_param("capital_social"), step=10000.0)
                reserve     = st.number_input("Réserve légale (FCFA)", min_value=0.0, value=get_param("reserve_legale"), step=1000.0)
                report      = st.number_input("Report à nouveau (FCFA)", min_value=0.0, value=get_param("report_a_nouveau"), step=1000.0)
            with c2:
                treso_init  = st.number_input("Trésorerie initiale (FCFA)", min_value=0.0, value=get_param("tresorerie_initiale"), step=1000.0)
                taux_is_p   = st.number_input("Taux IS (%)", min_value=0.0, max_value=100.0, value=get_param("taux_is", 30), step=0.5)

            if st.form_submit_button("💾 Enregistrer les paramètres", use_container_width=True):
                set_param("capital_social", capital)
                set_param("reserve_legale", reserve)
                set_param("report_a_nouveau", report)
                set_param("tresorerie_initiale", treso_init)
                set_param("taux_is", taux_is_p)
                st.markdown('<div class="alert-success">✅ Paramètres mis à jour.</div>', unsafe_allow_html=True)
                st.rerun()

        # Apports en capital
        st.markdown(section_title("Enregistrer un apport en capital"), unsafe_allow_html=True)
        from utils.database import add_capital, get_capitaux
        with st.form("form_capital", clear_on_submit=True):
            c1,c2,c3 = st.columns(3)
            with c1: date_cap = st.date_input("Date", date.today())
            with c2: montant_cap = st.number_input("Montant (FCFA)", min_value=0.0, step=1000.0)
            with c3: type_cap = st.selectbox("Type", ["Apport","Retrait","Autre"])
            desc_cap = st.text_input("Description")
            if st.form_submit_button("💾 Enregistrer", use_container_width=True):
                add_capital({"date":str(date_cap),"type":type_cap,"montant":montant_cap,"description":desc_cap})
                st.markdown('<div class="alert-success">✅ Mouvement de capital enregistré.</div>', unsafe_allow_html=True)
                st.rerun()

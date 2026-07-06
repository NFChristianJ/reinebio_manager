import sqlite3, os
from datetime import date

# Sur Streamlit Cloud, on écrit dans /tmp qui persiste pendant la session
# Pour une vraie persistance, on utilise st.session_state comme cache
DB_PATH = os.path.join("/tmp", "cosmetica.db")

def get_conn():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    conn = get_conn()
    c = conn.cursor()

    c.execute("""CREATE TABLE IF NOT EXISTS produits (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        nom TEXT NOT NULL, categorie TEXT,
        type TEXT CHECK(type IN ('achat_revente','production')) NOT NULL,
        prix_vente REAL NOT NULL, cout_unitaire REAL NOT NULL,
        unite TEXT DEFAULT 'unité', stock_actuel REAL DEFAULT 0,
        stock_min REAL DEFAULT 5, actif INTEGER DEFAULT 1,
        created_at TEXT DEFAULT (datetime('now')))""")

    c.execute("""CREATE TABLE IF NOT EXISTS ventes (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        date TEXT NOT NULL, produit_id INTEGER NOT NULL,
        quantite REAL NOT NULL, prix_unitaire REAL NOT NULL,
        remise REAL DEFAULT 0, ville TEXT NOT NULL,
        canal TEXT DEFAULT 'direct', mode_paiement TEXT DEFAULT 'cash',
        livraison REAL DEFAULT 0, commission REAL DEFAULT 0,
        notes TEXT, created_at TEXT DEFAULT (datetime('now')),
        FOREIGN KEY(produit_id) REFERENCES produits(id))""")

    c.execute("""CREATE TABLE IF NOT EXISTS achats (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        date TEXT NOT NULL,
        type_achat TEXT CHECK(type_achat IN ('produit_fini','matiere_premiere')) NOT NULL,
        produit_id INTEGER, matiere_nom TEXT,
        quantite REAL NOT NULL, prix_unitaire REAL NOT NULL,
        fournisseur TEXT, frais_transport REAL DEFAULT 0,
        mode_paiement TEXT DEFAULT 'cash', notes TEXT,
        created_at TEXT DEFAULT (datetime('now')))""")

    c.execute("""CREATE TABLE IF NOT EXISTS depenses (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        date TEXT NOT NULL, categorie TEXT NOT NULL,
        sous_categorie TEXT, montant REAL NOT NULL,
        description TEXT, ville TEXT,
        created_at TEXT DEFAULT (datetime('now')))""")

    c.execute("""CREATE TABLE IF NOT EXISTS immobilisations (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        date_acquisition TEXT NOT NULL, libelle TEXT NOT NULL,
        categorie TEXT NOT NULL, valeur_acquisition REAL NOT NULL,
        duree_amortissement INTEGER NOT NULL, taux_amortissement REAL NOT NULL,
        valeur_nette REAL NOT NULL, notes TEXT,
        created_at TEXT DEFAULT (datetime('now')))""")

    c.execute("""CREATE TABLE IF NOT EXISTS capitaux_propres (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        date TEXT NOT NULL, type TEXT NOT NULL,
        montant REAL NOT NULL, description TEXT,
        created_at TEXT DEFAULT (datetime('now')))""")

    c.execute("""CREATE TABLE IF NOT EXISTS dettes_financieres (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        date_debut TEXT NOT NULL, libelle TEXT NOT NULL,
        montant_initial REAL NOT NULL, montant_restant REAL NOT NULL,
        taux_interet REAL DEFAULT 0, duree_mois INTEGER DEFAULT 12,
        creancier TEXT, actif INTEGER DEFAULT 1,
        created_at TEXT DEFAULT (datetime('now')))""")

    c.execute("""CREATE TABLE IF NOT EXISTS encaissements (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        date TEXT NOT NULL, montant REAL NOT NULL,
        mode TEXT NOT NULL, description TEXT,
        created_at TEXT DEFAULT (datetime('now')))""")

    c.execute("""CREATE TABLE IF NOT EXISTS decaissements (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        date TEXT NOT NULL, montant REAL NOT NULL,
        categorie TEXT NOT NULL, description TEXT,
        created_at TEXT DEFAULT (datetime('now')))""")

    c.execute("""CREATE TABLE IF NOT EXISTS parametres (
        cle TEXT PRIMARY KEY, valeur TEXT)""")

    defaults = [
        ("taux_is", "30"), ("capital_social", "0"),
        ("reserve_legale", "0"), ("report_a_nouveau", "0"),
        ("tresorerie_initiale", "0"),
        ("exercice_annee", str(date.today().year)),
    ]
    for cle, val in defaults:
        c.execute("INSERT OR IGNORE INTO parametres VALUES (?,?)", (cle, val))

    c.execute("SELECT COUNT(*) FROM produits")
    if c.fetchone()[0] == 0:
        demo = [
            ("Crème Éclat Naturel","Crèmes","achat_revente",5000,2500,"pot",50,10),
            ("Sirop Détox Plantes","Sirops","production",7500,3000,"flacon",30,8),
            ("Comprimés Vitalité","Comprimés","achat_revente",3500,1500,"boîte",80,15),
            ("Gélules Minceur Pro","Gélules","production",8000,3500,"boîte",25,5),
            ("Thé Minceur Express","Thés","achat_revente",4000,1800,"sachet",60,12),
            ("Suppositoires Calmants","Suppositoires","achat_revente",6000,2800,"boîte",20,5),
        ]
        c.executemany("""INSERT INTO produits
            (nom,categorie,type,prix_vente,cout_unitaire,unite,stock_actuel,stock_min)
            VALUES (?,?,?,?,?,?,?,?)""", demo)

    conn.commit(); conn.close()

def get_param(cle, default=0):
    conn = get_conn()
    r = conn.execute("SELECT valeur FROM parametres WHERE cle=?", (cle,)).fetchone()
    conn.close()
    return float(r[0]) if r else default

def set_param(cle, valeur):
    conn = get_conn()
    conn.execute("INSERT OR REPLACE INTO parametres VALUES (?,?)", (cle, str(valeur)))
    conn.commit(); conn.close()

def get_produits(actif_only=True):
    conn = get_conn()
    q = "SELECT * FROM produits" + (" WHERE actif=1" if actif_only else "") + " ORDER BY nom"
    rows = conn.execute(q).fetchall(); conn.close()
    return [dict(r) for r in rows]

def add_produit(d):
    conn = get_conn()
    conn.execute("""INSERT INTO produits
        (nom,categorie,type,prix_vente,cout_unitaire,unite,stock_actuel,stock_min)
        VALUES (:nom,:categorie,:type,:prix_vente,:cout_unitaire,:unite,:stock_actuel,:stock_min)""", d)
    conn.commit(); conn.close()

def update_produit(pid, d):
    conn = get_conn()
    conn.execute("""UPDATE produits SET nom=:nom,categorie=:categorie,type=:type,
        prix_vente=:prix_vente,cout_unitaire=:cout_unitaire,unite=:unite,
        stock_actuel=:stock_actuel,stock_min=:stock_min WHERE id=:id""", {**d,"id":pid})
    conn.commit(); conn.close()

def delete_produit(pid):
    conn = get_conn()
    conn.execute("UPDATE produits SET actif=0 WHERE id=?", (pid,))
    conn.commit(); conn.close()

def add_vente(d):
    conn = get_conn()
    conn.execute("""INSERT INTO ventes
        (date,produit_id,quantite,prix_unitaire,remise,ville,canal,mode_paiement,livraison,commission,notes)
        VALUES (:date,:produit_id,:quantite,:prix_unitaire,:remise,:ville,:canal,:mode_paiement,:livraison,:commission,:notes)""", d)
    conn.execute("UPDATE produits SET stock_actuel=stock_actuel-:quantite WHERE id=:produit_id", d)
    conn.commit(); conn.close()

def get_ventes(d1=None, d2=None):
    conn = get_conn()
    q = """SELECT v.*,p.nom as produit_nom,p.cout_unitaire,p.categorie
           FROM ventes v JOIN produits p ON v.produit_id=p.id"""
    params = []
    if d1 and d2: q += " WHERE v.date BETWEEN ? AND ?"; params=[d1,d2]
    rows = conn.execute(q+" ORDER BY v.date DESC", params).fetchall()
    conn.close(); return [dict(r) for r in rows]

def delete_vente(vid):
    conn = get_conn()
    v = conn.execute("SELECT produit_id,quantite FROM ventes WHERE id=?", (vid,)).fetchone()
    if v:
        conn.execute("UPDATE produits SET stock_actuel=stock_actuel+? WHERE id=?", (v["quantite"],v["produit_id"]))
        conn.execute("DELETE FROM ventes WHERE id=?", (vid,))
    conn.commit(); conn.close()

def add_achat(d):
    conn = get_conn()
    conn.execute("""INSERT INTO achats
        (date,type_achat,produit_id,matiere_nom,quantite,prix_unitaire,fournisseur,frais_transport,mode_paiement,notes)
        VALUES (:date,:type_achat,:produit_id,:matiere_nom,:quantite,:prix_unitaire,:fournisseur,:frais_transport,:mode_paiement,:notes)""", d)
    if d.get("type_achat")=="produit_fini" and d.get("produit_id"):
        conn.execute("UPDATE produits SET stock_actuel=stock_actuel+? WHERE id=?", (d["quantite"],d["produit_id"]))
    conn.commit(); conn.close()

def get_achats(d1=None, d2=None):
    conn = get_conn()
    q = "SELECT a.*,p.nom as produit_nom FROM achats a LEFT JOIN produits p ON a.produit_id=p.id"
    params = []
    if d1 and d2: q += " WHERE a.date BETWEEN ? AND ?"; params=[d1,d2]
    rows = conn.execute(q+" ORDER BY a.date DESC", params).fetchall()
    conn.close(); return [dict(r) for r in rows]

def delete_achat(aid):
    conn = get_conn()
    a = conn.execute("SELECT * FROM achats WHERE id=?", (aid,)).fetchone()
    if a and a["type_achat"]=="produit_fini" and a["produit_id"]:
        conn.execute("UPDATE produits SET stock_actuel=stock_actuel-? WHERE id=?", (a["quantite"],a["produit_id"]))
    conn.execute("DELETE FROM achats WHERE id=?", (aid,))
    conn.commit(); conn.close()

def add_depense(d):
    conn = get_conn()
    conn.execute("""INSERT INTO depenses (date,categorie,sous_categorie,montant,description,ville)
        VALUES (:date,:categorie,:sous_categorie,:montant,:description,:ville)""", d)
    conn.commit(); conn.close()

def get_depenses(d1=None, d2=None):
    conn = get_conn()
    q = "SELECT * FROM depenses"
    params = []
    if d1 and d2: q += " WHERE date BETWEEN ? AND ?"; params=[d1,d2]
    rows = conn.execute(q+" ORDER BY date DESC", params).fetchall()
    conn.close(); return [dict(r) for r in rows]

def delete_depense(did):
    conn = get_conn()
    conn.execute("DELETE FROM depenses WHERE id=?", (did,))
    conn.commit(); conn.close()

def add_immobilisation(d):
    conn = get_conn()
    conn.execute("""INSERT INTO immobilisations
        (date_acquisition,libelle,categorie,valeur_acquisition,duree_amortissement,taux_amortissement,valeur_nette,notes)
        VALUES (:date_acquisition,:libelle,:categorie,:valeur_acquisition,:duree_amortissement,:taux_amortissement,:valeur_nette,:notes)""", d)
    conn.commit(); conn.close()

def get_immobilisations():
    conn = get_conn()
    rows = conn.execute("SELECT * FROM immobilisations ORDER BY date_acquisition DESC").fetchall()
    conn.close(); return [dict(r) for r in rows]

def delete_immobilisation(iid):
    conn = get_conn()
    conn.execute("DELETE FROM immobilisations WHERE id=?", (iid,))
    conn.commit(); conn.close()

def add_dette(d):
    conn = get_conn()
    conn.execute("""INSERT INTO dettes_financieres
        (date_debut,libelle,montant_initial,montant_restant,taux_interet,duree_mois,creancier)
        VALUES (:date_debut,:libelle,:montant_initial,:montant_restant,:taux_interet,:duree_mois,:creancier)""", d)
    conn.commit(); conn.close()

def get_dettes():
    conn = get_conn()
    rows = conn.execute("SELECT * FROM dettes_financieres WHERE actif=1 ORDER BY date_debut DESC").fetchall()
    conn.close(); return [dict(r) for r in rows]

def delete_dette(did):
    conn = get_conn()
    conn.execute("UPDATE dettes_financieres SET actif=0 WHERE id=?", (did,))
    conn.commit(); conn.close()

def add_capital(d):
    conn = get_conn()
    conn.execute("INSERT INTO capitaux_propres (date,type,montant,description) VALUES (:date,:type,:montant,:description)", d)
    conn.commit(); conn.close()

def get_capitaux():
    conn = get_conn()
    rows = conn.execute("SELECT * FROM capitaux_propres ORDER BY date DESC").fetchall()
    conn.close(); return [dict(r) for r in rows]

def add_encaissement(d):
    conn = get_conn()
    conn.execute("INSERT INTO encaissements (date,montant,mode,description) VALUES (:date,:montant,:mode,:description)", d)
    conn.commit(); conn.close()

def get_encaissements(d1=None, d2=None):
    conn = get_conn()
    q = "SELECT * FROM encaissements"
    params = []
    if d1 and d2: q += " WHERE date BETWEEN ? AND ?"; params=[d1,d2]
    rows = conn.execute(q+" ORDER BY date DESC", params).fetchall()
    conn.close(); return [dict(r) for r in rows]

def add_decaissement(d):
    conn = get_conn()
    conn.execute("INSERT INTO decaissements (date,montant,categorie,description) VALUES (:date,:montant,:categorie,:description)", d)
    conn.commit(); conn.close()

def get_decaissements(d1=None, d2=None):
    conn = get_conn()
    q = "SELECT * FROM decaissements"
    params = []
    if d1 and d2: q += " WHERE date BETWEEN ? AND ?"; params=[d1,d2]
    rows = conn.execute(q+" ORDER BY date DESC", params).fetchall()
    conn.close(); return [dict(r) for r in rows]

def get_stock_alerte():
    conn = get_conn()
    rows = conn.execute("SELECT * FROM produits WHERE actif=1 AND stock_actuel<=stock_min ORDER BY stock_actuel").fetchall()
    conn.close(); return [dict(r) for r in rows]

def get_ventes_par_produit(d1=None, d2=None):
    from collections import defaultdict
    ventes = get_ventes(d1, d2)
    data = defaultdict(lambda: {"ca":0,"cout":0,"qte":0,"benefice":0})
    for v in ventes:
        nom = v["produit_nom"]
        ca = (v["prix_unitaire"]-v["remise"])*v["quantite"]
        cout = v["cout_unitaire"]*v["quantite"]
        data[nom]["ca"] += ca; data[nom]["cout"] += cout
        data[nom]["qte"] += v["quantite"]; data[nom]["benefice"] += ca-cout
    return dict(data)

def get_ventes_par_ville(d1=None, d2=None):
    from collections import defaultdict
    ventes = get_ventes(d1, d2)
    data = defaultdict(lambda: {"ca":0,"qte":0})
    for v in ventes:
        ca = (v["prix_unitaire"]-v["remise"])*v["quantite"]
        data[v["ville"]]["ca"] += ca; data[v["ville"]]["qte"] += v["quantite"]
    return dict(data)

def compute_compte_resultat(d1, d2):
    ventes   = get_ventes(d1, d2)
    achats   = get_achats(d1, d2)
    depenses = get_depenses(d1, d2)
    immos    = get_immobilisations()
    dettes   = get_dettes()

    ca = sum((v["prix_unitaire"]-v["remise"])*v["quantite"] for v in ventes)
    cmv = sum(v["cout_unitaire"]*v["quantite"] for v in ventes)
    transport_ventes = sum(v["livraison"]+v["commission"] for v in ventes)
    cmv_total = cmv + transport_ventes
    marge_brute = ca - cmv_total

    pub       = sum(d["montant"] for d in depenses if d["categorie"]=="Publicité")
    transport = sum(d["montant"] for d in depenses if d["categorie"]=="Transport")
    personnel = sum(d["montant"] for d in depenses if d["categorie"]=="Personnel")
    fixes     = sum(d["montant"] for d in depenses if d["categorie"]=="Charges fixes")
    autres_ch = sum(d["montant"] for d in depenses if d["categorie"] not in
                    ["Publicité","Transport","Personnel","Charges fixes"])
    total_charges = pub + transport + personnel + fixes + autres_ch
    ebitda = marge_brute - total_charges

    from datetime import datetime
    d1_dt = datetime.strptime(d1, "%Y-%m-%d")
    d2_dt = datetime.strptime(d2, "%Y-%m-%d")
    nb_jours = max((d2_dt - d1_dt).days, 1)
    dap = sum(i["valeur_acquisition"]*i["taux_amortissement"]/100*nb_jours/365 for i in immos)
    ebit = ebitda - dap

    charges_interets = sum(d["montant_restant"]*d["taux_interet"]/100*nb_jours/365 for d in dettes)
    resultat_financier = -charges_interets
    rcai = ebit + resultat_financier
    resultat_exceptionnel = 0.0
    rai = rcai + resultat_exceptionnel
    taux_is = get_param("taux_is", 30) / 100
    is_du = max(rai * taux_is, 0)
    resultat_net = rai - is_du

    return {
        "ca": ca, "cmv": cmv, "transport_ventes": transport_ventes,
        "cmv_total": cmv_total, "marge_brute": marge_brute,
        "marge_brute_pct": (marge_brute/ca*100) if ca else 0,
        "pub": pub, "transport": transport, "personnel": personnel,
        "fixes": fixes, "autres_charges": autres_ch,
        "total_charges_exploitation": total_charges,
        "ebitda": ebitda, "ebitda_pct": (ebitda/ca*100) if ca else 0,
        "dap": dap, "ebit": ebit,
        "marge_oper_pct": (ebit/ca*100) if ca else 0,
        "charges_interets": charges_interets,
        "resultat_financier": resultat_financier,
        "rcai": rcai, "resultat_exceptionnel": resultat_exceptionnel,
        "rai": rai, "is_du": is_du, "taux_is": taux_is*100,
        "resultat_net": resultat_net,
        "marge_nette_pct": (resultat_net/ca*100) if ca else 0,
        "nb_ventes": len(ventes),
        "pub_par_vente": pub/len(ventes) if ventes else 0,
        "nb_jours": nb_jours,
    }

def compute_bilan(d2=None):
    produits = get_produits(actif_only=True)
    immos    = get_immobilisations()
    dettes   = get_dettes()

    valeur_brute_immos = sum(i["valeur_acquisition"] for i in immos)
    amort_cumulees     = sum(i["valeur_acquisition"]-i["valeur_nette"] for i in immos)
    valeur_nette_immos = sum(i["valeur_nette"] for i in immos)
    valeur_stock       = sum(p["stock_actuel"]*p["cout_unitaire"] for p in produits)
    creances_clients   = 0.0

    tresorerie_init = get_param("tresorerie_initiale", 0)
    total_enc = sum(e["montant"] for e in get_encaissements())
    total_dec = sum(d["montant"] for d in get_decaissements())
    tresorerie = tresorerie_init + total_enc - total_dec

    total_actif_immobilise = valeur_nette_immos
    total_actif_circulant  = valeur_stock + creances_clients + max(tresorerie, 0)
    total_actif            = total_actif_immobilise + total_actif_circulant

    capital_social = get_param("capital_social", 0)
    reserve_legale = get_param("reserve_legale", 0)
    report_nouveau = get_param("report_a_nouveau", 0)
    apports_divers = sum(k["montant"] for k in get_capitaux() if k["type"]=="Apport")

    annee = d2[:4] if d2 else str(date.today().year)
    cr = compute_compte_resultat(f"{annee}-01-01", d2 or str(date.today()))
    resultat_net_exercice  = cr["resultat_net"]
    total_capitaux_propres = capital_social + reserve_legale + report_nouveau + apports_divers + resultat_net_exercice
    total_dettes_financieres = sum(d["montant_restant"] for d in dettes)
    dettes_etat   = cr["is_du"]
    total_dettes_exploit = dettes_etat
    total_passif = total_capitaux_propres + total_dettes_financieres + total_dettes_exploit

    return {
        "valeur_brute_immos": valeur_brute_immos, "amort_cumulees": amort_cumulees,
        "valeur_nette_immos": valeur_nette_immos, "valeur_stock": valeur_stock,
        "creances_clients": creances_clients, "tresorerie": tresorerie,
        "total_actif_immobilise": total_actif_immobilise,
        "total_actif_circulant": total_actif_circulant, "total_actif": total_actif,
        "capital_social": capital_social, "reserve_legale": reserve_legale,
        "report_nouveau": report_nouveau, "apports_divers": apports_divers,
        "resultat_net_exercice": resultat_net_exercice,
        "total_capitaux_propres": total_capitaux_propres,
        "total_dettes_financieres": total_dettes_financieres,
        "dettes_fournisseurs": 0.0, "dettes_etat": dettes_etat,
        "total_dettes_exploit": total_dettes_exploit, "total_passif": total_passif,
        "equilibre": abs(total_actif-total_passif) < 1,
    }

def compute_flux_tresorerie(d1, d2):
    ventes   = get_ventes(d1, d2)
    achats   = get_achats(d1, d2)
    depenses = get_depenses(d1, d2)
    encaiss  = get_encaissements(d1, d2)
    decaiss  = get_decaissements(d1, d2)

    ca_periode = sum((v["prix_unitaire"]-v["remise"])*v["quantite"] for v in ventes)
    encaiss_clients = sum(e["montant"] for e in encaiss) if encaiss else ca_periode
    cout_achats  = sum(a["quantite"]*a["prix_unitaire"]+a["frais_transport"] for a in achats)
    cout_depenses = sum(d["montant"] for d in depenses)
    cout_livraison = sum(v["livraison"]+v["commission"] for v in ventes)
    is_paye = sum(d["montant"] for d in decaiss if "impôt" in (d["description"] or "").lower())
    flux_exploitation = encaiss_clients - cout_achats - cout_depenses - cout_livraison - is_paye

    from datetime import datetime
    immos = get_immobilisations()
    immos_periode = [i for i in immos if d1 <= i["date_acquisition"] <= d2]
    acquisitions = sum(i["valeur_acquisition"] for i in immos_periode)
    flux_investissement = -acquisitions

    remboursements = sum(d["montant"] for d in decaiss if "remboursement" in (d["description"] or "").lower())
    flux_financement = -remboursements

    tresorerie_init = get_param("tresorerie_initiale", 0)
    variation = flux_exploitation + flux_investissement + flux_financement

    return {
        "encaiss_clients": encaiss_clients, "cout_achats": cout_achats,
        "cout_depenses": cout_depenses, "cout_livraison": cout_livraison,
        "is_paye": is_paye, "flux_exploitation": flux_exploitation,
        "acquisitions": acquisitions, "cessions": 0.0,
        "flux_investissement": flux_investissement,
        "emprunts_nouveaux": 0.0, "remboursements": remboursements,
        "dividendes": 0.0, "flux_financement": flux_financement,
        "variation_tresorerie": variation,
        "tresorerie_init": tresorerie_init,
        "tresorerie_finale": tresorerie_init + variation,
    }

def compute_ratios(bilan, cr):
    ta = bilan["total_actif"]; cp = bilan["total_capitaux_propres"]
    df = bilan["total_dettes_financieres"]; de = bilan["total_dettes_exploit"]
    rn = cr["resultat_net"]; ac = bilan["total_actif_circulant"]
    total_dettes = df + de
    roe = (rn/cp*100) if cp and cp>0 else 0
    roa = (rn/ta*100) if ta and ta>0 else 0
    ratio_endettement = (total_dettes/cp) if cp and cp>0 else 0
    liquidite = (ac/de) if de>0 else float("inf")
    capitaux_permanents = cp + df
    fonds_roulement = capitaux_permanents - bilan["total_actif_immobilise"]
    bfr = bilan["valeur_stock"] + bilan["creances_clients"] - de
    tresorerie_nette = fonds_roulement - bfr
    return {
        "roe": roe, "roa": roa, "ratio_endettement": ratio_endettement,
        "liquidite_generale": liquidite, "fonds_roulement": fonds_roulement,
        "bfr": bfr, "tresorerie_nette": tresorerie_nette,
        "total_dettes": total_dettes, "cp": cp, "ta": ta,
    }

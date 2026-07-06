CSS = """
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800&display=swap');
html, body, [class*="css"] { font-family: 'Inter', sans-serif !important; }

/* Sidebar */
section[data-testid="stSidebar"] {
    background: linear-gradient(175deg,#1a1040 0%,#2d1b6e 55%,#3d1078 100%) !important;
}
section[data-testid="stSidebar"] * { color: #e9d5ff !important; }
section[data-testid="stSidebar"] hr { border-color: rgba(167,139,250,0.25) !important; }
.stRadio [data-baseweb="radio"] label { font-size:0.88rem !important; padding:4px 0 !important; }

/* Main */
.main .block-container { background:#f5f3ff; padding-top:1.2rem !important; }

/* Page header */
.page-header {
    background: linear-gradient(135deg,#6d28d9 0%,#be185d 100%);
    border-radius:14px; padding:1.3rem 1.8rem; margin-bottom:1.4rem; color:white;
}
.page-header h1 { color:white; font-size:1.4rem; font-weight:800; margin:0; letter-spacing:-0.02em; }
.page-header p  { color:rgba(255,255,255,0.78); font-size:0.82rem; margin:0.2rem 0 0; }

/* KPI cards */
.kpi-card {
    background:white; border-radius:12px; padding:1.1rem 1.3rem;
    border-left:4px solid #7c3aed;
    box-shadow:0 1px 8px rgba(109,40,217,0.09); margin-bottom:0.8rem;
}
.kpi-card.rose   { border-left-color:#db2777; }
.kpi-card.cyan   { border-left-color:#0891b2; }
.kpi-card.green  { border-left-color:#059669; }
.kpi-card.orange { border-left-color:#d97706; }
.kpi-card.red    { border-left-color:#dc2626; }
.kpi-label { font-size:0.72rem; font-weight:700; color:#6b7280; text-transform:uppercase; letter-spacing:.07em; margin-bottom:.25rem; }
.kpi-value { font-size:1.5rem; font-weight:800; color:#1e1b4b; line-height:1.1; }
.kpi-sub   { font-size:0.7rem; color:#9ca3af; margin-top:.2rem; }

/* Section title */
.section-title {
    font-size:.95rem; font-weight:700; color:#4c1d95;
    margin:1.1rem 0 .6rem; padding-bottom:.35rem;
    border-bottom:2px solid #ede9fe;
}

/* Info tooltip box */
.info-box {
    background:#f0fdf4; border-left:3px solid #22c55e;
    border-radius:8px; padding:.65rem .9rem; margin:.4rem 0;
    font-size:.8rem; color:#166534; line-height:1.5;
}
.info-box.blue  { background:#eff6ff; border-color:#3b82f6; color:#1e40af; }
.info-box.purple{ background:#faf5ff; border-color:#a855f7; color:#6b21a8; }
.info-box.amber { background:#fffbeb; border-color:#f59e0b; color:#92400e; }

/* Alert boxes */
.alert-success { background:#f0fdf4; border-left:4px solid #22c55e; border-radius:8px; padding:.75rem 1rem; margin:.4rem 0; color:#166534; font-size:.83rem; }
.alert-danger  { background:#fef2f2; border-left:4px solid #ef4444; border-radius:8px; padding:.75rem 1rem; margin:.4rem 0; color:#991b1b; font-size:.83rem; }
.alert-warning { background:#fffbeb; border-left:4px solid #f59e0b; border-radius:8px; padding:.75rem 1rem; margin:.4rem 0; color:#92400e; font-size:.83rem; }

/* Ligne de compte de résultat */
.cr-row { display:flex; justify-content:space-between; align-items:center; padding:.45rem .7rem; border-radius:7px; margin:.2rem 0; font-size:.87rem; }
.cr-row.header { background:#ede9fe; font-weight:700; color:#4c1d95; }
.cr-row.subtotal { background:#f3f4f6; font-weight:600; color:#1f2937; }
.cr-row.total   { background:linear-gradient(90deg,#6d28d9,#be185d); color:white; font-weight:800; border-radius:9px; }
.cr-row.indent  { padding-left:1.5rem; color:#4b5563; }
.cr-row.positive { color:#059669; font-weight:600; }
.cr-row.negative { color:#dc2626; }
.cr-val { font-weight:700; white-space:nowrap; }

/* Bilan lignes */
.bilan-section { background:white; border-radius:12px; padding:1rem 1.2rem; margin:.6rem 0; box-shadow:0 1px 6px rgba(0,0,0,.06); }
.bilan-header  { font-weight:800; color:#1e1b4b; font-size:.95rem; margin-bottom:.5rem; border-bottom:2px solid #ede9fe; padding-bottom:.3rem; }
.bilan-row     { display:flex; justify-content:space-between; padding:.3rem 0; font-size:.85rem; border-bottom:1px solid #f3f4f6; }
.bilan-total   { display:flex; justify-content:space-between; padding:.5rem 0 0; font-weight:800; font-size:.92rem; color:#4c1d95; border-top:2px solid #ede9fe; margin-top:.3rem; }

/* Ratio card */
.ratio-card {
    background:white; border-radius:12px; padding:1rem 1.2rem;
    box-shadow:0 1px 6px rgba(0,0,0,.07); margin-bottom:.8rem;
}
.ratio-name  { font-size:.78rem; font-weight:700; color:#6d28d9; text-transform:uppercase; letter-spacing:.05em; }
.ratio-value { font-size:1.6rem; font-weight:800; color:#1e1b4b; margin:.1rem 0; }
.ratio-formula { font-size:.72rem; color:#6b7280; font-style:italic; margin:.1rem 0; }
.ratio-desc  { font-size:.75rem; color:#374151; line-height:1.45; margin-top:.4rem; border-top:1px solid #f3f4f6; padding-top:.4rem; }
.ratio-signal.good   { color:#059669; font-weight:700; }
.ratio-signal.warn   { color:#d97706; font-weight:700; }
.ratio-signal.bad    { color:#dc2626; font-weight:700; }

/* Flux row */
.flux-row { display:flex; justify-content:space-between; padding:.38rem .6rem; border-radius:6px; font-size:.85rem; }
.flux-row.in  { color:#059669; }
.flux-row.out { color:#dc2626; }
.flux-row.total { font-weight:800; font-size:.93rem; }
.flux-section-header { font-weight:700; color:#1e1b4b; font-size:.88rem; background:#f3f4f6; padding:.4rem .6rem; border-radius:7px; margin:.5rem 0 .2rem; }

/* Logo */
.logo-area { text-align:center; padding:1.2rem .8rem .8rem; }
.logo-icon  { font-size:2.2rem; display:block; margin-bottom:.2rem; }
.logo-title { font-size:1rem; font-weight:800; color:#ede9fe; letter-spacing:.01em; }
.logo-sub   { font-size:.7rem; color:#a78bfa; margin-top:.1rem; }

/* Tabs */
.stTabs [data-baseweb="tab-list"] { background:white; border-radius:10px; padding:4px; gap:2px; border:1px solid #e5e7eb; }
.stTabs [data-baseweb="tab"]       { border-radius:8px !important; color:#6b7280 !important; font-weight:500 !important; }
.stTabs [aria-selected="true"]     { background:linear-gradient(135deg,#7c3aed,#db2777) !important; color:white !important; }

/* Buttons */
.stButton > button {
    border-radius:8px !important; font-weight:700 !important;
    border:none !important;
    background:linear-gradient(135deg,#7c3aed,#db2777) !important;
    color:white !important;
}
.stDownloadButton > button {
    border-radius:8px !important; font-weight:600 !important;
    background:white !important; color:#6d28d9 !important;
    border:2px solid #7c3aed !important;
}
</style>
"""

def kpi_card(label, value, sub="", color=""):
    return f"""<div class="kpi-card {color}">
        <div class="kpi-label">{label}</div>
        <div class="kpi-value">{value}</div>
        {'<div class="kpi-sub">' + sub + '</div>' if sub else ''}
    </div>"""

def page_header(title, subtitle=""):
    return f"""<div class="page-header">
        <h1>{title}</h1>{'<p>' + subtitle + '</p>' if subtitle else ''}
    </div>"""

def section_title(text):
    return f'<div class="section-title">{text}</div>'

def info_box(text, color=""):
    return f'<div class="info-box {color}">ℹ️ {text}</div>'

def cr_row(label, value, style="", indent=False):
    cls = f"cr-row {style}" + (" indent" if indent else "")
    return f'<div class="{cls}"><span>{label}</span><span class="cr-val">{value}</span></div>'

def fmt(n):
    try: return f"{n:,.0f} FCFA"
    except: return "— FCFA"

def fmt_pct(n):
    try: return f"{n:.1f}%"
    except: return "—%"

def fmt_x(n):
    try: return f"{n:.2f}x"
    except: return "—"

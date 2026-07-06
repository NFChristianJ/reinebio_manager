CSS = """
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800&display=swap');
html, body, [class*="css"] { font-family: 'Inter', sans-serif !important; }

section[data-testid="stSidebar"] {
    background: linear-gradient(175deg,#1a1040 0%,#2d1b6e 55%,#3d1078 100%) !important;
}
section[data-testid="stSidebar"] * { color: #e9d5ff !important; }
section[data-testid="stSidebar"] hr { border-color: rgba(167,139,250,.25) !important; }

.main .block-container { background:#f5f3ff; padding-top:1.2rem !important; }

.page-header {
    background: linear-gradient(135deg,#6d28d9 0%,#be185d 100%);
    border-radius:14px; padding:1.3rem 1.8rem; margin-bottom:1.4rem;
}
.page-header h1 { color:white !important; font-size:1.4rem; font-weight:800; margin:0; }
.page-header p  { color:rgba(255,255,255,0.78) !important; font-size:0.82rem; margin:0.2rem 0 0; }

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
.kpi-label { font-size:0.72rem; font-weight:700; color:#6b7280 !important; text-transform:uppercase; letter-spacing:.07em; margin-bottom:.25rem; }
.kpi-value { font-size:1.5rem; font-weight:800; color:#1e1b4b !important; line-height:1.1; }
.kpi-sub   { font-size:0.7rem; color:#9ca3af !important; margin-top:.2rem; }

.section-title {
    font-size:.95rem; font-weight:700; color:#4c1d95 !important;
    margin:1.1rem 0 .6rem; padding-bottom:.35rem;
    border-bottom:2px solid #ede9fe;
}

.info-box {
    background:#f0fdf4; border-left:3px solid #22c55e;
    border-radius:8px; padding:.65rem .9rem; margin:.4rem 0;
    font-size:.8rem; color:#166534 !important; line-height:1.5;
}
.info-box.blue   { background:#eff6ff; border-color:#3b82f6; color:#1e40af !important; }
.info-box.purple { background:#faf5ff; border-color:#a855f7; color:#6b21a8 !important; }
.info-box.amber  { background:#fffbeb; border-color:#f59e0b; color:#92400e !important; }

.alert-success { background:#f0fdf4; border-left:4px solid #22c55e; border-radius:8px; padding:.75rem 1rem; margin:.4rem 0; color:#166534 !important; font-size:.83rem; }
.alert-danger  { background:#fef2f2; border-left:4px solid #ef4444; border-radius:8px; padding:.75rem 1rem; margin:.4rem 0; color:#991b1b !important; font-size:.83rem; }
.alert-warning { background:#fffbeb; border-left:4px solid #f59e0b; border-radius:8px; padding:.75rem 1rem; margin:.4rem 0; color:#92400e !important; font-size:.83rem; }

.cr-row { display:flex; justify-content:space-between; align-items:center; padding:.45rem .7rem; border-radius:7px; margin:.2rem 0; font-size:.87rem; }
.cr-row.header  { background:#ede9fe; font-weight:700; color:#4c1d95 !important; }
.cr-row.subtotal{ background:#f3f4f6; font-weight:600; color:#1f2937 !important; }
.cr-row.total   { background:linear-gradient(90deg,#6d28d9,#be185d); color:white !important; font-weight:800; border-radius:9px; }
.cr-row.indent  { padding-left:1.5rem; color:#4b5563 !important; }
.cr-row.green   { color:#059669 !important; font-weight:600; }
.cr-row.red     { color:#dc2626 !important; }
.cr-val { font-weight:700; white-space:nowrap; }

.bilan-section { background:white; border-radius:12px; padding:1rem 1.2rem; margin:.6rem 0; box-shadow:0 1px 6px rgba(0,0,0,.06); }
.bilan-header  { font-weight:800; color:#1e1b4b !important; font-size:.95rem; margin-bottom:.5rem; border-bottom:2px solid #ede9fe; padding-bottom:.3rem; }
.bilan-row     { display:flex; justify-content:space-between; padding:.3rem 0; font-size:.85rem; border-bottom:1px solid #f3f4f6; color:#374151 !important; }
.bilan-total   { display:flex; justify-content:space-between; padding:.5rem 0 0; font-weight:800; font-size:.92rem; color:#4c1d95 !important; border-top:2px solid #ede9fe; margin-top:.3rem; }

.ratio-card { background:white; border-radius:12px; padding:1rem 1.2rem; box-shadow:0 1px 6px rgba(0,0,0,.07); margin-bottom:.8rem; }
.ratio-name    { font-size:.78rem; font-weight:700; color:#6d28d9 !important; text-transform:uppercase; letter-spacing:.05em; }
.ratio-value   { font-size:1.6rem; font-weight:800; color:#1e1b4b !important; margin:.1rem 0; }
.ratio-formula { font-size:.72rem; color:#6b7280 !important; font-style:italic; margin:.1rem 0; }
.ratio-desc    { font-size:.75rem; color:#374151 !important; line-height:1.45; margin-top:.4rem; border-top:1px solid #f3f4f6; padding-top:.4rem; }
.ratio-signal.good { color:#059669 !important; font-weight:700; }
.ratio-signal.warn { color:#d97706 !important; font-weight:700; }
.ratio-signal.bad  { color:#dc2626 !important; font-weight:700; }

.logo-area { text-align:center; padding:1.2rem .8rem .8rem; }
.logo-icon  { font-size:2.2rem; display:block; margin-bottom:.2rem; }
.logo-title { font-size:1rem; font-weight:800; color:#ede9fe !important; }
.logo-sub   { font-size:.7rem; color:#a78bfa !important; margin-top:.1rem; }

.stTabs [data-baseweb="tab-list"] { background:white; border-radius:10px; padding:4px; gap:2px; border:1px solid #e5e7eb; }
.stTabs [data-baseweb="tab"] { border-radius:8px !important; color:#6b7280 !important; font-weight:500 !important; }
.stTabs [aria-selected="true"] { background:linear-gradient(135deg,#7c3aed,#db2777) !important; color:white !important; }

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
    border = {
        "rose": "#db2777", "cyan": "#0891b2", "green": "#059669",
        "orange": "#d97706", "red": "#dc2626", "": "#7c3aed"
    }.get(color, "#7c3aed")
    return f"""
    <div style="background:white;border-radius:12px;padding:1.1rem 1.3rem;
                border-left:4px solid {border};
                box-shadow:0 1px 8px rgba(109,40,217,0.09);margin-bottom:0.8rem">
        <div style="font-size:0.72rem;font-weight:700;color:#6b7280;text-transform:uppercase;
                    letter-spacing:.07em;margin-bottom:.25rem">{label}</div>
        <div style="font-size:1.5rem;font-weight:800;color:#1e1b4b;line-height:1.1">{value}</div>
        {'<div style="font-size:0.7rem;color:#9ca3af;margin-top:.2rem">' + sub + '</div>' if sub else ''}
    </div>"""

def page_header(title, subtitle=""):
    return f"""
    <div style="background:linear-gradient(135deg,#6d28d9 0%,#be185d 100%);
                border-radius:14px;padding:1.3rem 1.8rem;margin-bottom:1.4rem">
        <h1 style="color:white;font-size:1.4rem;font-weight:800;margin:0">{title}</h1>
        {'<p style="color:rgba(255,255,255,0.78);font-size:0.82rem;margin:0.2rem 0 0">' + subtitle + '</p>' if subtitle else ''}
    </div>"""

def section_title(text):
    return f'<div style="font-size:.95rem;font-weight:700;color:#4c1d95;margin:1.1rem 0 .6rem;padding-bottom:.35rem;border-bottom:2px solid #ede9fe">{text}</div>'

def info_box(text, color=""):
    configs = {
        "blue":   ("#eff6ff", "#3b82f6", "#1e40af"),
        "purple": ("#faf5ff", "#a855f7", "#6b21a8"),
        "amber":  ("#fffbeb", "#f59e0b", "#92400e"),
        "":       ("#f0fdf4", "#22c55e", "#166534"),
    }
    bg, border, tc = configs.get(color, configs[""])
    return f'<div style="background:{bg};border-left:3px solid {border};border-radius:8px;padding:.65rem .9rem;margin:.4rem 0;font-size:.8rem;color:{tc};line-height:1.5">ℹ️ {text}</div>'

def cr_row(label, value, style="", indent=False):
    styles = {
        "header":   ("background:#ede9fe", "#4c1d95", "700"),
        "subtotal": ("background:#f3f4f6", "#1f2937", "600"),
        "total":    ("background:linear-gradient(90deg,#6d28d9,#be185d);border-radius:9px", "white", "800"),
        "green":    ("background:white", "#059669", "600"),
        "red":      ("background:white", "#dc2626", "400"),
        "indent":   ("background:white", "#4b5563", "400"),
        "":         ("background:white", "#374151", "400"),
    }
    bg_style, color, weight = styles.get(style, styles[""])
    padding = "padding:.45rem 1.5rem" if indent else "padding:.45rem .7rem"
    return f'<div style="{bg_style};display:flex;justify-content:space-between;align-items:center;{padding};border-radius:7px;margin:.2rem 0;font-size:.87rem"><span style="color:{color};font-weight:{weight}">{label}</span><span style="color:{color};font-weight:700;white-space:nowrap">{value}</span></div>'

def fmt(n):
    try: return f"{n:,.0f} FCFA"
    except: return "— FCFA"

def fmt_pct(n):
    try: return f"{n:.1f}%"
    except: return "—%"

def fmt_x(n):
    try: return f"{n:.2f}x"
    except: return "—"

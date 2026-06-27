"""
app.py
------
Industry-style Streamlit frontend for Agentic SQL Analyst.

Flow:
Streamlit UI -> FastAPI Backend -> Agent Workflow -> PostgreSQL -> Response UI
"""

import html
import os
from datetime import datetime

import pandas as pd
import plotly.express as px
import streamlit as st
from PIL import Image

from api_client import (
    clear_history_api,
    get_dashboard_metrics,
    get_history_api,
    get_orders_by_status,
    get_revenue_by_category,
    get_revenue_by_country,
    get_top_products,
    login_api,
    run_query_api,
)


APP_NAME = "Agentic SQL Analyst"
APP_TAGLINE = "Natural-language analytics for SQL-backed business data"

CHART_COLORS = [
    "#2563EB",
    "#059669",
    "#D97706",
    "#7C3AED",
    "#DC2626",
    "#0891B2",
    "#4F46E5",
    "#65A30D",
]

PAGE_CONFIG = {
    "Dashboard": {
        "title": "Executive Dashboard",
        "subtitle": "Track revenue, orders, customers, and product performance from live operational data.",
        "kicker": "Business Performance",
    },
    "Ask Query": {
        "title": "Ask a Business Question",
        "subtitle": "Turn plain-English questions into validated SQL, result tables, charts, and business insights.",
        "kicker": "Query Studio",
    },
    "Analysis History": {
        "title": "Analysis History",
        "subtitle": "Review previous questions, generated SQL, result tables, charts, reports, and insights.",
        "kicker": "Audit Trail",
    },
    "Project Info": {
        "title": "Project Information",
        "subtitle": "A production-style natural-language analytics assistant built for SQL business intelligence workflows.",
        "kicker": "System Overview",
    },
}


st.set_page_config(
    page_title=APP_NAME,
    page_icon="A",
    layout="wide",
    initial_sidebar_state="expanded",
)


st.markdown(
    """
    <style>
    :root {
        --bg: #F8FAFC;
        --surface: #FFFFFF;
        --surface-soft: #F1F5F9;
        --text: #0F172A;
        --muted: #64748B;
        --border: #E2E8F0;
        --border-strong: #CBD5E1;
        --primary: #2563EB;
        --primary-dark: #1D4ED8;
        --success: #059669;
        --danger: #DC2626;
        --sidebar: #0B1220;
        --sidebar-soft: #111827;
    }

    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    .stDeployButton {display: none;}

    .stApp {
        background: var(--bg);
        color: var(--text);
    }

    .block-container {
        max-width: 1480px;
        padding: 1.35rem 2.4rem 2.2rem 2.4rem;
    }

    section[data-testid="stSidebar"] {
        background: var(--sidebar);
        border-right: 1px solid #1E293B;
    }

    section[data-testid="stSidebar"] * {
        color: #F8FAFC;
    }

    section[data-testid="stSidebar"] div[role="radiogroup"] label {
        background: transparent;
        border: 1px solid transparent;
        border-radius: 8px;
        padding: 8px 10px;
        margin-bottom: 4px;
    }

    section[data-testid="stSidebar"] div[role="radiogroup"] label:hover {
        background: rgba(148, 163, 184, 0.12);
        border-color: rgba(148, 163, 184, 0.16);
    }

    section[data-testid="stSidebar"] div[role="radiogroup"] label[data-baseweb="radio"] {
        color: #F8FAFC;
    }

    .brand-block {
        padding: 4px 0 18px 0;
    }

    .brand-row {
        display: flex;
        align-items: center;
        gap: 12px;
        margin-bottom: 14px;
    }

    .brand-mark {
        width: 38px;
        height: 38px;
        border-radius: 9px;
        background: linear-gradient(135deg, #2563EB, #1D4ED8);
        color: #FFFFFF;
        display: inline-flex;
        align-items: center;
        justify-content: center;
        font-weight: 850;
        letter-spacing: 0;
        box-shadow: 0 10px 26px rgba(37, 99, 235, 0.26);
    }

    .brand-title {
        font-size: 19px;
        font-weight: 850;
        color: #FFFFFF;
        line-height: 1.15;
    }

    .brand-subtitle {
        font-size: 12px;
        color: #CBD5E1;
        line-height: 1.45;
        margin-top: 2px;
    }

    .system-pill {
        display: inline-flex;
        align-items: center;
        gap: 8px;
        background: rgba(5, 150, 105, 0.14);
        border: 1px solid rgba(16, 185, 129, 0.32);
        border-radius: 999px;
        color: #D1FAE5;
        padding: 7px 11px;
        font-size: 12px;
        font-weight: 750;
    }

    .system-dot {
        width: 7px;
        height: 7px;
        border-radius: 999px;
        background: #10B981;
    }

    .user-panel {
        background: var(--sidebar-soft);
        border: 1px solid #334155;
        border-radius: 10px;
        padding: 13px;
        margin-top: 16px;
    }

    .user-label {
        font-size: 11px;
        color: #94A3B8;
        text-transform: uppercase;
        letter-spacing: 0.06em;
        font-weight: 800;
        margin-bottom: 4px;
    }

    .user-name {
        font-size: 14px;
        color: #FFFFFF;
        font-weight: 750;
        word-break: break-word;
    }

    .header-status-row {
        display: flex;
        flex-wrap: wrap;
        gap: 8px;
        margin-top: 14px;
    }

    .header-badge {
        display: inline-flex;
        align-items: center;
        border: 1px solid var(--border);
        background: #F8FAFC;
        color: #334155;
        border-radius: 999px;
        padding: 7px 11px;
        font-size: 12px;
        font-weight: 750;
        white-space: nowrap;
    }

    .page-header {
        background: var(--surface);
        border: 1px solid var(--border);
        border-radius: 10px;
        padding: 22px 24px;
        margin-bottom: 18px;
        box-shadow: 0 1px 2px rgba(15, 23, 42, 0.04);
    }

    .page-header-top {
        display: flex;
        align-items: center;
        justify-content: space-between;
        gap: 12px;
        margin-bottom: 14px;
    }

    .page-breadcrumb {
        color: var(--muted);
        font-size: 13px;
        font-weight: 700;
        min-width: 0;
        overflow: hidden;
        text-overflow: ellipsis;
        white-space: nowrap;
    }

    .header-online {
        display: inline-flex;
        align-items: center;
        gap: 7px;
        background: #F0FDF4;
        border: 1px solid #BBF7D0;
        color: #047857;
        border-radius: 999px;
        padding: 6px 10px;
        font-size: 12px;
        font-weight: 850;
        white-space: nowrap;
    }

    .header-online::before {
        content: "";
        width: 7px;
        height: 7px;
        border-radius: 999px;
        background: #10B981;
    }

    .page-kicker {
        color: var(--primary);
        text-transform: uppercase;
        letter-spacing: 0.08em;
        font-size: 12px;
        font-weight: 850;
        margin-bottom: 7px;
    }

    .page-title {
        color: var(--text);
        font-size: 30px;
        font-weight: 850;
        line-height: 1.16;
        margin-bottom: 5px;
    }

    .page-subtitle {
        color: var(--muted);
        font-size: 14px;
        line-height: 1.55;
        max-width: 860px;
    }

    .metric-card {
        background: var(--surface);
        border: 1px solid var(--border);
        border-radius: 10px;
        padding: 20px;
        min-height: 136px;
        box-shadow: 0 1px 2px rgba(15, 23, 42, 0.04);
    }

    .metric-card:hover {
        border-color: var(--border-strong);
        box-shadow: 0 10px 24px rgba(15, 23, 42, 0.06);
        transform: translateY(-1px);
        transition: all 0.18s ease;
    }

    .metric-topline {
        display: flex;
        align-items: center;
        justify-content: space-between;
        gap: 10px;
        margin-bottom: 13px;
    }

    .metric-label {
        color: var(--muted);
        font-size: 13px;
        font-weight: 800;
    }

    .metric-index {
        width: 30px;
        height: 30px;
        border-radius: 8px;
        background: #EFF6FF;
        color: var(--primary);
        display: inline-flex;
        align-items: center;
        justify-content: center;
        font-size: 12px;
        font-weight: 850;
    }

    .metric-value {
        color: var(--text);
        font-size: 29px;
        font-weight: 850;
        line-height: 1.15;
        margin-bottom: 8px;
    }

    .metric-note {
        color: var(--muted);
        font-size: 12px;
        font-weight: 600;
        line-height: 1.45;
    }

    .section-title {
        color: var(--text);
        font-size: 18px;
        font-weight: 850;
        line-height: 1.25;
        margin-bottom: 4px;
    }

    .section-subtitle {
        color: var(--muted);
        font-size: 13px;
        line-height: 1.5;
        margin-bottom: 14px;
    }

    .query-guide {
        background: #F8FAFC;
        border: 1px solid var(--border);
        border-radius: 10px;
        padding: 18px;
        min-height: 132px;
    }

    .guide-title {
        color: var(--text);
        font-weight: 850;
        font-size: 15px;
        margin-bottom: 8px;
    }

    .guide-item {
        color: var(--muted);
        font-size: 13px;
        line-height: 1.55;
        margin-bottom: 8px;
    }

    .insight-box {
        background: #F8FAFC;
        border: 1px solid var(--border-strong);
        border-left: 4px solid var(--primary);
        border-radius: 8px;
        padding: 18px 20px;
        color: var(--text);
        line-height: 1.7;
        font-size: 14px;
    }

    .empty-state {
        border: 1px dashed var(--border-strong);
        background: #F8FAFC;
        border-radius: 10px;
        padding: 24px;
        color: var(--muted);
        font-size: 14px;
        text-align: center;
    }

    .error-card {
        background: #FEF2F2;
        border: 1px solid #FECACA;
        border-left: 4px solid var(--danger);
        border-radius: 8px;
        padding: 14px 16px;
        color: #7F1D1D;
        font-size: 14px;
        line-height: 1.55;
    }

    .login-top-space {
        height: 5vh;
        min-height: 28px;
        max-height: 68px;
    }

    .auth-panel {
        background: linear-gradient(135deg, #0F172A 0%, #1E3A8A 100%);
        border-radius: 14px;
        padding: 28px;
        color: #FFFFFF;
        min-height: 430px;
        display: flex;
        flex-direction: column;
        justify-content: space-between;
        box-shadow: 0 24px 52px rgba(15, 23, 42, 0.18);
    }

    .auth-kicker {
        color: #BFDBFE;
        text-transform: uppercase;
        letter-spacing: 0.08em;
        font-size: 12px;
        font-weight: 850;
        margin-bottom: 10px;
    }

    .auth-title {
        font-size: 33px;
        font-weight: 900;
        line-height: 1.12;
        margin-bottom: 12px;
    }

    .auth-copy {
        color: #DBEAFE;
        font-size: 14px;
        line-height: 1.65;
        max-width: 480px;
    }

    .auth-points {
        display: grid;
        grid-template-columns: 1fr 1fr;
        gap: 10px;
        margin-top: 26px;
    }

    .auth-point {
        background: rgba(255, 255, 255, 0.08);
        border: 1px solid rgba(255, 255, 255, 0.14);
        border-radius: 10px;
        padding: 12px;
        color: #EFF6FF;
        font-size: 12px;
        font-weight: 700;
    }

    .auth-form-shell {
        min-height: 430px;
        display: flex;
        flex-direction: column;
        justify-content: center;
    }

    .auth-form-title {
        color: var(--text);
        font-size: 24px;
        font-weight: 900;
        margin-bottom: 6px;
    }

    .auth-form-subtitle {
        color: var(--muted);
        font-size: 13px;
        line-height: 1.55;
        margin-bottom: 20px;
    }

    div[data-testid="stDataFrame"] {
        border-radius: 8px;
        overflow: hidden;
        border: 1px solid var(--border);
    }

    textarea, input {
        border-radius: 8px !important;
    }

    .stButton > button,
    .stDownloadButton > button,
    button[kind="primary"] {
        border-radius: 8px !important;
        min-height: 42px;
        font-weight: 750 !important;
    }

    .stButton > button[kind="primary"],
    .stDownloadButton > button[kind="primary"],
    button[kind="primary"] {
        background: var(--primary) !important;
        border: 1px solid var(--primary) !important;
        color: #FFFFFF !important;
    }

    .stButton > button[kind="primary"]:hover,
    .stDownloadButton > button[kind="primary"]:hover,
    button[kind="primary"]:hover {
        background: var(--primary-dark) !important;
        border-color: var(--primary-dark) !important;
    }

    div[data-testid="stVerticalBlockBorderWrapper"] {
        border-radius: 10px !important;
        border-color: var(--border) !important;
        box-shadow: 0 1px 2px rgba(15, 23, 42, 0.03);
    }

    div[data-testid="stTabs"] div[role="tablist"] {
        gap: 10px;
        border-bottom: 1px solid var(--border);
        padding-bottom: 8px;
        margin-bottom: 16px;
    }

    div[data-testid="stTabs"] button[role="tab"] {
        border: 1px solid var(--border);
        background: #FFFFFF;
        border-radius: 999px;
        padding: 8px 18px;
        min-height: 40px;
        color: #475569;
        font-weight: 750;
    }

    div[data-testid="stTabs"] button[role="tab"][aria-selected="true"] {
        background: #EFF6FF;
        border-color: #BFDBFE;
        color: var(--primary);
    }

    @media (max-width: 900px) {
        .block-container {
            padding: 1rem;
        }

        .page-header-top {
            align-items: flex-start;
            flex-direction: column;
        }

        .page-title {
            font-size: 25px;
        }

        .auth-points {
            grid-template-columns: 1fr;
        }

        .metric-value {
            font-size: 24px;
        }

        .auth-panel,
        .auth-form-shell {
            min-height: 300px;
        }
    }
    </style>
    """,
    unsafe_allow_html=True,
)


if "logged_in" not in st.session_state:
    st.session_state.logged_in = False

if "username" not in st.session_state:
    st.session_state.username = ""

if "page" not in st.session_state:
    st.session_state.page = "Dashboard"

if "last_response" not in st.session_state:
    st.session_state.last_response = None


def set_page(page_name: str) -> None:
    st.session_state.page = page_name


def logout_user() -> None:
    st.session_state.logged_in = False
    st.session_state.username = ""
    st.session_state.page = "Dashboard"
    st.session_state.last_response = None
    st.rerun()


def format_currency(value) -> str:
    try:
        return f"INR {float(value):,.0f}"
    except Exception:
        return "N/A"


def format_number(value) -> str:
    try:
        return f"{int(value):,}"
    except Exception:
        return "N/A"


def parse_datetime(value) -> str:
    try:
        if not value:
            return "No timestamp"
        dt = datetime.fromisoformat(str(value))
        return dt.strftime("%d %b %Y, %I:%M %p")
    except Exception:
        return str(value)


def safe_text(value) -> str:
    return html.escape(str(value)) if value is not None else ""


def safe_api_call(func, *args, default=None):
    try:
        return func(*args)
    except Exception as exc:
        render_error(
            "The backend service is not reachable. Start the FastAPI server and try again.",
            technical_detail=str(exc),
        )
        return default


def dataframe_from_records(records) -> pd.DataFrame:
    if not records:
        return pd.DataFrame()
    return pd.DataFrame(records)


def dataframe_from_result(columns, result) -> pd.DataFrame:
    if not result or not columns:
        return pd.DataFrame()
    return pd.DataFrame(result, columns=columns)


def normalize_dataframe_for_display(df: pd.DataFrame) -> pd.DataFrame:
    display_df = df.copy()
    for col in display_df.columns:
        col_lower = str(col).lower()
        if any(token in col_lower for token in ["revenue", "amount", "sales", "spending", "price"]):
            try:
                display_df[col] = display_df[col].apply(format_currency)
            except Exception:
                pass
    return display_df


def style_plotly_chart(fig, height: int = 360, showlegend: bool = False):
    fig.update_layout(
        height=height,
        showlegend=showlegend,
        plot_bgcolor="#FFFFFF",
        paper_bgcolor="#FFFFFF",
        margin=dict(l=20, r=20, t=24, b=20),
        font=dict(color="#0F172A", size=12),
        colorway=CHART_COLORS,
    )
    fig.update_xaxes(
        showgrid=True,
        gridcolor="#E2E8F0",
        zeroline=False,
        title_font=dict(size=12, color="#475569"),
        tickfont=dict(size=11, color="#64748B"),
    )
    fig.update_yaxes(
        showgrid=True,
        gridcolor="#E2E8F0",
        zeroline=False,
        title_font=dict(size=12, color="#475569"),
        tickfont=dict(size=11, color="#64748B"),
    )
    return fig


def render_topbar() -> None:
    return None


def render_page_header(page_name: str) -> None:
    page = PAGE_CONFIG.get(page_name, PAGE_CONFIG["Dashboard"])
    st.markdown(
        f"""
        <div class="page-header">
            <div class="page-header-top">
                <div class="page-breadcrumb">{safe_text(APP_NAME)} / {safe_text(page_name)}</div>
                <div class="header-online">System online</div>
            </div>
            <div class="page-kicker">{safe_text(page["kicker"])}</div>
            <div class="page-title">{safe_text(page["title"])}</div>
            <div class="page-subtitle">{safe_text(page["subtitle"])}</div>
            <div class="header-status-row">
                <span class="header-badge">Validated SQL workflow</span>
                <span class="header-badge">Read-only execution</span>
                <span class="header-badge">Live analytics workspace</span>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def render_empty_state(message: str) -> None:
    st.markdown(
        f"""
        <div class="empty-state">
            {safe_text(message)}
        </div>
        """,
        unsafe_allow_html=True,
    )


def render_error(message: str, technical_detail: str | None = None) -> None:
    detail_html = ""
    if technical_detail:
        detail_html = f"<br><span style='font-size:12px;'>Technical detail: {safe_text(technical_detail)}</span>"
    st.markdown(
        f"""
        <div class="error-card">
            <strong>Action needed:</strong> {safe_text(message)}
            {detail_html}
        </div>
        """,
        unsafe_allow_html=True,
    )


def render_metric_card(index: int, label: str, value: str, note: str) -> None:
    st.markdown(
        f"""
        <div class="metric-card">
            <div class="metric-topline">
                <div class="metric-label">{safe_text(label)}</div>
                <div class="metric-index">{index:02d}</div>
            </div>
            <div class="metric-value">{safe_text(value)}</div>
            <div class="metric-note">{safe_text(note)}</div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def login_page() -> None:
    st.markdown("<div class='login-top-space'></div>", unsafe_allow_html=True)

    outer_left, center, outer_right = st.columns([0.12, 0.76, 0.12])

    with outer_left:
        st.empty()

    with outer_right:
        st.empty()

    with center:
        left, right = st.columns([1, 1], gap="large", vertical_alignment="center")

        with left:
            st.markdown(
                f"""
                <div class="auth-panel">
                    <div>
                        <div class="auth-kicker">Business Intelligence Workspace</div>
                        <div class="auth-title">{safe_text(APP_NAME)}</div>
                        <div class="auth-copy">
                            {safe_text(APP_TAGLINE)}. Ask questions in plain English, review validated SQL,
                            analyze result tables, generate charts, export reports, and keep a clean audit trail.
                        </div>
                        <div class="auth-points">
                            <div class="auth-point">Natural language to SQL</div>
                            <div class="auth-point">Validated read-only queries</div>
                            <div class="auth-point">Charts and insights</div>
                            <div class="auth-point">Persistent history</div>
                        </div>
                    </div>
                    <div class="auth-copy">
                        Built with Streamlit, FastAPI, PostgreSQL, Gemini, Pandas, and Plotly.
                    </div>
                </div>
                """,
                unsafe_allow_html=True,
            )

        with right:
            with st.container(border=True):
                st.markdown(
                    """
                    <div class="auth-form-title">Welcome back</div>
                    <div class="auth-form-subtitle">
                        Sign in to open the analytics dashboard and query workspace.
                    </div>
                    """,
                    unsafe_allow_html=True,
                )

                with st.form("login_form", clear_on_submit=False):
                    username = st.text_input("Username", placeholder="Enter username")
                    password = st.text_input("Password", placeholder="Enter password", type="password")
                    submitted = st.form_submit_button("Open Workspace", width="stretch", type="primary")

                st.caption("Use the project demo credentials configured in your backend.")
                st.markdown("<div style='height: 76px;'></div>", unsafe_allow_html=True)

                if submitted:
                    result = safe_api_call(
                        login_api,
                        username,
                        password,
                        default={"success": False, "error": "Backend error"},
                    )

                    if result and result.get("success"):
                        st.session_state.logged_in = True
                        st.session_state.username = result.get("username", username)
                        st.rerun()

                    error_message = result.get("error", "Invalid username or password.") if result else "Login failed."
                    render_error(error_message)


def render_sidebar() -> None:
    with st.sidebar:
        st.markdown(
            f"""
            <div class="brand-block">
                <div class="brand-row">
                    <div class="brand-mark">A</div>
                    <div>
                        <div class="brand-title">Agentic SQL</div>
                        <div class="brand-subtitle">Business intelligence workspace</div>
                    </div>
                </div>
                <div class="system-pill">
                    <span class="system-dot"></span>
                    System online
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )

        pages = ["Dashboard", "Ask Query", "Analysis History", "Project Info"]
        current_index = pages.index(st.session_state.page) if st.session_state.page in pages else 0
        selected_page = st.radio(
            "Navigation",
            pages,
            index=current_index,
            label_visibility="visible",
        )

        if selected_page != st.session_state.page:
            set_page(selected_page)
            st.rerun()

        st.markdown("---")

        st.markdown(
            f"""
            <div class="user-panel">
                <div class="user-label">Signed in as</div>
                <div class="user-name">{safe_text(st.session_state.username)}</div>
            </div>
            """,
            unsafe_allow_html=True,
        )

        st.markdown("<br>", unsafe_allow_html=True)
        if st.button("Sign Out", width="stretch"):
            logout_user()


def render_dashboard() -> None:
    render_topbar()
    render_page_header("Dashboard")

    metrics = safe_api_call(
        get_dashboard_metrics,
        default={
            "total_revenue": 0,
            "total_orders": 0,
            "total_customers": 0,
            "total_products": 0,
        },
    )

    if metrics is None:
        return

    metric_items = [
        ("Total Revenue", format_currency(metrics.get("total_revenue")), "Gross sales value across completed data"),
        ("Total Orders", format_number(metrics.get("total_orders")), "Orders captured in the system"),
        ("Customers", format_number(metrics.get("total_customers")), "Unique customer records available"),
        ("Products", format_number(metrics.get("total_products")), "Products available for analysis"),
    ]

    metric_cols = st.columns(4)
    for idx, (column, item) in enumerate(zip(metric_cols, metric_items), start=1):
        label, value, note = item
        with column:
            render_metric_card(idx, label, value, note)

    st.markdown("<br>", unsafe_allow_html=True)

    left, right = st.columns([1.2, 1], gap="medium")

    with left:
        with st.container(border=True):
            st.markdown("<div class='section-title'>Revenue by Category</div>", unsafe_allow_html=True)
            st.markdown(
                "<div class='section-subtitle'>Revenue contribution across product categories.</div>",
                unsafe_allow_html=True,
            )

            data = safe_api_call(get_revenue_by_category, default=[])
            df_category = dataframe_from_records(data)

            if df_category.empty:
                render_empty_state("No category revenue data is available yet.")
            else:
                fig = px.bar(
                    df_category,
                    x="category",
                    y="revenue",
                    text="revenue",
                    color="category",
                    color_discrete_sequence=CHART_COLORS,
                )
                fig = style_plotly_chart(fig, height=385)
                fig.update_layout(xaxis_title="Category", yaxis_title="Revenue")
                fig.update_traces(texttemplate="INR %{text:,.0f}", textposition="outside")
                st.plotly_chart(fig, width="stretch")

    with right:
        with st.container(border=True):
            st.markdown("<div class='section-title'>Top Products</div>", unsafe_allow_html=True)
            st.markdown(
                "<div class='section-subtitle'>Highest-performing products ranked by revenue.</div>",
                unsafe_allow_html=True,
            )

            data = safe_api_call(get_top_products, default=[])
            df_products = dataframe_from_records(data)

            if df_products.empty:
                render_empty_state("No product performance data is available yet.")
            else:
                st.dataframe(normalize_dataframe_for_display(df_products), width="stretch", hide_index=True)

    bottom_left, bottom_right = st.columns([1, 1], gap="medium")

    with bottom_left:
        with st.container(border=True):
            st.markdown("<div class='section-title'>Orders by Status</div>", unsafe_allow_html=True)
            st.markdown(
                "<div class='section-subtitle'>Current mix of order processing states.</div>",
                unsafe_allow_html=True,
            )

            data = safe_api_call(get_orders_by_status, default=[])
            df_status = dataframe_from_records(data)

            if df_status.empty:
                render_empty_state("No order status data is available yet.")
            else:
                fig = px.pie(
                    df_status,
                    names="status",
                    values="total_orders",
                    hole=0.5,
                    color_discrete_sequence=CHART_COLORS,
                )
                fig.update_layout(
                    height=340,
                    margin=dict(l=20, r=20, t=24, b=20),
                    paper_bgcolor="#FFFFFF",
                    font=dict(color="#0F172A", size=12),
                    legend=dict(orientation="h", y=-0.14),
                )
                st.plotly_chart(fig, width="stretch")

    with bottom_right:
        with st.container(border=True):
            st.markdown("<div class='section-title'>Revenue by Country</div>", unsafe_allow_html=True)
            st.markdown(
                "<div class='section-subtitle'>Revenue distribution across customer markets.</div>",
                unsafe_allow_html=True,
            )

            data = safe_api_call(get_revenue_by_country, default=[])
            df_country = dataframe_from_records(data)

            if df_country.empty:
                render_empty_state("No country revenue data is available yet.")
            else:
                fig = px.bar(
                    df_country,
                    x="revenue",
                    y="country",
                    orientation="h",
                    text="revenue",
                    color="country",
                    color_discrete_sequence=CHART_COLORS,
                )
                fig = style_plotly_chart(fig, height=340)
                fig.update_layout(xaxis_title="Revenue", yaxis_title="Country")
                fig.update_traces(texttemplate="INR %{text:,.0f}", textposition="outside")
                st.plotly_chart(fig, width="stretch")


def render_query_page() -> None:
    render_topbar()
    render_page_header("Ask Query")

    examples = [
        "show revenue by category",
        "show revenue share by category",
        "show revenue trend by month",
        "show top 5 products by revenue",
        "show order status distribution",
        "show all products whose revenue is greater than the average revenue of all products",
    ]

    guide_col_1, guide_col_2, guide_col_3 = st.columns(3, gap="medium")

    with guide_col_1:
        st.markdown(
            """
            <div class="query-guide">
                <div class="guide-title">Ask in business language</div>
                <div class="guide-item">Example: show revenue trend by month.</div>
                <div class="guide-item">Use simple words like revenue, orders, products, customers, country, category, status, and month.</div>
            </div>
            """,
            unsafe_allow_html=True,
        )

    with guide_col_2:
        st.markdown(
            """
            <div class="query-guide">
                <div class="guide-title">Better chart output</div>
                <div class="guide-item">Chart-friendly output needs one label column and one numeric column.</div>
                <div class="guide-item">Use words like share, distribution, trend, top, or revenue by category.</div>
            </div>
            """,
            unsafe_allow_html=True,
        )

    with guide_col_3:
        st.markdown(
            """
            <div class="query-guide">
                <div class="guide-title">Safety layer</div>
                <div class="guide-item">The backend validates generated SQL before execution.</div>
                <div class="guide-item">Write operations are blocked so analysis remains read-only.</div>
            </div>
            """,
            unsafe_allow_html=True,
        )

    st.markdown("<br>", unsafe_allow_html=True)

    with st.container(border=True):
        st.markdown("<div class='section-title'>Query Composer</div>", unsafe_allow_html=True)
        st.markdown(
            "<div class='section-subtitle'>Choose an example or write your own business question.</div>",
            unsafe_allow_html=True,
        )

        selected = st.selectbox("Try an example", [""] + examples)
        question = st.text_area(
            "Business question",
            value=selected,
            placeholder="Example: show top 5 products by revenue",
            height=155,
        )

        run_button = st.button("Run Analysis", width="stretch", type="primary")

    if run_button:
        if not question.strip():
            st.warning("Please enter a business question.")
            return

        with st.spinner("Generating SQL, validating it, querying the database, and preparing insights..."):
            response = safe_api_call(
                run_query_api,
                st.session_state.username,
                question,
                default={"error": "API call failed"},
            )

        if not response:
            return

        if "error" in response:
            render_error(response["error"], response.get("technical_detail"))
            return

        st.session_state.last_response = response

    if st.session_state.last_response:
        render_analysis_response(st.session_state.last_response)


def render_analysis_response(response) -> None:
    st.markdown("<br>", unsafe_allow_html=True)

    tab_summary, tab_sql, tab_result, tab_artifacts = st.tabs(
        ["Summary", "Generated SQL", "Result Table", "Chart and Report"]
    )

    with tab_summary:
        with st.container(border=True):
            st.markdown("<div class='section-title'>User Question</div>", unsafe_allow_html=True)
            st.write(response.get("question", ""))

        with st.container(border=True):
            st.markdown("<div class='section-title'>Business Insight</div>", unsafe_allow_html=True)
            insight = response.get("insight", "No insight generated.")
            insight_html = safe_text(insight).replace("\n", "<br>")
            st.markdown(f"<div class='insight-box'>{insight_html}</div>", unsafe_allow_html=True)

    with tab_sql:
        with st.container(border=True):
            st.markdown("<div class='section-title'>Generated SQL</div>", unsafe_allow_html=True)
            st.markdown(
                "<div class='section-subtitle'>Validated read-only SQL generated for this question.</div>",
                unsafe_allow_html=True,
            )
            st.code(response.get("sql", ""), language="sql")

    with tab_result:
        with st.container(border=True):
            st.markdown("<div class='section-title'>Query Result</div>", unsafe_allow_html=True)

            result = response.get("result", [])
            columns = response.get("columns", [])
            df = dataframe_from_result(columns, result)

            if df.empty:
                render_empty_state("The query executed successfully, but no rows were returned.")
            else:
                st.dataframe(normalize_dataframe_for_display(df), width="stretch", hide_index=True)
                csv_data = df.to_csv(index=False).encode("utf-8")
                st.download_button(
                    label="Download Result CSV",
                    data=csv_data,
                    file_name="query_result.csv",
                    mime="text/csv",
                    width="stretch",
                )

    with tab_artifacts:
        left, right = st.columns([1, 1], gap="medium")

        with left:
            with st.container(border=True):
                st.markdown("<div class='section-title'>Analysis Chart</div>", unsafe_allow_html=True)
                chart_path = response.get("chart_path")

                if chart_path and os.path.exists(chart_path):
                    image = Image.open(chart_path)
                    st.image(image, width="stretch")
                else:
                    render_empty_state("No chart was generated for this query.")

        with right:
            with st.container(border=True):
                st.markdown("<div class='section-title'>Export Report</div>", unsafe_allow_html=True)
                report_path = response.get("report_path")

                if report_path and os.path.exists(report_path):
                    with open(report_path, "r", encoding="utf-8") as file:
                        report_text = file.read()

                    st.download_button(
                        label="Download Analysis Report",
                        data=report_text,
                        file_name=os.path.basename(report_path),
                        mime="text/plain",
                        width="stretch",
                    )
                    st.caption(f"Report saved at: {report_path}")
                else:
                    render_empty_state("No report was generated for this query.")


def render_history_page() -> None:
    render_topbar()
    render_page_header("Analysis History")

    history = safe_api_call(get_history_api, st.session_state.username, default=[])

    if not history:
        render_empty_state("No saved analysis history yet. Run an analysis to begin building your audit trail.")
        return

    col1, col2 = st.columns([4, 1], vertical_alignment="center")
    with col1:
        st.success(f"Found {len(history)} saved analysis records.")
    with col2:
        if st.button("Clear History", width="stretch"):
            result = safe_api_call(clear_history_api, st.session_state.username, default={"success": False})
            if result and result.get("success"):
                st.success("History cleared successfully.")
                st.rerun()
            else:
                render_error("Unable to clear history.")

    search_text = st.text_input("Search history", placeholder="Search by question text").strip().lower()
    filtered_history = history

    if search_text:
        filtered_history = [
            item for item in history
            if search_text in item.get("question", "").lower()
        ]

    if not filtered_history:
        render_empty_state("No history records match your search.")
        return

    for index, item in enumerate(filtered_history, start=1):
        created_text = parse_datetime(item.get("created_at"))
        question = item.get("question", "")

        with st.expander(f"{index}. {question} | {created_text}"):
            st.markdown("### Generated SQL")
            st.code(item.get("sql", ""), language="sql")

            st.markdown("### Query Result")
            result = item.get("result", [])
            columns = item.get("columns", [])
            df = dataframe_from_result(columns, result)

            if df.empty:
                st.info("No result saved.")
            else:
                st.dataframe(normalize_dataframe_for_display(df), width="stretch", hide_index=True)

            st.markdown("### Business Insight")
            st.info(item.get("insight", "No insight saved."))

            if item.get("chart_path"):
                st.caption(f"Chart path: {item['chart_path']}")
            if item.get("report_path"):
                st.caption(f"Report path: {item['report_path']}")


def render_project_info() -> None:
    render_topbar()
    render_page_header("Project Info")

    with st.container(border=True):
        st.markdown("## Project Overview")
        st.write(
            """
            Agentic SQL Analyst allows users to ask data questions in plain English.
            The system translates each question into validated PostgreSQL, executes it safely,
            generates result tables, creates business insights, produces charts, exports reports,
            and stores analysis history for review.
            """
        )

    col1, col2, col3 = st.columns(3, gap="medium")

    with col1:
        with st.container(border=True):
            st.markdown("## Core Capabilities")
            st.write("- Natural language to SQL")
            st.write("- PostgreSQL query execution")
            st.write("- SQL safety validation")
            st.write("- Automatic SQL correction")
            st.write("- Business insight generation")

    with col2:
        with st.container(border=True):
            st.markdown("## User Features")
            st.write("- Executive dashboard")
            st.write("- Query workspace")
            st.write("- Chart generation")
            st.write("- Exportable reports")
            st.write("- Persistent history")

    with col3:
        with st.container(border=True):
            st.markdown("## Technology Stack")
            st.write("- Python")
            st.write("- Streamlit")
            st.write("- FastAPI")
            st.write("- PostgreSQL")
            st.write("- Gemini API")
            st.write("- Pandas and Plotly")


if not st.session_state.logged_in:
    login_page()
else:
    render_sidebar()

    if st.session_state.page == "Dashboard":
        render_dashboard()
    elif st.session_state.page == "Ask Query":
        render_query_page()
    elif st.session_state.page == "Analysis History":
        render_history_page()
    elif st.session_state.page == "Project Info":
        render_project_info()

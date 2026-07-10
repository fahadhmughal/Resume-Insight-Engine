"""Resume Insight Engine - main Streamlit application."""

import os

os.environ.setdefault("TRANSFORMERS_NO_TF", "1")
os.environ.setdefault("USE_TF", "0")

import io
import csv
import base64
from typing import List, Dict, Any

import streamlit as st
import pandas as pd
import plotly.graph_objects as go

from core.parser import extract_text_from_pdf, ParserError
from core.section_splitter import split_into_sections
from core.jd_extractor import extract_jd_keywords
from core.scoring_engine import compute_section_scores, compute_final_score
from core.explainer import get_score_contributors
from services.report_generator import generate_candidate_report

NAVY       = "#1B2A4A"
DARK_GREY  = "#374151"
MID_GREY   = "#6B7280"
LIGHT_GREY = "#E5E7EB"
BG_WHITE   = "#FFFFFF"
CARD_BG    = "#F9FAFB"

SECTION_ORDER = ["skills", "experience", "projects", "education", "certifications"]
SECTION_LABELS = {
    "skills":           "Skills",
    "experience":       "Experience",
    "projects":         "Projects",
    "education":        "Education",
    "certifications":   "Certifications",
}


def configure_page():
    """Set page config and inject global CSS."""
    st.set_page_config(
        page_title="Resume Insight Engine",
        layout="wide",
        initial_sidebar_state="expanded",
    )

    st.markdown("""
    <style>
        #MainMenu {visibility: hidden;}
        footer     {visibility: hidden;}
        header     {visibility: hidden;}

        html, body, [class*="css"] {
            font-family: 'Inter', 'Segoe UI', system-ui, sans-serif;
            color: #374151;
        }
        .block-container {
            padding-top: 1.4rem;
            padding-bottom: 2rem;
        }

        [data-testid="stSidebar"] {
            background-color: #FFFFFF;
            border-right: 2px solid #E5E7EB;
        }
        [data-testid="stSidebar"] > div:first-child {
            padding: 1.2rem 1.2rem 1.5rem 1.2rem;
        }

        [data-testid="stSidebar"] textarea {
            background-color: #FFFFFF !important;
            color: #374151 !important;
            border: 1.5px solid #D1D5DB !important;
            border-radius: 6px !important;
            font-size: 0.88rem !important;
            line-height: 1.5 !important;
            padding: 0.65rem 0.75rem !important;
        }
        [data-testid="stSidebar"] textarea:focus {
            border-color: #1B2A4A !important;
            box-shadow: 0 0 0 2px rgba(27, 42, 74, 0.12) !important;
        }
        [data-testid="stSidebar"] textarea::placeholder {
            color: #9CA3AF !important;
            opacity: 1 !important;
        }

        .sb-header {
            border-bottom: 1px solid #E5E7EB;
            padding-bottom: 0.9rem;
            margin-bottom: 1.2rem;
        }
        .sb-app-name {
            font-size: 0.95rem;
            font-weight: 700;
            color: #1B2A4A;
            letter-spacing: -0.01em;
        }
        .sb-app-tag {
            font-size: 0.72rem;
            color: #9CA3AF;
            margin-top: 0.1rem;
        }

        .sb-label {
            font-size: 0.72rem;
            font-weight: 700;
            text-transform: uppercase;
            letter-spacing: 0.07em;
            color: #6B7280;
            margin: 0 0 0.35rem 0;
        }
        .sb-divider {
            border: none;
            border-top: 1px solid #E5E7EB;
            margin: 1rem 0;
        }
        .sb-hint {
            font-size: 0.76rem;
            color: #9CA3AF;
            margin-top: 0.3rem;
            line-height: 1.4;
        }

        .page-header {
            margin-bottom: 1.6rem;
            padding-bottom: 1.2rem;
            border-bottom: 2px solid #E5E7EB;
        }
        .page-title {
            font-size: 2rem;
            font-weight: 800;
            color: #1B2A4A;
            letter-spacing: -0.03em;
            margin: 0 0 0.35rem 0;
            line-height: 1.2;
        }
        .page-subtitle {
            font-size: 0.95rem;
            color: #6B7280;
            margin: 0;
            line-height: 1.5;
        }
        .page-tag {
            display: inline-block;
            background: #EEF2FF;
            color: #4338CA;
            font-size: 0.72rem;
            font-weight: 600;
            padding: 0.18rem 0.6rem;
            border-radius: 20px;
            margin-left: 0.6rem;
            vertical-align: middle;
            letter-spacing: 0.03em;
        }

        .sec-heading {
            font-size: 0.9rem;
            font-weight: 700;
            text-transform: uppercase;
            letter-spacing: 0.06em;
            color: #1B2A4A;
            border-left: 3px solid #1B2A4A;
            padding-left: 0.6rem;
            margin: 0 0 0.75rem 0;
            line-height: 1;
        }

        .metric-card {
            background: #FFFFFF;
            border: 1px solid #E5E7EB;
            border-radius: 6px;
            padding: 0.9rem 1.1rem;
        }
        .metric-label {
            font-size: 0.72rem;
            font-weight: 600;
            text-transform: uppercase;
            letter-spacing: 0.06em;
            color: #6B7280;
            margin: 0 0 0.3rem 0;
        }
        .metric-value {
            font-size: 1.6rem;
            font-weight: 800;
            color: #1B2A4A;
            margin: 0;
            letter-spacing: -0.02em;
        }
        .metric-sub {
            font-size: 0.75rem;
            color: #9CA3AF;
            margin: 0.1rem 0 0 0;
        }

        .score-badge {
            display: inline-block;
            padding: 0.2rem 0.6rem;
            border-radius: 4px;
            font-weight: 700;
            font-size: 0.88rem;
        }
        .score-high { background: #D1FAE5; color: #065F46; }
        .score-mid  { background: #FEF3C7; color: #92400E; }
        .score-low  { background: #FEE2E2; color: #991B1B; }

        .results-table {
            width: 100%;
            border-collapse: collapse;
            font-size: 0.875rem;
        }
        .results-table th {
            background-color: #1B2A4A;
            color: #FFFFFF;
            padding: 0.55rem 0.8rem;
            text-align: left;
            font-weight: 600;
            font-size: 0.8rem;
            text-transform: uppercase;
            letter-spacing: 0.04em;
        }
        .results-table td {
            padding: 0.55rem 0.8rem;
            border-bottom: 1px solid #F3F4F6;
            color: #374151;
        }
        .results-table tbody tr:hover td {
            background-color: #F9FAFB;
        }

        .contrib-header {
            font-size: 0.78rem;
            font-weight: 700;
            text-transform: uppercase;
            letter-spacing: 0.05em;
            color: #374151;
            margin: 0 0 0.5rem 0;
        }
        .booster-item {
            font-size: 0.85rem;
            color: #065F46;
            padding: 0.15rem 0;
        }
        .dragger-item {
            font-size: 0.85rem;
            color: #991B1B;
            padding: 0.15rem 0;
        }

        .dl-link {
            display: inline-block;
            padding: 0.4rem 1rem;
            background: #1B2A4A;
            color: #FFFFFF !important;
            text-decoration: none;
            border-radius: 4px;
            font-size: 0.82rem;
            font-weight: 600;
            letter-spacing: 0.02em;
            cursor: pointer;
        }
        .dl-link:hover {
            background: #2A3F6E;
        }
        .dl-link-secondary {
            display: inline-block;
            padding: 0.35rem 0.9rem;
            background: #FFFFFF;
            color: #1B2A4A !important;
            text-decoration: none;
            border: 1px solid #D1D5DB;
            border-radius: 4px;
            font-size: 0.82rem;
            font-weight: 600;
            cursor: pointer;
            margin-left: 0.5rem;
        }
        .dl-link-secondary:hover {
            background: #F9FAFB;
        }

        .gs-wrap {
            border: 1px solid #E5E7EB;
            border-radius: 8px;
            padding: 1.8rem;
            background: #FFFFFF;
        }
        .gs-title {
            font-size: 1.05rem;
            font-weight: 700;
            color: #1B2A4A;
            margin: 0 0 0.3rem 0;
        }
        .gs-desc {
            font-size: 0.85rem;
            color: #6B7280;
            margin: 0 0 1.4rem 0;
        }
        .gs-grid {
            display: grid;
            grid-template-columns: repeat(4, 1fr);
            gap: 1rem;
        }
        .gs-card {
            background: #F9FAFB;
            border: 1px solid #E5E7EB;
            border-radius: 6px;
            padding: 1.1rem 1rem;
            text-align: center;
        }
        .gs-num {
            width: 26px;
            height: 26px;
            border-radius: 50%;
            background: #1B2A4A;
            color: #FFFFFF;
            font-size: 0.78rem;
            font-weight: 800;
            display: flex;
            align-items: center;
            justify-content: center;
            margin: 0 auto 0.6rem auto;
        }
        .gs-step-title {
            font-size: 0.85rem;
            font-weight: 700;
            color: #1B2A4A;
            margin: 0 0 0.25rem 0;
        }
        .gs-step-desc {
            font-size: 0.78rem;
            color: #6B7280;
            line-height: 1.4;
            margin: 0;
        }
        .gs-info {
            margin-top: 1.2rem;
            padding: 0.7rem 0.9rem;
            background: #F8FAFC;
            border: 1px solid #E5E7EB;
            border-left: 3px solid #1B2A4A;
            border-radius: 0 6px 6px 0;
            font-size: 0.8rem;
            color: #4B5563;
            line-height: 1.5;
        }
        .gs-info ul {
            margin: 0.4rem 0 0 0;
            padding-left: 1.2rem;
        }
        .gs-info li {
            margin-bottom: 0.2rem;
        }

        .validation-msg { color: #991B1B; font-size: 0.88rem; padding: 0.4rem 0; }
        .status-text    { color: #6B7280; font-size: 0.88rem; }
        .section-label  { font-size: 0.82rem; font-weight: 600; color: #374151; }
    </style>
    """, unsafe_allow_html=True)


def score_css_class(score: float) -> str:
    """Return CSS class name based on score threshold."""
    if score >= 70:
        return "score-high"
    elif score >= 50:
        return "score-mid"
    return "score-low"


def _pdf_download_anchor(data: bytes, filename: str, label: str, css: str = "dl-link") -> str:
    """Return an <a> tag that downloads a PDF via a base64 data-URI."""
    b64 = base64.b64encode(data).decode()
    href = f"data:application/pdf;base64,{b64}"
    return f'<a href="{href}" download="{filename}" class="{css}">{label}</a>'


def _csv_download_anchor(data: str, filename: str, label: str, css: str = "dl-link-secondary") -> str:
    """Return an <a> tag that downloads CSV via a base64 data-URI."""
    b64 = base64.b64encode(data.encode()).decode()
    href = f"data:text/csv;base64,{b64}"
    return f'<a href="{href}" download="{filename}" class="{css}">{label}</a>'


def build_results_table_html(results: List[Dict[str, Any]]) -> str:
    """Build an HTML table for the ranked results."""
    rows = ""
    for i, r in enumerate(results, 1):
        badge_cls = score_css_class(r["final_score"])
        section_cells = "".join(
            f'<td style="text-align:center;">{r["section_scores"].get(s, 0.0):.1f}</td>'
            for s in SECTION_ORDER
        )
        rows += f"""
        <tr>
            <td style="text-align:center; color:#6B7280;">{i}</td>
            <td><strong>{r["filename"]}</strong></td>
            <td style="text-align:center;">
                <span class="score-badge {badge_cls}">{r["final_score"]:.1f}</span>
            </td>
            {section_cells}
        </tr>"""

    section_headers = "".join(
        f'<th style="text-align:center;">{SECTION_LABELS[s]}</th>'
        for s in SECTION_ORDER
    )

    return f"""
    <table class="results-table">
        <thead>
            <tr>
                <th style="text-align:center; width:50px;">#</th>
                <th>Candidate</th>
                <th style="text-align:center;">Score</th>
                {section_headers}
            </tr>
        </thead>
        <tbody>{rows}</tbody>
    </table>
    """


def results_to_csv(results: List[Dict[str, Any]]) -> str:
    """Convert results to a CSV string."""
    output = io.StringIO()
    writer = csv.writer(output)
    header = ["Rank", "Candidate", "Final Score"] + [SECTION_LABELS[s] for s in SECTION_ORDER]
    writer.writerow(header)
    for i, r in enumerate(results, 1):
        row = [i, r["filename"], round(r["final_score"], 2)]
        row += [round(r["section_scores"].get(s, 0.0), 2) for s in SECTION_ORDER]
        writer.writerow(row)
    return output.getvalue()


def make_candidate_chart(results: List[Dict[str, Any]]) -> go.Figure:
    """Bar chart of candidate scores."""
    names  = [r["filename"] for r in results]
    scores = [r["final_score"] for r in results]
    colors = [
        "#059669" if s >= 70 else "#D97706" if s >= 50 else "#DC2626"
        for s in scores
    ]

    fig = go.Figure(go.Bar(
        x=names,
        y=scores,
        marker_color=colors,
        text=[f"{s:.1f}" for s in scores],
        textposition="outside",
        textfont=dict(size=11, color=NAVY),
    ))
    fig.update_layout(
        title=dict(text="Candidate Scores", font=dict(size=14, color=NAVY, family="Inter, Segoe UI, sans-serif")),
        xaxis_title=None,
        yaxis_title="Score",
        yaxis=dict(range=[0, 110], autorange=False, gridcolor=LIGHT_GREY),
        plot_bgcolor=BG_WHITE,
        paper_bgcolor=BG_WHITE,
        font=dict(family="Inter, Segoe UI, sans-serif", color=DARK_GREY, size=12),
        margin=dict(t=55, b=50, l=50, r=20),
        height=360,
        hoverlabel=dict(bgcolor=NAVY, font_color="white"),
    )
    return fig


def make_missing_skills_chart(results: List[Dict[str, Any]]) -> go.Figure:
    """Horizontal bar chart of most commonly missing skills."""
    dragger_counts: Dict[str, List[float]] = {}
    for r in results:
        for kw, score in r.get("draggers", []):
            kw_lower = kw.lower()
            dragger_counts.setdefault(kw_lower, []).append(score)

    if not dragger_counts:
        return None

    sorted_draggers = sorted(
        dragger_counts.items(),
        key=lambda x: (-len(x[1]), sum(x[1]) / len(x[1])),
    )[:10]

    keywords = [d[0] for d in sorted_draggers]
    counts   = [len(d[1]) for d in sorted_draggers]

    fig = go.Figure(go.Bar(
        x=counts,
        y=keywords,
        orientation="h",
        marker_color="#DC2626",
        text=counts,
        textposition="outside",
        textfont=dict(size=11, color=NAVY),
    ))
    fig.update_layout(
        title=dict(
            text="Most Common Skill Gaps",
            font=dict(size=14, color=NAVY, family="Inter, Segoe UI, sans-serif"),
        ),
        xaxis_title="Number of Candidates",
        yaxis_title=None,
        yaxis=dict(autorange="reversed"),
        xaxis=dict(gridcolor=LIGHT_GREY, dtick=1),
        plot_bgcolor=BG_WHITE,
        paper_bgcolor=BG_WHITE,
        font=dict(family="Inter, Segoe UI, sans-serif", color=DARK_GREY, size=12),
        margin=dict(t=55, b=50, l=170, r=40),
        height=max(280, len(keywords) * 35 + 120),
        hoverlabel=dict(bgcolor=NAVY, font_color="white"),
    )
    return fig


def process_resumes(jd_text: str, uploaded_files: list) -> List[Dict[str, Any]]:
    """Run the full analysis pipeline on all uploaded resumes."""
    results = []
    jd_keywords = extract_jd_keywords(jd_text, top_n=20)

    total        = len(uploaded_files)
    progress_bar = st.progress(0)
    status_text  = st.empty()

    for idx, uploaded_file in enumerate(uploaded_files):
        filename = uploaded_file.name
        status_text.markdown(
            f'<p class="status-text">Processing {idx + 1} of {total}: {filename}</p>',
            unsafe_allow_html=True,
        )

        result = {
            "filename":       filename,
            "final_score":    0.0,
            "section_scores": {},
            "sections":       {},
            "boosters":       [],
            "draggers":       [],
            "error":          None,
        }

        try:
            text     = extract_text_from_pdf(uploaded_file)
            sections = split_into_sections(text)
            result["sections"] = sections

            section_scores           = compute_section_scores(jd_text, sections)
            result["section_scores"] = section_scores

            final_score           = compute_final_score(section_scores)
            result["final_score"] = final_score

            contributors       = get_score_contributors(jd_keywords, text, top_k=5)
            result["boosters"] = contributors["boosters"]
            result["draggers"] = contributors["draggers"]

        except ParserError as e:
            result["error"] = str(e)
        except Exception as e:
            result["error"] = f"Unexpected error: {e}"

        results.append(result)
        progress_bar.progress((idx + 1) / total)

    status_text.empty()
    progress_bar.empty()

    results.sort(key=lambda x: x["final_score"], reverse=True)
    return results


def render_sidebar():
    """Render the sidebar inputs and return (jd_text, uploaded_files, run_clicked)."""
    with st.sidebar:
        with st.container():
            st.markdown(
                '<div class="sb-header">'
                '<div class="sb-app-name">Resume Insight Engine</div>'
                '<div class="sb-app-tag">v1.0 &nbsp;&middot;&nbsp; AI-Powered Screening</div>'
                '</div>',
                unsafe_allow_html=True,
            )

        with st.container():
            st.markdown('<p class="sb-label">Job Description</p>', unsafe_allow_html=True)
            jd_text = st.text_area(
                "Job description",
                height=230,
                placeholder="Paste the full job description here...",
                label_visibility="collapsed",
            )
            st.markdown(
                '<p class="sb-hint">Include required skills, tools, and responsibilities for best results.</p>',
                unsafe_allow_html=True,
            )

        st.markdown('<hr class="sb-divider">', unsafe_allow_html=True)

        with st.container():
            st.markdown('<p class="sb-label">Resume PDFs</p>', unsafe_allow_html=True)
            uploaded_files = st.file_uploader(
                "Upload resume PDFs",
                type=["pdf"],
                accept_multiple_files=True,
                label_visibility="collapsed",
            )
            st.markdown(
                '<p class="sb-hint">Supports multiple PDFs. Max 5 MB per file.</p>',
                unsafe_allow_html=True,
            )

        st.markdown("<br>", unsafe_allow_html=True)
        run_clicked = st.button(
            "Run Analysis",
            type="primary",
            use_container_width=True,
        )

    return jd_text, uploaded_files, run_clicked


def render_header():
    """Render the page header."""
    with st.container():
        st.markdown(
            '<div class="page-header">'
            '<h1 class="page-title">Resume Insight Engine'
            '<span class="page-tag">AI-Powered</span>'
            '</h1>'
            '<p class="page-subtitle">'
            'Paste a job description, upload candidate resumes, and get instant ranked results with skill gap analysis.'
            '</p>'
            '</div>',
            unsafe_allow_html=True,
        )


def render_empty_state():
    """Render the getting-started view."""
    with st.container():
        st.markdown(
            '<div class="gs-wrap">'
            '<p class="gs-title">Ready to Screen Candidates</p>'
            '<p class="gs-desc">Complete the steps in the sidebar, then click Run Analysis.</p>'
            '<div class="gs-grid">'

            '<div class="gs-card">'
            '<div class="gs-num">1</div>'
            '<p class="gs-step-title">Paste Job Description</p>'
            '<p class="gs-step-desc">Add the full job description text in the left panel.</p>'
            '</div>'

            '<div class="gs-card">'
            '<div class="gs-num">2</div>'
            '<p class="gs-step-title">Upload Resumes</p>'
            '<p class="gs-step-desc">Upload one or more candidate PDF files.</p>'
            '</div>'

            '<div class="gs-card">'
            '<div class="gs-num">3</div>'
            '<p class="gs-step-title">Run Analysis</p>'
            '<p class="gs-step-desc">Click the Run Analysis button to start.</p>'
            '</div>'

            '<div class="gs-card">'
            '<div class="gs-num">4</div>'
            '<p class="gs-step-title">Review Results</p>'
            '<p class="gs-step-desc">View ranked scores, charts, and download reports.</p>'
            '</div>'

            '</div>'
            '<div class="gs-info">'
            '<strong>How scoring works:</strong>'
            '<ul>'
            '<li>Each resume is parsed into sections: Skills, Experience, Projects, Education, and Certifications</li>'
            '<li>Sections are embedded using a Sentence-Transformer model (all-MiniLM-L6-v2)</li>'
            '<li>Each section embedding is compared to the job description via cosine similarity</li>'
            '<li>Final score weights: Skills 45%, Experience 35%, Projects 10%, Education 8%, Certifications 2%</li>'
            '</ul>'
            '</div>'
            '</div>',
            unsafe_allow_html=True,
        )


def render_results(results: List[Dict[str, Any]]):
    """Render the full results view."""
    valid_results   = [r for r in results if r["error"] is None]
    errored_results = [r for r in results if r["error"] is not None]

    if valid_results:
        avg_score = sum(r["final_score"] for r in valid_results) / len(valid_results)
        top_score = max(r["final_score"] for r in valid_results)
        above_70  = sum(1 for r in valid_results if r["final_score"] >= 70)

        with st.container():
            col1, col2, col3, col4 = st.columns(4)
            with col1:
                st.markdown(
                    '<div class="metric-card">'
                    '<p class="metric-label">Candidates Analysed</p>'
                    f'<p class="metric-value">{len(valid_results)}</p>'
                    '</div>',
                    unsafe_allow_html=True,
                )
            with col2:
                st.markdown(
                    '<div class="metric-card">'
                    '<p class="metric-label">Average Score</p>'
                    f'<p class="metric-value">{avg_score:.1f}</p>'
                    '</div>',
                    unsafe_allow_html=True,
                )
            with col3:
                st.markdown(
                    '<div class="metric-card">'
                    '<p class="metric-label">Highest Score</p>'
                    f'<p class="metric-value">{top_score:.1f}</p>'
                    '</div>',
                    unsafe_allow_html=True,
                )
            with col4:
                st.markdown(
                    '<div class="metric-card">'
                    '<p class="metric-label">Strong Matches (70+)</p>'
                    f'<p class="metric-value">{above_70}</p>'
                    '</div>',
                    unsafe_allow_html=True,
                )

        st.markdown("<br>", unsafe_allow_html=True)

    for r in errored_results:
        st.markdown(
            f'<div class="card" style="border-color:#FCA5A5;">'
            f'<p class="card-header" style="color:#991B1B;">{r["filename"]}</p>'
            f'<p style="color:#991B1B; font-size:0.88rem;">{r["error"]}</p>'
            f'</div>',
            unsafe_allow_html=True,
        )

    if not valid_results:
        st.markdown(
            '<p class="validation-msg">No valid resumes could be processed.</p>',
            unsafe_allow_html=True,
        )
        return

    with st.container():
        st.markdown('<div class="sec-heading">Ranked Results</div>', unsafe_allow_html=True)
        st.markdown(build_results_table_html(valid_results), unsafe_allow_html=True)

        csv_data   = results_to_csv(valid_results)
        csv_anchor = _csv_download_anchor(csv_data, "resume_insight_results.csv", "Export as CSV")
        st.markdown(f"<br>{csv_anchor}", unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)

    with st.container():
        st.markdown('<div class="sec-heading">Score Analysis</div>', unsafe_allow_html=True)

        _modebar_cfg = {
            "modeBarButtonsToRemove": ["toImage"],
            "displaylogo": False,
        }
        chart_col1, chart_col2 = st.columns(2)
        with chart_col1:
            fig_scores = make_candidate_chart(valid_results)
            st.plotly_chart(fig_scores, use_container_width=True, config=_modebar_cfg)

        with chart_col2:
            fig_missing = make_missing_skills_chart(valid_results)
            if fig_missing:
                st.plotly_chart(fig_missing, use_container_width=True, config=_modebar_cfg)
            else:
                st.markdown('<p class="status-text">No skill gap data available.</p>', unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)

    with st.container():
        st.markdown('<div class="sec-heading">Candidate Details</div>', unsafe_allow_html=True)

        for rank, r in enumerate(valid_results, 1):
            badge_cls      = score_css_class(r["final_score"])
            rank_label     = f"#{rank}"
            expander_label = f"{rank_label}  {r['filename']}  --  Score: {r['final_score']:.1f} / 100"

            with st.expander(expander_label):
                detail_cols = st.columns(len(SECTION_ORDER))
                for col, section in zip(detail_cols, SECTION_ORDER):
                    val   = r["section_scores"].get(section, 0.0)
                    s_cls = score_css_class(val)
                    with col:
                        st.markdown(
                            f'<p class="metric-label">{SECTION_LABELS[section]}</p>'
                            f'<p><span class="score-badge {s_cls}">{val:.1f}</span></p>',
                            unsafe_allow_html=True,
                        )

                st.markdown("<br>", unsafe_allow_html=True)

                contrib_col1, contrib_col2 = st.columns(2)
                with contrib_col1:
                    st.markdown('<p class="contrib-header">Matched Skills</p>', unsafe_allow_html=True)
                    if r["boosters"]:
                        for kw, score in r["boosters"]:
                            st.markdown(
                                f'<p class="booster-item">+ {kw} &nbsp;<span style="color:#9CA3AF;font-size:0.78rem;">({score:.1f})</span></p>',
                                unsafe_allow_html=True,
                            )
                    else:
                        st.markdown('<p class="status-text">No data available.</p>', unsafe_allow_html=True)

                with contrib_col2:
                    st.markdown('<p class="contrib-header">Skill Gaps</p>', unsafe_allow_html=True)
                    if r["draggers"]:
                        for kw, score in r["draggers"]:
                            st.markdown(
                                f'<p class="dragger-item">- {kw} &nbsp;<span style="color:#9CA3AF;font-size:0.78rem;">({score:.1f})</span></p>',
                                unsafe_allow_html=True,
                            )
                    else:
                        st.markdown('<p class="status-text">No data available.</p>', unsafe_allow_html=True)

                st.markdown("<br>", unsafe_allow_html=True)
                safe_name = r["filename"].replace(".pdf", "").replace(" ", "_")
                state_key = f"report_pdf_{safe_name}"

                if state_key not in st.session_state:
                    if st.button("Generate Report", key=f"gen_report_{safe_name}"):
                        with st.spinner("Generating PDF report..."):
                            st.session_state[state_key] = generate_candidate_report(
                                candidate_name=r["filename"],
                                final_score=r["final_score"],
                                section_scores=r["section_scores"],
                                boosters=r["boosters"],
                                draggers=r["draggers"],
                            )
                        st.rerun()
                else:
                    pdf_anchor = _pdf_download_anchor(
                        st.session_state[state_key],
                        f"report_{safe_name}.pdf",
                        "Download Report PDF",
                    )
                    st.markdown(pdf_anchor, unsafe_allow_html=True)


def main():
    """Application entry point."""
    configure_page()
    render_header()

    jd_text, uploaded_files, run_clicked = render_sidebar()

    if "results" not in st.session_state:
        st.session_state.results = None

    if run_clicked:
        if not jd_text or not jd_text.strip():
            st.markdown(
                '<p class="validation-msg">Please paste a job description in the sidebar before running analysis.</p>',
                unsafe_allow_html=True,
            )
            return

        if not uploaded_files:
            st.markdown(
                '<p class="validation-msg">Please upload at least one resume PDF before running analysis.</p>',
                unsafe_allow_html=True,
            )
            return

        with st.spinner("Processing resumes..."):
            results = process_resumes(jd_text, uploaded_files)
        st.session_state.results = results

        for _k in [k for k in st.session_state if k.startswith("report_pdf_")]:
            del st.session_state[_k]

    if st.session_state.results:
        render_results(st.session_state.results)
    else:
        render_empty_state()


if __name__ == "__main__":
    main()

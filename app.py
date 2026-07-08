"""Resume Insight Engine - main Streamlit application."""

import os

# Prevent transformers from loading TensorFlow
os.environ.setdefault("TRANSFORMERS_NO_TF", "1")
os.environ.setdefault("USE_TF", "0")

import io
import csv
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

# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------
NAVY = "#1B2A4A"
DARK_GREY = "#4A4A4A"
MID_GREY = "#6B7280"
LIGHT_GREY = "#E5E7EB"
BG_WHITE = "#FFFFFF"
CARD_BG = "#F9FAFB"

SECTION_ORDER = ["skills", "experience", "projects", "education", "certifications"]
SECTION_LABELS = {
    "skills": "Skills",
    "experience": "Experience",
    "projects": "Projects",
    "education": "Education",
    "certifications": "Certifications",
}


# ---------------------------------------------------------------------------
# Page config and global styles
# ---------------------------------------------------------------------------
def configure_page():
    st.set_page_config(
        page_title="Resume Insight Engine",
        layout="wide",
        initial_sidebar_state="expanded",
    )

    st.markdown("""
    <style>
        /* Hide Streamlit chrome */
        #MainMenu {visibility: hidden;}
        footer {visibility: hidden;}
        header {visibility: hidden;}

        /* Global font */
        html, body, [class*="css"] {
            font-family: 'Inter', 'Segoe UI', sans-serif;
            color: #4A4A4A;
        }

        /* Page title */
        .main-title {
            color: #1B2A4A;
            font-size: 1.8rem;
            font-weight: 700;
            margin-bottom: 0.2rem;
            letter-spacing: -0.01em;
        }
        .main-subtitle {
            color: #6B7280;
            font-size: 0.95rem;
            margin-bottom: 1.5rem;
        }

        /* Sidebar styling */
        [data-testid="stSidebar"] {
            background-color: #F9FAFB;
            border-right: 1px solid #E5E7EB;
        }
        [data-testid="stSidebar"] .stMarkdown h2 {
            color: #1B2A4A;
            font-size: 1.1rem;
            font-weight: 600;
        }

        /* Card container */
        .card {
            border: 1px solid #E5E7EB;
            border-radius: 6px;
            padding: 1.2rem;
            margin-bottom: 1rem;
            background-color: #FFFFFF;
        }
        .card-header {
            color: #1B2A4A;
            font-size: 1rem;
            font-weight: 600;
            margin-bottom: 0.6rem;
        }

        /* Score badge */
        .score-badge {
            display: inline-block;
            padding: 0.25rem 0.75rem;
            border-radius: 4px;
            font-weight: 600;
            font-size: 0.9rem;
        }
        .score-high { background-color: #D1FAE5; color: #065F46; }
        .score-mid { background-color: #FEF3C7; color: #92400E; }
        .score-low { background-color: #FEE2E2; color: #991B1B; }

        /* Table styling */
        .results-table {
            width: 100%;
            border-collapse: collapse;
            font-size: 0.9rem;
        }
        .results-table th {
            background-color: #1B2A4A;
            color: #FFFFFF;
            padding: 0.6rem 0.8rem;
            text-align: left;
            font-weight: 600;
        }
        .results-table td {
            padding: 0.6rem 0.8rem;
            border-bottom: 1px solid #E5E7EB;
            color: #4A4A4A;
        }
        .results-table tr:hover td {
            background-color: #F3F4F6;
        }

        /* Metric label */
        .metric-label {
            color: #6B7280;
            font-size: 0.8rem;
            text-transform: uppercase;
            letter-spacing: 0.04em;
            margin-bottom: 0.15rem;
        }
        .metric-value {
            color: #1B2A4A;
            font-size: 1.4rem;
            font-weight: 700;
        }

        /* Section labels */
        .section-label {
            color: #1B2A4A;
            font-weight: 600;
            font-size: 0.95rem;
        }

        /* Contributor lists */
        .booster-item {
            color: #065F46;
            font-size: 0.88rem;
            padding: 0.2rem 0;
        }
        .dragger-item {
            color: #991B1B;
            font-size: 0.88rem;
            padding: 0.2rem 0;
        }

        /* Validation messages */
        .validation-msg {
            color: #991B1B;
            font-size: 0.9rem;
            padding: 0.5rem 0;
        }

        /* Status text */
        .status-text {
            color: #6B7280;
            font-size: 0.9rem;
        }

        /* Reduce default padding */
        .block-container {
            padding-top: 1.5rem;
        }
    </style>
    """, unsafe_allow_html=True)


# ---------------------------------------------------------------------------
# Helper functions
# ---------------------------------------------------------------------------
def score_css_class(score: float) -> str:
    if score >= 70:
        return "score-high"
    elif score >= 50:
        return "score-mid"
    return "score-low"


def build_results_table_html(results: List[Dict[str, Any]]) -> str:
    """Build an HTML table for the ranked results."""
    rows = ""
    for i, r in enumerate(results, 1):
        badge_cls = score_css_class(r["final_score"])
        section_cells = ""
        for s in SECTION_ORDER:
            val = r["section_scores"].get(s, 0.0)
            section_cells += f'<td style="text-align:center;">{val:.1f}</td>'

        rows += f"""
        <tr>
            <td style="text-align:center;">{i}</td>
            <td>{r["filename"]}</td>
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
                <th style="text-align:center; width:50px;">Rank</th>
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

    header = ["Rank", "Candidate", "Final Score"]
    header += [SECTION_LABELS[s] for s in SECTION_ORDER]
    writer.writerow(header)

    for i, r in enumerate(results, 1):
        row = [i, r["filename"], round(r["final_score"], 2)]
        row += [round(r["section_scores"].get(s, 0.0), 2) for s in SECTION_ORDER]
        writer.writerow(row)

    return output.getvalue()


def make_candidate_chart(results: List[Dict[str, Any]]) -> go.Figure:
    """Bar chart of candidate scores."""
    names = [r["filename"] for r in results]
    scores = [r["final_score"] for r in results]
    colors = [
        "#065F46" if s >= 70 else "#92400E" if s >= 50 else "#991B1B"
        for s in scores
    ]

    fig = go.Figure(go.Bar(
        x=names,
        y=scores,
        marker_color=colors,
        text=[f"{s:.1f}" for s in scores],
        textposition="outside",
        textfont=dict(size=12, color=NAVY),
    ))
    fig.update_layout(
        title=dict(text="Candidate Scores", font=dict(size=16, color=NAVY)),
        xaxis_title=None,
        yaxis_title="Score",
        yaxis=dict(range=[0, 105], gridcolor=LIGHT_GREY),
        plot_bgcolor=BG_WHITE,
        paper_bgcolor=BG_WHITE,
        font=dict(family="Inter, Segoe UI, sans-serif", color=DARK_GREY),
        margin=dict(t=50, b=40, l=50, r=20),
        height=350,
    )
    return fig


def make_missing_skills_chart(results: List[Dict[str, Any]]) -> go.Figure:
    """Bar chart of most commonly missing/weak skills across all resumes."""
    # Aggregate all draggers across candidates
    dragger_counts: Dict[str, List[float]] = {}
    for r in results:
        for kw, score in r.get("draggers", []):
            kw_lower = kw.lower()
            if kw_lower not in dragger_counts:
                dragger_counts[kw_lower] = []
            dragger_counts[kw_lower].append(score)

    if not dragger_counts:
        return None

    # Sort by frequency (how many candidates are missing this skill), then by avg weakness
    sorted_draggers = sorted(
        dragger_counts.items(),
        key=lambda x: (-len(x[1]), sum(x[1]) / len(x[1])),
    )[:10]

    keywords = [d[0] for d in sorted_draggers]
    counts = [len(d[1]) for d in sorted_draggers]

    fig = go.Figure(go.Bar(
        x=counts,
        y=keywords,
        orientation="h",
        marker_color="#991B1B",
        text=counts,
        textposition="outside",
        textfont=dict(size=12, color=NAVY),
    ))
    fig.update_layout(
        title=dict(
            text="Most Common Skill Gaps Across Candidates",
            font=dict(size=16, color=NAVY),
        ),
        xaxis_title="Number of Candidates",
        yaxis_title=None,
        yaxis=dict(autorange="reversed"),
        xaxis=dict(gridcolor=LIGHT_GREY, dtick=1),
        plot_bgcolor=BG_WHITE,
        paper_bgcolor=BG_WHITE,
        font=dict(family="Inter, Segoe UI, sans-serif", color=DARK_GREY),
        margin=dict(t=50, b=40, l=180, r=20),
        height=max(250, len(keywords) * 35 + 100),
    )
    return fig


# ---------------------------------------------------------------------------
# Processing pipeline
# ---------------------------------------------------------------------------
def process_resumes(
    jd_text: str,
    uploaded_files: list,
) -> List[Dict[str, Any]]:
    """Run the full analysis pipeline on all uploaded resumes."""
    results = []

    # Extract JD keywords once
    jd_keywords = extract_jd_keywords(jd_text, top_n=20)

    total = len(uploaded_files)
    progress_bar = st.progress(0)
    status_text = st.empty()

    for idx, uploaded_file in enumerate(uploaded_files):
        filename = uploaded_file.name
        status_text.markdown(
            f'<p class="status-text">Processing {idx + 1} of {total}: {filename}</p>',
            unsafe_allow_html=True,
        )

        result = {
            "filename": filename,
            "final_score": 0.0,
            "section_scores": {},
            "sections": {},
            "boosters": [],
            "draggers": [],
            "error": None,
        }

        try:
            # Extract text
            text = extract_text_from_pdf(uploaded_file)

            # Split into sections
            sections = split_into_sections(text)
            result["sections"] = sections

            # Compute section scores
            section_scores = compute_section_scores(jd_text, sections)
            result["section_scores"] = section_scores

            # Compute final weighted score
            final_score = compute_final_score(section_scores)
            result["final_score"] = final_score

            # Get score contributors
            contributors = get_score_contributors(jd_keywords, text, top_k=5)
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

    # Sort by final score descending
    results.sort(key=lambda x: x["final_score"], reverse=True)
    return results


# ---------------------------------------------------------------------------
# UI Components
# ---------------------------------------------------------------------------
def render_sidebar():
    """Render the sidebar inputs and return (jd_text, uploaded_files, run_clicked)."""
    with st.sidebar:
        st.markdown("## Job Description")
        jd_text = st.text_area(
            "Paste the job description below",
            height=250,
            placeholder="Paste the full job description here...",
            label_visibility="collapsed",
        )

        st.markdown("---")
        st.markdown("## Resume Upload")
        uploaded_files = st.file_uploader(
            "Upload resume PDFs",
            type=["pdf"],
            accept_multiple_files=True,
            label_visibility="collapsed",
        )

        st.markdown("---")
        run_clicked = st.button(
            "Run Analysis",
            type="primary",
            use_container_width=True,
        )

    return jd_text, uploaded_files, run_clicked


def render_header():
    """Render the page header."""
    st.markdown('<p class="main-title">Resume Insight Engine</p>', unsafe_allow_html=True)
    st.markdown(
        '<p class="main-subtitle">Upload resumes and a job description to generate '
        'scored rankings and skill gap analysis.</p>',
        unsafe_allow_html=True,
    )


def render_empty_state():
    """Render the empty state before any analysis has run."""
    st.markdown(
        '<div class="card">'
        '<p class="card-header">Getting Started</p>'
        '<p style="color: #6B7280; font-size: 0.9rem;">'
        '1. Paste a job description in the sidebar.<br>'
        '2. Upload one or more resume PDFs.<br>'
        '3. Click "Run Analysis" to generate results.'
        '</p></div>',
        unsafe_allow_html=True,
    )


def render_results(results: List[Dict[str, Any]]):
    """Render the full results view."""
    # Filter out errored results for charts/table, but show errors separately
    valid_results = [r for r in results if r["error"] is None]
    errored_results = [r for r in results if r["error"] is not None]

    # Summary metrics
    if valid_results:
        col1, col2, col3, col4 = st.columns(4)
        with col1:
            st.markdown(
                f'<p class="metric-label">Candidates Analysed</p>'
                f'<p class="metric-value">{len(valid_results)}</p>',
                unsafe_allow_html=True,
            )
        with col2:
            avg_score = sum(r["final_score"] for r in valid_results) / len(valid_results)
            st.markdown(
                f'<p class="metric-label">Average Score</p>'
                f'<p class="metric-value">{avg_score:.1f}</p>',
                unsafe_allow_html=True,
            )
        with col3:
            top_score = max(r["final_score"] for r in valid_results)
            st.markdown(
                f'<p class="metric-label">Highest Score</p>'
                f'<p class="metric-value">{top_score:.1f}</p>',
                unsafe_allow_html=True,
            )
        with col4:
            above_70 = sum(1 for r in valid_results if r["final_score"] >= 70)
            st.markdown(
                f'<p class="metric-label">Strong Matches (70+)</p>'
                f'<p class="metric-value">{above_70}</p>',
                unsafe_allow_html=True,
            )

        st.markdown("---")

    # Errors (if any)
    if errored_results:
        for r in errored_results:
            st.markdown(
                f'<div class="card" style="border-color: #FCA5A5;">'
                f'<p class="card-header" style="color: #991B1B;">{r["filename"]}</p>'
                f'<p style="color: #991B1B; font-size: 0.9rem;">{r["error"]}</p>'
                f'</div>',
                unsafe_allow_html=True,
            )

    if not valid_results:
        st.markdown(
            '<p class="validation-msg">No valid resumes could be processed.</p>',
            unsafe_allow_html=True,
        )
        return

    # Ranked results table
    st.markdown(
        '<p class="section-label" style="font-size: 1.1rem; margin-bottom: 0.6rem;">'
        'Ranked Results</p>',
        unsafe_allow_html=True,
    )
    table_html = build_results_table_html(valid_results)
    st.markdown(table_html, unsafe_allow_html=True)

    # CSV export
    csv_data = results_to_csv(valid_results)
    st.download_button(
        label="Export Results as CSV",
        data=csv_data,
        file_name="resume_insight_results.csv",
        mime="text/csv",
    )

    st.markdown("---")

    # Charts
    chart_col1, chart_col2 = st.columns(2)
    with chart_col1:
        fig_scores = make_candidate_chart(valid_results)
        st.plotly_chart(fig_scores, use_container_width=True)

    with chart_col2:
        fig_missing = make_missing_skills_chart(valid_results)
        if fig_missing:
            st.plotly_chart(fig_missing, use_container_width=True)
        else:
            st.markdown(
                '<p class="status-text">No skill gap data available.</p>',
                unsafe_allow_html=True,
            )

    st.markdown("---")

    # Per-candidate detail views
    st.markdown(
        '<p class="section-label" style="font-size: 1.1rem; margin-bottom: 0.6rem;">'
        'Candidate Details</p>',
        unsafe_allow_html=True,
    )

    for r in valid_results:
        badge_cls = score_css_class(r["final_score"])
        with st.expander(f'{r["filename"]}  --  Score: {r["final_score"]:.1f}'):
            # Section score breakdown
            detail_cols = st.columns(len(SECTION_ORDER))
            for col, section in zip(detail_cols, SECTION_ORDER):
                val = r["section_scores"].get(section, 0.0)
                s_cls = score_css_class(val)
                with col:
                    st.markdown(
                        f'<p class="metric-label">{SECTION_LABELS[section]}</p>'
                        f'<p><span class="score-badge {s_cls}">{val:.1f}</span></p>',
                        unsafe_allow_html=True,
                    )

            st.markdown("<br>", unsafe_allow_html=True)

            # Boosters and draggers
            contrib_col1, contrib_col2 = st.columns(2)
            with contrib_col1:
                st.markdown(
                    '<p class="section-label">Matched Skills (Boosters)</p>',
                    unsafe_allow_html=True,
                )
                if r["boosters"]:
                    for kw, score in r["boosters"]:
                        st.markdown(
                            f'<p class="booster-item">'
                            f'+ {kw} ({score:.1f})</p>',
                            unsafe_allow_html=True,
                        )
                else:
                    st.markdown(
                        '<p class="status-text">No data available.</p>',
                        unsafe_allow_html=True,
                    )

            with contrib_col2:
                st.markdown(
                    '<p class="section-label">Skill Gaps (Draggers)</p>',
                    unsafe_allow_html=True,
                )
                if r["draggers"]:
                    for kw, score in r["draggers"]:
                        st.markdown(
                            f'<p class="dragger-item">'
                            f'- {kw} ({score:.1f})</p>',
                            unsafe_allow_html=True,
                        )
                else:
                    st.markdown(
                        '<p class="status-text">No data available.</p>',
                        unsafe_allow_html=True,
                    )

            # Download Report button
            st.markdown("<br>", unsafe_allow_html=True)
            safe_name = r["filename"].replace(".pdf", "").replace(" ", "_")
            report_pdf = generate_candidate_report(
                candidate_name=r["filename"],
                final_score=r["final_score"],
                section_scores=r["section_scores"],
                boosters=r["boosters"],
                draggers=r["draggers"],
            )
            st.download_button(
                label="Download Report",
                data=report_pdf,
                file_name=f"report_{safe_name}.pdf",
                mime="application/pdf",
                key=f"report_{safe_name}",
            )


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------
def main():
    configure_page()
    render_header()

    jd_text, uploaded_files, run_clicked = render_sidebar()

    # Session state for persisting results across reruns
    if "results" not in st.session_state:
        st.session_state.results = None

    if run_clicked:
        # Validation
        if not jd_text or not jd_text.strip():
            st.markdown(
                '<p class="validation-msg">'
                'Please paste a job description in the sidebar before running analysis.'
                '</p>',
                unsafe_allow_html=True,
            )
            return

        if not uploaded_files:
            st.markdown(
                '<p class="validation-msg">'
                'Please upload at least one resume PDF before running analysis.'
                '</p>',
                unsafe_allow_html=True,
            )
            return

        # Run pipeline
        with st.spinner("Processing resumes..."):
            results = process_resumes(jd_text, uploaded_files)
        st.session_state.results = results

    # Render results if available
    if st.session_state.results:
        render_results(st.session_state.results)
    else:
        render_empty_state()


if __name__ == "__main__":
    main()

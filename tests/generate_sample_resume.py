"""Generate a sample resume PDF for testing purposes."""

from fpdf import FPDF
import os


def create_sample_resume(output_path: str) -> None:
    """Create a minimal but realistic sample resume PDF."""

    pdf = FPDF()
    pdf.set_auto_page_break(auto=True, margin=15)
    pdf.add_page()

    pdf.set_font("Helvetica", "B", 18)
    pdf.cell(0, 12, "Jane Doe", ln=True, align="C")
    pdf.set_font("Helvetica", "", 10)
    pdf.cell(0, 6, "jane.doe@email.com | (555) 123-4567 | San Francisco, CA", ln=True, align="C")
    pdf.ln(8)

    def section_header(title: str):
        pdf.set_font("Helvetica", "B", 13)
        pdf.cell(0, 10, title, ln=True)
        pdf.set_draw_color(27, 42, 74)
        pdf.line(10, pdf.get_y(), 200, pdf.get_y())
        pdf.ln(3)
        pdf.set_font("Helvetica", "", 10)

    section_header("Skills")
    pdf.multi_cell(0, 5,
        "Python, Java, SQL, JavaScript, TypeScript, React, Node.js, "
        "Django, Flask, PostgreSQL, MongoDB, Docker, Kubernetes, AWS, "
        "Git, CI/CD, REST APIs, GraphQL, Machine Learning, pandas, "
        "scikit-learn, TensorFlow, Agile/Scrum"
    )
    pdf.ln(4)

    section_header("Experience")
    pdf.set_font("Helvetica", "B", 11)
    pdf.cell(0, 6, "Senior Software Engineer - Acme Corp", ln=True)
    pdf.set_font("Helvetica", "I", 9)
    pdf.cell(0, 5, "Jan 2021 - Present | San Francisco, CA", ln=True)
    pdf.set_font("Helvetica", "", 10)
    pdf.multi_cell(0, 5,
        "Led a team of 5 engineers to redesign the core data pipeline, "
        "reducing processing time by 40%. Designed and implemented RESTful "
        "APIs serving 2M requests per day. Introduced automated testing "
        "practices that improved code coverage from 45% to 88%."
    )
    pdf.ln(3)

    pdf.set_font("Helvetica", "B", 11)
    pdf.cell(0, 6, "Software Engineer - Beta Inc", ln=True)
    pdf.set_font("Helvetica", "I", 9)
    pdf.cell(0, 5, "Jun 2018 - Dec 2020 | New York, NY", ln=True)
    pdf.set_font("Helvetica", "", 10)
    pdf.multi_cell(0, 5,
        "Developed full-stack web applications using React and Django. "
        "Built a recommendation engine using collaborative filtering that "
        "increased user engagement by 25%. Managed PostgreSQL databases "
        "with 50M+ records and optimised query performance."
    )
    pdf.ln(4)

    section_header("Education")
    pdf.set_font("Helvetica", "B", 11)
    pdf.cell(0, 6, "B.S. Computer Science - University of California, Berkeley", ln=True)
    pdf.set_font("Helvetica", "I", 9)
    pdf.cell(0, 5, "Graduated May 2018 | GPA: 3.7/4.0", ln=True)
    pdf.set_font("Helvetica", "", 10)
    pdf.multi_cell(0, 5,
        "Relevant coursework: Data Structures, Algorithms, Machine Learning, "
        "Database Systems, Operating Systems, Computer Networks."
    )
    pdf.ln(4)

    section_header("Projects")
    pdf.set_font("Helvetica", "B", 11)
    pdf.cell(0, 6, "Open Source Analytics Dashboard", ln=True)
    pdf.set_font("Helvetica", "", 10)
    pdf.multi_cell(0, 5,
        "Built a real-time analytics dashboard using Plotly Dash and "
        "PostgreSQL. The project has 1.2k stars on GitHub and is used by "
        "several small businesses for sales tracking."
    )
    pdf.ln(4)

    section_header("Certifications")
    pdf.multi_cell(0, 5,
        "AWS Certified Solutions Architect - Associate (2023)\n"
        "Google Professional Data Engineer (2022)\n"
        "Certified Kubernetes Administrator (2021)"
    )

    pdf.output(output_path)


if __name__ == "__main__":
    out_dir = os.path.join(os.path.dirname(__file__), "..", "test_artifacts")
    os.makedirs(out_dir, exist_ok=True)
    out = os.path.normpath(os.path.join(out_dir, "sample_resume.pdf"))
    create_sample_resume(out)
    print(f"Sample resume created at: {out}")

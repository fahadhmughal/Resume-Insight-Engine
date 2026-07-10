"""Generate multiple sample resume PDFs with different profiles for testing."""

import os
import sys

PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
sys.path.insert(0, PROJECT_ROOT)

from fpdf import FPDF


def create_resume(output_path: str, profile: dict) -> None:
    """Create a resume PDF from a profile dictionary."""
    pdf = FPDF()
    pdf.set_auto_page_break(auto=True, margin=15)
    pdf.add_page()

    pdf.set_font("Helvetica", "B", 18)
    pdf.cell(0, 12, profile["name"], ln=True, align="C")
    pdf.set_font("Helvetica", "", 10)
    pdf.cell(0, 6, profile["contact"], ln=True, align="C")
    pdf.ln(8)

    def section_header(title: str):
        pdf.set_font("Helvetica", "B", 13)
        pdf.cell(0, 10, title, ln=True)
        pdf.set_draw_color(27, 42, 74)
        pdf.line(10, pdf.get_y(), 200, pdf.get_y())
        pdf.ln(3)
        pdf.set_font("Helvetica", "", 10)

    for section_title, content in profile["sections"]:
        section_header(section_title)
        if isinstance(content, list):
            for item in content:
                if isinstance(item, dict):
                    pdf.set_font("Helvetica", "B", 11)
                    pdf.cell(0, 6, item.get("title", ""), ln=True)
                    if "subtitle" in item:
                        pdf.set_font("Helvetica", "I", 9)
                        pdf.cell(0, 5, item["subtitle"], ln=True)
                    pdf.set_font("Helvetica", "", 10)
                    pdf.multi_cell(0, 5, item.get("body", ""))
                    pdf.ln(2)
                else:
                    pdf.multi_cell(0, 5, str(item))
        else:
            pdf.multi_cell(0, 5, str(content))
        pdf.ln(4)

    pdf.output(output_path)


PROFILES = [
    {
        "name": "Alice Chen",
        "contact": "alice.chen@email.com | (555) 100-0001 | San Francisco, CA",
        "sections": [
            ("Skills", "Python, SQL, Apache Spark, Apache Airflow, Snowflake, "
             "BigQuery, AWS (S3, Glue, Redshift, Lambda), Docker, Kubernetes, "
             "Terraform, dbt, Kafka, PostgreSQL, data modelling, ETL, CI/CD, Git"),
            ("Experience", [
                {
                    "title": "Senior Data Engineer - DataScale Inc",
                    "subtitle": "Mar 2021 - Present | San Francisco, CA",
                    "body": ("Architected a real-time data pipeline processing 800M events/day "
                             "using Kafka and Spark Structured Streaming on AWS. Migrated legacy "
                             "ETL to Airflow with 99.9% SLA. Reduced Snowflake costs by 35% "
                             "through query optimisation and clustering strategies."),
                },
                {
                    "title": "Data Engineer - CloudFirst",
                    "subtitle": "Jun 2018 - Feb 2021 | Seattle, WA",
                    "body": ("Built batch and streaming pipelines for a 50TB data warehouse. "
                             "Implemented data quality checks with Great Expectations. Managed "
                             "infrastructure with Terraform and Docker on AWS ECS."),
                },
            ]),
            ("Education", [
                {
                    "title": "M.S. Computer Science - University of Washington",
                    "subtitle": "Graduated 2018 | Focus: Distributed Systems",
                    "body": "",
                },
            ]),
            ("Projects", "Open-source dbt package for Snowflake cost monitoring. "
             "500+ GitHub stars. Used by 30+ companies for warehouse spend tracking."),
            ("Certifications", "AWS Certified Data Analytics - Specialty (2023)\n"
             "Snowflake SnowPro Core Certification (2022)"),
        ],
    },
    {
        "name": "Bob Martinez",
        "contact": "bob.martinez@email.com | (555) 200-0002 | Austin, TX",
        "sections": [
            ("Skills", "Python, R, SQL, TensorFlow, PyTorch, scikit-learn, pandas, "
             "NumPy, Spark MLlib, Airflow, Docker, AWS SageMaker, Tableau, "
             "statistical modelling, A/B testing, NLP, computer vision"),
            ("Experience", [
                {
                    "title": "Senior Data Scientist - PredictCo",
                    "subtitle": "Jan 2020 - Present | Austin, TX",
                    "body": ("Built and deployed ML models for customer churn prediction, "
                             "achieving 92% AUC. Designed A/B testing framework used across "
                             "5 product teams. Led NLP project for automated support ticket "
                             "classification reducing manual triage by 60%."),
                },
                {
                    "title": "Data Scientist - AnalytiCorp",
                    "subtitle": "Aug 2017 - Dec 2019 | Chicago, IL",
                    "body": ("Developed recommendation engine using collaborative filtering. "
                             "Built time-series forecasting models for demand planning. "
                             "Created executive dashboards in Tableau."),
                },
            ]),
            ("Education", [
                {
                    "title": "Ph.D. Statistics - University of Texas at Austin",
                    "subtitle": "Graduated 2017 | Dissertation: Bayesian Methods for Time Series",
                    "body": "",
                },
            ]),
            ("Projects", "Kaggle Grandmaster (top 100). Published 3 NLP research papers. "
             "Contributor to scikit-learn open source project."),
            ("Certifications", "Google Professional Machine Learning Engineer (2022)"),
        ],
    },
    {
        "name": "Carol Nguyen",
        "contact": "carol.nguyen@email.com | (555) 300-0003 | New York, NY",
        "sections": [
            ("Skills", "JavaScript, TypeScript, React, Next.js, Node.js, GraphQL, "
             "PostgreSQL, MongoDB, Redis, Docker, AWS, Vercel, Tailwind CSS, "
             "HTML, CSS, Figma, Jest, Cypress"),
            ("Experience", [
                {
                    "title": "Senior Frontend Engineer - DesignTech",
                    "subtitle": "Feb 2021 - Present | New York, NY",
                    "body": ("Led frontend architecture for a SaaS platform serving 200k users. "
                             "Built design system with 40+ reusable React components. Improved "
                             "Lighthouse score from 52 to 95. Mentored 3 junior engineers."),
                },
                {
                    "title": "Full-Stack Developer - WebAgency",
                    "subtitle": "May 2018 - Jan 2021 | Brooklyn, NY",
                    "body": ("Developed client websites using Next.js and Node.js. "
                             "Built REST and GraphQL APIs. Managed PostgreSQL and MongoDB "
                             "databases."),
                },
            ]),
            ("Education", [
                {
                    "title": "B.S. Computer Science - NYU",
                    "subtitle": "Graduated 2018 | Dean's List",
                    "body": "",
                },
            ]),
            ("Projects", "Open-source React component library with 2k GitHub stars. "
             "Personal blog built with Next.js, 50k monthly readers."),
            ("Certifications", ""),
        ],
    },
    {
        "name": "David Kim",
        "contact": "david.kim@email.com | (555) 400-0004 | Denver, CO",
        "sections": [
            ("Skills", "Python, SQL, dbt, Snowflake, Fivetran, Airflow, Looker, "
             "Tableau, Git, AWS, data modelling, ETL, analytics engineering"),
            ("Experience", [
                {
                    "title": "Analytics Engineer - MetricsDash",
                    "subtitle": "Jun 2022 - Present | Denver, CO",
                    "body": ("Built and maintained 200+ dbt models powering company analytics. "
                             "Designed dimensional data models for the Snowflake warehouse. "
                             "Created self-serve Looker dashboards used by 150+ stakeholders."),
                },
                {
                    "title": "Data Analyst - RetailGroup",
                    "subtitle": "Jan 2020 - May 2022 | Denver, CO",
                    "body": ("Wrote complex SQL queries for sales and inventory analysis. "
                             "Built Tableau dashboards for executive reporting. Automated "
                             "weekly reports using Python scripts."),
                },
            ]),
            ("Education", [
                {
                    "title": "B.A. Economics - University of Colorado Boulder",
                    "subtitle": "Graduated 2019",
                    "body": "",
                },
            ]),
            ("Projects", ""),
            ("Certifications", "dbt Analytics Engineering Certification (2023)"),
        ],
    },
    {
        "name": "Elena Petrova",
        "contact": "elena.petrova@email.com | (555) 500-0005 | Boston, MA",
        "sections": [
            ("Skills", "Python, Java, Scala, SQL, Apache Spark, Kafka, Flink, "
             "Hadoop, Hive, Airflow, Docker, Kubernetes, Terraform, AWS, GCP, "
             "PostgreSQL, Cassandra, data lake architecture, stream processing"),
            ("Experience", [
                {
                    "title": "Staff Data Engineer - BigDataCorp",
                    "subtitle": "Apr 2019 - Present | Boston, MA",
                    "body": ("Designed and built a petabyte-scale data lake on AWS S3 with "
                             "Delta Lake. Led migration from Hadoop to Spark on Kubernetes, "
                             "reducing infrastructure costs by 45%. Architected real-time "
                             "streaming platform processing 2B events/day using Kafka and Flink."),
                },
                {
                    "title": "Data Engineer - TechGiant",
                    "subtitle": "Jul 2016 - Mar 2019 | San Jose, CA",
                    "body": ("Maintained Hadoop/Hive data warehouse. Built ETL pipelines "
                             "with Spark and Airflow. Optimised Cassandra cluster performance "
                             "for low-latency serving."),
                },
            ]),
            ("Education", [
                {
                    "title": "M.S. Computer Engineering - MIT",
                    "subtitle": "Graduated 2016",
                    "body": "Focus: Large-scale distributed systems and data processing.",
                },
            ]),
            ("Projects", "Apache Spark contributor (50+ commits). Speaker at Data "
             "Engineering Summit 2023. Author of a technical blog on stream processing "
             "with 10k subscribers."),
            ("Certifications", "AWS Certified Solutions Architect - Professional (2022)\n"
             "Google Professional Data Engineer (2021)\n"
             "Certified Kubernetes Administrator (2020)"),
        ],
    },
]


def main():
    output_dir = os.path.join(PROJECT_ROOT, "test_artifacts")
    os.makedirs(output_dir, exist_ok=True)

    for profile in PROFILES:
        safe_name = profile["name"].lower().replace(" ", "_")
        filename = f"resume_{safe_name}.pdf"
        path = os.path.join(output_dir, filename)
        create_resume(path, profile)
        print(f"Created: {path}")

    print(f"\nGenerated {len(PROFILES)} sample resumes in {output_dir}")


if __name__ == "__main__":
    main()

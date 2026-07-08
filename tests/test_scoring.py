"""Test script for the scoring engine (hardcoded inputs, no PDF needed)."""

import os
import sys

PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
sys.path.insert(0, PROJECT_ROOT)

from core.scoring_engine import compute_section_scores, compute_final_score


# ---------------------------------------------------------------------------
# Hardcoded test data
# ---------------------------------------------------------------------------

SAMPLE_JD = """
Senior Data Engineer

We are seeking a Senior Data Engineer to build and maintain scalable data
infrastructure. You will design data pipelines, work with large-scale
distributed systems, and collaborate closely with data scientists and
analysts.

Responsibilities:
- Design and build reliable, scalable ETL and ELT data pipelines
- Manage data warehouses (Snowflake, BigQuery, Redshift)
- Implement data quality monitoring and alerting
- Optimise query performance across petabyte-scale datasets
- Collaborate with machine learning engineers on feature stores

Requirements:
- 5+ years of experience in data engineering
- Proficiency in Python and SQL
- Experience with Apache Spark, Airflow, or similar tools
- Hands-on experience with cloud platforms (AWS, GCP, or Azure)
- Strong understanding of data modelling and database design
- Familiarity with Docker, Kubernetes, and CI/CD practices
"""

SAMPLE_RESUME_SECTIONS = {
    "skills": (
        "Python, SQL, Java, Scala, Apache Spark, Apache Airflow, "
        "PostgreSQL, Snowflake, BigQuery, AWS (S3, Glue, Redshift, Lambda), "
        "Docker, Kubernetes, Terraform, Git, CI/CD, dbt, Kafka, "
        "data modelling, ETL pipeline design"
    ),
    "experience": (
        "Data Engineer at TechCorp (2020 - Present). "
        "Built and maintained production ETL pipelines processing 500M+ "
        "records daily using Apache Spark and Airflow on AWS. Migrated the "
        "data warehouse from on-prem PostgreSQL to Snowflake, reducing "
        "query latency by 60%. Implemented data quality checks with Great "
        "Expectations, reducing data incidents by 75%. "
        "Junior Data Engineer at DataStart (2018 - 2020). "
        "Developed Python-based ingestion scripts for REST API data sources. "
        "Managed PostgreSQL databases and wrote complex analytical queries."
    ),
    "projects": (
        "Open-source streaming pipeline: Built a real-time event processing "
        "pipeline using Kafka and Apache Flink, handling 100k events/sec. "
        "Published on GitHub with 800+ stars."
    ),
    "education": (
        "M.S. Computer Science, Stanford University (2018). "
        "B.S. Computer Engineering, University of Michigan (2016). "
        "Coursework: Distributed Systems, Database Systems, Machine Learning."
    ),
    "certifications": "",  # intentionally empty to test weight redistribution
}


def main():
    print("Computing section scores...\n")

    section_scores = compute_section_scores(SAMPLE_JD, SAMPLE_RESUME_SECTIONS)

    print(f"{'Section':<20} {'Score':>8}")
    print("-" * 30)
    for section in ["skills", "experience", "projects", "education", "certifications"]:
        score = section_scores.get(section, 0.0)
        print(f"{section:<20} {score:>8.2f}")

    final_score = compute_final_score(section_scores)
    print(f"\n{'Final Score':<20} {final_score:>8.2f}")

    # Sanity checks
    for section, score in section_scores.items():
        assert 0.0 <= score <= 100.0, (
            f"{section} score {score} is outside [0, 100] range."
        )
    assert 0.0 <= final_score <= 100.0, (
        f"Final score {final_score} is outside [0, 100] range."
    )
    assert section_scores["certifications"] == 0.0, (
        "Certifications should be 0 (empty section)."
    )

    print("\nAll checks passed.")


if __name__ == "__main__":
    main()

"""Test script for the score explainer (keyword-level similarity attribution)."""

import os
import sys

PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
sys.path.insert(0, PROJECT_ROOT)

from core.explainer import get_score_contributors


SAMPLE_JD_KEYWORDS = [
    ("python programming", 0.68),
    ("data pipelines", 0.65),
    ("machine learning models", 0.60),
    ("sql databases", 0.58),
    ("apache spark", 0.55),
    ("docker kubernetes", 0.52),
    ("aws cloud", 0.50),
    ("react frontend", 0.45),
    ("ios swift development", 0.42),
    ("graphic design", 0.40),
    ("data warehousing", 0.48),
    ("etl processing", 0.47),
    ("agile scrum methodology", 0.38),
    ("blockchain smart contracts", 0.35),
    ("embedded systems firmware", 0.30),
]

SAMPLE_RESUME_TEXT = """
Senior Data Engineer with 6 years of experience building production data
pipelines and analytics infrastructure.

Skills: Python, SQL, Java, Scala, Apache Spark, Apache Airflow,
PostgreSQL, Snowflake, BigQuery, AWS (S3, Glue, Redshift, Lambda),
Docker, Kubernetes, Terraform, Git, CI/CD, dbt, Kafka, data modelling,
ETL pipeline design, machine learning feature engineering.

Experience: Built and maintained production ETL pipelines processing
500M+ records daily using Apache Spark and Airflow on AWS. Migrated
data warehouse from on-prem PostgreSQL to Snowflake. Implemented data
quality monitoring with Great Expectations. Developed Python-based
ingestion scripts for REST API data sources.

Education: M.S. Computer Science, Stanford University.
"""


def main():
    print("Computing keyword-level similarity attribution...\n")

    result = get_score_contributors(
        jd_keywords=SAMPLE_JD_KEYWORDS,
        resume_text=SAMPLE_RESUME_TEXT,
        top_k=5,
    )

    print(f"{'BOOSTERS (well-represented in resume)'}")
    print(f"{'Keyword':<35} {'Similarity':>10}")
    print("-" * 47)
    for keyword, score in result["boosters"]:
        print(f"{keyword:<35} {score:>10.2f}")

    print()

    print(f"{'DRAGGERS (weak or missing in resume)'}")
    print(f"{'Keyword':<35} {'Similarity':>10}")
    print("-" * 47)
    for keyword, score in result["draggers"]:
        print(f"{keyword:<35} {score:>10.2f}")

    assert len(result["boosters"]) == 5, "Should return exactly 5 boosters."
    assert len(result["draggers"]) == 5, "Should return exactly 5 draggers."

    min_booster = min(s for _, s in result["boosters"])
    max_dragger = max(s for _, s in result["draggers"])
    assert min_booster > max_dragger, (
        f"Lowest booster ({min_booster}) should exceed "
        f"highest dragger ({max_dragger})."
    )

    all_scores = [s for _, s in result["boosters"]] + [s for _, s in result["draggers"]]
    for s in all_scores:
        assert 0.0 <= s <= 100.0, f"Score {s} is outside [0, 100] range."

    print("\nAll checks passed.")


if __name__ == "__main__":
    main()

"""Test script for JD keyword extraction."""

import os
import sys

PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
sys.path.insert(0, PROJECT_ROOT)

from core.jd_extractor import extract_jd_keywords


SAMPLE_JD = """
Data Scientist

Location: San Francisco, CA
Department: Analytics and Machine Learning

About the Role:

We are looking for a Data Scientist to join our analytics team. You will
work closely with product managers and engineers to design, build, and
deploy machine learning models that drive business decisions across the
organisation. The ideal candidate has strong experience with statistical
modelling, data pipelines, and communicating results to non-technical
stakeholders.

Responsibilities:

- Develop and deploy machine learning models for classification,
  regression, and clustering problems
- Build and maintain scalable data pipelines using Python, SQL, and
  Apache Spark
- Perform exploratory data analysis on large datasets to identify trends
  and actionable insights
- Design and run A/B tests and analyse experimental results with
  statistical rigour
- Collaborate with engineering to integrate models into production
  systems via REST APIs
- Create dashboards and reports using Tableau or similar BI tools
- Mentor junior analysts and contribute to internal knowledge sharing

Requirements:

- M.S. or Ph.D. in Computer Science, Statistics, Mathematics, or a
  related quantitative field
- 3+ years of professional experience in a data science or machine
  learning role
- Proficiency in Python and its data ecosystem: pandas, NumPy,
  scikit-learn, TensorFlow or PyTorch
- Strong SQL skills and experience working with data warehouses such as
  Snowflake, BigQuery, or Redshift
- Experience building and deploying end-to-end ML pipelines
- Familiarity with cloud platforms (AWS, GCP, or Azure)
- Excellent written and verbal communication skills
- Experience with version control (Git) and CI/CD practices

Nice to Have:

- Experience with natural language processing or computer vision
- Knowledge of causal inference and Bayesian methods
- Contributions to open source projects
- Experience with Docker and Kubernetes for model serving
"""


def main():
    print("Extracting keyphrases from sample Data Scientist job description...\n")

    keywords = extract_jd_keywords(SAMPLE_JD, top_n=20)

    print(f"{'Rank':<6} {'Keyphrase':<40} {'Score':<8}")
    print("-" * 54)
    for i, (phrase, score) in enumerate(keywords, start=1):
        print(f"{i:<6} {phrase:<40} {score:.4f}")

    print(f"\nTotal keyphrases returned: {len(keywords)}")

    # Basic sanity checks
    assert len(keywords) > 0, "Should return at least one keyphrase."
    assert len(keywords) <= 20, "Should return at most 20 keyphrases."

    phrases_lower = [p.lower() for p, _ in keywords]
    # Scores should be in descending order
    scores = [s for _, s in keywords]
    assert scores == sorted(scores, reverse=True), "Scores should be in descending order."

    print("All checks passed.")


if __name__ == "__main__":
    main()

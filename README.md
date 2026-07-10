# Resume Insight Engine

An AI-powered resume screening application built with Streamlit. Paste a job description, upload candidate resumes in PDF format, and get instant ranked results with detailed skill gap analysis.

---

## Table of Contents

- [Features](#features)
- [How It Works](#how-it-works)
- [Scoring Methodology](#scoring-methodology)
- [Technology Stack](#technology-stack)
- [Project Structure](#project-structure)
- [Prerequisites](#prerequisites)
- [Installation](#installation)
- [Running the Application](#running-the-application)
- [Usage Guide](#usage-guide)
- [Running Tests](#running-tests)
- [Deployment](#deployment)
- [Configuration](#configuration)
- [License](#license)

---

## Features

- **Job Description Analysis** -- Extracts key skills and requirements from any job description using KeyBERT
- **Multi-Resume Upload** -- Upload and analyse multiple candidate resumes simultaneously (PDF format)
- **AI-Powered Scoring** -- Computes per-section similarity scores using Sentence-Transformer embeddings
- **Ranked Results Table** -- Candidates ranked by weighted composite score with per-section breakdowns
- **Skill Gap Identification** -- Identifies matched skills (boosters) and missing skills (draggers) for each candidate
- **Interactive Charts** -- Visual bar charts for candidate comparison and most common skill gaps
- **PDF Report Generation** -- Generate downloadable single-page PDF reports for individual candidates
- **CSV Export** -- Export ranked results to CSV for further analysis
- **Weight Redistribution** -- Handles missing resume sections gracefully by redistributing weights

---

## How It Works

1. **Paste a Job Description** -- The job description text is analysed to extract the most relevant keyphrases using KeyBERT with Maximal Marginal Relevance for diversity
2. **Upload Resume PDFs** -- Each resume is parsed from PDF using pdfplumber and split into canonical sections (Skills, Experience, Projects, Education, Certifications) via header keyword matching
3. **Embedding and Scoring** -- Both the job description and each resume section are embedded using the `all-MiniLM-L6-v2` Sentence-Transformer model. Cosine similarity between embeddings produces a 0-100 score per section
4. **Final Score Computation** -- Section scores are combined using weighted averaging. Missing sections have their weights redistributed across present sections
5. **Skill Attribution** -- Individual JD keywords are embedded and compared against the full resume embedding to identify the strongest matches (boosters) and weakest matches (draggers)

---

## Scoring Methodology

### Section Weights

| Section        | Weight |
|----------------|--------|
| Skills         | 45%    |
| Experience     | 35%    |
| Projects       | 10%    |
| Education      | 8%     |
| Certifications | 2%     |

### Score Ranges

| Range    | Classification |
|----------|----------------|
| 70 - 100 | Strong Match   |
| 50 - 69  | Moderate Match |
| 0 - 49   | Weak Match     |

### Weight Redistribution

When a section is not found in a resume (score of 0), its weight is redistributed proportionally across the remaining present sections. This prevents candidates from being unfairly penalised for resumes that do not include every section.

**Example:** If Certifications (2%) and Projects (10%) are missing, the remaining weights (Skills 45%, Experience 35%, Education 8% = 88% total) are each scaled by `1.0 / 0.88` so they sum to 100%.

---

## Technology Stack

| Component            | Technology                                               |
|----------------------|----------------------------------------------------------|
| Web Framework        | Streamlit                                                |
| PDF Parsing          | pdfplumber                                               |
| NLP (Section Split)  | spaCy (en_core_web_sm)                                   |
| Keyword Extraction   | KeyBERT                                                  |
| Sentence Embeddings  | sentence-transformers (all-MiniLM-L6-v2)                 |
| Scoring              | cosine similarity (NumPy)                                |
| Charts               | Plotly                                                   |
| PDF Reports          | fpdf2                                                    |
| Data Handling        | pandas                                                   |

---

## Project Structure

```
resume-insight-engine/
├── app.py                          Main Streamlit application
├── core/
│   ├── __init__.py                 Package exports
│   ├── parser.py                   PDF text extraction and validation
│   ├── section_splitter.py         Resume section detection using header keywords
│   ├── jd_extractor.py             Job description keyword extraction (KeyBERT)
│   ├── scoring_engine.py           Per-section and composite scoring
│   ├── embedding_engine.py         Sentence-Transformer embedding utilities
│   └── explainer.py                Keyword-level similarity attribution
├── services/
│   ├── __init__.py
│   └── report_generator.py         PDF report generation (fpdf2)
├── tests/
│   ├── __init__.py
│   ├── test_parser.py              Parser and section splitter tests
│   ├── test_scoring.py             Scoring engine tests
│   ├── test_explainer.py           Explainer tests
│   ├── test_jd_extractor.py        Keyword extraction tests
│   ├── test_report.py              Report generator tests
│   ├── generate_sample_resume.py   Generates a sample resume PDF for testing
│   └── generate_test_resumes.py    Generates multiple diverse sample resumes
├── .streamlit/
│   └── config.toml                 Streamlit theme and server configuration
├── requirements.txt                Python dependencies
├── packages.txt                    System packages for Streamlit Cloud
├── runtime.txt                     Python version for Streamlit Cloud
├── .gitignore
└── README.md
```

---

## Prerequisites

- **Python 3.11** or higher
- **pip** (Python package installer)
- **Git** (for cloning the repository)

---

## Installation

### 1. Clone the Repository

```bash
git clone https://github.com/your-username/resume-insight-engine.git
cd resume-insight-engine
```

### 2. Create a Virtual Environment

```bash
python -m venv venv
```

Activate the virtual environment:

- **Windows:**
  ```bash
  venv\Scripts\activate
  ```
- **macOS/Linux:**
  ```bash
  source venv/bin/activate
  ```

### 3. Install Dependencies

```bash
pip install -r requirements.txt
```

This installs all required packages including:
- Streamlit
- pdfplumber
- spaCy and the en_core_web_sm model
- sentence-transformers
- KeyBERT
- plotly
- fpdf2
- pandas
- scikit-learn

The spaCy `en_core_web_sm` model is included directly in `requirements.txt` and will be installed automatically.

---

## Running the Application

```bash
streamlit run app.py
```

The application will start and open in your default browser at `http://localhost:8501`.

To specify a custom port:

```bash
streamlit run app.py --server.port 8080
```

---

## Usage Guide

### Step 1: Paste a Job Description

In the left sidebar, paste the full text of the job description you want to screen candidates against. Include required skills, tools, responsibilities, and qualifications for best results.

### Step 2: Upload Resume PDFs

Click the file uploader in the sidebar to upload one or more resume PDFs. Each file must be under 5 MB. Multiple files can be selected at once.

### Step 3: Run Analysis

Click the **Run Analysis** button. The application will:
- Extract text from each PDF
- Split each resume into sections
- Extract keywords from the job description
- Compute similarity scores for each section
- Identify matched and missing skills
- Rank candidates by composite score

A progress bar shows the processing status.

### Step 4: Review Results

After analysis completes, you will see:

- **Summary Metrics** -- Total candidates analysed, average score, highest score, and count of strong matches (70+)
- **Ranked Results Table** -- All candidates ranked by composite score with per-section breakdowns
- **Score Analysis Charts** -- Bar chart of candidate scores and horizontal bar chart of most common skill gaps across all candidates
- **Candidate Details** -- Expandable sections for each candidate showing section scores, matched skills, and skill gaps
- **Export Options** -- Download results as CSV or generate individual PDF reports for each candidate

### Generating PDF Reports

Inside each candidate's expanded detail view, click **Generate Report** to create a one-page PDF report. Once generated, a **Download Report PDF** link appears.

---

## Running Tests

The `tests/` directory contains standalone test scripts for each module. Run them individually:

```bash
python tests/test_scoring.py
python tests/test_explainer.py
python tests/test_jd_extractor.py
python tests/test_report.py
python tests/test_parser.py
```

Each test script prints results and runs assertion checks, printing "All checks passed." on success.

To generate sample resume PDFs for manual testing:

```bash
python tests/generate_sample_resume.py
python tests/generate_test_resumes.py
```

---

## Deployment

### Streamlit Community Cloud

This project is ready to deploy on [Streamlit Community Cloud](https://streamlit.io/cloud):

1. Push your code to a GitHub repository
2. Go to [share.streamlit.io](https://share.streamlit.io)
3. Connect your GitHub account and select the repository
4. Set the main file path to `app.py`
5. Deploy

The following files are included for Streamlit Cloud compatibility:
- `requirements.txt` -- Python dependencies
- `packages.txt` -- System-level apt packages (libgomp1 for spaCy)
- `runtime.txt` -- Python version specification (python-3.11)
- `.streamlit/config.toml` -- Theme and server configuration

### Docker (Optional)

To deploy with Docker, create a `Dockerfile`:

```dockerfile
FROM python:3.11-slim

WORKDIR /app

RUN apt-get update && apt-get install -y libgomp1 && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

EXPOSE 8501

CMD ["streamlit", "run", "app.py", "--server.port=8501", "--server.address=0.0.0.0"]
```

Build and run:

```bash
docker build -t resume-insight-engine .
docker run -p 8501:8501 resume-insight-engine
```

---

## Configuration

### Streamlit Theme

The application theme is configured in `.streamlit/config.toml`:

| Setting                   | Value       |
|---------------------------|-------------|
| Primary Color             | #1B2A4A     |
| Background Color          | #FFFFFF     |
| Secondary Background      | #F0F2F6     |
| Text Color                | #31333F     |
| Font                      | sans serif  |

### Scoring Weights

Section weights can be adjusted in `core/scoring_engine.py` by modifying the `SECTION_WEIGHTS` dictionary. Weights must sum to 1.0.

### Keyword Extraction

The number of keywords extracted from the job description can be adjusted by changing the `top_n` parameter in the `extract_jd_keywords` call within `app.py` (default: 20).

---

## License

This project is provided as-is for educational and professional use.

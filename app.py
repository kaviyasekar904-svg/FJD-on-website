import streamlit as st
import torch
from transformers import AutoTokenizer, AutoModelForSequenceClassification
import urllib.parse
import re
import html

# -------------------------
# Page Config
# -------------------------

st.set_page_config(
    page_title="AI Fake Job Detector",
    page_icon="🔍",
    layout="wide"
)

st.title("🔍 AI Fake Job Detection System")

st.markdown(
    """
<style>
@import url('https://fonts.googleapis.com/css2?family=Manrope:wght@400;600;700&family=Space+Grotesk:wght@500;700&display=swap');

:root {
    --ink: #0b1f2a;
    --muted: #5b6b7a;
    --card: #ffffff;
    --border: #e4e8ef;
    --real: #10b981;
    --fake: #ef4444;
    --accent: #0f766e;
    --accent-dark: #0b5f58;
}

.stApp {
    background: radial-gradient(1200px 500px at 10% -10%, #e8f6ff 0%, rgba(232, 246, 255, 0) 60%),
                radial-gradient(900px 500px at 90% -20%, #e9f8f1 0%, rgba(233, 248, 241, 0) 55%),
                #f6f8fb;
    color: var(--ink);
    font-family: "Manrope", "Segoe UI", sans-serif;
}

h1, h2, h3, h4 {
    font-family: "Space Grotesk", "Segoe UI", sans-serif;
    color: var(--ink);
}

.job-card {
    background: var(--card);
    border: 1px solid var(--border);
    border-radius: 18px;
    padding: 18px 22px;
    margin-bottom: 16px;
    box-shadow: 0 10px 30px rgba(15, 23, 42, 0.08);
}

.job-header {
    display: flex;
    justify-content: space-between;
    gap: 16px;
    align-items: flex-start;
    flex-wrap: wrap;
}

.job-title {
    font-size: 1.35rem;
    font-weight: 700;
    margin: 0 0 6px 0;
}

.job-company {
    font-size: 1.05rem;
    font-weight: 600;
    color: var(--muted);
}

.job-badge {
    padding: 6px 12px;
    border-radius: 999px;
    font-size: 0.8rem;
    font-weight: 700;
    letter-spacing: 0.02em;
    text-transform: uppercase;
}

.badge-real {
    background: rgba(16, 185, 129, 0.12);
    color: #047857;
}

.badge-fake {
    background: rgba(239, 68, 68, 0.12);
    color: #b91c1c;
}

.job-actions {
    margin-top: 12px;
}

.job-link {
    display: inline-block;
    background: var(--accent);
    color: #ffffff !important;
    padding: 8px 16px;
    border-radius: 999px;
    font-weight: 700;
    text-decoration: none;
    transition: transform 0.2s ease, background 0.2s ease;
}

.job-link:hover {
    background: var(--accent-dark);
    transform: translateY(-1px);
}

.job-link.disabled {
    background: #cbd5e1;
    color: #475569 !important;
    cursor: default;
}

.section-subtitle {
    color: var(--muted);
    margin-top: -6px;
    margin-bottom: 14px;
}
</style>
""",
    unsafe_allow_html=True
)

# -------------------------
# Load Model
# -------------------------

model_path = "saved_model"

@st.cache_resource
def load_model():
    tokenizer = AutoTokenizer.from_pretrained(model_path)
    model = AutoModelForSequenceClassification.from_pretrained(model_path)
    return tokenizer, model

tokenizer, model = load_model()

# -------------------------
# Prediction Function
# -------------------------

def predict_job(text):

    inputs = tokenizer(text, return_tensors="pt", truncation=True, padding=True)

    with torch.no_grad():
        outputs = model(**inputs)

    pred = torch.argmax(outputs.logits).item()

    if pred == 1:
        return "Fake"
    else:
        return "Real"

# -------------------------
# Get jobs from URL
# -------------------------

def get_jobs_text():
    job_values = None

    # New API (Streamlit 1.30+)
    try:
        params = st.query_params
        if hasattr(params, "get_all"):
            job_values = params.get_all("jobs")
        else:
            job_values = params.get("jobs", None)
    except Exception:
        job_values = None

    # Fallback for older Streamlit versions
    if job_values is None:
        try:
            params = st.experimental_get_query_params()
            job_values = params.get("jobs", None)
        except Exception:
            job_values = None

    if job_values is None:
        return ""

    if isinstance(job_values, list):
        # If multiple values are present, join them into a single payload
        job_text = "|".join(job_values)
    else:
        job_text = str(job_values)

    try:
        return urllib.parse.unquote(job_text)
    except Exception:
        return job_text


job_text = get_jobs_text()

def split_jobs(text):
    if not text:
        return []
    # Split on single "|" that is not part of "||"
    return [j for j in re.split(r"(?<!\|)\|(?!\|)", text) if j]

jobs = split_jobs(job_text)

def parse_job_entry(raw_job):
    parts = [p.strip() for p in raw_job.split("||")]
    if len(parts) >= 3:
        title = parts[0]
        company = parts[1]
        url = "||".join(parts[2:]).strip()
    elif len(parts) == 2:
        title = parts[0]
        company = ""
        url = parts[1]
    else:
        title = parts[0] if parts else ""
        company = ""
        url = ""
    return title, company, url

def normalize_company(company):
    cleaned = company.strip()
    if cleaned:
        return cleaned
    return "Unknown"

# -------------------------
# Process Jobs
# -------------------------

real_jobs = []
fake_jobs = []

for job in jobs:
    title, company, url = parse_job_entry(job)
    title = title.strip()
    url = url.strip()
    company = normalize_company(company)

    result = predict_job(title)

    job_data = {
        "title": title,
        "company": company,
        "url": url
    }

    if result == "Fake":
        fake_jobs.append(job_data)
    else:
        real_jobs.append(job_data)

# -------------------------
# Stats
# -------------------------

total_jobs = len(real_jobs) + len(fake_jobs)

col1, col2, col3 = st.columns(3)

with col1:
    st.metric("Total Jobs", total_jobs)

with col2:
    st.metric("Real Jobs", len(real_jobs))

with col3:
    st.metric("Fake Jobs", len(fake_jobs))

# -------------------------
# Real Jobs
# -------------------------

st.header("✅ Real Jobs")
st.markdown('<div class="section-subtitle">Verified roles for quick review</div>', unsafe_allow_html=True)

if len(real_jobs) == 0:
    st.write("No real jobs detected.")

for job in real_jobs:
    title = html.escape(job["title"] or "Untitled Role")
    company = html.escape(job["company"])
    if job["url"]:
        safe_url = html.escape(job["url"], quote=True)
        link = f'<a class="job-link" href="{safe_url}" target="_blank" rel="noopener">Open Job Posting</a>'
    else:
        link = '<span class="job-link disabled">No link provided</span>'

    st.markdown(
        f"""
        <div class="job-card">
            <div class="job-header">
                <div>
                    <div class="job-title">{title}</div>
                    <div class="job-company">{company}</div>
                </div>
                <div class="job-badge badge-real">Real</div>
            </div>
            <div class="job-actions">{link}</div>
        </div>
        """,
        unsafe_allow_html=True
    )

# -------------------------
# Fake Jobs
# -------------------------

st.header("⚠ Fake Jobs")
st.markdown('<div class="section-subtitle">Flagged roles requiring caution</div>', unsafe_allow_html=True)

if len(fake_jobs) == 0:
    st.write("No fake jobs detected.")

for job in fake_jobs:
    title = html.escape(job["title"] or "Untitled Role")
    company = html.escape(job["company"])
    if job["url"]:
        safe_url = html.escape(job["url"], quote=True)
        link = f'<a class="job-link" href="{safe_url}" target="_blank" rel="noopener">Open Job Posting</a>'
    else:
        link = '<span class="job-link disabled">No link provided</span>'

    st.markdown(
        f"""
        <div class="job-card">
            <div class="job-header">
                <div>
                    <div class="job-title">{title}</div>
                    <div class="job-company">{company}</div>
                </div>
                <div class="job-badge badge-fake">Fake</div>
            </div>
            <div class="job-actions">{link}</div>
        </div>
        """,
        unsafe_allow_html=True
    )

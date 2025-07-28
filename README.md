
---

## 📘 Round 1A: Understand Your Document

### 🎯 Objective

Extract a structured outline from a given PDF, identifying:

- 📌 **Document Title**
- 🧩 **Hierarchical Headings**: H1, H2, H3 with page numbers

---

### 🧠 Approach

1. **PDF Parsing**
   - Utilizes `pdfplumber` to extract text with font metadata (size, boldness, positioning).
   
2. **Header/Footer Filtering**
   - Detects and removes recurring elements across pages.

3. **Heading Identification**
   - Scoring mechanism based on:
     - Font size
     - Boldness
     - Numbering patterns (e.g., `1.`, `1.1`)
     - Keywords (e.g., Introduction, References)

4. **Hierarchy Assignment**
   - Based on numbering depth (e.g., `1.` = H1, `1.1` = H2)
   - Fallback to font size + score-based comparison

5. **Title Extraction**
   - Searches early pages for large, bold, top-centered text not matching generic terms (e.g., “Table of Contents”).

6. **Output Formatting**
   - Results sorted by page number and vertical position
   - Output structured as JSON

---

### 🧰 Libraries Used

- `pdfplumber` – PDF parsing
- `statistics` – Median font size detection
- `collections` – Frequency analysis for headers/footers

---

## 📘 Round 1B: Persona-Driven Document Intelligence

### 🎯 Objective

Given a user’s **persona** and **job-to-be-done**, rank the most relevant sections from a collection of PDF documents and return the most informative content.

---

### 🛠️ Pipeline Overview

1. **Section Extraction**
   - Uses `pdfplumber` + heading detection (from Round 1A) to break documents into logical sections (H1–H3).
   
2. **Text Representation**
   - Uses `TfidfVectorizer` from `scikit-learn` to convert:
     - Each section’s content
     - The user's job description
   - Into comparable numeric vectors based on keyword importance

3. **Similarity Scoring**
   - Computes **cosine similarity** between vectors to measure semantic relevance
   - Sections are ranked by descending similarity

4. **Subsection Refinement**
   - Extracts and returns full original content of the top-ranked sections

5. **Final Output**
   - Structured JSON with:
     - Metadata (persona, job, timestamp)
     - Ranked `extracted_sections`
     - `subsection_analysis` with actual section content

---

### 🧰 Technologies Used

| Library         | Purpose                                       |
|----------------|-----------------------------------------------|
| `pdfplumber`    | Parsing PDF with font/position awareness     |
| `scikit-learn`  | TF-IDF vectorization + cosine similarity     |
| `numpy`         | Numerical operations for scoring              |

---

## 🐳 Docker Setup (For Both Rounds)

> All dependencies are pre-installed and bundled in a lightweight Docker container (<1GB).

### 🧱 Build Docker Image

```bash
docker build --platform linux/amd64 -t adobe-hackathon-solution .


docker run --rm -v "$(pwd)/input:/app/input" -v "$(pwd)/output:/app/output" --network none adobe-hackathon-solution
docker run --rm -v "%cd%\input:/app/input" -v "%cd%\output:/app/output" --network none adobe-hackathon-solution


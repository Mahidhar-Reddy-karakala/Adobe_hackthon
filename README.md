# Adobe India Hackathon 2025 - Round 1A: Understand Your Document

This project implements a solution for Adobe's "Connecting the Dots" Hackathon Round 1A challenge. The goal is to extract a structured outline (Title, H1, H2, H3 headings with page numbers) from a given PDF file.

## Approach

This solution uses a heuristic-based approach implemented in Python, leveraging the `pdfplumber` library for robust PDF parsing. It focuses on common typographical features of headings:

1.  **PDF Parsing:** `pdfplumber` is used to extract text, font information (size, name), and positional data for each character and text line.
2.  **Header/Footer Detection:** Lines that appear repeatedly across multiple pages are identified and excluded from heading consideration.
3.  **Heading Candidate Identification:** For each text line:
    *   It checks if the line is likely a header/footer or body text.
    *   A scoring mechanism evaluates the line based on:
        *   **Font Size:** Lines significantly larger than the document's median text size receive a higher score.
        *   **Boldness:** Lines using fonts identified as bold receive a higher score.
        *   **Text Patterns:** Matches against common heading numbering patterns (`1. Title`, `1.1 Subtitle`) and keywords (`Introduction`, `References`) boost the score.
    *   Lines scoring above a threshold are considered potential headings.
4.  **Level Assignment (H1/H2/H3):**
    *   Primary assignment is based on the depth of numbering patterns found in the text (e.g., `1.` -> H1, `1.1` -> H2, `1.1.1` -> H3).
    *   A fallback mechanism uses relative score and font size among the identified candidates to assign levels if clear patterns are absent.
5.  **Post-Processing:**
    *   Obvious non-headings (like standalone page numbers) are filtered out.
    *   Duplicate or near-duplicate headings appearing on the same page are removed.
6.  **Title Extraction:**
    *   A dedicated search is performed on the first few pages (1-3).
    *   Lines are scored based on font size, boldness, position (preferring upper-mid areas of page 1), and length.
    *   The highest-scoring line that doesn't match common section names like "Table of Contents" is selected as the title.
    *   If no strong title is found this way, a prominent H1 candidate or the first heading is used as a fallback.
7.  **Output Formatting:**
    *   The final list of headings is sorted first by page number and then by their vertical position (top to bottom) on the page.
    *   The result is formatted into the required JSON structure.

## Libraries Used

*   `pdfplumber`: For parsing PDFs and extracting text with formatting and positional information.
*   `statistics`: For calculating median font sizes.
*   `collections` (`defaultdict`, `Counter`): For efficient data handling and counting during analysis.

## How to Build and Run

This solution is packaged using Docker for consistent execution.

### Prerequisites

*   Docker installed on your system.

### Building the Docker Image

Navigate to the root directory of this project (where the `Dockerfile` is located) and run:

```bash
docker build --platform linux/amd64 -t mysolutionname:somerandomidentifier .

```For Linux/macOS/PowerShell:
docker run --rm -v "$(pwd)/input:/app/input" -v "$(pwd)/output:/app/output" --network none mysolutionname:somerandomidentifier
```For Windows Command Prompt:
docker run --rm -v "%cd%\input:/app/input" -v "%cd%\output:/app/output" --network none mysolutionname:somerandomidentifier







# Approach Explanation for Round 1B: Persona-Driven Document Intelligence

## Overview

Our solution for Round 1B aims to intelligently identify and rank the most relevant sections from a collection of PDF documents based on a user's specific persona and job-to-be-done. It focuses on semantic relevance while keeping dependencies lightweight to meet the 1GB model size constraint.

## Methodology

The solution follows a structured pipeline:

1.  **Document Parsing & Structure Extraction:**
    *   We utilize `pdfplumber` to parse each input PDF.
    *   A heuristic-based approach analyzes font properties (size, boldness) and text patterns (numbering like `1.`, `1.1`, common keywords like "Introduction", "Beaches", "Cuisine") to identify potential section headings (H1, H2, H3).
    *   For each identified heading, the subsequent text content is extracted until the next potential heading. This creates a flat list of document sections, each associated with its title, page number, and content.

2.  **Semantic Content Representation:**
    *   To understand the relevance of text, we employ the TF-IDF (Term Frequency-Inverse Document Frequency) method from the `scikit-learn` library.
    *   TF-IDF converts text snippets (the user's job description and each document section's content) into numerical vectors. It emphasizes words that are frequent in a specific document section but rare across the entire collection of documents and the job description, thus highlighting distinctive, potentially relevant terms.

3.  **Relevance Scoring & Ranking:**
    *   The core of our approach is calculating the relevance of each document section to the user's task.
    *   The system first preprocesses the text (lowercasing, removing punctuation) and then uses `TfidfVectorizer` to create vectors for the user's "Job-to-be-Done" description and the content of every extracted section.
    *   The cosine similarity is computed between the job vector and each section content vector. Cosine similarity measures the cosine of the angle between two vectors, providing a score between -1 and 1 (where 1 indicates identical direction/meaning in vector space, implying shared important terms).
    *   Sections are ranked in descending order based on these similarity scores. The section with the highest score is considered most relevant to the user's job based on shared key terms.

4.  **Sub-section Analysis (Refined Text):**
    *   To provide the user with the actual relevant information, the "Refined Text" in the output corresponds directly to the full original content text of the ranked section. This ensures the user gets the most pertinent details immediately.

5.  **Output Generation:**
    *   The system compiles the results into the required JSON format (`challenge1b_output.json`).
    *   It includes metadata (input documents, persona, job, timestamp).
    *   The `extracted_sections` list contains the document source, page number, title, and `importance_rank` for each ranked section.
    *   The `subsection_analysis` list provides the document, title, `Refined Text` (the section's original content), and page number.

## Technologies Used

*   **`pdfplumber`:** For robust PDF parsing and extraction of text with formatting information.
*   **`scikit-learn`:** Provides `TfidfVectorizer` for creating TF-IDF representations and `cosine_similarity` for efficient comparison. This is a much lighter alternative to sentence-transformers.
*   **`numpy`:** Fundamental library for numerical operations, used by `scikit-learn`.

## Design Considerations

*   **Modularity:** The code is structured into distinct modules (`main`, `parser`, `ranker`) for clarity and easier maintenance.
*   **Efficiency & Size:** The choice of TF-IDF significantly reduces the dependency footprint, ensuring the Docker image easily stays under the 1GB limit. It's also computationally efficient for the scale of documents (3-10) specified.
*   **Offline Operation:** The solution relies solely on libraries that can be installed via `pip` and does not require downloading external models at runtime, ensuring it runs entirely offline.
*   **Scalability:** The architecture is designed to handle the specified range of documents within the time constraints (60 seconds), primarily limited by the TF-IDF calculation time for the text corpus.
*   **Generic Approach:** The logic is designed to be generic and handle diverse document types, personas, and jobs by relying on general semantic similarity based on term frequency rather than hard-coded rules specific to one domain.


```bash
docker build --platform linux/amd64 -t mysolutionname:somerandomidentifier .

```For Linux/macOS/PowerShell:
docker run --rm -v "$(pwd)/input:/app/input" -v "$(pwd)/output:/app/output" --network none mysolutionname:somerandomidentifier
```For Windows Command Prompt:
docker run --rm -v "%cd%\input:/app/input" -v "%cd%\output:/app/output" --network none mysolutionname:somerandomidentifier

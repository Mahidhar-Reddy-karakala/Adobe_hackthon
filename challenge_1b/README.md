


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

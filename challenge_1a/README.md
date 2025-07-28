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
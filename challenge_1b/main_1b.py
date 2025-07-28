


# main_1b.py
import os
import json
from datetime import datetime
from document_parser_1b import parse_document
from relevance_ranker_1b import rank_sections

def load_inputs(input_dir):
    """Loads PDFs, persona, and job from the input directory."""
    pdf_paths = []
    persona = ""
    job = ""

    for filename in os.listdir(input_dir):
        filepath = os.path.join(input_dir, filename)
        if filename.lower().endswith('.pdf'):
            pdf_paths.append(filepath)
        elif filename.lower() == 'persona.txt':
            with open(filepath, 'r', encoding='utf-8') as f:
                persona = f.read().strip()
        elif filename.lower() == 'job.txt':
            with open(filepath, 'r', encoding='utf-8') as f:
                job = f.read().strip()

    return pdf_paths, persona, job

def main():
    """Main function to run the Round 1B solution."""
    INPUT_DIR = "/app/input"
    OUTPUT_FILE = "/app/output/challenge1b_output.json"

    print("Loading inputs...")
    pdf_paths, persona, job = load_inputs(INPUT_DIR)

    if not pdf_paths:
        print("No PDF files found in input directory.")
        return
    if not persona:
        print("Warning: persona.txt not found or empty.")
    if not job:
        print("Warning: job.txt not found or empty.")

    print(f"Found {len(pdf_paths)} PDF(s) to process.")

    # --- Step 1: Parse Documents ---
    print("Parsing documents...")
    parsed_documents = []
    for pdf_path in pdf_paths:
        doc_id = os.path.basename(pdf_path)
        print(f"  Parsing {doc_id}...")
        try:
            parsed_doc = parse_document(pdf_path)
            parsed_doc['doc_id'] = doc_id
            parsed_documents.append(parsed_doc)
        except Exception as e:
            print(f"    Error parsing {pdf_path}: {e}")

    # --- Step 2: Rank Sections ---
    print("Ranking sections based on relevance...")
    ranked_output_data = rank_sections(parsed_documents, persona, job)

    # --- Step 3: Add Metadata ---
    print("Adding metadata...")
    metadata = {
        "input_documents": [os.path.basename(p) for p in pdf_paths],
        "persona": persona,
        "job_to_be_done": job,
        "processing_timestamp": datetime.utcnow().isoformat() + "Z"
    }
    ranked_output_data["metadata"] = metadata
    # Ensure keys match expected output format exactly
    # The ranker should return the correct keys, but let's make sure
    extracted_sections = ranked_output_data.pop("extracted_sections", [])
    subsection_analysis = ranked_output_data.pop("subsection_analysis", [])
    ranked_output_data["extracted_sections"] = extracted_sections
    ranked_output_data["subsection_analysis"] = subsection_analysis

    # --- Step 4: Write Output ---
    print(f"Writing output to {OUTPUT_FILE}...")
    os.makedirs(os.path.dirname(OUTPUT_FILE), exist_ok=True)
    with open(OUTPUT_FILE, 'w', encoding='utf-8') as f:
        json.dump(ranked_output_data, f, indent=2, ensure_ascii=False)

    print("Round 1B processing complete.")

if __name__ == "__main__":
    main()



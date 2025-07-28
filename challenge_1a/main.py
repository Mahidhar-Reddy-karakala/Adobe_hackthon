# main.py
import os
import json
from heading_extractor import extract_outline

def process_pdfs(input_dir, output_dir):
    """Processes all PDFs in the input directory and saves JSON outlines."""
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)

    for filename in os.listdir(input_dir):
        if filename.lower().endswith('.pdf'):
            pdf_path = os.path.join(input_dir, filename)
            print(f"Processing: {pdf_path}")

            try:
                outline_data = extract_outline(pdf_path)
                json_filename = os.path.splitext(filename)[0] + '.json'
                json_path = os.path.join(output_dir, json_filename)

                with open(json_path, 'w', encoding='utf-8') as f:
                    json.dump(outline_data, f, indent=2, ensure_ascii=False)
                print(f"Saved: {json_path}")

            except Exception as e:
                print(f"Error processing {pdf_path}: {e}")
                # Optionally, create an empty JSON or error indicator
                error_data = {"title": "Error", "outline": []}
                json_filename = os.path.splitext(filename)[0] + '.json'
                json_path = os.path.join(output_dir, json_filename)
                with open(json_path, 'w') as f:
                    json.dump(error_data, f, indent=2)


if __name__ == "__main__":
    INPUT_DIR = "input"
    OUTPUT_DIR = "output"
    process_pdfs(INPUT_DIR, OUTPUT_DIR)

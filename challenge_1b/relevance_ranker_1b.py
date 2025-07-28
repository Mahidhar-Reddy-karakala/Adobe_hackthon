


# relevance_ranker_1b.py
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
import numpy as np
import re

def preprocess_text(text):
    """Basic text preprocessing."""
    if not text:
        return ""
    text = text.lower()
    # Keep letters, numbers, and spaces. Replace punctuation with space.
    text = re.sub(r'[^a-zA-Z0-9\s]', ' ', text)
    text = ' '.join(text.split()) # Normalize whitespace
    return text

def rank_sections(parsed_documents, persona, job):
    """
    Ranks document sections based on their relevance to the job/persona using TF-IDF.
    """
    print("Starting relevance ranking using TF-IDF...")

    # --- Prepare Data for TF-IDF ---
    sections_to_rank = [] # Flat list of all sections
    all_section_texts = [] # List of texts for TF-IDF

    for doc_data in parsed_documents:
        doc_id = doc_data.get('doc_id', 'Unknown')
        # Iterate through the flat list of sections from the parser
        for section in doc_data.get('sections', []):
             # Basic check to avoid ranking empty sections
            if not section.get('content', '').strip():
                continue
            sections_to_rank.append({
                'document': doc_id,
                'title': section['title'],
                'page': section['page'],
                'content': section['content'], # Keep original for Refined Text
                'level': section.get('level', 'H3') # Default to H3 if missing
            })
            # Preprocess content for TF-IDF
            processed_content = preprocess_text(section['content'])
            all_section_texts.append(processed_content)

    if not sections_to_rank:
        print("No sections with content found to rank.")
        return {"extracted_sections": [], "subsection_analysis": []}

    print(f"Found {len(sections_to_rank)} sections with content to analyze.")

    # --- TF-IDF Vectorization ---
    print("Creating TF-IDF vectors...")
    # Prepare texts for vectorization: [job, persona] + section contents
    job_processed = preprocess_text(job)
    persona_processed = preprocess_text(persona)
    # corpus = [job_processed] + all_section_texts # Just job
    corpus = [job_processed, persona_processed] + all_section_texts # Job + Persona

    # Use TF-IDF with reasonable parameters
    vectorizer = TfidfVectorizer(
        stop_words='english',
        max_features=15000, # Slightly larger vocab
        ngram_range=(1, 2), # Use unigrams and bigrams
        lowercase=False # We already lowercased
    )

    try:
        tfidf_matrix = vectorizer.fit_transform(corpus)
    except ValueError as e:
        print(f"Error during TF-IDF fitting: {e}")
        return {"extracted_sections": [], "subsection_analysis": []}

    # --- Calculate Similarity ---
    print("Calculating similarities...")
    # tfidf_matrix shape: (len(corpus), num_features)
    # First row(s) are query vectors (job, persona)
    # Rest are section content vectors
    # job_vector = tfidf_matrix[0] # Shape: (1, num_features)
    # persona_vector = tfidf_matrix[1] # Shape: (1, num_features)
    # section_vectors = tfidf_matrix[2:] # Shape: (num_sections, num_features)

    # Calculate similarity of job and persona to all sections
    # job_similarities = cosine_similarity(job_vector, section_vectors).flatten() # Shape: (num_sections,)
    # persona_similarities = cosine_similarity(persona_vector, section_vectors).flatten()
    # Combine scores (simple average)
    # final_scores = (job_similarities + persona_similarities) / 2.0

    # --- Simpler: Just use Job for similarity ---
    job_vector = tfidf_matrix[0] # Shape: (1, num_features)
    section_vectors = tfidf_matrix[2:] # Shape: (num_sections, num_features)
    final_scores = cosine_similarity(job_vector, section_vectors).flatten() # Shape: (num_sections,)


    # --- Assign Scores and Rank ---
    print("Assigning scores and ranking...")
    for i, section in enumerate(sections_to_rank):
        if i < len(final_scores):
            section['relevance_score'] = float(final_scores[i])
        else:
            section['relevance_score'] = 0.0

    # Sort sections by relevance score descending
    sections_to_rank.sort(key=lambda x: x['relevance_score'], reverse=True)

    # Assign importance_rank
    for i, section in enumerate(sections_to_rank):
        section['importance_rank'] = i + 1

    # --- Prepare Output JSON ---
    print("Preparing output JSON...")
    extracted_sections = []
    subsection_analyses = []

    # Take top sections (e.g., top 20-50 or all above a threshold like 0.01)
    # top_sections = [s for s in sections_to_rank if s['relevance_score'] > 0.01] # Threshold example
    top_sections = sections_to_rank[:50] # Take top 50

    for section in top_sections:
        extracted_sections.append({
            "document": section['document'],
            "page": section['page'],
            "title": section['title'], # Use 'title' as per expected output
            "importance_rank": section['importance_rank']
        })
        subsection_analyses.append({
            "document": section['document'],
            "title": section['title'], # Parent section title
            "Refined Text": section['content'], # The actual relevant content
            "page": section['page']
        })

    print("Ranking complete.")
    return {
        "extracted_sections": extracted_sections,
        "subsection_analysis": subsection_analyses
    }


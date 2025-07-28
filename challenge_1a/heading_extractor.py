
# heading_extractor.py
import pdfplumber
import re
from collections import defaultdict, Counter
import statistics

def extract_outline(pdf_path):
    """
    Extracts title and structured outline (H1, H2, H3) from a PDF using general heuristics.
    Focuses on font size, boldness, position, and common heading patterns.
    """
    title = ""
    outline = []
    
    with pdfplumber.open(pdf_path) as pdf:
        # --- PASS 1: Collect Global Font Statistics and Detect Headers/Footers ---
        all_chars = []
        page_texts = []
        for page in pdf.pages:
            all_chars.extend(page.chars)
            text = page.extract_text()
            if text:
                page_texts.append(text)

        if not all_chars:
            return {"title": "", "outline": []}

        # Font/Size Stats
        sizes = [c['size'] for c in all_chars if c['size'] > 0]
        if not sizes:
             return {"title": "", "outline": []}
        median_text_size = statistics.median(sizes)
        # Define a threshold for "large" text (potential headings)
        # Use 75th percentile or a multiplier, whichever is larger, to be adaptive
        size_threshold_75 = sorted(sizes)[int(len(sizes) * 0.75)]
        size_threshold_multiplier = median_text_size * 1.2
        heading_size_threshold = max(size_threshold_75, size_threshold_multiplier)

        # Font analysis for boldness
        fonts = [c['fontname'] for c in all_chars]
        font_counter = Counter(fonts)
        bold_indicators = ['Bold', 'bold', 'Black', 'black', 'Heavy', 'heavy', 'Semibold', 'SemiBold']
        bold_fonts = {f for f in font_counter if any(b in f for b in bold_indicators)}

        # Header/Footer Detection (content that repeats across many pages)
        line_counter = defaultdict(int)
        for text_content in page_texts:
            lines = text_content.split('\n')
            # Count unique lines per page to avoid skew from repetition within a page
            unique_lines_on_page = set(line.strip() for line in lines if len(line.strip()) > 5 and not re.match(r'^[\d\s\-\.\|]*$', line.strip()))
            for line in unique_lines_on_page:
                line_counter[line] += 1
        num_pages = len(pdf.pages)
        # Candidate headers/footers appear on a significant portion of pages
        header_footer_lines = {line for line, count in line_counter.items() if count > max(2, num_pages * 0.3)}


        # --- PASS 2: Extract Potential Headings ---
        potential_headings = []
        for page_num, page in enumerate(pdf.pages, start=1):
            lines = page.extract_text_lines()
            for line_obj in lines:
                text = line_obj.get('text', '').strip()
                if not text or len(text) < 3:
                    continue

                # Filter out likely headers/footers and obvious non-headings
                if text in header_footer_lines or \
                   re.match(r'^\d+$', text) or \
                   '......' in text or \
                   len(text) > 150: # Too long, likely body text or TOC line
                    continue

                line_chars = line_obj.get('chars', [])
                if not line_chars:
                    continue

                avg_size = sum(c['size'] for c in line_chars) / len(line_chars)
                is_bold = any(c['fontname'] in bold_fonts for c in line_chars)
                # Normalize position: 0=top, 1=bottom
                y_pos_norm = 1.0 - (line_chars[0]['y0'] / page.height) if page.height > 0 else 0

                # --- Scoring based on key factors ---
                score = 0
                features = []

                # 1. Font Size (PRIMARY FACTOR)
                if avg_size >= heading_size_threshold:
                    # Score based on how much larger it is
                    size_factor = (avg_size - heading_size_threshold) / median_text_size
                    score += size_factor * 3.0 # Strong weight
                    features.append(f"Large({avg_size:.1f})")

                # 2. Bold Font (PRIMARY FACTOR)
                if is_bold:
                    score += 2.5 # Strong weight
                    features.append("Bold")

                # 3. Position (SECONDARY FACTOR)
                # Headings often appear in the main content area
                if 0.1 < y_pos_norm < 0.9: # Avoid extreme top/bottom (often headers/footers)
                     score += 0.5
                     features.append("MidPos")

                # 4. Text Patterns (SECONDARY FACTOR - Boosts score if present)
                # Strong indicators for H1/H2 based on numbering
                if re.match(r"^\d+\.\s+[A-Z][\w\s]{2,}", text): # e.g., "1. Introduction"
                    score += 2.0
                    features.append("H1Pattern")
                elif re.match(r"^\d+\.\d+(\.\d+)?\s+[A-Z]", text): # e.g., "2.1 Details", "3.1.1 More"
                    score += 1.5
                    features.append("H2/H3Pattern")
                # Common section title keywords (case-insensitive)
                elif re.search(r"\b(Acknowledgements|Table of Contents|Revision History|References|Introduction|Overview|Abstract|Conclusion|Appendix|Bibliography|Index|Glossary|Copyright|Version|Syllabus|Business Outcomes|Content|Authors|Internal Reviewers|Intended Audience|Career Paths|Learning Objectives|Entry Requirements|Structure|Keeping It Current|Documents|Trademarks)\b", text, re.IGNORECASE):
                    score += 1.5
                    features.append("Keyword")

                # Filter based on score to ensure it's likely a heading
                # This threshold balances inclusion and noise reduction
                if score >= 2.0:
                    potential_headings.append({
                        'text': text,
                        'page': page_num,
                        'score': score,
                        'size': avg_size,
                        'is_bold': is_bold,
                        'position': y_pos_norm, # 0=top, 1=bottom
                        'features': features
                    })

        # --- Process and Assign Levels ---
        if potential_headings:
            # Sort by page and position (top to bottom within a page)
            potential_headings.sort(key=lambda x: (x['page'], -x['position']))

            # Assign levels primarily based on numbering pattern depth
            for heading in potential_headings:
                text = heading['text']

                # Determine level based on strong numbering patterns first
                if re.match(r"^\d+\.\s", text): # e.g., "1. Title"
                    level = "H1"
                elif re.match(r"^\d+\.\d+\s", text): # e.g., "2.1 Sub"
                    level = "H2"
                elif re.match(r"^\d+\.\d+\.\d+\s", text): # e.g., "3.1.1 SubSub"
                    level = "H3"
                else:
                    # Fallback: Assign level based on relative characteristics
                    # within the pool of identified headings
                    scores = [h['score'] for h in potential_headings]
                    sizes_h = [h['size'] for h in potential_headings]
                    
                    max_score = max(scores) if scores else 1
                    min_score = min(scores) if scores else 0
                    score_range = max_score - min_score if max_score != min_score else 1
                    
                    max_size_h = max(sizes_h) if sizes_h else 1
                    min_size_h = min(sizes_h) if sizes_h else 0
                    size_range_h = max_size_h - min_size_h if max_size_h != min_size_h else 1

                    norm_score = (heading['score'] - min_score) / score_range if score_range > 0 else 0.5
                    norm_size = (heading['size'] - min_size_h) / size_range_h if size_range_h > 0 else 0.5

                    # Combined heuristic for level if no clear pattern matched
                    combined_metric = (norm_score * 0.6) + (norm_size * 0.4)

                    if combined_metric > 0.7:
                        level = "H1"
                    elif combined_metric > 0.4:
                        level = "H2"
                    else:
                        level = "H3"

                outline.append({
                    'level': level,
                    'text': text,
                    'page': heading['page']
                })

            # --- Post-process Outline ---
            # 1. Remove obvious non-headings (like standalone page numbers)
            outline = [item for item in outline if not re.fullmatch(r'\d+', item['text'].strip())]

            # 2. Deduplicate based on text and page proximity
            #    (e.g., if "Overview" appears twice on the same page, likely only one is the true heading)
            cleaned_outline = []
            for i, current in enumerate(outline):
                is_duplicate = False
                if i > 0:
                    prev = outline[i-1]
                    # Check same page and very similar/identical text
                    if current['page'] == prev['page']:
                        curr_norm = re.sub(r'\W+', '', current['text']).lower()
                        prev_norm = re.sub(r'\W+', '', prev['text']).lower()
                        # If one is a significant substring of the other, consider it a duplicate
                        if (curr_norm == prev_norm) or \
                           (curr_norm in prev_norm and len(curr_norm) > len(prev_norm) * 0.6) or \
                           (prev_norm in curr_norm and len(prev_norm) > len(curr_norm) * 0.6):
                            is_duplicate = True
                if not is_duplicate:
                    cleaned_outline.append(current)
            outline = cleaned_outline

            # --- Assign Title ---
            # Best candidate is usually a prominent H1 or a large/bold item on early pages
            # that doesn't look like a generic section name.
            title_candidates = [h for h in outline if h['level'] == 'H1']
            
            # If no strong H1s found, look among potential headings for prominent early ones
            if not title_candidates:
                 early_prominent = [h for h in potential_headings if h['page'] <= 2]
                 early_prominent.sort(key=lambda x: (x['size'], x['score']), reverse=True)
                 # Filter out obvious section names
                 title_candidates_raw = [
                     h for h in early_prominent 
                     if not re.search(r"\b(Table of Contents|Revision History|Copyright|Version)\b", h['text'], re.IGNORECASE) and
                        len(h['text']) > 10 # Avoid very short generic text
                 ]
                 if title_candidates_raw:
                     title = title_candidates_raw[0]['text']
                 elif outline:
                     title = outline[0]['text'] # Ultimate fallback

            # From the H1 candidates, select the best title
            if title_candidates:
                # Avoid picking generic "Table of Contents" etc. if better options exist
                non_generic_candidates = [
                    h for h in title_candidates
                    if not re.search(r"\b(Table of Contents|Revision History|Copyright|Version)\b", h['text'], re.IGNORECASE) and
                       len(h['text']) > 10
                ]
                if non_generic_candidates:
                    # Pick the first non-generic one, or the first one if all are generic
                    title = non_generic_candidates[0]['text']
                else:
                    title = title_candidates[0]['text'] # Take the first one if no better found

    return {
        "title": title.strip(),
        "outline": outline
    }



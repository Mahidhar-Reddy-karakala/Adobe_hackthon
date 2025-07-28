


# document_parser_1b.py
import pdfplumber
import re
from collections import defaultdict
import statistics

def parse_document(pdf_path):
    """
    Parses a PDF to extract its title and a hierarchical structure of sections with content.
    """
    doc_title = ""
    sections = []

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
            return {"title": "", "sections": []}

        sizes = [c['size'] for c in all_chars if c['size'] > 0]
        if not sizes:
             return {"title": "", "sections": []}
        median_text_size = statistics.median(sizes)
        # Use 85th percentile for a stricter heading size threshold
        size_threshold_85 = sorted(sizes)[int(len(sizes) * 0.85)]
        size_threshold_multiplier = median_text_size * 1.3
        heading_size_threshold = max(size_threshold_85, size_threshold_multiplier)

        fonts = [c['fontname'] for c in all_chars]
        bold_indicators = ['Bold', 'bold', 'Black', 'black', 'Heavy', 'heavy', 'Semibold', 'SemiBold']
        bold_fonts = {f for f in fonts if any(b in f for b in bold_indicators)}

        line_counter = defaultdict(int)
        for text_content in page_texts:
            lines = text_content.split('\n')
            unique_lines_on_page = set(line.strip() for line in lines if len(line.strip()) > 5 and not re.match(r'^[\d\s\-\.\|]*$', line.strip()))
            for line in unique_lines_on_page:
                line_counter[line] += 1
        num_pages = len(pdf.pages)
        # Higher threshold for headers/footers to be more specific
        header_footer_lines = {line for line, count in line_counter.items() if count > max(2, num_pages * 0.5)}


        # --- Extract Title (Focus on first page) ---
        if pdf.pages:
            first_page = pdf.pages[0]
            lines = first_page.extract_text_lines()
            title_candidates = []
            for line_obj in lines:
                text = line_obj.get('text', '').strip()
                if not text or len(text) < 5 or len(text) > 100: continue
                if text in header_footer_lines or re.match(r'^(page|copyright|version|\d+)', text, re.IGNORECASE) or '......' in text:
                    continue
                line_chars = line_obj.get('chars', [])
                if not line_chars: continue
                avg_size = sum(c['size'] for c in line_chars) / len(line_chars)
                is_bold = any(c['fontname'] in bold_fonts for c in line_chars)
                y_pos_norm = 1.0 - (line_chars[0]['y0'] / first_page.height) if first_page.height > 0 else 0
                if avg_size >= heading_size_threshold * 0.9 and (is_bold or y_pos_norm < 0.5): # Likely title area
                     score = avg_size + (5 if is_bold else 0) + (3 if y_pos_norm < 0.4 else 0)
                     title_candidates.append({'text': text, 'score': score})
            if title_candidates:
                title_candidates.sort(key=lambda x: x['score'], reverse=True)
                doc_title = title_candidates[0]['text']


        # --- PASS 2: Extract Potential Headings (Simpler Heuristic) ---
        all_potential_headings = []
        for page_num, page in enumerate(pdf.pages, start=1):
             lines = page.extract_text_lines()
             for line_obj in lines:
                text = line_obj.get('text', '').strip()
                if not text or len(text) < 3: continue
                if text in header_footer_lines or re.match(r'^\d+$', text) or '......' in text or len(text) > 150:
                    continue
                line_chars = line_obj.get('chars', [])
                if not line_chars: continue
                avg_size = sum(c['size'] for c in line_chars) / len(line_chars)
                is_bold = any(c['fontname'] in bold_fonts for c in line_chars)
                y_pos_norm = 1.0 - (line_chars[0]['y0'] / page.height) if page.height > 0 else 0

                score = 0
                # Scoring for headings - focus on size, boldness, and common patterns
                if avg_size >= heading_size_threshold * 0.8: score += 2 # Relaxed size threshold
                if is_bold: score += 1.5
                # Patterns for common section titles (more flexible)
                if re.search(r"\b(Acknowledgements|Table of Contents|Revision History|References|Introduction|Overview|Abstract|Conclusion|Appendix|Bibliography|Index|Glossary|Preface|Chapter|Section|Beaches?|Restaurants?|Nightlife|Cuisine|Cities?|History|Traditions?|Tips|Tricks|Things to Do|Hotels?)\b", text, re.IGNORECASE):
                    score += 2.5 # High weight for keywords
                # Numbered patterns (e.g., 1. Introduction, 1.1 Setup)
                elif re.match(r"^\d+(\.\d+)*\s+[A-Z][\w\s]{2,}", text):
                    score += 2

                # Threshold to identify headings - lower to catch more
                if score >= 1.5:
                    # Determine level primarily by pattern, fallback to size/score
                    level = "H3" # Default
                    if re.match(r"^\d+\.\s", text) or re.search(r"\b(Introduction|Overview|References|Acknowledgements|Chapter)\b", text, re.IGNORECASE):
                        level = "H1"
                    elif re.match(r"^\d+\.\d+\s", text) or re.search(r"\b(\d+\.\s)?(Preface|Abstract|Conclusion|Appendix|Bibliography|Index|Glossary)\b", text, re.IGNORECASE):
                        level = "H2"
                    # Keywords like "Beaches", "Restaurants" are likely H2 or H3 depending on context
                    elif re.search(r"\b(Beaches?|Restaurants?|Nightlife|Cuisine|Cities?|History|Traditions?|Tips|Tricks|Things to Do|Hotels?)\b", text, re.IGNORECASE):
                         # If it's large/bold, maybe H2, otherwise H3. Let's default to H2 for key topics.
                         level = "H2"

                    all_potential_headings.append({
                        'text': text, 'page': page_num, 'level': level,
                        'y_pos': y_pos_norm, 'end_y': line_chars[-1]['y0'] if line_chars else 0
                    })

        # Sort headings by page and position (top to bottom)
        all_potential_headings.sort(key=lambda x: (x['page'], -x['y_pos']))

        # --- Group into Hierarchy and Extract Content ---
        # Simplified: Treat all as potential top-level sections for ranking.
        # The ranking logic will determine importance.
        for heading in all_potential_headings:
             # --- Extract Content ---
            content_text = ""
            try:
                page_obj = pdf.pages[heading['page'] - 1] # 0-indexed
                page_text = page_obj.extract_text()
                if page_text:
                    lines_on_page = page_text.split('\n')
                    start_found = False
                    content_lines = []
                    for line in lines_on_page:
                         line_stripped = line.strip()
                         if not start_found:
                            # Match the heading text
                            if heading['text'] == line_stripped or line_stripped.startswith(heading['text'][:min(20, len(heading['text']))]):
                                start_found = True
                                continue # Skip the heading line itself
                         else:
                            # Stop when we hit the next potential heading on the same page
                            is_next_heading = False
                            # Find the next heading in the sorted list
                            current_index = all_potential_headings.index(heading)
                            if current_index + 1 < len(all_potential_headings):
                                next_h = all_potential_headings[current_index + 1]
                                if next_h['page'] == heading['page']:
                                    if next_h['text'] == line_stripped or line_stripped.startswith(next_h['text'][:min(20, len(next_h['text']))]):
                                        is_next_heading = True
                            # Also stop if line looks like a new section heading (simplistic check)
                            elif re.match(r"^(\d+\.)*\d+\.\s+[A-Z]", line_stripped) or \
                                 re.search(r"\b(Acknowledgements|Table of Contents|Revision History|References|Introduction|Overview|Abstract|Conclusion|Appendix|Bibliography|Index|Glossary)\b", line_stripped, re.IGNORECASE):
                                 is_next_heading = True

                            if is_next_heading:
                                break
                            content_lines.append(line_stripped)
                    content_text = " ".join(content_lines).strip()
            except Exception as e:
                 print(f"Warning: Content extraction issue for '{heading['text']}' in {pdf_path}: {e}")
                 content_text = "[Content Extraction Error]"

            # Add section to the flat list for ranking
            sections.append({
                'level': heading['level'],
                'title': heading['text'],
                'page': heading['page'],
                'content': content_text
            })

    return {
        "title": doc_title,
        "sections": sections # Flat list of sections with content
    }




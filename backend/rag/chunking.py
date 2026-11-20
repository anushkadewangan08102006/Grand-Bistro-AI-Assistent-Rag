import re
from typing import List, Dict, Any

class DocumentChunker:
    def __init__(self, target_chunk_size: int = 500, overlap: int = 80):
        self.target_chunk_size = target_chunk_size
        self.overlap = overlap

    def chunk_pages(self, pages: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        chunks = []
        chunk_idx = 0

        for page in pages:
            page_num = page["page_num"]
            text = page["text"]
            module_num = page["module_num"]
            module_topic = page["module_topic"]
            chapter = page["chapter"]

            # Specialized handling for atomic high-value pages
            if page["is_recipe"]:
                # Keep recipe cards completely unified
                chunks.append({
                    "chunk_id": f"p{page_num}_c{chunk_idx}",
                    "page_num": page_num,
                    "chapter": chapter,
                    "module_num": module_num,
                    "module_topic": module_topic,
                    "section_title": "Recipe Card: Signature Truffle Ganache",
                    "chunk_type": "recipe",
                    "text": text,
                    "word_count": len(text.split())
                })
                chunk_idx += 1
                continue

            if page["is_allergen"]:
                # Keep allergen matrix completely unified
                chunks.append({
                    "chunk_id": f"p{page_num}_c{chunk_idx}",
                    "page_num": page_num,
                    "chapter": chapter,
                    "module_num": module_num,
                    "module_topic": module_topic,
                    "section_title": "Autumn Tasting Menu Allergen Matrix",
                    "chunk_type": "allergen",
                    "text": text,
                    "word_count": len(text.split())
                })
                chunk_idx += 1
                continue

            if page["is_safety"]:
                # Keep HACCP food safety standards completely unified
                chunks.append({
                    "chunk_id": f"p{page_num}_c{chunk_idx}",
                    "page_num": page_num,
                    "chapter": chapter,
                    "module_num": module_num,
                    "module_topic": module_topic,
                    "section_title": "HACCP Food Safety & Sous-Vide Pasteurization",
                    "chunk_type": "food_safety",
                    "text": text,
                    "word_count": len(text.split())
                })
                chunk_idx += 1
                continue

            # Standard structured operational pages: chunk by logical clauses
            clauses = re.split(r'(?=\d+\.\s+Overview|\d+\.\s+Standard|\d+\.\s+Archival)', text)
            clauses = [c.strip() for c in clauses if c.strip()]

            if not clauses:
                clauses = [text]

            # Header info for context
            header_prefix = f"Chapter {chapter} | Module {module_num}: {module_topic} (Page {page_num})\n"

            for c in clauses:
                # Extract clause title if present
                title_match = re.match(r'^\d+\.\s*([^\n\(]+)', c)
                clause_title = title_match.group(1).strip() if title_match else module_topic

                chunk_text = header_prefix + c
                chunks.append({
                    "chunk_id": f"p{page_num}_c{chunk_idx}",
                    "page_num": page_num,
                    "chapter": chapter,
                    "module_num": module_num,
                    "module_topic": module_topic,
                    "section_title": clause_title,
                    "chunk_type": "operations",
                    "text": chunk_text,
                    "word_count": len(chunk_text.split())
                })
                chunk_idx += 1

        return chunks

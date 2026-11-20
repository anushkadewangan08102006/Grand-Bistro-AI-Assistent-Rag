import os
import re
from typing import List, Dict, Any
import pypdf

class PDFIngestionService:
    def __init__(self, pdf_path: str = None):
        self.pdf_path = pdf_path

    def extract_pages(self, pdf_path: str = None) -> List[Dict[str, Any]]:
        target_path = pdf_path or self.pdf_path
        if not target_path or not os.path.exists(target_path):
            raise FileNotFoundError(f"PDF document not found at: {target_path}")

        reader = pypdf.PdfReader(target_path)
        pages_data = []

        for index, page in enumerate(reader.pages):
            page_num = index + 1
            raw_text = page.extract_text() or ""
            cleaned_text = self._clean_text(raw_text)

            # Metadata extraction
            chapter_match = re.search(r"CHAPTER\s+(\d+)", cleaned_text, re.IGNORECASE)
            chapter = int(chapter_match.group(1)) if chapter_match else ((page_num - 1) // 10) + 1

            module_match = re.search(r"MODULE\s+([\d\.]+):?\s*([^\n\=]+)", cleaned_text, re.IGNORECASE)
            module_num = module_match.group(1) if module_match else f"{page_num}.0"
            module_topic = module_match.group(2).strip() if module_match else "Culinary Standard Clause"

            is_recipe = "RECIPE CARD" in cleaned_text or "Signature Truffle Ganache" in cleaned_text
            is_allergen = "ALLERGEN MATRIX" in cleaned_text or "TREE NUTS" in cleaned_text or "Autumn Tasting Menu" in cleaned_text
            is_safety = "HACCP" in cleaned_text or "PASTEURIZATION" in cleaned_text or "Sous-Vide" in cleaned_text or "Salmonella" in cleaned_text

            pages_data.append({
                "page_num": page_num,
                "text": cleaned_text,
                "chapter": chapter,
                "module_num": module_num,
                "module_topic": module_topic,
                "is_recipe": is_recipe,
                "is_allergen": is_allergen,
                "is_safety": is_safety,
                "char_count": len(cleaned_text),
                "word_count": len(cleaned_text.split())
            })

        return pages_data

    def _clean_text(self, text: str) -> str:
        # Normalize newlines and excess whitespace while preserving paragraph breaks
        lines = [line.strip() for line in text.splitlines()]
        cleaned = "\n".join([l for l in lines if l])
        return cleaned

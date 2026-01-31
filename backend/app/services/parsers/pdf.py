from pypdf import PdfReader
from .base import BaseParser
from typing import Tuple

class PdfParser(BaseParser):
    def parse(self, file_path: str) -> Tuple[str, str]:
        try:
            reader = PdfReader(file_path)
            full_text = []
            
            for i, page in enumerate(reader.pages):
                text = page.extract_text()
                if text:
                    # Add page marker to each line to ensure visibility in snippets
                    lines = text.split('\n')
                    for line in lines:
                        if line.strip():
                            full_text.append(f"[Page:{i+1}] {line}")
                    
            return "\n".join(full_text), ""
        except Exception:
            return "", "" # Encrypted or unreadable PDF

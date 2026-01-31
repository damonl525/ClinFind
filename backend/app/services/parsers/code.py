import re
from .base import BaseParser
from typing import Tuple

class CodeParser(BaseParser):
    def __init__(self, file_type: str):
        self.file_type = file_type
        
    def parse(self, file_path: str) -> Tuple[str, str]:
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
        except UnicodeDecodeError:
            # Fallback for legacy encoding (e.g. GBK/Windows-1252)
            try:
                with open(file_path, 'r', encoding='gb18030') as f:
                    content = f.read()
            except Exception:
                return "", ""
                
        keywords = self._extract_keywords(content)
        return content, keywords
    
    def _extract_keywords(self, content: str) -> str:
        keywords = []
        if self.file_type == 'sas':
            # Extract PROC steps and DATA steps
            keywords.extend(re.findall(r'proc\s+(\w+)', content, re.IGNORECASE))
            keywords.extend(re.findall(r'data\s+(\w+)', content, re.IGNORECASE))
        elif self.file_type == 'python':
            # Extract function and class definitions
            keywords.extend(re.findall(r'def\s+(\w+)', content))
            keywords.extend(re.findall(r'class\s+(\w+)', content))
        elif self.file_type == 'r':
             # Extract function assignments: my_func <- function(...)
             keywords.extend(re.findall(r'(\w+)\s*<-\s*function', content))
             
        return " ".join(set(keywords)) # Deduplicate

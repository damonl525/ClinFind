from striprtf.striprtf import rtf_to_text
from .base import BaseParser
from typing import Tuple

class TextParser(BaseParser):
    def parse(self, file_path: str) -> Tuple[str, str]:
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                return f.read(), ""
        except UnicodeDecodeError:
             try:
                with open(file_path, 'r', encoding='gb18030') as f:
                    return f.read(), ""
             except:
                 return "", ""

class RtfParser(BaseParser):
    def parse(self, file_path: str) -> Tuple[str, str]:
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
                return rtf_to_text(content), ""
        except:
             # RTF usually ASCII, but just in case
             try:
                 with open(file_path, 'r', encoding='mbcs') as f: # Windows default
                    content = f.read()
                    return rtf_to_text(content), ""
             except:
                 return "", ""

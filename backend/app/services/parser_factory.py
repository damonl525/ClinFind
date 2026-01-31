import os
from .parsers.office import DocxParser, XlsxParser, PptxParser
from .parsers.code import CodeParser
from .parsers.pdf import PdfParser
from .parsers.text import TextParser, RtfParser
from .parsers.base import BaseParser

class ParserFactory:
    _parsers = {}

    @classmethod
    def get_parser(cls, file_path: str) -> BaseParser:
        ext = os.path.splitext(file_path)[1].lower()
        
        if ext in cls._parsers:
            return cls._parsers[ext]
            
        # Initialize parser based on extension
        if ext == '.docx':
            parser = DocxParser()
        elif ext == '.xlsx':
            parser = XlsxParser()
        elif ext == '.pptx':
            parser = PptxParser()
        elif ext == '.pdf':
            parser = PdfParser()
        elif ext == '.rtf':
            parser = RtfParser()
        elif ext in ['.txt', '.log', '.csv', '.md', '.json']:
            parser = TextParser()
        elif ext == '.sas':
            parser = CodeParser('sas')
        elif ext in ['.py', '.pyw']:
            parser = CodeParser('python')
        elif ext in ['.r', '.rh']:
            parser = CodeParser('r')
        else:
            return None
            
        cls._parsers[ext] = parser
        return parser

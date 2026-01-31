from abc import ABC, abstractmethod
from typing import Tuple

class BaseParser(ABC):
    """Abstract base class for all file parsers."""
    
    @abstractmethod
    def parse(self, file_path: str) -> Tuple[str, str]:
        """
        Parse file and return content and keywords.
        
        Args:
            file_path: Absolute path to the file.
            
        Returns:
            Tuple[str, str]: (content, keywords)
            - content: Full text content for indexing.
            - keywords: High-value keywords (e.g. function names) for boosting.
        """
        pass

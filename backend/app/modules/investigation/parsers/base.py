from abc import ABC, abstractmethod
from typing import Iterator
from app.modules.investigation.schemas import NormalizedEventCreate

class BaseParser(ABC):
    """
    Abstract base class for all deterministic log parsers.
    """
    
    @classmethod
    @abstractmethod
    def can_parse(cls, sample: bytes) -> bool:
        """
        Determine if this parser can parse the given sample of the file (e.g., first 4KB).
        """
        pass
        
    @abstractmethod
    def parse_file(self, file_path: str) -> Iterator[NormalizedEventCreate]:
        """
        Parse the file and yield normalized events one by one to keep memory footprint low.
        """
        pass

from abc import ABC, abstractmethod
from typing import List, Tuple
from app.modules.investigation.schemas import NormalizedEventCreate

class BaseIOCExtractor(ABC):
    """
    Abstract base class for all IOC extractor plugins.
    """
    @abstractmethod
    def extract(self, event: NormalizedEventCreate) -> List[Tuple[str, str]]:
        """
        Extract IOCs from the normalized event.
        Returns a list of tuples (ioc_type, ioc_value).
        """
        pass

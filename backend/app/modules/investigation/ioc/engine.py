from typing import List, Tuple
from app.modules.investigation.schemas import NormalizedEventCreate
from app.modules.investigation.ioc.base import BaseIOCExtractor
from app.modules.investigation.ioc.extractors import (
    IPv4Extractor, IPv6Extractor, DomainExtractor, URLExtractor,
    HashExtractor, CVEExtractor, EmailExtractor, HostnameExtractor, UsernameExtractor
)

class IOCEngine:
    def __init__(self):
        self.plugins: List[BaseIOCExtractor] = [
            IPv4Extractor(),
            IPv6Extractor(),
            DomainExtractor(),
            URLExtractor(),
            HashExtractor(),
            CVEExtractor(),
            EmailExtractor(),
            HostnameExtractor(),
            UsernameExtractor()
        ]

    def extract_all(self, event: NormalizedEventCreate) -> List[Tuple[str, str]]:
        """
        Runs all registered IOC extractor plugins against the given event.
        Returns a deduplicated list of (type, value) tuples.
        """
        iocs = []
        for plugin in self.plugins:
            iocs.extend(plugin.extract(event))
            
        # Deduplicate
        return list(set(iocs))

ioc_engine = IOCEngine()

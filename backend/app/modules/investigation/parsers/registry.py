from typing import Type, Optional
from app.modules.investigation.parsers.base import BaseParser

class ParserRegistry:
    def __init__(self):
        self._parsers: list[Type[BaseParser]] = []

    def register(self, parser_class: Type[BaseParser]):
        self._parsers.append(parser_class)

    def detect(self, sample: bytes) -> Optional[Type[BaseParser]]:
        """
        Detects the correct parser for the sample by iterating through registered parsers.
        """
        for parser in self._parsers:
            if parser.can_parse(sample):
                return parser
        return None

# Global registry instance
parser_registry = ParserRegistry()

from app.modules.investigation.parsers.registry import parser_registry
from app.modules.investigation.parsers.syslog import SyslogParser
from app.modules.investigation.parsers.evtx import EVTXParser
from app.modules.investigation.parsers.json_parser import JSONParser
from app.modules.investigation.parsers.csv_parser import CSVParser
from app.modules.investigation.parsers.cef_parser import CEFParser

# Register all implemented deterministic parsers
parser_registry.register(EVTXParser)
parser_registry.register(CEFParser)
parser_registry.register(JSONParser)
parser_registry.register(CSVParser)
parser_registry.register(SyslogParser)

__all__ = ["parser_registry"]

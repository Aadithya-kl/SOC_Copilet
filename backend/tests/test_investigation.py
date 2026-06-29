import os
from datetime import datetime
from app.modules.investigation.parsers.registry import parser_registry
from app.modules.investigation.schemas import NormalizedEventCreate
from app.modules.investigation.ioc.engine import ioc_engine

FIXTURES_DIR = os.path.join(os.path.dirname(__file__), "fixtures", "logs")

def test_syslog_parser():
    file_path = os.path.join(FIXTURES_DIR, "syslog.log")
    with open(file_path, "rb") as f:
        sample = f.read(4096)
    
    parser_class = parser_registry.detect(sample)
    assert parser_class is not None
    assert parser_class.__name__ == "SyslogParser"
    
    parser = parser_class()
    events = list(parser.parse_file(file_path))
    assert len(events) == 2
    assert events[0].event_provider == "su"
    assert "lonvick" in events[0].raw_message
    
def test_json_parser():
    file_path = os.path.join(FIXTURES_DIR, "test.json")
    with open(file_path, "rb") as f:
        sample = f.read(4096)
        
    parser_class = parser_registry.detect(sample)
    assert parser_class is not None
    assert parser_class.__name__ == "JSONParser"
    
    parser = parser_class()
    events = list(parser.parse_file(file_path))
    assert len(events) == 2
    assert events[0].source_ip == "10.0.0.5"
    assert events[0].user_name == "admin"
    assert events[1].source_ip == "192.168.1.100"

def test_ioc_engine():
    event = NormalizedEventCreate(
        timestamp=datetime.utcnow(),
        raw_message="Suspicious login from 8.8.8.8 using evil-domain.com and hash 44d88612fea8a8f36de82e1278abb02f",
        source_ip="8.8.8.8"
    )
    
    iocs = ioc_engine.extract_all(event)
    ioc_dict = {t: v for t, v in iocs}
    
    assert ioc_dict.get("ipv4") == "8.8.8.8"
    assert ioc_dict.get("domain") == "evil-domain.com"
    assert ioc_dict.get("md5") == "44d88612fea8a8f36de82e1278abb02f"

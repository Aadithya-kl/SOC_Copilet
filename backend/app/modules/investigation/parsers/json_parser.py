import json
from typing import Iterator
from app.modules.investigation.parsers.base import BaseParser
from app.modules.investigation.schemas import NormalizedEventCreate
from datetime import datetime

class JSONParser(BaseParser):
    @classmethod
    def can_parse(cls, sample: bytes) -> bool:
        try:
            text = sample.decode('utf-8', errors='ignore')
            first_line = text.split('\n', 1)[0].strip()
            # If it parses as a JSON dict, it's likely NDJSON
            parsed = json.loads(first_line)
            return isinstance(parsed, dict)
        except Exception:
            return False

    def parse_file(self, file_path: str) -> Iterator[NormalizedEventCreate]:
        with open(file_path, 'r', encoding='utf-8', errors='replace') as f:
            for line in f:
                line = line.strip()
                if not line:
                    continue
                try:
                    data = json.loads(line)
                    
                    # Extract timestamp
                    ts_str = data.get('@timestamp') or data.get('timestamp') or data.get('time')
                    if ts_str:
                        try:
                            ts = datetime.fromisoformat(str(ts_str).replace('Z', '+00:00'))
                        except ValueError:
                            ts = datetime.utcnow()
                    else:
                        ts = datetime.utcnow()
                        
                    yield NormalizedEventCreate(
                        timestamp=ts,
                        event_provider=data.get('event', {}).get('provider') if isinstance(data.get('event'), dict) else data.get('provider'),
                        event_action=data.get('event', {}).get('action') if isinstance(data.get('event'), dict) else data.get('action'),
                        source_ip=data.get('source', {}).get('ip') if isinstance(data.get('source'), dict) else data.get('src_ip'),
                        destination_ip=data.get('destination', {}).get('ip') if isinstance(data.get('destination'), dict) else data.get('dest_ip'),
                        user_name=data.get('user', {}).get('name') if isinstance(data.get('user'), dict) else data.get('username'),
                        host_name=data.get('host', {}).get('name') if isinstance(data.get('host'), dict) else data.get('hostname'),
                        raw_message=line
                    )
                except json.JSONDecodeError:
                    yield NormalizedEventCreate(
                        timestamp=datetime.utcnow(),
                        raw_message=line
                    )

import re
from typing import Iterator
from app.modules.investigation.parsers.base import BaseParser
from app.modules.investigation.schemas import NormalizedEventCreate
from datetime import datetime

class SyslogParser(BaseParser):
    # Matches common syslog formats, e.g., "<34>Oct 11 22:14:15 mymachine su: 'su root' failed"
    # Or "Oct 11 22:14:15 mymachine su: ..."
    SYSLOG_REGEX = re.compile(
        r'^(?:<(?P<pri>\d+)>)?'
        r'(?P<timestamp>[A-Z][a-z]{2}\s+\d+\s+\d{2}:\d{2}:\d{2}|'
        r'\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}(?:\.\d+)?(?:Z|[+-]\d{2}:\d{2}))\s+'
        r'(?P<host>\S+)\s+'
        r'(?P<program>[a-zA-Z0-9_\/\-]+)(?:\[(?P<pid>\d+)\])?:\s+'
        r'(?P<message>.*)$'
    )

    @classmethod
    def can_parse(cls, sample: bytes) -> bool:
        try:
            text = sample.decode('utf-8', errors='ignore')
            first_line = text.split('\n', 1)[0].strip()
            return bool(cls.SYSLOG_REGEX.match(first_line))
        except Exception:
            return False

    def parse_file(self, file_path: str) -> Iterator[NormalizedEventCreate]:
        with open(file_path, 'r', encoding='utf-8', errors='replace') as f:
            for line in f:
                line = line.strip()
                if not line:
                    continue
                
                match = self.SYSLOG_REGEX.match(line)
                if match:
                    groupdict = match.groupdict()
                    
                    # Parse timestamp (rudimentary, just using now if unparseable easily)
                    # In a real system, we'd handle the exact syslog time format mapping
                    timestamp_str = groupdict.get('timestamp')
                    try:
                        # Attempt ISO format first
                        if timestamp_str and 'T' in timestamp_str:
                            ts = datetime.fromisoformat(timestamp_str.replace('Z', '+00:00'))
                        elif timestamp_str:
                            # E.g., "Oct 11 22:14:15" -> add current year
                            year = datetime.utcnow().year
                            ts = datetime.strptime(f"{year} {timestamp_str}", "%Y %b %d %H:%M:%S")
                    except Exception:
                        ts = datetime.utcnow()

                    yield NormalizedEventCreate(
                        timestamp=ts,
                        event_provider=groupdict.get('program'),
                        event_action=None,
                        source_ip=None, # Cannot reliably extract from standard syslog header
                        destination_ip=None,
                        user_name=None,
                        host_name=groupdict.get('host'),
                        raw_message=line
                    )
                else:
                    # Fallback for unrecognized lines in syslog
                    yield NormalizedEventCreate(
                        timestamp=datetime.utcnow(),
                        raw_message=line
                    )

import re
from typing import Iterator
from app.modules.investigation.parsers.base import BaseParser
from app.modules.investigation.schemas import NormalizedEventCreate
from datetime import datetime

class CEFParser(BaseParser):
    CEF_REGEX = re.compile(r'^CEF:\d+\|([^|]*)\|([^|]*)\|([^|]*)\|([^|]*)\|([^|]*)\|([^|]*)\|(.*)$')

    @classmethod
    def can_parse(cls, sample: bytes) -> bool:
        try:
            text = sample.decode('utf-8', errors='ignore')
            first_line = text.split('\n', 1)[0].strip()
            # If syslog prefix is prepended, find where CEF starts
            cef_idx = first_line.find("CEF:")
            if cef_idx >= 0:
                match = cls.CEF_REGEX.match(first_line[cef_idx:])
                return bool(match)
            return False
        except Exception:
            return False

    def parse_file(self, file_path: str) -> Iterator[NormalizedEventCreate]:
        with open(file_path, 'r', encoding='utf-8', errors='replace') as f:
            for line in f:
                line = line.strip()
                if not line:
                    continue
                
                cef_idx = line.find("CEF:")
                if cef_idx >= 0:
                    match = self.CEF_REGEX.match(line[cef_idx:])
                    if match:
                        vendor, product, version, event_class, name, severity, extension = match.groups()
                        
                        # Parse extension as key=value
                        ext_dict = {}
                        if extension:
                            # Split by space, but handle spaces in values if needed (naive split for now)
                            # A real CEF parser uses a more robust regex for extension splitting
                            ext_pairs = re.findall(r'(\w+)=([^=\s]+(?:\s+[^=\s]+)*?)(?=\s+\w+=|$)', extension)
                            for k, v in ext_pairs:
                                ext_dict[k] = v
                                
                        # Extract timestamp
                        ts_str = ext_dict.get('rt') or ext_dict.get('end')
                        ts = datetime.utcnow()
                        if ts_str:
                            try:
                                # Try standard epoch string or format
                                if ts_str.isdigit():
                                    ts = datetime.fromtimestamp(int(ts_str[:10]))
                            except Exception:
                                pass
                                
                        yield NormalizedEventCreate(
                            timestamp=ts,
                            event_provider=f"{vendor} {product}",
                            event_action=name,
                            source_ip=ext_dict.get('src'),
                            destination_ip=ext_dict.get('dst'),
                            user_name=ext_dict.get('suser') or ext_dict.get('duser'),
                            host_name=ext_dict.get('shost') or ext_dict.get('dhost'),
                            raw_message=line
                        )
                        continue
                
                # Fallback for unrecognized lines
                yield NormalizedEventCreate(
                    timestamp=datetime.utcnow(),
                    raw_message=line
                )

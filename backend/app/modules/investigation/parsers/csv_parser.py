import csv
from typing import Iterator
from app.modules.investigation.parsers.base import BaseParser
from app.modules.investigation.schemas import NormalizedEventCreate
from datetime import datetime
import io

class CSVParser(BaseParser):
    @classmethod
    def can_parse(cls, sample: bytes) -> bool:
        try:
            text = sample.decode('utf-8', errors='ignore')
            first_line = text.split('\n', 1)[0].strip()
            # Simple heuristic: must have at least 2 commas
            if first_line.count(',') < 2:
                return False
            # Check if it parses as CSV headers
            reader = csv.reader([first_line])
            headers = next(reader)
            return len(headers) > 2
        except Exception:
            return False

    def parse_file(self, file_path: str) -> Iterator[NormalizedEventCreate]:
        with open(file_path, 'r', encoding='utf-8', errors='replace') as f:
            reader = csv.DictReader(f)
            for row in reader:
                # Naive mapping by looking for common CSV headers
                ts_str = row.get('timestamp') or row.get('time') or row.get('date')
                if ts_str:
                    try:
                        ts = datetime.fromisoformat(str(ts_str).replace('Z', '+00:00'))
                    except ValueError:
                        ts = datetime.utcnow()
                else:
                    ts = datetime.utcnow()
                
                # Reconstruct raw message
                out = io.StringIO()
                csv.writer(out).writerow(row.values())
                raw_message = out.getvalue().strip()
                
                yield NormalizedEventCreate(
                    timestamp=ts,
                    event_provider=row.get('provider') or row.get('source'),
                    event_action=row.get('action') or row.get('event_id'),
                    source_ip=row.get('src_ip') or row.get('source_ip'),
                    destination_ip=row.get('dest_ip') or row.get('destination_ip'),
                    user_name=row.get('user') or row.get('username'),
                    host_name=row.get('host') or row.get('hostname'),
                    raw_message=raw_message
                )

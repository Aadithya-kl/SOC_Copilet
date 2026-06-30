import json
from typing import Iterator
from evtx import PyEvtxParser
from app.modules.investigation.parsers.base import BaseParser
from app.modules.investigation.schemas import NormalizedEventCreate
from datetime import datetime

class EVTXParser(BaseParser):
    @classmethod
    def can_parse(cls, sample: bytes) -> bool:
        return sample.startswith(b"ElfFile\x00")
        
    def parse_file(self, file_path: str) -> Iterator[NormalizedEventCreate]:
        parser = PyEvtxParser(file_path)
        for record_str in parser.records_json():
            try:
                record = json.loads(record_str)  # type: ignore
                data = json.loads(record['data'])
                # Extract basic EVTX fields
                event = data.get("Event", {})
                if not isinstance(event, dict):
                    event = {}
                system = event.get("System", {})
                if not isinstance(system, dict):
                    system = {}
                event_data = event.get("EventData", {})
                if not isinstance(event_data, dict):
                    event_data = {}
                
                # EVTX System fields
                provider = system.get("Provider", {}).get("#attributes", {}).get("Name")
                event_id = system.get("EventID")
                time_created_str = system.get("TimeCreated", {}).get("#attributes", {}).get("SystemTime")
                
                if time_created_str:
                    try:
                        timestamp = datetime.fromisoformat(time_created_str.replace("Z", "+00:00"))
                    except ValueError:
                        timestamp = datetime.utcnow()
                else:
                    timestamp = datetime.utcnow()

                # IP extraction based on common fields (e.g. 4624 Logon)
                source_ip = event_data.get("IpAddress")
                user_name = event_data.get("TargetUserName") or event_data.get("SubjectUserName")
                host_name = system.get("Computer")
                
                yield NormalizedEventCreate(
                    timestamp=timestamp,
                    event_provider=provider,
                    event_action=str(event_id) if event_id else None,
                    source_ip=source_ip if isinstance(source_ip, str) and source_ip != "-" else None,
                    destination_ip=None,
                    user_name=user_name if isinstance(user_name, str) else None,
                    host_name=host_name if isinstance(host_name, str) else None,
                    raw_message=record['data']
                )
            except Exception:
                # If a single record fails, we shouldn't fail the whole file
                continue

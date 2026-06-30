import json
import uuid
import tempfile
import os
from datetime import datetime
from minio import Minio
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, update
import redis.asyncio as redis

from app.core.config import settings
from app.models.file_record import FileRecord
from app.models.investigation import InvestigationState
from app.models.normalized_event import NormalizedEvent
from app.models.ioc import IOC
from app.models.incident import Incident
from app.modules.investigation.parsers.registry import parser_registry
from app.modules.investigation.ioc.engine import ioc_engine
from app.modules.threat_intel.aggregator import TIAggregator
from app.modules.mitre.engine import mapping_engine
from app.models.threat_intel import ThreatIntelligence
from app.models.evidence import Evidence, EvidenceTIReference
from app.modules.correlation.engine import CorrelationEngine
from app.modules.graph.engine import RelationshipBuilder
from app.modules.timeline.engine import TimelineEngine

class InvestigationPipeline:
    def __init__(self, session: AsyncSession, redis_client: redis.Redis):
        self.session = session
        self.redis = redis_client
        self.minio_client = Minio(
            f"{settings.MINIO_HOST}:{settings.MINIO_PORT}",
            access_key=settings.MINIO_ROOT_USER,
            secret_key=settings.MINIO_ROOT_PASSWORD,
            secure=settings.MINIO_SECURE
        )

    async def _publish_progress(self, inv_id: uuid.UUID, stage: str, progress: int, events_processed: int, ioc_count: int, status: str):
        channel = f"investigation_{inv_id}_progress"
        message = {
            "investigation_id": str(inv_id),
            "stage": stage,
            "progress": progress,
            "events_processed": events_processed,
            "ioc_count": ioc_count,
            "status": status,
            "timestamp": datetime.utcnow().isoformat()
        }
        await self.redis.publish(channel, json.dumps(message))

    async def run(self, investigation_id: uuid.UUID):
        # Fetch investigation
        result = await self.session.execute(
            select(InvestigationState).where(InvestigationState.id == investigation_id)
        )
        investigation = result.scalar_one_or_none()
        if not investigation:
            return

        # Fetch file record
        file_record_result = await self.session.execute(
            select(FileRecord).where(FileRecord.id == investigation.file_record_id)
        )
        file_record: FileRecord | None = file_record_result.scalar_one_or_none()
        if not file_record:
            investigation.status = "failed"
            investigation.error_message = "File record not found"
            await self.session.commit()
            return

        try:
            investigation.status = "parsing"
            investigation.started_at = datetime.utcnow()
            await self.session.commit()
            
            await self._publish_progress(investigation_id, "parsing", 10, 0, 0, "running")

            # 1. Download to temp file
            bucket_name = "soc-copilot-storage"
            object_name = file_record.stored_path.replace(f"s3://{bucket_name}/", "")
            
            # Read first 4KB to detect format
            response = self.minio_client.get_object(bucket_name, object_name, offset=0, length=4096)
            sample = response.read()
            response.close()
            response.release_conn()
            
            parser_class = parser_registry.detect(sample)
            if not parser_class:
                raise ValueError("Unsupported log format")
            
            parser = parser_class()
            
            with tempfile.NamedTemporaryFile(delete=False) as tmp:
                temp_path = tmp.name
                
            self.minio_client.fget_object(bucket_name, object_name, temp_path)
            
            events_processed = 0
            iocs_extracted = 0
            
            # Batching structures
            event_batch = []
            ioc_batch = []
            BATCH_SIZE = 1000

            # 2. Parse and Extract
            try:
                for event in parser.parse_file(temp_path):
                    # Normalization happens in parser, so this is normalized
                    # Prepare dict for bulk insert
                    event_dict = event.model_dump()
                    event_id = uuid.uuid4()
                    event_dict['id'] = event_id
                    event_dict['organization_id'] = investigation.organization_id
                    event_dict['incident_id'] = investigation.incident_id
                    event_dict['investigation_id'] = investigation_id
                    
                    event_batch.append(event_dict)
                    events_processed += 1
                    
                    # IOC Extraction
                    extracted = ioc_engine.extract_all(event)
                    for ioc_type, ioc_value in extracted:
                        ioc_batch.append({
                            "id": uuid.uuid4(),
                            "organization_id": investigation.organization_id,
                            "incident_id": investigation.incident_id,
                            "investigation_id": investigation_id,
                            "ioc_type": ioc_type,
                            "value": ioc_value,
                            "source_event_id": event_id
                        })
                        iocs_extracted += 1
                        
                    if len(event_batch) >= BATCH_SIZE:
                        await self._flush_batches(event_batch, ioc_batch)
                        event_batch.clear()
                        ioc_batch.clear()
                        
                        # Progress roughly (progress is hard for streaming without pre-calculating total, so we just bump it)
                        await self._publish_progress(investigation_id, "normalizing_and_extracting", 50, events_processed, iocs_extracted, "running")
                
                # Flush remainder
                if event_batch:
                    await self._flush_batches(event_batch, ioc_batch)
                    
                # Phase 3.5: Correlation & Graph
                await self._publish_progress(investigation_id, "correlating", 80, events_processed, iocs_extracted, "running")
                correlation_engine = CorrelationEngine(self.session)
                await correlation_engine.run_correlation(investigation.organization_id, investigation_id)
                
                await self._publish_progress(investigation_id, "building_graph", 90, events_processed, iocs_extracted, "running")
                graph_builder = RelationshipBuilder(self.session)
                await graph_builder.build_projection(investigation_id)
                
                timeline_engine = TimelineEngine(self.session)
                await timeline_engine.generate_summary(investigation_id)
                
                # Update status
                investigation.status = "completed"
                investigation.completed_at = datetime.utcnow()
                investigation.events_processed = events_processed
                investigation.iocs_extracted = iocs_extracted
                await self.session.commit()
                
                await self._publish_progress(investigation_id, "completed", 100, events_processed, iocs_extracted, "completed")
                
                # Update incident stats
                await self.session.execute(
                    update(Incident).where(Incident.id == investigation.incident_id)
                    .values(
                        total_events_count=Incident.total_events_count + events_processed,
                        status="investigating",
                        investigation_started_at=investigation.started_at,
                        investigation_completed_at=investigation.completed_at
                    )
                )
                await self.session.commit()
                
            finally:
                if os.path.exists(temp_path):
                    os.remove(temp_path)
                    
        except Exception as e:
            investigation.status = "failed"
            investigation.error_message = str(e)
            investigation.completed_at = datetime.utcnow()
            await self.session.commit()
            await self._publish_progress(investigation_id, "failed", 0, 0, 0, "failed")

    async def _flush_batches(self, event_batch, ioc_batch):
        from sqlalchemy.dialects.postgresql import insert as pg_insert
        import asyncio
        import uuid
        
        # We need aggregator in scope. Let's create it.
        aggregator = TIAggregator(self.redis_client)
        evidence_batch = []
        ti_batch = []
        ti_ref_batch = []
        
        # We need event objects to evaluate rules. We'll reconstruct them from dicts.
        if event_batch:
            stmt = pg_insert(NormalizedEvent).values(event_batch).on_conflict_do_nothing()
            await self.session.execute(stmt)
            
            for event_dict in event_batch:
                # Rule matching
                event_obj = NormalizedEvent(**event_dict)
                matches = mapping_engine.evaluate_event(event_obj)
                for match in matches:
                    evidence_batch.append({
                        "id": uuid.uuid4(),
                        "organization_id": event_dict["organization_id"],
                        "incident_id": event_dict["incident_id"],
                        "investigation_id": event_dict["investigation_id"],
                        "source_event_id": event_dict["id"],
                        "ioc_id": None,
                        "mitre_technique_id": match["technique_id"],
                        "confidence": match["confidence"],
                        "description": match["description"]
                    })
            
        if ioc_batch:
            stmt = pg_insert(IOC).values(ioc_batch)
            stmt = stmt.on_conflict_do_nothing(
                index_elements=['investigation_id', 'ioc_type', 'value']
            )
            await self.session.execute(stmt)
            
            # Enrich IOCs concurrently
            enrich_tasks = []
            for ioc_dict in ioc_batch:
                enrich_tasks.append(aggregator.enrich_ioc(ioc_dict["ioc_type"], ioc_dict["value"]))
                
            enrich_results = await asyncio.gather(*enrich_tasks, return_exceptions=True)
            
            for ioc_dict, enrich_res in zip(ioc_batch, enrich_results):
                if isinstance(enrich_res, list) and enrich_res:
                    # Create evidence for IOC if there is threat intel
                    high_conf = any(r.confidence > 0.8 for r in enrich_res)
                    med_conf = any(r.confidence > 0.4 for r in enrich_res)
                    
                    if high_conf or med_conf:
                        evidence_id = uuid.uuid4()
                        evidence_batch.append({
                            "id": evidence_id,
                            "organization_id": ioc_dict["organization_id"],
                            "incident_id": ioc_dict["incident_id"],
                            "investigation_id": ioc_dict["investigation_id"],
                            "source_event_id": ioc_dict.get("source_event_id"),
                            "ioc_id": ioc_dict["id"],
                            "mitre_technique_id": None,
                            "confidence": "high" if high_conf else "medium",
                            "description": f"Threat Intelligence found for IOC {ioc_dict['value']}"
                        })
                        
                        # Store TI results
                        for r in enrich_res:
                            ti_id = uuid.uuid4()
                            ti_batch.append({
                                "id": ti_id,
                                "ioc_id": ioc_dict["id"],
                                "provider_name": r.provider_name,
                                "provider_version": r.provider_version,
                                "confidence_score": r.confidence,
                                "weighted_confidence": r.weighted_confidence,
                                "raw_response": r.raw_response,
                                "normalized_response": r.normalized_response,
                                "response_time_ms": r.response_time_ms,
                                "rate_limit_remaining": r.rate_limit_remaining,
                                "cache_hit": r.cache_hit,
                                "error_reason": r.error_reason
                            })
                            ti_ref_batch.append({
                                "id": uuid.uuid4(),
                                "evidence_id": evidence_id,
                                "threat_intel_id": ti_id
                            })

        if ti_batch:
            stmt = pg_insert(ThreatIntelligence).values(ti_batch).on_conflict_do_nothing()
            await self.session.execute(stmt)

        if evidence_batch:
            stmt = pg_insert(Evidence).values(evidence_batch).on_conflict_do_nothing()
            await self.session.execute(stmt)
            
        if ti_ref_batch:
            stmt = pg_insert(EvidenceTIReference).values(ti_ref_batch).on_conflict_do_nothing()
            await self.session.execute(stmt)
            
        await self.session.commit()

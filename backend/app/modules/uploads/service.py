import uuid
import hashlib
from io import BytesIO
from minio import Minio
from sqlalchemy.ext.asyncio import AsyncSession
from typing import Optional

from app.core.config import settings
from app.models.file_record import FileRecord
from app.models.audit_log import AuditLog

class UploadsService:
    def __init__(self, session: AsyncSession):
        self.session = session
        self.minio_client = Minio(
            f"{settings.MINIO_HOST}:{settings.MINIO_PORT}",
            access_key=settings.MINIO_ROOT_USER,
            secret_key=settings.MINIO_ROOT_PASSWORD,
            secure=settings.MINIO_SECURE
        )
        self.bucket_name = "soc-copilot-storage"
        self._ensure_bucket_exists()

    def _ensure_bucket_exists(self):
        if not self.minio_client.bucket_exists(self.bucket_name):
            self.minio_client.make_bucket(self.bucket_name)

    def _calculate_hash(self, content: bytes) -> str:
        return hashlib.sha256(content).hexdigest()

    async def upload_file(
        self,
        file_content: bytes,
        filename: str,
        content_type: str,
        organization_id: uuid.UUID,
        incident_id: uuid.UUID,
        user_id: uuid.UUID,
        ip_address: Optional[str] = None,
        user_agent: Optional[str] = None
    ) -> FileRecord:
        
        file_hash = self._calculate_hash(file_content)
        size_bytes = len(file_content)
        
        object_name = f"{organization_id}/{incident_id}/uploads/{uuid.uuid4()}_{filename}"
        
        # Upload to MinIO
        self.minio_client.put_object(
            bucket_name=self.bucket_name,
            object_name=object_name,
            data=BytesIO(file_content),
            length=size_bytes,
            content_type=content_type
        )
        
        storage_path = f"s3://{self.bucket_name}/{object_name}"
        
        # Create DB Record
        file_record = FileRecord(
            incident_id=incident_id,
            filename=filename,
            storage_path=storage_path,
            content_type=content_type,
            size_bytes=size_bytes,
            hash_sha256=file_hash
        )
        self.session.add(file_record)
        
        # Audit Log
        audit = AuditLog(
            user_id=user_id,
            organization_id=organization_id,
            action="file.uploaded",
            target_type="FileRecord",
            target_id=file_record.id, # id will be set on flush, but actually it's uuid.uuid4() by default in model so it exists
            ip_address=ip_address,
            user_agent=user_agent,
            details={
                "filename": filename,
                "incident_id": str(incident_id),
                "storage_path": storage_path
            }
        )
        self.session.add(audit)
        
        await self.session.commit()
        await self.session.refresh(file_record)
        
        return file_record

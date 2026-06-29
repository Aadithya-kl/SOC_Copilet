from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column
from sqlalchemy.types import DateTime
from sqlalchemy.sql import func
import uuid
from datetime import datetime

class Base(DeclarativeBase):
    pass

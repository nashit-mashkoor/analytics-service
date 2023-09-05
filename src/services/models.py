import uuid

from sqlalchemy import TEXT, TIMESTAMP, Column, ForeignKey, Integer, String
from sqlalchemy.dialects.mysql import VARCHAR
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from sqlalchemy.types import JSON

Base = declarative_base()


class Process(Base):
    __tablename__ = "process"

    id = Column(Integer, primary_key=True, autoincrement="auto")
    uuid = Column(
        VARCHAR(36), default=lambda: str(uuid.uuid4()), unique=True, index=True, nullable=False
    )
    status = Column(Integer, ForeignKey("status.id"))
    status_id = relationship("Status", backref="process")
    configurationId = Column(String(36), unique=True, index=True)
    configurationVersion = Column(Integer, index=True)
    params = Column(JSON, index=True, nullable=True)
    error = Column(JSON, index=True, nullable=True)
    data = Column(JSON, index=True, nullable=True)
    processTime = Column(Integer, index=True)
    createdAt = Column(
        TIMESTAMP(timezone=True), nullable=False, server_default=func.now()
    )
    createdBy = Column(String(36), unique=True, index=True)
    updatedAt = Column(TIMESTAMP(timezone=True), default=None, onupdate=func.now())
    updatedBy = Column(String(36), unique=True, index=True)


class Status(Base):
    __tablename__ = "status"

    id = Column(Integer, primary_key=True, autoincrement="auto")
    value = Column(VARCHAR(256), unique=True, index=True)
    description = Column(TEXT, nullable=True)
    createdAt = Column(
        TIMESTAMP(timezone=True), nullable=False, server_default=func.now()
    )
    createdBy = Column(String(36), unique=True, index=True)
    updatedAt = Column(TIMESTAMP(timezone=True), default=None, onupdate=func.now())
    updatedBy = Column(String(36), unique=True, index=True)

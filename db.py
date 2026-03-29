import os
from datetime import datetime

from sqlalchemy import (
    create_engine,
    Column,
    Integer,
    String,
    Float,
    Text,
    DateTime,
)
from sqlalchemy.orm import declarative_base, sessionmaker

DATABASE_URL = os.getenv("DATABASE_URL")

engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()


class SignalLog(Base):
    __tablename__ = "signal_logs"

    id = Column(Integer, primary_key=True, index=True)
    created_at = Column(DateTime, default=datetime.utcnow, index=True)

    cmd = Column(String(20), index=True)
    order_type = Column(String(20), index=True)
    symbol = Column(String(50), index=True)

    volume = Column(Float)
    price = Column(Float)
    sl = Column(Float)
    tp = Column(Float)

    magic = Column(Integer, index=True)
    comment = Column(String(200))
    ticket_to_modify = Column(Integer)
    cmd_id = Column(String(100), index=True)

    status = Column(String(50), default="received")
    raw_body = Column(Text)

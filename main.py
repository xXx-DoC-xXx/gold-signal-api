from fastapi import FastAPI, HTTPException, Depends, Query
from pydantic import BaseModel
from typing import List
import json
import os

from sqlalchemy.orm import Session
from db import Base, engine, SessionLocal, SignalLog

app = FastAPI()

# --- DB startup ---
@app.on_event("startup")
def on_startup():
    Base.metadata.create_all(bind=engine)

# --- file storage for last signal (όπως πριν) ---
SIGNAL_FILE = "last_signal.json"


class Signal(BaseModel):
    cmd: str          # OPEN, MODIFY, CLOSE
    order_type: str   # BUY, SELL, BUY_LIMIT, SELL_LIMIT, BUY_STOP, SELL_STOP
    symbol: str
    volume: float
    price: float | None = None
    sl: float | None = None
    tp: float | None = None
    magic: int | None = 0
    comment: str | None = ""
    ticket_to_modify: int | None = 0
    cmd_id: str


# --- DB dependency ---
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@app.post("/signal")
def set_signal(signal: Signal, db: Session = Depends(get_db)):
    # 1. γράφουμε το τελευταίο σήμα σε αρχείο (για το EA)
    with open(SIGNAL_FILE, "w", encoding="utf-8") as f:
        json.dump(signal.dict(), f)

    # 2. log στη PostgreSQL
    log = SignalLog(
        cmd=signal.cmd,
        order_type=signal.order_type,
        symbol=signal.symbol,
        volume=signal.volume,
        price=signal.price,
        sl=signal.sl,
        tp=signal.tp,
        magic=signal.magic,
        comment=signal.comment,
        ticket_to_modify=signal.ticket_to_modify,
        cmd_id=signal.cmd_id,
        status="received",
        raw_body=json.dumps(signal.dict(), ensure_ascii=False),
    )
    db.add(log)
    db.commit()
    db.refresh(log)

    return {"status": "ok", "id": log.id}


@app.get("/signal")
def get_signal():
    if not os.path.exists(SIGNAL_FILE):
        return {"status": "none"}
    with open(SIGNAL_FILE, "r", encoding="utf-8") as f:
        data = json.load(f)
    return data


@app.get("/signals/recent")
def get_recent_signals(
    limit: int = Query(50, le=500),
    db: Session = Depends(get_db),
):
    logs = (
        db.query(SignalLog)
        .order_by(SignalLog.id.desc())
        .limit(limit)
        .all()
    )
    return [
        {
            "id": l.id,
            "created_at": l.created_at,
            "cmd": l.cmd,
            "order_type": l.order_type,
            "symbol": l.symbol,
            "volume": l.volume,
            "price": l.price,
            "sl": l.sl,
            "tp": l.tp,
            "magic": l.magic,
            "status": l.status,
            "cmd_id": l.cmd_id,
        }
        for l in logs
    ]

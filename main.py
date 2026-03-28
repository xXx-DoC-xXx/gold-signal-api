from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import json
import os

app = FastAPI()

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

@app.post("/signal")
def set_signal(signal: Signal):
    with open(SIGNAL_FILE, "w", encoding="utf-8") as f:
        json.dump(signal.dict(), f)
    return {"status": "ok"}

@app.get("/signal")
def get_signal():
    if not os.path.exists(SIGNAL_FILE):
        return {"status": "none"}
    with open(SIGNAL_FILE, "r", encoding="utf-8") as f:
        data = json.load(f)
    return data

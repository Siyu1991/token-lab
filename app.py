"""Token 可视化 + 成本计算器（不跑模型，只做分词）。"""
import os
from pathlib import Path
import tiktoken
from fastapi import FastAPI
from fastapi.responses import HTMLResponse
from pydantic import BaseModel

ENCODINGS = ["o200k_base", "cl100k_base"]
_cache = {}
MAX_CHARS = 20000

def enc(name):
    if name not in _cache:
        _cache[name] = tiktoken.get_encoding(name)
    return _cache[name]

app = FastAPI(title="Token Lab")

class Req(BaseModel):
    text: str
    encoding: str = "o200k_base"

@app.get("/", response_class=HTMLResponse)
def index():
    return (Path(__file__).parent / "static" / "index.html").read_text(encoding="utf-8")

@app.post("/api/tokenize")
def tokenize(r: Req):
    if r.encoding not in ENCODINGS:
        return {"error": "unknown encoding"}
    text = r.text[:MAX_CHARS]
    e = enc(r.encoding)
    ids = e.encode(text)
    pieces = [e.decode_single_token_bytes(i).decode("utf-8", errors="replace") for i in ids]
    return {"encoding": r.encoding, "chars": len(text), "count": len(ids),
            "tokens": [{"id": i, "text": p} for i, p in zip(ids, pieces)]}

@app.get("/healthz")
def health():
    return {"ok": True}

"""Persistent JSON vector index for Gemini caption embeddings."""
import json
import math
from pathlib import Path
from datetime import datetime, timezone

ROOT = Path(__file__).resolve().parents[1]
INDEX_PATH = ROOT / "data" / "caption_vectors.json"
MODEL = "gemini-embedding-001"

def _load():
    if not INDEX_PATH.exists():
        return {"model": MODEL, "updated_at": None, "vectors": {}}
    try:
        data = json.loads(INDEX_PATH.read_text(encoding="utf-8"))
        if data.get("model") != MODEL or not isinstance(data.get("vectors"), dict):
            return {"model": MODEL, "updated_at": None, "vectors": {}}
        return data
    except (OSError, json.JSONDecodeError):
        return {"model": MODEL, "updated_at": None, "vectors": {}}

def _save(data):
    INDEX_PATH.parent.mkdir(parents=True, exist_ok=True)
    temp = INDEX_PATH.with_suffix(".tmp")
    temp.write_text(json.dumps(data, ensure_ascii=False), encoding="utf-8")
    temp.replace(INDEX_PATH)

def upsert(image_id, text, vector):
    data = _load()
    data["vectors"][str(image_id)] = {
        "text": text, "embedding": [float(x) for x in vector],
        "updated_at": datetime.now(timezone.utc).isoformat()
    }
    data["updated_at"] = datetime.now(timezone.utc).isoformat()
    _save(data)

def remove(image_id):
    data = _load()
    data["vectors"].pop(str(image_id), None)
    data["updated_at"] = datetime.now(timezone.utc).isoformat()
    _save(data)

def get_indexed_ids():
    return set(_load()["vectors"].keys())

def index_stats():
    data = _load()
    return {"count": len(data["vectors"]), "updated_at": data.get("updated_at"), "model": data.get("model")}

def search(vector, records, top_k=30, min_score=0.25):
    data = _load()
    record_map = {str(r["id"]): r for r in records}
    ranked = []
    for image_id, item in data["vectors"].items():
        record = record_map.get(image_id)
        if not record: continue
        candidate = item.get("embedding", [])
        if len(candidate) != len(vector) or not candidate: continue
        dot = sum(float(a) * float(b) for a, b in zip(vector, candidate))
        na = math.sqrt(sum(float(a) ** 2 for a in vector))
        nb = math.sqrt(sum(float(b) ** 2 for b in candidate))
        score = dot / (na * nb) if na and nb else 0.0
        if score >= min_score:
            ranked.append((score, record))
    ranked.sort(key=lambda x: x[0], reverse=True)
    return [(r, score) for score, r in ranked[:top_k]]

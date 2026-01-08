# NaMo Train (Cloud Ready) — core.py
# FastAPI app: Vertex AI (google-genai) + Firestore + BigQuery
# Cloud Run friendly (uses PORT env)
import os, uuid, json, datetime, logging
from typing import Optional, List, Dict, Any
import yaml
from fastapi import FastAPI, HTTPException, Query
from pydantic import BaseModel, Field
from google.cloud import firestore, bigquery
from google.api_core.exceptions import NotFound
from google import genai
from google.genai import types as genai_types
logging.basicConfig(level=logging.INFO)
log = logging.getLogger("namo-train")
app = FastAPI(title="NaMo Train (Cloud Ready)")
# ------------ Env Defaults -----------PROJECT_ID = os.getenv("GOOGLE_CLOUD_PROJECT", "")
GENAI_LOCATION = os.getenv("GOOGLE_CLOUD_LOCATION", "global")
os.environ.setdefault("GOOGLE_GENAI_USE_VERTEXAI", "True")
BQ_DATASET = os.getenv("BQ_DATASET", "namo_memory")
BQ_TABLE = os.getenv("BQ_TABLE", "long_term_memories")
BQ_LOCATION = os.getenv("BQ_LOCATION", "asia-southeast1")
FS_COLLECTION = os.getenv("FS_COLLECTION_EMOTIONS", "emotion_events")
EMBEDDING_MODEL = os.getenv("EMBEDDING_MODEL", "gemini-embedding-001")
GENERATIVE_MODEL = os.getenv("GENERATIVE_MODEL", "gemini-2.0-flash")
MEMORY_YAML_PATH = os.getenv("MEMORY_YAML", "memory.yaml")
# ------------ Clients -----------genai_client = genai.Client()
bq_client = bigquery.Client(project=PROJECT_ID, location=BQ_LOCATION) if
PROJECT_ID else bigquery.Client()
fs_client = firestore.Client(project=PROJECT_ID) if PROJECT_ID else firestore.Client()
# ------------ Models -----------class MemoryIn(BaseModel):
text: str
user_id: Optional[str] = None
source: Optional[str] = "api"

metadata: Optional[Dict[str, Any]] = None
class MemoryRow(BaseModel):
id: str
created_at: datetime.datetime
text: str
embedding: List[float]
user_id: Optional[str] = None
source: Optional[str] = None
metadata: Optional[Dict[str, Any]] = None
class MemoryHit(BaseModel):
id: str
text: str
score: float
created_at: datetime.datetime
user_id: Optional[str] = None
source: Optional[str] = None
metadata: Optional[Dict[str, Any]] = None
class EmotionIn(BaseModel):
text: str
user_id: Optional[str] = None
context: Optional[str] = None
persist_memory: bool = False
class EmotionOut(BaseModel):
label: str
score: float
distribution: Dict[str, float]
actions: List[str] = []
memory_row_id: Optional[str] = None
firestore_doc_id: Optional[str] = None
model: Dict[str, str] = Field(default_factory=dict)
# ------------ Utilities -----------def load_memory_yaml():
try:
with open(MEMORY_YAML_PATH, "r", encoding="utf-8") as f:
return yaml.safe_load(f)
except FileNotFoundError:
log.warning("memory.yaml not found; using env defaults")
return {}
def ensure_bq_table():
cfg = load_memory_yaml().get("bigquery", {})
dataset_id = cfg.get("dataset_id", BQ_DATASET)
table_id = cfg.get("table_id", BQ_TABLE)

location = cfg.get("location", BQ_LOCATION)
dataset_ref = bigquery.Dataset(f"{PROJECT_ID}.{dataset_id}")
dataset_ref.location = location
try:
bq_client.get_dataset(dataset_ref)
except NotFound:
log.info(f"Creating dataset {PROJECT_ID}.{dataset_id} in {location}")
bq_client.create_dataset(dataset_ref, exists_ok=True)
schema_cfg = cfg.get("schema") or [
{"name": "id", "type": "STRING", "mode": "REQUIRED", "description": "UUID"},
{"name": "created_at", "type": "TIMESTAMP", "mode": "REQUIRED", "description":
"Creation time"},
{"name": "text", "type": "STRING", "mode": "REQUIRED", "description": "Content"},
{"name": "embedding", "type": "FLOAT64", "mode": "REPEATED", "description":
"Embedding"},
{"name": "user_id", "type": "STRING", "mode": "NULLABLE", "description": "User id"},
{"name": "source", "type": "STRING", "mode": "NULLABLE", "description": "Source
tag"},
{"name": "metadata", "type": "JSON", "mode": "NULLABLE", "description": "Metadata"},
]
schema = [
bigquery.SchemaField(s["name"], s["type"], mode=s.get("mode", "NULLABLE"),
description=s.get("description", ""))
for s in schema_cfg
]
table_ref = f"{PROJECT_ID}.{dataset_id}.{table_id}"
try:
bq_client.get_table(table_ref)
except NotFound:
log.info(f"Creating table {table_ref}")
table = bigquery.Table(table_ref, schema=schema)
if cfg.get("partitioning", {}).get("field") == "created_at":
table.time_partitioning = bigquery.TimePartitioning(field="created_at")
cluster_fields = (cfg.get("clustering") or {}).get("fields")
if cluster_fields:
table.clustering_fields = cluster_fields
bq_client.create_table(table)
return dataset_id, table_id
def get_table_ref():
dataset_id, table_id = ensure_bq_table()
return f"{PROJECT_ID}.{dataset_id}.{table_id}"

def embed_texts(texts: List[str]) -> List[List[float]]:
resp = genai_client.models.embed_content(
model=os.getenv("EMBEDDING_MODEL", EMBEDDING_MODEL),
contents=texts,
config=genai_types.EmbedContentConfig(),
)
return [list(e.values) for e in resp.embeddings]
def classify_emotion(text: str, context: Optional[str] = None) -> Dict[str, Any]:
sys = (
"You are an emotion classifier. "
"Return a compact JSON with keys: label (one of: joy, sadness, anger, fear, surprise,
neutral), "
"score (0..1), distribution (object of the same labels with 0..1), and actions (array of
short suggestions). "
"No narration."
)
user_prompt = f"TEXT: {text}\n" + (f"CONTEXT: {context}" if context else "")
result = genai_client.models.generate_content(
model=os.getenv("GENERATIVE_MODEL", GENERATIVE_MODEL),
contents=user_prompt,
config=genai_types.GenerateContentConfig(
system_instruction=sys,
response_mime_type="application/json"
),
)
try:
data = json.loads(result.text)
return {
"label": str(data.get("label", "neutral")).lower(),
"score": float(data.get("score", 0.0)),
"distribution": data.get("distribution", {}),
"actions": data.get("actions", []),
}
except Exception:
return {"label": "neutral", "score": 0.0, "distribution": {"neutral": 1.0}, "actions": []}
# ------------ API Routes -----------@app.get("/healthz")
def healthz():
return {
"ok": True,
"project": PROJECT_ID,
"bq_dataset": BQ_DATASET,
"bq_table": BQ_TABLE,
"fs_collection": FS_COLLECTION,
"embedding_model": EMBEDDING_MODEL,
"generative_model": GENERATIVE_MODEL,

"location": GENAI_LOCATION,
}
@app.post("/memory", response_model=MemoryRow)
def create_memory(body: MemoryIn):
table_ref = get_table_ref()
emb = embed_texts([body.text])[0]
row_id = str(uuid.uuid4())
created_at = datetime.datetime.utcnow().isoformat()
bq_row = {
"id": row_id,
"created_at": created_at,
"text": body.text,
"embedding": emb,
"user_id": body.user_id,
"source": body.source,
"metadata": body.metadata,
}
errors = bq_client.insert_rows_json(table_ref, [bq_row])
if errors:
raise HTTPException(status_code=500, detail=f"BigQuery insert failed: {errors}")
return MemoryRow(
id=row_id,
created_at=datetime.datetime.fromisoformat(created_at),
text=body.text,
embedding=emb,
user_id=body.user_id,
source=body.source,
metadata=body.metadata,
)
@app.get("/memory/search", response_model=List[MemoryHit])
def memory_search(q: str = Query(..., description="query text"),
top_k: int = Query(5, ge=1, le=50)):
table_ref = get_table_ref()
q_emb = embed_texts([q])[0]
query = f"""
DECLARE q_emb ARRAY<FLOAT64>;
SET q_emb = @embedding;
SELECT
id, text, user_id, source, metadata, created_at,
1 - ML.DISTANCE(embedding, q_emb, 'COSINE') AS score
FROM `{table_ref}`
ORDER BY score DESC
LIMIT @k
"""

job_config = bigquery.QueryJobConfig(
query_parameters=[
bigquery.ArrayQueryParameter("embedding", "FLOAT64", q_emb),
bigquery.ScalarQueryParameter("k", "INT64", top_k),
]
)
results = bq_client.query(query, job_config=job_config).result()
return [
MemoryHit(
id=r["id"], text=r["text"], score=float(r["score"]), created_at=r["created_at"],
user_id=r.get("user_id"), source=r.get("source"), metadata=r.get("metadata"),
)
for r in results
]
@app.post("/emotion/analyze", response_model=EmotionOut)
def emotion_analyze(body: EmotionIn):
emo = classify_emotion(body.text, body.context)
memory_row_id = None
if body.persist_memory:
mem = create_memory(MemoryIn(
text=body.text, user_id=body.user_id, source="emotion", metadata={"context":
body.context}
))
memory_row_id = mem.id
doc = {
"user_id": body.user_id,
"text": body.text,
"label": emo["label"],
"score": emo["score"],
"distribution": emo.get("distribution", {}),
"actions": emo.get("actions", []),
"created_at": datetime.datetime.utcnow(),
"memory_row_id": memory_row_id,
}
doc_ref = fs_client.collection(FS_COLLECTION).document()
doc_ref.set(doc)
firestore_doc_id = doc_ref.id
return EmotionOut(
label=emo["label"], score=emo["score"], distribution=emo.get("distribution", {}),
actions=emo.get("actions", []), memory_row_id=memory_row_id,
firestore_doc_id=firestore_doc_id,
model={"embedding_model": EMBEDDING_MODEL, "generative_model":
GENERATIVE_MODEL, "location": GENAI_LOCATION},
)

if __name__ == "__main__":
import uvicorn
port = int(os.getenv("PORT", "8080"))
uvicorn.run("core:app", host="0.0.0.0", port=port, log_level="info")


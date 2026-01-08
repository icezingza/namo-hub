#!/usr/bin/env python
import argparse
import json
import os
import threading
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from urllib.parse import urlparse, parse_qs


STORE = {}
STORE_LOCK = threading.Lock()
API_KEY = os.getenv("NAMO_API_KEY", "")


def _json_response(handler, status, payload):
    body = json.dumps(payload, separators=(",", ":"), ensure_ascii=True).encode("utf-8")
    handler.send_response(status)
    handler.send_header("Content-Type", "application/json")
    handler.send_header("Content-Length", str(len(body)))
    handler.end_headers()
    handler.wfile.write(body)


def _read_json(handler):
    length = int(handler.headers.get("Content-Length", "0"))
    if length == 0:
        return None, "empty_body"
    raw = handler.rfile.read(length).decode("utf-8")
    try:
        return json.loads(raw), None
    except json.JSONDecodeError:
        return None, "invalid_json"


def _require_api_key(handler):
    if not API_KEY:
        return True
    return handler.headers.get("x-api-key") == API_KEY


def _validate_item(item):
    required = ["id", "text", "tags", "timestamp"]
    for key in required:
        if key not in item:
            return f"missing_{key}"
    if not isinstance(item.get("tags"), list):
        return "tags_must_be_array"
    if not item.get("text"):
        return "text_required"
    return None


def _score_match(query, item):
    q = query.lower()
    text = item.get("text", "").lower()
    tags = [str(t).lower() for t in item.get("tags", [])]
    if q in text:
        return 0.9
    if any(q in t for t in tags):
        return 0.6
    return 0.0


class MemoryAPIHandler(BaseHTTPRequestHandler):
    server_version = "NaMoMemoryAPI/0.2"

    def _auth_or_401(self):
        if _require_api_key(self):
            return True
        _json_response(self, 401, {"code": "unauthorized", "message": "invalid_api_key"})
        return False

    def do_POST(self):
        if not self._auth_or_401():
            return

        path = urlparse(self.path).path
        payload, err = _read_json(self)
        if err:
            _json_response(self, 400, {"code": "invalid_request", "message": err})
            return

        if path == "/upsert":
            tenant_id = payload.get("tenant_id")
            items = payload.get("items", [])
            if not tenant_id or not isinstance(items, list):
                _json_response(self, 400, {"code": "invalid_request", "message": "tenant_id and items required"})
                return
            accepted_ids = []
            with STORE_LOCK:
                STORE.setdefault(tenant_id, {})
                for item in items:
                    msg = _validate_item(item)
                    if msg:
                        _json_response(self, 400, {"code": "invalid_request", "message": msg})
                        return
                    STORE[tenant_id][item["id"]] = item
                    accepted_ids.append(item["id"])
            _json_response(self, 200, {"accepted": len(accepted_ids), "ids": accepted_ids})
            return

        if path == "/retrieve":
            tenant_id = payload.get("tenant_id")
            query = payload.get("query")
            k = payload.get("k")
            if not tenant_id or not query or not isinstance(k, int):
                _json_response(self, 400, {"code": "invalid_request", "message": "tenant_id, query, k required"})
                return
            matches = []
            with STORE_LOCK:
                items = list(STORE.get(tenant_id, {}).values())
            for item in items:
                score = _score_match(query, item)
                if score <= 0.0:
                    continue
                matches.append(
                    {
                        "id": item.get("id"),
                        "text": item.get("text"),
                        "score": score,
                        "tags": item.get("tags", []),
                        "timestamp": item.get("timestamp"),
                    }
                )
            matches.sort(key=lambda m: m["score"], reverse=True)
            _json_response(self, 200, {"matches": matches[:k]})
            return

        _json_response(self, 404, {"code": "not_found", "message": "unknown_endpoint"})

    def do_DELETE(self):
        if not self._auth_or_401():
            return

        parsed = urlparse(self.path)
        path = parsed.path.strip("/")
        if not path:
            _json_response(self, 404, {"code": "not_found", "message": "missing_id"})
            return

        params = parse_qs(parsed.query)
        tenant_id = params.get("tenant_id", [None])[0]
        target_id = path
        deleted = False

        with STORE_LOCK:
            if tenant_id:
                if target_id in STORE.get(tenant_id, {}):
                    del STORE[tenant_id][target_id]
                    deleted = True
            else:
                for t_id, t_store in STORE.items():
                    if target_id in t_store:
                        del t_store[target_id]
                        deleted = True
                        break

        if deleted:
            _json_response(self, 200, {"status": "deleted", "id": target_id})
        else:
            _json_response(self, 404, {"code": "not_found", "message": "id_not_found"})

    def log_message(self, format, *args):
        return


def main():
    parser = argparse.ArgumentParser(description="NaMo Memory API demo server")
    parser.add_argument("--port", type=int, default=8080, help="Port to listen on")
    args = parser.parse_args()

    server = ThreadingHTTPServer(("0.0.0.0", args.port), MemoryAPIHandler)
    print(f"NaMo Memory API demo running on http://localhost:{args.port}")
    server.serve_forever()


if __name__ == "__main__":
    main()

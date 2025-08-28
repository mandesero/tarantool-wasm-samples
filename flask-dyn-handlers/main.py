from wit_world import exports
from wit_world.imports import say
from wit_world.imports.tarantool_tarantool_types import *

from wit_world.imports.dyn_http import (
    Header,
    Param,
    UriComponents,
    Request as DRequest,
    Response as DResponse,
    handler as dyn_handler
)

# Patch zlib for componentize-py WASM runtime
import __zlib
import sys
sys.modules["zlib"] = __zlib

# Patch importlib.metadata.version to avoid runtime errors
import importlib.metadata
importlib.metadata.version = lambda _: ""

# Ensure idna encoding is pre-loaded for WASM
"".encode('idna')

from flask import Flask, request as FRequest, Response as FResponse, jsonify
from urllib.parse import parse_qsl
import threading
from typing import List, Optional, Tuple

app = Flask(__name__)
_lock = threading.Lock()
_registry: set[str] = set()


def to_dataclass_request(req: FRequest, path_for_handler: str) -> DRequest:
    headers_list: List[Header] = []
    for name in req.headers.keys():
        for val in req.headers.getlist(name):
            headers_list.append(Header(name=name, value=val))

    http_version = req.environ.get("SERVER_PROTOCOL", "HTTP/1.1")

    host_hdr = req.host or ""
    if ":" in host_hdr:
        host, port_str = host_hdr.rsplit(":", 1)
        port = int(port_str) if port_str.isdigit() else (443 if req.scheme == "https" else 80)
    else:
        host = host_hdr
        port = 443 if req.scheme == "https" else int(req.environ.get("SERVER_PORT", 80))

    query_str = req.query_string.decode(errors="ignore")
    query_args_list: List[Param] = [
        Param(name=k, value=v) for k, v in parse_qsl(query_str, keep_blank_values=True)
    ]

    uri = UriComponents(
        scheme=req.scheme,
        host=host,
        port=port,
        path=req.path,
        query=query_str,
        query_args=query_args_list,
        fragment="",
    )

    target = req.path + (("?" + query_str) if query_str else "")
    body: Optional[bytes] = req.get_data(cache=False) or None

    return DRequest(
        method=req.method,
        target=target,
        http_version=http_version,
        uri=uri,
        headers=headers_list,
        body=body,
        body_done=True,
        done=True,
    )


def to_flask_response(resp: DResponse) -> FResponse:
    status = int(resp.status)
    reason = resp.reason or ""
    body: bytes = resp.body or b""

    def headers_to_pairs(hs: List[Header]) -> List[Tuple[str, str]]:
        return [(h.name, h.value) for h in (hs or [])]

    header_pairs: List[Tuple[str, str]] = []
    header_pairs.extend(headers_to_pairs(resp.headers))
    header_pairs.extend(headers_to_pairs(resp.trailers))

    lower_names = {k.lower() for k, _ in header_pairs}
    if reason and "x-reason" not in lower_names:
        header_pairs.append(("X-Reason", reason))

    return FResponse(body, status=status, headers=header_pairs)


def __handler(path: str, req_dc: DRequest) -> DResponse:
    return dyn_handler(path, req_dc)


@app.post("/register-handler/<path:route_path>")
def register_handler(route_path: str):
    route_path = route_path.lstrip("/")
    with _lock:
        if route_path in _registry:
            return jsonify({"error": "route already exists", "route": f"/{route_path}"}), 409
        _registry.add(route_path)
    return jsonify({"registered": f"/{route_path}"}), 200


@app.delete("/unregister-handler/<path:route_path>")
def unregister_handler(route_path: str):
    route_path = route_path.lstrip("/")
    with _lock:
        if route_path not in _registry:
            return jsonify({"error": "route not found", "route": f"/{route_path}"}), 404
        _registry.remove(route_path)
    return jsonify({"unregistered": f"/{route_path}"}), 200


from markupsafe import escape

@app.route("/", methods=["GET", "POST", "PUT", "PATCH", "DELETE", "HEAD", "OPTIONS"])
def dispatch_root():
    with _lock:
        routes = sorted(f"/{r}" if r != "" else "/" for r in _registry)

    items = "\n".join(
        f'<li><code>{escape(p)}</code></li>' for p in routes if p != "/"
    ) or "<li><em>пока пусто</em></li>"

    html = f"""<!doctype html>
<html lang="ru">
<head>
  <meta charset="utf-8">
  <title>Tarantool Wasm HTTP Server</title>
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <style>
    :root {{
      --bg: #0f172a;      /* slate-900 */
      --card: #111827;    /* gray-900 */
      --text: #e5e7eb;    /* gray-200 */
      --muted: #9ca3af;   /* gray-400 */
      --accent: #22d3ee;  /* cyan-400 */
      --ok: #10b981;      /* emerald-500 */
    }}
    * {{ box-sizing: border-box; }}
    body {{
      margin: 0; padding: 0; background: radial-gradient(1200px 600px at 10% 10%, #111827 0%, #0b1220 40%, #050915 100%), var(--bg);
      color: var(--text); font: 16px/1.5 system-ui, -apple-system, Segoe UI, Roboto, Ubuntu, Cantarell, Noto Sans, sans-serif;
    }}
    .wrap {{ max-width: 840px; margin: 6vh auto; padding: 24px; }}
    .card {{
      background: linear-gradient(180deg, rgba(255,255,255,0.04), rgba(255,255,255,0.02));
      border: 1px solid rgba(255,255,255,0.08);
      border-radius: 16px; padding: 28px 24px; box-shadow: 0 10px 30px rgba(0,0,0,0.35);
      backdrop-filter: blur(6px);
    }}
    h1 {{ margin: 0 0 8px; font-size: 28px; letter-spacing: 0.3px; }}
    .sub {{ color: var(--muted); margin: 0 0 18px; }}
    .ok {{ color: var(--ok); font-weight: 600; }}
    .pill {{
      display: inline-block; padding: 4px 10px; border-radius: 999px;
      background: rgba(34, 211, 238, 0.12); color: var(--accent); border: 1px solid rgba(34, 211, 238, 0.35);
      font-size: 12px; letter-spacing: .3px;
    }}
    ul {{ list-style: none; padding-left: 0; margin: 12px 0 0; }}
    li {{ padding: 6px 0; border-bottom: 1px dashed rgba(255,255,255,0.08); }}
    code {{
      background: rgba(255,255,255,0.06); padding: 3px 8px; border-radius: 8px; font-family: ui-monospace, SFMono-Regular, Menlo, Monaco, Consolas, 'Liberation Mono', monospace;
    }}
    .grid {{ display: grid; gap: 12px; grid-template-columns: repeat(auto-fit, minmax(260px, 1fr)); margin-top: 18px; }}
    .box {{ border: 1px solid rgba(255,255,255,0.08); border-radius: 12px; padding: 14px; background: rgba(255,255,255,0.03); }}
    .muted {{ color: var(--muted); font-size: 14px; }}
    a {{ color: var(--accent); text-decoration: none; }}
    a:hover {{ text-decoration: underline; }}
  </style>
</head>
<body>
  <div class="wrap">
    <div class="card">
      <div class="pill">Tarantool Wasm http server</div>
      <h1>Сервер запущен <span class="ok">OK</span></h1>
      <p class="sub">Root-страница не проксирует запросы в handler. Используйте зарегистрированные пути ниже.</p>

      <div class="grid">
        <div class="box">
          <div class="muted">Зарегистрированные пути</div>
          <ul>
            {items}
          </ul>
        </div>
        <div class="box">
          <div class="muted">Подсказка по API</div>
          <p>Регистрируйте обработчик:</p>
          <code>POST /register-handler/&lt;path&gt;</code>
          <p style="margin-top:10px;">Пример:</p>
          <code>POST /register-handler/hello</code>
          <p style="margin-top:10px;">Затем вызывайте:</p>
          <code>GET /hello</code>
        </div>
      </div>
    </div>
  </div>
</body>
</html>"""

    return FResponse(html, status=200, headers=[("Content-Type", "text/html; charset=utf-8")])


@app.route("/<path:subpath>", methods=["GET", "POST", "PUT", "PATCH", "DELETE", "HEAD", "OPTIONS"])
def dispatch(subpath: str):
    if subpath not in _registry:
        return jsonify({"error": "not found"}), 404
    req_dc = to_dataclass_request(FRequest, subpath)
    print(f"Call /{subpath}")
    resp_dc = __handler(f"/{subpath}", req_dc)
    return to_flask_response(resp_dc)


class Run(exports.Run):
    def run(self) -> None:
        try:
            app.run(host="127.0.0.1", port=8000, debug=False, threaded=False)
        except Exception as e:
            say.say_error(str(e), None)

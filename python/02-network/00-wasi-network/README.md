## Python Example: Wasi Network Test

### How to run

```bash
tarawasm build
python3 server.py > server.log 2>&1 &
tarantool run.lua
```

---

### Expected output

```
Load WASM module...
Run WASM module...
PY | ===== Test resolve start =====
PY | Resolved address: IpAddress_Ipv4(value=(87, 240, 132, 72))
PY | Resolved address: IpAddress_Ipv4(value=(87, 240, 132, 78))
PY | Resolved address: IpAddress_Ipv4(value=(93, 186, 225, 194))
PY | Resolved address: IpAddress_Ipv4(value=(87, 240, 137, 164))
PY | Resolved address: IpAddress_Ipv4(value=(87, 240, 129, 133))
PY | Resolved address: IpAddress_Ipv4(value=(87, 240, 132, 67))
PY | ===== Test resolve done =====
PY | ===== Test http start =====
PY | HTTP status: 302
PY | Header: server = kittenx
PY | Header: date = Wed, 02 Jul 2025 12:59:09 GMT
PY | Header: content-type = text/html; charset=windows-1251
PY | Header: content-length = 0
PY | Header: server-timing = tid;desc="p0lEdgL_MMuoVm879PKlsgct2-QSMw",front;dur=7.662
PY | Header: x-powered-by = KPHP/7.4.123786
PY | Header: set-cookie = remixir=DELETED; expires=Thu, 01 Jan 1970 00:00:01 GMT; path=/; domain=.vk.com; secure; HttpOnly
PY | Header: set-cookie = remixlang=0; expires=Mon, 29 Jun 2026 19:01:04 GMT; path=/; domain=.vk.com
PY | Header: set-cookie = remixstlid=9052866210916371310_QyeYP1BLyaki9EVBeXLzaKnQky7ix4lcj0puTlYkac0; expires=Thu, 02 Jul 2026 12:59:09 GMT; path=/; domain=.vk.com; secure
PY | Header: location = https://m.vk.com/
PY | Header: strict-transport-security = max-age=15768000
PY | Header: nel = {"report_to":"default","max_age":86400,"include_subdomains":true,"failure_fraction":1.0}
PY | Header: report-to = {"group":"default","max_age":86400,"endpoints":[{"url":"https://akashi.vk-portal.net/api/v1/nel"}],"include_subdomains":true}
PY | Header: x-frontend = front656702
PY | Header: access-control-expose-headers = X-Frontend
PY | Header: x-trace-id = p0lEdgL_MMuoVm879PKlsgct2-QSMw
PY | ===== Test http done =====
PY | ===== Test connect start =====
PY | Msg from server: b'Hello from server!\n'
PY | ===== Test connect done =====
WASM module finished...
```

### Server logs

```
$ cat server.log

Server listening on 127.0.0.1:12121
Connection established with ('127.0.0.1', 45264)
Received from ('127.0.0.1', 45264): hello from python wasm

Connection closed by ('127.0.0.1', 45264)
```

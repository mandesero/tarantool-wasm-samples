#include "dyn_http_sdk.h"
#include <stdio.h>
#include <stdlib.h>

/* /hello — простой текст */
static docs_adder_dyn_http_response_t hello(const docs_adder_dyn_http_request_t* req) {
  (void)req;
  DhRespBuilder* b = dh_resp_builder_new();
  dh_resp_set_status_reason(b, 200, "OK");
  dh_resp_add_header(b, "Content-Type", "text/plain; charset=utf-8");
  dh_resp_set_body_text(b, "Hello from C handler\n");
  return dh_resp_build_and_free(b);
}

/* /echo — эхо method/target */
static docs_adder_dyn_http_response_t echo_meta(const docs_adder_dyn_http_request_t* req) {
  char* m = dh_to_cstr(req->method);
  char* t = dh_to_cstr(req->target);

  char buf[512];
  snprintf(buf, sizeof(buf), "method=%s target=%s\n", m?m:"", t?t:"");
  if (m) free(m); if (t) free(t);

  DhRespBuilder* b = dh_resp_builder_new();
  dh_resp_add_header(b, "Content-Type", "text/plain; charset=utf-8");
  dh_resp_set_body_text(b, buf);
  return dh_resp_build_and_free(b);
}

/* /bin — бинарный ответ */
static docs_adder_dyn_http_response_t bin_data(const docs_adder_dyn_http_request_t* req) {
  (void)req;
  static const unsigned char data[] = { 0xDE, 0xAD, 0xBE, 0xEF };
  DhRespBuilder* b = dh_resp_builder_new();
  dh_resp_set_status_reason(b, 200, "OK");
  dh_resp_add_header(b, "Content-Type", "application/octet-stream");
  dh_resp_set_body_copy(b, data, sizeof(data));
  return dh_resp_build_and_free(b);
}

/* Таблица маршрутов плагина */
DYNHTTP_ROUTES(
  DYNHTTP_ROUTE("/hello", hello),
  DYNHTTP_ROUTE("/echo",  echo_meta),
  DYNHTTP_ROUTE("/bin",   bin_data)
)

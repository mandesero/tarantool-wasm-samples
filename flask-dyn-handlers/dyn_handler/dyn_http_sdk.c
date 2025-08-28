#include "dyn_http_sdk.h"
#include <stdlib.h>
#include <string.h>

static adder_string_t str_dup_from_cstr(const char* s) {
  if (!s) return (adder_string_t){NULL,0};
  size_t n = strlen(s);
  uint8_t* p = (n ? (uint8_t*)malloc(n) : NULL);
  if (n && !p) return (adder_string_t){NULL,0};
  if (p) memcpy(p, s, n);
  return (adder_string_t){p, n};
}

char* dh_to_cstr(adder_string_t s) {
  char* p = (char*)malloc(s.len + 1);
  if (!p) return NULL;
  if (s.len) memcpy(p, s.ptr, s.len);
  p[s.len] = '\0';
  return p;
}

bool dh_eq(adder_string_t s, const char* lit) {
  size_t n = s.len;
  size_t m = lit ? strlen(lit) : 0;
  if (n != m) return false;
  return (n == 0) || (memcmp(s.ptr, lit, n) == 0);
}

typedef struct {
  docs_adder_dyn_http_header_t* ptr;
  size_t len, cap;
} HVec;

static void hvec_init(HVec* v) { v->ptr=NULL; v->len=0; v->cap=0; }
static void hvec_reset(HVec* v) {
  if (v->ptr) {
    for (size_t i=0;i<v->len;i++) {
      if (v->ptr[i].name.ptr)  free(v->ptr[i].name.ptr);
      if (v->ptr[i].value.ptr) free(v->ptr[i].value.ptr);
    }
    free(v->ptr);
  }
  v->ptr=NULL; v->len=0; v->cap=0;
}
static int hvec_push(HVec* v, adder_string_t n, adder_string_t val) {
  if (v->len == v->cap) {
    size_t newcap = v->cap ? v->cap*2 : 4;
    void* np = realloc(v->ptr, newcap * sizeof(*v->ptr));
    if (!np) return -1;
    v->ptr = (docs_adder_dyn_http_header_t*)np;
    v->cap = newcap;
  }
  v->ptr[v->len].name  = n;
  v->ptr[v->len].value = val;
  v->len += 1;
  return 0;
}

struct DhRespBuilder {
  uint16_t status;
  adder_string_t reason;
  HVec headers;
  HVec trailers;
  bool has_body;
  docs_adder_dyn_http_bytes_t body;
  bool failed;
};

static void dh_resp_builder_init_(DhRespBuilder* b) {
  b->status = 200;
  b->reason = str_dup_from_cstr("OK");
  hvec_init(&b->headers);
  hvec_init(&b->trailers);
  b->has_body = false;
  b->body.ptr = NULL; b->body.len = 0;
  b->failed = false;
}
static void dh_resp_builder_reset_(DhRespBuilder* b) {
  if (b->reason.ptr) free(b->reason.ptr);
  hvec_reset(&b->headers);
  hvec_reset(&b->trailers);
  if (b->has_body && b->body.ptr) free(b->body.ptr);
  b->status = 200;
  b->reason.ptr = NULL; b->reason.len = 0;
  b->has_body = false; b->body.ptr = NULL; b->body.len = 0;
  b->failed = false;
}

DhRespBuilder* dh_resp_builder_new(void) {
  DhRespBuilder* b = (DhRespBuilder*)malloc(sizeof(DhRespBuilder));
  if (!b) return NULL;
  dh_resp_builder_init_(b);
  return b;
}
void dh_resp_builder_free(DhRespBuilder* b) {
  if (!b) return;
  dh_resp_builder_reset_(b);
  free(b);
}

/* setters */
int dh_resp_set_status_reason(DhRespBuilder* b, uint16_t status, const char* reason_utf8) {
  if (!b) return -1;
  if (b->reason.ptr) { free(b->reason.ptr); b->reason.ptr=NULL; b->reason.len=0; }
  if (reason_utf8) {
    size_t n = strlen(reason_utf8);
    if (n) {
      uint8_t* p = (uint8_t*)malloc(n);
      if (!p) { b->failed=true; return -1; }
      memcpy(p, reason_utf8, n);
      b->reason.ptr = p; b->reason.len = n;
    }
  }
  b->status = status;
  return 0;
}
int dh_resp_add_header(DhRespBuilder* b, const char* name_utf8, const char* value_utf8) {
  if (!b) return -1;
  adder_string_t n  = str_dup_from_cstr(name_utf8  ? name_utf8  : "");
  adder_string_t val= str_dup_from_cstr(value_utf8 ? value_utf8 : "");
  if ((name_utf8  && !n.ptr  && strlen(name_utf8)  > 0) ||
      (value_utf8 && !val.ptr && strlen(value_utf8) > 0)) {
    if (n.ptr) free(n.ptr);
    if (val.ptr) free(val.ptr);
    b->failed = true;
    return -1;
  }
  if (hvec_push(&b->headers, n, val) != 0) {
    if (n.ptr) free(n.ptr);
    if (val.ptr) free(val.ptr);
    b->failed = true;
    return -1;
  }
  return 0;
}
int dh_resp_add_trailer(DhRespBuilder* b, const char* name_utf8, const char* value_utf8) {
  if (!b) return -1;
  adder_string_t n  = str_dup_from_cstr(name_utf8  ? name_utf8  : "");
  adder_string_t val= str_dup_from_cstr(value_utf8 ? value_utf8 : "");
  if ((name_utf8  && !n.ptr  && strlen(name_utf8)  > 0) ||
      (value_utf8 && !val.ptr && strlen(value_utf8) > 0)) {
    if (n.ptr) free(n.ptr);
    if (val.ptr) free(val.ptr);
    b->failed = true;
    return -1;
  }
  if (hvec_push(&b->trailers, n, val) != 0) {
    if (n.ptr) free(n.ptr);
    if (val.ptr) free(val.ptr);
    b->failed = true;
    return -1;
  }
  return 0;
}
int dh_resp_set_body_text(DhRespBuilder* b, const char* text_utf8) {
  if (!b) return -1;
  size_t n = text_utf8 ? strlen(text_utf8) : 0;
  uint8_t* p = (n ? (uint8_t*)malloc(n) : NULL);
  if (n && !p) { b->failed = true; return -1; }
  if (p && n) memcpy(p, text_utf8, n);
  if (b->has_body && b->body.ptr) free(b->body.ptr);
  b->body.ptr = p; b->body.len = n; b->has_body = true;
  return 0;
}
int dh_resp_set_body_copy(DhRespBuilder* b, const void* data, size_t len) {
  if (!b) return -1;
  const uint8_t* src = (const uint8_t*)data;
  uint8_t* p = (len ? (uint8_t*)malloc(len) : NULL);
  if (len && !p) { b->failed = true; return -1; }
  if (p && len) memcpy(p, src, len);
  if (b->has_body && b->body.ptr) free(b->body.ptr);
  b->body.ptr = p; b->body.len = len; b->has_body = true;
  return 0;
}

docs_adder_dyn_http_response_t dh_resp_build_and_free(DhRespBuilder* b) {
  docs_adder_dyn_http_response_t out;
  if (!b || b->failed) {
    memset(&out, 0, sizeof out);
    out.status = 500;
    out.reason = str_dup_from_cstr("OOM");
    if (b) { dh_resp_builder_free(b); }
    return out;
  }

  out.status  = b->status;
  out.reason  = b->reason;
  out.headers.ptr = b->headers.ptr; out.headers.len = b->headers.len;
  out.trailers.ptr = b->trailers.ptr; out.trailers.len = b->trailers.len;
  out.body.is_some = b->has_body;
  out.body.val = b->has_body ? b->body : (docs_adder_dyn_http_bytes_t){NULL,0};

  b->reason.ptr = NULL; b->reason.len = 0;
  b->headers.ptr = NULL; b->headers.len = b->headers.cap = 0;
  b->trailers.ptr = NULL; b->trailers.len = b->trailers.cap = 0;
  b->has_body = false; b->body.ptr = NULL; b->body.len = 0;
  free(b);
  return out;
}

void free_response(docs_adder_dyn_http_response_t resp) {
  if (resp.reason.ptr) free(resp.reason.ptr);

  if (resp.headers.ptr && resp.headers.len) {
    for (size_t i=0;i<resp.headers.len;i++) {
      if (resp.headers.ptr[i].name.ptr)  free(resp.headers.ptr[i].name.ptr);
      if (resp.headers.ptr[i].value.ptr) free(resp.headers.ptr[i].value.ptr);
    }
    free(resp.headers.ptr);
  }

  if (resp.trailers.ptr && resp.trailers.len) {
    for (size_t i=0;i<resp.trailers.len;i++) {
      if (resp.trailers.ptr[i].name.ptr)  free(resp.trailers.ptr[i].name.ptr);
      if (resp.trailers.ptr[i].value.ptr) free(resp.trailers.ptr[i].value.ptr);
    }
    free(resp.trailers.ptr);
  }

  if (resp.body.is_some && resp.body.val.ptr) {
    free(resp.body.val.ptr);
  }
}

extern const DhRoute* dh_get_routes(size_t* out_len);

docs_adder_dyn_http_response_t
f(adder_string_t name, const docs_adder_dyn_http_request_t* req) {
  size_t n = 0;
  const DhRoute* routes = dh_get_routes(&n);

  if (!routes || n == 0) {
    DhRespBuilder* b = dh_resp_builder_new();
    dh_resp_set_status_reason(b, 404, "No routes");
    dh_resp_add_header(b, "Content-Type", "text/plain; charset=utf-8");
    dh_resp_set_body_text(b, "No routes defined\n");
    return dh_resp_build_and_free(b);
  }

  for (size_t i=0; i<n; ++i) {
    if (routes[i].path && dh_eq(name, routes[i].path)) {
      return routes[i].fn(req);
    }
  }

  DhRespBuilder* b = dh_resp_builder_new();
  dh_resp_set_status_reason(b, 404, "Not Found");
  dh_resp_add_header(b, "Content-Type", "text/plain; charset=utf-8");
  dh_resp_set_body_text(b, "Handler not found\n");
  return dh_resp_build_and_free(b);
}

#pragma once
#include <stdint.h>
#include <stddef.h>
#include <stdbool.h>

#ifdef __cplusplus
extern "C" {
#endif

/* ========= ABI-типы ========= */
typedef struct adder_string_t {
  uint8_t *ptr;
  size_t   len;
} adder_string_t;

typedef struct docs_adder_dyn_http_bytes_t {
  uint8_t *ptr;
  size_t   len;
} docs_adder_dyn_http_bytes_t;

typedef struct docs_adder_dyn_http_header_t {
  adder_string_t name;
  adder_string_t value;
} docs_adder_dyn_http_header_t;

typedef struct docs_adder_dyn_http_headers_t {
  docs_adder_dyn_http_header_t *ptr;
  size_t len;
} docs_adder_dyn_http_headers_t;

typedef struct docs_adder_dyn_http_param_t {
  adder_string_t name;
  adder_string_t value;
} docs_adder_dyn_http_param_t;

typedef struct docs_adder_dyn_http_query_args_t {
  docs_adder_dyn_http_param_t *ptr;
  size_t len;
} docs_adder_dyn_http_query_args_t;

typedef struct docs_adder_dyn_http_uri_components_t {
  adder_string_t scheme;
  adder_string_t host;
  uint16_t       port;
  adder_string_t path;
  adder_string_t query;
  docs_adder_dyn_http_query_args_t query_args;
  adder_string_t fragment;
} docs_adder_dyn_http_uri_components_t;

typedef struct {
  bool is_some;
  docs_adder_dyn_http_bytes_t val;
} adder_option_bytes_t;

typedef struct docs_adder_dyn_http_request_t {
  adder_string_t method;
  adder_string_t target;
  adder_string_t http_version;
  docs_adder_dyn_http_uri_components_t uri;
  docs_adder_dyn_http_headers_t headers;
  adder_option_bytes_t body;
  bool body_done;
  bool done;
} docs_adder_dyn_http_request_t;

typedef struct docs_adder_dyn_http_response_t {
  uint16_t status;
  adder_string_t reason;
  docs_adder_dyn_http_headers_t headers;
  docs_adder_dyn_http_headers_t trailers;
  adder_option_bytes_t body;
} docs_adder_dyn_http_response_t;

/* ========= утилиты ========= */
/* Копирует adder_string_t в \0-terminated C-строку (malloc). Освобождать free(). */
char* dh_to_cstr(adder_string_t s);
/* Сравнение adder_string_t с C-строкой lit. */
bool  dh_eq(adder_string_t s, const char* lit);

/* ========= билдер ответа (opaque) ========= */
typedef struct DhRespBuilder DhRespBuilder;

/* Создать/освободить билдер (new -> malloc, build_and_free -> free(builder)). */
DhRespBuilder* dh_resp_builder_new(void);
void           dh_resp_builder_free(DhRespBuilder* b);

/* Наполнение ответа; значения копируются внутрь билдера. Возвращают 0/−1. */
int  dh_resp_set_status_reason(DhRespBuilder* b, uint16_t status, const char* reason_utf8);
int  dh_resp_add_header       (DhRespBuilder* b, const char* name_utf8, const char* value_utf8);
int  dh_resp_add_trailer      (DhRespBuilder* b, const char* name_utf8, const char* value_utf8);
int  dh_resp_set_body_text    (DhRespBuilder* b, const char* text_utf8);
int  dh_resp_set_body_copy    (DhRespBuilder* b, const void* data, size_t len);

/* Сборка ответа и автоматическое освобождение билдера. */
docs_adder_dyn_http_response_t dh_resp_build_and_free(DhRespBuilder* b);

/* ========= таблица роутов ========= */
typedef docs_adder_dyn_http_response_t
(*DhHandler)(const docs_adder_dyn_http_request_t* req);

typedef struct DhRoute {
  const char* path;  /* абсолютный HTTP-путь, например "/hello" */
  DhHandler   fn;    /* функция-хэндлер */
} DhRoute;

/* Пользователь должен определить эту функцию (см. макрос ниже). */
const DhRoute* dh_get_routes(size_t* out_len);

/* Макросы для объявления таблицы маршрутов. */
#define DYNHTTP_ROUTE(_path, _fn) ((DhRoute){ (_path), (_fn) })
#define DYNHTTP_ROUTES(...) \
  const DhRoute* dh_get_routes(size_t* out_len) { \
    static const DhRoute _routes[] = { __VA_ARGS__ }; \
    *out_len = sizeof(_routes)/sizeof(_routes[0]); \
    return _routes; \
  }

/* ========= экспортируемые символы для рантайма ========= */
docs_adder_dyn_http_response_t
__attribute__((visibility("default")))
f(adder_string_t name, const docs_adder_dyn_http_request_t* req);

void __attribute__((visibility("default")))
free_response(docs_adder_dyn_http_response_t resp);

#ifdef __cplusplus
}
#endif

SHELL := /bin/sh
TARAWASM_IMAGE ?= mandeser0/tarawasm:v0.3.0
KAFKA_IMAGE ?= docker.redpanda.com/redpandadata/redpanda:v25.1.3
POSTGRES_IMAGE ?= postgres:17.6-alpine
REDIS_IMAGE ?= redis:8.10.0-alpine
NATS_IMAGE ?= nats:2.14.4-alpine
MQTT_IMAGE ?= eclipse-mosquitto:2.1.2-alpine
TARANTOOL ?= tarantool

.PHONY: setup check-wasm tarawasm-image kafka-image postgres-image redis-image nats-image mqtt-image deps build clean lint run smoke kafka-smoke postgres-smoke postgres-tls-smoke redis-smoke nats-smoke websocket-smoke mqtt-smoke test status

setup:
	@test -n "$(WASM_SO)" || { echo "WASM_SO must be an absolute path" >&2; exit 2; }
	@./scripts/dev.sh link-wasm "$(WASM_SO)"
	@$(MAKE) check-wasm

check-wasm:
	@TARANTOOL="$(TARANTOOL)" ./scripts/dev.sh check-wasm

tarawasm-image:
	@docker pull "$(TARAWASM_IMAGE)"

kafka-image:
	@docker pull "$(KAFKA_IMAGE)"

postgres-image:
	@docker pull "$(POSTGRES_IMAGE)"

redis-image:
	@docker pull "$(REDIS_IMAGE)"

nats-image:
	@docker pull "$(NATS_IMAGE)"

mqtt-image:
	@docker pull "$(MQTT_IMAGE)"

deps:
	@TARAWASM_IMAGE="$(TARAWASM_IMAGE)" ./scripts/dev.sh deps

build: deps
	@if [ -n "$(SAMPLE)" ]; then \
		TARAWASM_IMAGE="$(TARAWASM_IMAGE)" ./scripts/dev.sh tarawasm-one "$(SAMPLE)" all; \
	else \
		TARAWASM_IMAGE="$(TARAWASM_IMAGE)" ./scripts/dev.sh tarawasm all; \
	fi

clean:
	@TARAWASM_IMAGE="$(TARAWASM_IMAGE)" ./scripts/dev.sh tarawasm clean
	@rm -rf -- "$(CURDIR)/.tarawasm"

lint:
	@./scripts/dev.sh lint

run: check-wasm
	@test -n "$(SAMPLE)" || { echo "SAMPLE is required" >&2; exit 2; }
	@TARANTOOL="$(TARANTOOL)" ./scripts/dev.sh run "$(SAMPLE)"

smoke: check-wasm
	@TARANTOOL="$(TARANTOOL)" ./scripts/dev.sh smoke

kafka-smoke: check-wasm
	@TARANTOOL="$(TARANTOOL)" KAFKA_IMAGE="$(KAFKA_IMAGE)" ./scripts/test-kafka.sh

postgres-smoke: check-wasm
	@TARANTOOL="$(TARANTOOL)" POSTGRES_IMAGE="$(POSTGRES_IMAGE)" ./scripts/test-postgres.sh

postgres-tls-smoke: check-wasm
	@TARANTOOL="$(TARANTOOL)" ./scripts/test-postgres-tls.sh

redis-smoke: check-wasm
	@TARANTOOL="$(TARANTOOL)" REDIS_IMAGE="$(REDIS_IMAGE)" ./scripts/test-redis.sh

nats-smoke: check-wasm
	@TARANTOOL="$(TARANTOOL)" NATS_IMAGE="$(NATS_IMAGE)" ./scripts/test-nats.sh

websocket-smoke: check-wasm
	@TARANTOOL="$(TARANTOOL)" ./scripts/test-websocket.sh

mqtt-smoke: check-wasm
	@TARANTOOL="$(TARANTOOL)" MQTT_IMAGE="$(MQTT_IMAGE)" ./scripts/test-mqtt.sh

test: lint build smoke kafka-smoke postgres-smoke postgres-tls-smoke redis-smoke nats-smoke websocket-smoke mqtt-smoke

status:
	@git status --short

# pgrust в Tarantool

Этот пример собирает `pgrust` как core-модуль `wasm32-wasip1`, преобразует
его в WebAssembly Component Model command и запускает PostgreSQL backend через
duplex pipe streams из `tarantool-wasm`.

Lua-модуль `pgwire.lua` реализует минимальный PostgreSQL wire client поверх
`wasm.pipe`. `run.lua` открывает одну долгоживущую backend-сессию, выполняет в
ней `smoke.sql`, затем отдельный `SELECT` и проверяет полученные строки. Таким
образом пример сохраняет состояние PostgreSQL-сессии между запросами.

## Подготовить окружение

Нужны Linux, Git, Rustup, Docker, Tarantool и `wasm-tools`. Используемая версия
`tarantool-wasm` должна предоставлять API `wasm.pipe`.

```sh
cd ~/tarantool-wasm-samples
make setup WASM_SO=/absolute/path/to/libtarantool_wasm_rs.so

git --version
rustup --version
docker --version
wasm-tools --version
tarantool --version
```

Сборка pgrust занимает несколько гигабайт и требует около 15 ГБ свободного
места.

## Собрать pgrust в core-модуль

Upstream-скрипт устанавливает нужный nightly toolchain и собирает PostgreSQL
для `wasm32-wasip1` с профилем `wasm-release`.

```sh
cd ~/tarantool-wasm-samples/pgrust
mkdir -p build artifacts

git clone https://github.com/malisper/pgrust.git build/pgrust
cd build/pgrust
PGRUST_WASM_PROFILE=wasm-release ./wasm/wasm-build.sh

cd ../..
cp build/pgrust/target/wasm32-wasip1/wasm-release/postgres.wasm \
  artifacts/postgres.wasm
```

`artifacts/postgres.wasm` — WASI Preview 1 core-модуль. Его нельзя передать
напрямую в `wasm.load`: runtime ожидает Component Model component с экспортом
`wasi:cli/run`.

## Преобразовать core-модуль в component

Для PostgreSQL нужен command adapter, а не reactor adapter. Команды ниже
скачивают adapter, создают component, удаляют отладочную информацию и
валидируют итоговый файл.

```sh
cd ~/tarantool-wasm-samples/pgrust

mkdir -p build/wasi-preview1-command-adapter
curl --fail --location \
  https://crates.io/api/v1/crates/wasi-preview1-component-adapter-provider/46.0.1/download \
  --output build/wasi-preview1-command-adapter.crate
tar -xzf build/wasi-preview1-command-adapter.crate \
  --strip-components=1 \
  -C build/wasi-preview1-command-adapter

wasm-tools component new artifacts/postgres.wasm \
  --adapt build/wasi-preview1-command-adapter/artefacts/wasi_snapshot_preview1.command.wasm \
  --output artifacts/pgrust.component.unstripped.wasm

wasm-tools validate artifacts/pgrust.component.unstripped.wasm
wasm-tools strip artifacts/pgrust.component.unstripped.wasm \
  --output artifacts/pgrust.component.wasm
wasm-tools validate artifacts/pgrust.component.wasm
```

Tarantool загружает итоговый `artifacts/pgrust.component.wasm`.

## Подготовить PostgreSQL datadir

Команды создают отдельный datadir и копируют PostgreSQL share files и базу
часовых поясов. Повторно запускать `initdb` для уже подготовленного datadir не
нужно.

```sh
cd ~/tarantool-wasm-samples/pgrust
mkdir -p runtime/pgdata runtime/share runtime/zoneinfo

HOST_UID=$(id -u)
HOST_GID=$(id -g)

docker run --rm -u 0 \
  -v "$PWD/runtime:/work" \
  --entrypoint bash \
  postgres:18 -lc "
    set -e
    chown postgres:postgres /work/pgdata
    gosu postgres /usr/lib/postgresql/18/bin/initdb \
      -D /work/pgdata \
      --no-locale \
      --encoding=UTF8 \
      -U postgres \
      -A trust
    cp -a /usr/share/postgresql/18/. /work/share/
    cp -RL /usr/share/zoneinfo/. /work/zoneinfo/
    chown -R $HOST_UID:$HOST_GID /work
  "
```

## Создать таблицу и выполнить SELECT

`smoke.sql` пересоздаёт таблицу `inventory`, вставляет четыре товара и
фиксирует транзакцию. После этого `run.lua` отправляет отдельный запрос через
ту же pipe-сессию:

```sql
SELECT id, product, quantity, price * quantity AS total
FROM inventory
WHERE quantity > 0
ORDER BY id;
```

Запустить пример можно из корня репозитория.

```sh
cd ~/tarantool-wasm-samples
export PGRUST_SAMPLE_ROOT="$PWD/pgrust"
export TARANTOOL_CPATH="$PWD/.rocks/lib/tarantool/?.so;;"

timeout 360s tarantool pgrust/run.lua
```

Ожидаемый результат:

```text
id=1 product=keyboard quantity=3 total=15000
id=2 product=mouse quantity=7 total=10500
id=4 product=webcam quantity=2 total=14000
PGRUST_PIPE_QUERY_OK
```

`pgwire.lua` выполняет startup handshake, кодирует запросы Simple Query
Protocol и разбирает `RowDescription`, `DataRow`, `CommandComplete`, ошибки и
`ReadyForQuery`. `session:close()` отправляет PostgreSQL Terminate, закрывает
stdin компонента и ожидает штатного завершения `wasi:cli/run`; при ошибке
адаптер отменяет процесс. `run.lua` закрывает сессию и выгружает модуль как на
успешном пути, так и после ошибки запроса или проверки.

## Ограничения

Это экспериментальный stdio-wire PoC с одной backend-сессией на экземпляр
компонента. Он не открывает PostgreSQL TCP-порт, не реализует конкурентный
server mode и хранит данные в собственном datadir, а не в Tarantool spaces.
Сеть, DNS, TCP и UDP для компонента отключены. Не используйте пример для
важных данных.

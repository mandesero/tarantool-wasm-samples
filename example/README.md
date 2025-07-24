# gRPC WASM-компонент

Пример, как вызывать gRPC-сервисы из Tarantool через WASM-компонент, реализованный на Python.

## Создание компонента

```bash
mkdir example && cd example
```

Создаём интерфейс для вызова gRPC-функций:

<details>
<summary><code>wit/grpc.wit</code></summary>

```wit
package example:grpc@0.1.0;

world grpc {
  // Импорт стандартных WASI-интерфейсов
  import wasi:cli/environment@0.2.3;
  import wasi:cli/exit@0.2.3;
  import wasi:io/error@0.2.3;
  import wasi:io/poll@0.2.3;
  import wasi:io/streams@0.2.3;
  import wasi:cli/stdin@0.2.3;
  import wasi:cli/stdout@0.2.3;
  import wasi:cli/stderr@0.2.3;
  import wasi:cli/terminal-input@0.2.3;
  import wasi:cli/terminal-output@0.2.3;
  import wasi:cli/terminal-stdin@0.2.3;
  import wasi:cli/terminal-stdout@0.2.3;
  import wasi:cli/terminal-stderr@0.2.3;
  import wasi:clocks/monotonic-clock@0.2.3;
  import wasi:clocks/wall-clock@0.2.3;
  import wasi:filesystem/types@0.2.3;
  import wasi:filesystem/preopens@0.2.3;
  import wasi:sockets/network@0.2.3;
  import wasi:sockets/instance-network@0.2.3;
  import wasi:sockets/udp@0.2.3;
  import wasi:sockets/udp-create-socket@0.2.3;
  import wasi:sockets/tcp@0.2.3;
  import wasi:sockets/tcp-create-socket@0.2.3;
  import wasi:sockets/ip-name-lookup@0.2.3;
  import wasi:random/random@0.2.3;
  import wasi:random/insecure@0.2.3;
  import wasi:random/insecure-seed@0.2.3;
  import wasi:http/types@0.2.3;
  import wasi:http/outgoing-handler@0.2.3;
  import wasi:tls/types@0.2.0-draft;

  // Варианты аргументов
  variant v-arg {
    name(string),
    number(s32),
  }

  // Варианты возвращаемых значений
  variant v-responce {
    none,
    str(string),
    num(s32),
  }

  record responce {
    status: string,
    value: v-responce,
    error: string,
  }

  export call: func(address: string, service: string, method: string, args: v-arg) -> responce;
}
```

</details>

---

## Зависимости

Для `wasi:tls`:

```bash
git clone https://github.com/WebAssembly/wasi-tls.git
```

Добавим в `wkg.toml`:

```toml
[overrides]
"wasi:tls" = { path = "./wasi-tls/wit" }
```

Сборка WIT:

```bash
wkg wit build
```

Инициализация и генерация биндингов:

```bash
tarawasm init --lang python --wasm-file example:grpc@0.1.0.wasm grpc
tarawasm bind
```

---

## Протокол gRPC

<details>
<summary><code>example.proto</code></summary>

```proto
syntax = "proto3";

package example;

service Greeter {
  rpc SayHello (HelloRequest) returns (HelloReply) {}
  rpc ProcessNumber (NumberRequest) returns (NumberReply) {}
}

message HelloRequest {
  string name = 1;
}

message HelloReply {
  string message = 1;
}

message NumberRequest {
  int32 value = 1;
}

message NumberReply {
  int32 result = 1;
}
```

</details>

---

## Установка зависимостей

```bash
pip3 install "grpclib[protobuf]" grpcio-tools
python3 -m grpc_tools.protoc -I. --python_out=. --grpclib_python_out=. example.proto
```

---

## Реализация клиента (WASM-сторона)

<details>
<summary><code>main.py</code></summary>

```python
from wit_world import VArg, Responce, VArg_Number, VArg_Name, VResponce_Num, VResponce_Str, VResponce_None_

import asyncio
from grpclib.client import Channel
from example_pb2 import HelloRequest, NumberRequest
from example_grpc import GreeterStub

async def say_hello(address: str, name: str) -> Responce:
    host, port = address.split(":")
    async with Channel(host, int(port)) as channel:
        stub = GreeterStub(channel)
        reply = await stub.SayHello(HelloRequest(name=name))
        return Responce(status="OK", value=VResponce_Str(reply.message), error="")

async def process_number(address: str, number: int) -> Responce:
    host, port = address.split(":")
    async with Channel(host, int(port)) as channel:
        stub = GreeterStub(channel)
        reply = await stub.ProcessNumber(NumberRequest(value=number))
        return Responce(status="OK", value=VResponce_Num(reply.result), error="")

class WitWorld:
    def call(self, address: str, service: str, method: str, args: VArg) -> Responce:
        try:
            if service != "example.Greeter":
                return Responce(status="Error", value=VResponce_None_(), error=f"Unsupported service: {service}")
            if isinstance(args, VArg_Name) and method == "SayHello":
                return asyncio.run(say_hello(address, args.value))
            if isinstance(args, VArg_Number) and method == "ProcessNumber":
                return asyncio.run(process_number(address, args.value))
            return Responce(status="Error", value=VResponce_None_(), error=f"Unsupported method {method} for argument type {type(args).__name__}")
        except Exception as e:
            return Responce(status="Error", value=VResponce_None_(), error=f"gRPC call failed: {e}")
```

</details>

---

## Сервер gRPC (внешний)

<details>
<summary><code>server.py</code></summary>

```python
import asyncio
from grpclib.server import Server
from grpclib.utils import graceful_exit
from example_pb2 import HelloReply, NumberReply
from example_grpc import GreeterBase

class Greeter(GreeterBase):
    async def SayHello(self, stream):
        req = await stream.recv_message()
        await stream.send_message(HelloReply(message=f"Hello, {req.name}!"))

    async def ProcessNumber(self, stream):
        req = await stream.recv_message()
        await stream.send_message(NumberReply(result=req.value * 2))

async def main():
    server = Server([Greeter()])
    with graceful_exit([server]):
        await server.start("127.0.0.1", 50051)
        print("Serving on 127.0.0.1:50051")
        await server.wait_closed()

if __name__ == "__main__":
    asyncio.run(main())
```

</details>

---

## Тестирование в Tarantool

> Необходим Tarantool, собранный с `-DTARANTOOL_WASM=ON`.
> Форк: (ветка wasm-module) https://github.com/mandesero/tarantool/tree/wasm-module
> Необходимо так же принести библиотеку `wasm.so`

```bash
mkdir build && cd build
cmake .. -DCMAKE_BUILD_TYPE=Debug -DENABLE_BACKTRACE=ON -DTARANTOOL_WASM=ON
make -j
```

---

## Пример запуска

```
Tarantool 3.5.0-entrypoint-104-g18fe056f3e
type 'help' for interactive help
tarantool> lwasm = require('luawasm')
---
...

tarantool> m = lwasm:new({ dir = "./example" }) -- путь до директории с компонентом, собранным с помощью tarawasm
---
...

tarantool> m:call("127.0.0.1:50051", "example.Greeter", "SayHello", { name = "LuaUser" })
---
- status: OK
  error:
  value:
    str: Hello, LuaUser!
...

tarantool> m:call("127.0.0.1:50051", "example.Greeter", "SayHello", { number = 3 })
---
- status: Error
  error: Unsupported method SayHello for argument type VArg_Number
  value: []
...

tarantool> m:call("127.0.0.1:50051", "example.Greeter", "ProcessNumber", { number = 3 })
---
- status: OK
  error:
  value:
    num: 6
...
```

## Tarantool logs

```sh
$ tarantool --name instance-001 --config config.yaml -i
started
2025-08-28 15:17:34.085 [187015] main/104/interactive main.cc:507 I> Tarantool 3.6.0-entrypoint-5-g310d334c51 Linux-x86_64-Debug
2025-08-28 15:17:34.085 [187015] main/104/interactive main.cc:510 I> log level 5 (INFO)
2025-08-28 15:17:34.085 [187015] main/104/interactive gc.c:132 I> wal/engine cleanup is paused
2025-08-28 15:17:34.087 [187015] main/104/interactive tuple.c:410 I> mapping 268435456 bytes for memtx tuple arena...
2025-08-28 15:17:34.087 [187015] main/104/interactive memtx_engine.cc:2063 I> Actual slab_alloc_factor calculated on the basis of desired slab_alloc_factor = 1.044274
2025-08-28 15:17:34.087 [187015] main/104/interactive tuple.c:410 I> mapping 134217728 bytes for vinyl tuple arena...
2025-08-28 15:17:34.099 [187015] main/104/interactive box.cc:2473 I> update replication_synchro_quorum = 1
2025-08-28 15:17:34.099 [187015] main/104/interactive box.cc:3565 I> The option replication_synchro_queue_max_size will actually take effect after the recovery is finished
2025-08-28 15:17:34.099 [187015] main/104/interactive box.cc:5758 I> instance uuid cdefcc21-adec-4d9f-bd54-95af1425c70f
2025-08-28 15:17:34.099 [187015] main/104/interactive memtx_engine.cc:903 I> initializing an empty data directory
2025-08-28 15:17:34.128 [187015] main/104/interactive replication.cc:575 I> assigned id 1 to replica cdefcc21-adec-4d9f-bd54-95af1425c70f
2025-08-28 15:17:34.128 [187015] main/104/interactive replication.cc:593 I> assigned name instance-001 to replica cdefcc21-adec-4d9f-bd54-95af1425c70f
2025-08-28 15:17:34.128 [187015] main/104/interactive box.cc:2473 I> update replication_synchro_quorum = 1
2025-08-28 15:17:34.128 [187015] main/104/interactive alter.cc:4201 I> replicaset uuid 69f47655-6523-43c6-93a8-3df6f344f3d7
2025-08-28 15:17:34.128 [187015] main/104/interactive alter.cc:4214 I> replicaset name: replicaset-001
2025-08-28 15:17:34.131 [187015] snapshot/101/main memtx_engine.cc:1310 I> saving snapshot `var/lib/instance-001/00000000000000000000.snap.inprogress'
2025-08-28 15:17:34.133 [187015] snapshot/101/main memtx_engine.cc:1473 I> done
2025-08-28 15:17:34.134 [187015] main/104/interactive box.cc:684 I> leaving waiting_for_own_rows mode
2025-08-28 15:17:34.134 [187015] main/104/interactive box.cc:6276 I> ready to accept requests
2025-08-28 15:17:34.134 [187015] main/108/gc gc.c:320 I> wal/engine cleanup is resumed
2025-08-28 15:17:34.134 [187015] main/104/interactive/box.load_cfg load_cfg.lua:988 I> set 'custom_proc_title' configuration option to "tarantool - instance-001"
2025-08-28 15:17:34.134 [187015] main/104/interactive/box.load_cfg load_cfg.lua:988 I> set 'instance_name' configuration option to "instance-001"
2025-08-28 15:17:34.134 [187015] main/104/interactive/box.load_cfg load_cfg.lua:988 I> set 'log_nonblock' configuration option to false
2025-08-28 15:17:34.134 [187015] main/104/interactive/box.load_cfg load_cfg.lua:988 I> set 'replicaset_name' configuration option to "replicaset-001"
2025-08-28 15:17:34.134 [187015] main/104/interactive/box.load_cfg load_cfg.lua:988 I> set 'replication' configuration option to []
2025-08-28 15:17:34.134 [187015] main/109/checkpoint_daemon gc.c:654 I> scheduled next checkpoint for Thu Aug 28 16:49:31 2025
2025-08-28 15:17:34.134 [187015] main/104/interactive box.cc:446 I> box switched to rw
2025-08-28 15:17:34.134 [187015] main/104/interactive/box.load_cfg load_cfg.lua:988 I> set 'metrics' configuration option to {"labels":{"alias":"instance-001"},"include":["all"],"exclude":[]}
Added handler '/hello' from 'libhandlers'
Added handler '/echo' from 'libhandlers'
Added handler '/bin' from 'libhandlers'
2025-08-28 15:17:36.742 [187015] main/104/interactive init.c:1176 C> Tarantool 3.6.0-entrypoint-5-g310d334c51
type 'help' for interactive help
tarantool> WARNING: This is a development server. Do not use it in a production deployment. Use a production WSGI server instead.
 * Running on http://127.0.0.1:39983
Press CTRL+C to quit

127.0.0.1 - - [28/Aug/2025 12:20:19] "POST /register-handler/hello HTTP/1.1" 200 -
127.0.0.1 - - [28/Aug/2025 12:20:40] "GET / HTTP/1.0" 200 -
127.0.0.1 - - [28/Aug/2025 12:22:16] "HEAD /hello HTTP/1.1" 200 -
```

## HTTP client

```sh
$ curl -X POST http://127.0.0.1:39983/register-handler/hello
{"registered":"/hello"}

$ curl -I http://127.0.0.1:39983/hello
HTTP/1.0 200 OK
Server: Werkzeug/ Python/3.12.1
Date: Thu, 28 Aug 2025 12:22:16 GMT
Content-Type: text/plain; charset=utf-8
X-Reason: OK
Content-Length: 21
Connection: close

$ curl -I http://127.0.0.1:39983/unknown
HTTP/1.0 404 NOT FOUND
Server: Werkzeug/ Python/3.12.1
Date: Thu, 28 Aug 2025 12:24:41 GMT
Content-Type: application/json
Content-Length: 22
Connection: close
```
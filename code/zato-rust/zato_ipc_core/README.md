# zato_ipc_core

Shared memory region of a Zato server - the heartbeat of the worker, the keyed locks of outgoing connections with their counters and the first-in first-out queues through which the worker and the config process take turns holding them, and the wake-up descriptors of the places of those queues.

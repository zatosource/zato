# The runtime image of the Zato pods of the Kubernetes suites. The pods run the node, the scheduler and the server
# from the repository that they mount, so the image provides the interpreter of its virtual environment, the shared
# libraries that its extension modules load, Redis and the process tools that the faults of the suites use.

FROM ubuntu:24.04 AS keyring

RUN apt-get update && \
    DEBIAN_FRONTEND=noninteractive apt-get install -y --no-install-recommends ca-certificates curl gnupg && \
    curl -fsSL https://packages.redis.io/gpg | gpg --dearmor -o /redis-archive-keyring.gpg

FROM ubuntu:24.04

COPY --from=keyring /redis-archive-keyring.gpg /usr/share/keyrings/redis-archive-keyring.gpg

RUN apt-get update && \
    DEBIAN_FRONTEND=noninteractive apt-get install -y --no-install-recommends ca-certificates && \
    echo "deb [signed-by=/usr/share/keyrings/redis-archive-keyring.gpg] https://packages.redis.io/deb noble main" \
        > /etc/apt/sources.list.d/redis.list && \
    apt-get update && \
    DEBIAN_FRONTEND=noninteractive apt-get install -y --no-install-recommends \
        python3.12 libpq5 libodbc2 libodbcinst2 libltdl7 libsqlite3-0 libmagic1 tzdata procps redis-server && \
    rm -rf /var/lib/apt/lists/*

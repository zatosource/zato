# The runtime that the entrypoint of the Zato image expects. The repository is mounted from the host at its own path,
# in place of the code that the image installs, and the entrypoint and its scripts are mounted from the Docker repository.
FROM ubuntu:noble

ARG Zato_Repository_Directory
ARG Zato_User_ID
ARG Zato_Group_ID

ENV Zato_Version=4.1 \
    Zato_Python_Version=3.12 \
    Zato_Env_Path=/opt/zato/env/qs-1 \
    Zato_Log_Env_Details=False \
    Zato_Update_CA_Certificates=False \
    Zato_Install_Updates=False \
    Zato_Start_Scheduler=False \
    SSL_CERT_FILE=/etc/ssl/certs/ca-certificates.crt \
    REQUESTS_CA_BUNDLE=/etc/ssl/certs/ca-certificates.crt \
    Zato_Port_Dashboard=8183 \
    Zato_Port_Dashboard_SSL=8184 \
    Zato_Port_API_Portal=8185 \
    Zato_Port_API_Portal_SSL=8186 \
    Zato_Port_Server=17010 \
    Zato_Port_Load_Balancer=11223 \
    Zato_Port_Load_Balancer_SSL=11224 \
    Zato_Port_MLLP=11553 \
    Zato_Port_MLLP_SSL=11554 \
    Zato_HL7_MLLP_Port=31312 \
    Zato_Port_On_Prem_Gateway_Hub=11226 \
    Zato_Port_On_Prem_Gateway_Admin=11227 \
    Zato_Port_SSH=22

RUN apt-get update && \
    DEBIAN_FRONTEND=noninteractive apt-get install -y --no-install-recommends \
        ca-certificates cron curl gettext-base haproxy libgmp10 libgssapi-krb5-2 libkrb5-3 libldap2 libltdl7 \
        libmagic1 libodbc2 libodbcinst2 libpq5 libsasl2-2 logrotate make openssh-server openssl procps \
        python3.12 redis-server sudo tzdata && \
    rm -rf /var/lib/apt/lists/*

# The zato account takes the host user's identifiers, because the host's key files are readable by their owner only.
# The entrypoint adds the account to the ubuntu group, which is recreated once the ubuntu account releases the identifiers.
RUN userdel --remove ubuntu && \
    groupadd --gid ${Zato_Group_ID} zato && \
    groupadd ubuntu && \
    useradd --uid ${Zato_User_ID} --gid zato --home-dir /opt/zato --create-home --shell /bin/bash zato && \
    ln -s ${Zato_Repository_Directory} /opt/zato/4.1 && \
    ln -s /opt/zato/4.1/code /opt/zato/current && \
    mkdir -p /opt/zato/env/details /opt/hot-deploy/services /opt/hot-deploy/user-conf /opt/hot-deploy/enmasse && \
    touch /opt/hot-deploy/enmasse/env.ini && \
    chown -R zato:zato /opt/zato /opt/hot-deploy

ENTRYPOINT ["/entrypoint.sh"]

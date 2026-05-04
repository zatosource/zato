#!/bin/bash

set -e

if [ -z "$1" ] || [ -z "$2" ] || [ -z "$3" ] || [ -z "$4" ] || [ -z "$5" ] || [ -z "$6" ]; then
    echo "Usage: $0 <fernet-key> <provider> <bucket> <access-key> <secret-key> <env-dir> [backup-password]"
    echo ""
    echo "  fernet-key      - Fernet encryption key for storing settings in Redis"
    echo "  provider        - Cloud provider: aws, gcs, azure"
    echo "  bucket          - Bucket or container name"
    echo "  access-key      - Cloud provider access key"
    echo "  secret-key      - Cloud provider secret key"
    echo "  env-dir         - Path to the environment directory to back up"
    echo "  backup-password - (optional) Archive encryption password for cron use"
    exit 1
fi

FERNET_KEY="$1"
PROVIDER="$2"
BUCKET="$3"
ACCESS_KEY="$4"
SECRET_KEY="$5"
ENV_DIR="$6"
BACKUP_PASSWORD="$7"

ENCRYPTED_SETTINGS=$(python3 -c "
from cryptography.fernet import Fernet
import json
fernet = Fernet('${FERNET_KEY}'.encode())
settings = json.dumps({
    'provider': '${PROVIDER}',
    'bucket_name': '${BUCKET}',
    'access_key': '${ACCESS_KEY}',
    'secret_key': '${SECRET_KEY}',
    'env_dir': '${ENV_DIR}',
})
print(fernet.encrypt(settings.encode()).decode())
")

redis-cli SET zato:backup:settings "$ENCRYPTED_SETTINGS"
echo "Stored backup settings in Redis (zato:backup:settings)"

if [ -n "$BACKUP_PASSWORD" ]; then
    ENCRYPTED_PASSWORD=$(python3 -c "
from cryptography.fernet import Fernet
fernet = Fernet('${FERNET_KEY}'.encode())
print(fernet.encrypt('${BACKUP_PASSWORD}'.encode()).decode())
")
    redis-cli SET zato:backup:password "$ENCRYPTED_PASSWORD"
    echo "Stored backup password in Redis (zato:backup:password)"
fi

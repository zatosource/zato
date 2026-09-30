#!/bin/bash

# Downloads the deployment program, installs its systemd units and starts them.
# cloud-init runs it once, with the base URL of the program's files as the only argument.

set -euo pipefail

base_url="$1"
target_dir=/opt/zato-deploy

curl_opts=(-fsSL --retry 10 --retry-all-errors)

mkdir -p "$target_dir" /var/lib/zato-deploy/link /var/log/zato-deploy /etc/systemd/journald.conf.d

curl "${curl_opts[@]}" -o "$target_dir/files.txt" "$base_url/files.txt"

while read -r name; do
  if [ -n "$name" ]; then
    curl "${curl_opts[@]}" --create-dirs -o "$target_dir/$name" "$base_url/$name"
  fi
done < "$target_dir/files.txt"

chmod 0644 "$target_dir/github_known_hosts"

if ! command -v git >/dev/null; then
  export DEBIAN_FRONTEND=noninteractive
  apt-get -q -o DPkg::Lock::Timeout=600 update
  apt-get -q -o DPkg::Lock::Timeout=600 install -y git
fi

install -m 0644 "$target_dir"/units/*.service "$target_dir"/units/*.path "$target_dir"/units/*.timer /etc/systemd/system/
install -m 0644 "$target_dir/journald/zato.conf" /etc/systemd/journald.conf.d/zato.conf
install -m 0644 "$target_dir/logrotate/zato-deploy" /etc/logrotate.d/zato-deploy

systemctl restart systemd-journald
systemctl daemon-reload
systemctl enable --now zato-deploy.service zato-env-repo.path zato-env-repo.timer

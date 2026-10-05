#!/bin/bash

# Downloads the deployment program, installs its systemd units and starts them.
# cloud-init runs it once, with the base URL of the program's files as the only argument.
# Each line of files.txt names a file to download, and a line with a second word names
# a file shared with the rest of the repository, given as its path from the repository's root.

set -euo pipefail

base_url="$1"
repo_url="${base_url%/cloud/deploy}"
target_dir=/opt/zato-deploy

curl_opts=(-fsSL --retry 10 --retry-all-errors)

mkdir -p "$target_dir" /var/lib/zato-deploy/link /var/log/zato-deploy /etc/systemd/journald.conf.d

curl "${curl_opts[@]}" -o "$target_dir/files.txt" "$base_url/files.txt"

while read -r name source; do
  if [ -n "$source" ]; then
    curl "${curl_opts[@]}" --create-dirs -o "$target_dir/$name" "$repo_url/$source"
  elif [ -n "$name" ]; then
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

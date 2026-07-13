#!/usr/bin/env bash
set -euo pipefail

root="${1:-projects/sock-shop/sources}"
mkdir -p "$root"
repos=(front-end catalogue carts orders payment shipping user)
for repo in "${repos[@]}"; do
  if [[ -d "$root/$repo/.git" ]]; then
    printf 'exists: %s\n' "$repo"
  else
    git clone --depth 1 "https://github.com/microservices-demo/$repo.git" "$root/$repo"
  fi
done
printf 'Fetched Sock Shop sources under %s\n' "$root"

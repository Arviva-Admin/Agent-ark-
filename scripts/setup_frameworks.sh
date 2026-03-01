#!/usr/bin/env bash
set -euo pipefail

mkdir -p third_party

if [ ! -d third_party/Agent-S ]; then
  git clone https://github.com/simular-ai/Agent-S.git third_party/Agent-S
else
  echo "Agent-S already present"
fi

if [ ! -d third_party/SuperAGI ]; then
  git clone https://github.com/TransformerOptimus/SuperAGI.git third_party/SuperAGI
else
  echo "SuperAGI already present"
fi

echo "Framework repositories ready under third_party/."

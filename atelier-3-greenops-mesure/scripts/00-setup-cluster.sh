#!/usr/bin/env bash
# Atelier 3 — Cluster Kind pour Kepler
set -euo pipefail

CLUSTER_NAME="greenops-lab"

if kind get clusters | grep -q "^${CLUSTER_NAME}$"; then
  kind delete cluster --name "${CLUSTER_NAME}"
fi

cat <<EOF | kind create cluster --name "${CLUSTER_NAME}" --config=-
kind: Cluster
apiVersion: kind.x-k8s.io/v1alpha4
nodes:
  - role: control-plane
  - role: worker
EOF

echo "==> Cluster '${CLUSTER_NAME}' prêt."
kubectl get nodes

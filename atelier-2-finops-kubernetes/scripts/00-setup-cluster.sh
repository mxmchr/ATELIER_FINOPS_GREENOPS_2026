#!/usr/bin/env bash
# Atelier 2 — Crée un cluster Kind à 3 nœuds avec labels d'instance simulés.
set -euo pipefail

CLUSTER_NAME="finops-lab"

if kind get clusters | grep -q "^${CLUSTER_NAME}$"; then
  echo "Cluster '${CLUSTER_NAME}' existe déjà — suppression..."
  kind delete cluster --name "${CLUSTER_NAME}"
fi

cat <<EOF | kind create cluster --name "${CLUSTER_NAME}" --config=-
kind: Cluster
apiVersion: kind.x-k8s.io/v1alpha4
nodes:
  - role: control-plane
    labels:
      node.kubernetes.io/instance-type: t3.medium
      topology.kubernetes.io/region: eu-west-1
      topology.kubernetes.io/zone: eu-west-1a
  - role: worker
    labels:
      node.kubernetes.io/instance-type: m5.large
      topology.kubernetes.io/region: eu-west-1
      topology.kubernetes.io/zone: eu-west-1a
  - role: worker
    labels:
      node.kubernetes.io/instance-type: m5.large
      topology.kubernetes.io/region: eu-west-1
      topology.kubernetes.io/zone: eu-west-1b
EOF

echo ""
echo "==> Cluster créé. Nœuds :"
kubectl get nodes --show-labels | cut -c1-160
echo ""
echo "Prochaine étape : helm install OpenCost et Prometheus (voir README Partie 2)."

#!/usr/bin/env bash
# Atelier 3 — Déploie Kepler en mode estimation (compatible Codespaces VM).
set -euo pipefail

kubectl create namespace kepler --dry-run=client -o yaml | kubectl apply -f -

# Installation via le manifest officiel (release v0.7.x)
kubectl apply -f https://raw.githubusercontent.com/sustainable-computing-io/kepler/main/manifests/k8s/config/exporter/exporter.yaml

echo "==> Attente du DaemonSet Kepler..."
kubectl -n kepler rollout status ds/kepler-exporter --timeout=180s || true

kubectl -n kepler get pods
echo ""
echo "==> Test des métriques :"
echo "kubectl port-forward -n kepler ds/kepler-exporter 9102:9102 &"
echo "curl -s localhost:9102/metrics | grep kepler_container_joules_total | head"

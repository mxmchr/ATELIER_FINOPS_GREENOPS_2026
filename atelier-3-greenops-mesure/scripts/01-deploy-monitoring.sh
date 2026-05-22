#!/usr/bin/env bash
# Atelier 3 — Déploie Prometheus + Grafana sur le cluster.
set -euo pipefail

helm repo add prometheus-community https://prometheus-community.github.io/helm-charts >/dev/null 2>&1 || true
helm repo update >/dev/null

kubectl create namespace monitoring --dry-run=client -o yaml | kubectl apply -f -

helm upgrade --install kps prometheus-community/kube-prometheus-stack \
  --namespace monitoring \
  --set alertmanager.enabled=false \
  --set grafana.adminPassword="prom-operator" \
  --set prometheus.prometheusSpec.retention=3d \
  --wait --timeout 5m

echo "==> Prometheus + Grafana installés."
echo "    Grafana : kubectl port-forward -n monitoring svc/kps-grafana 3000:80"
echo "              login admin / prom-operator"

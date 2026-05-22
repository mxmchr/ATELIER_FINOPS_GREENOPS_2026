#!/usr/bin/env bash
# Atelier 3 — Déploie 3 workloads contrastés pour profiler avec Kepler.
set -euo pipefail

kubectl apply -f - <<'EOF'
apiVersion: v1
kind: Namespace
metadata: { name: workloads }
---
# Workload 1 : IDLE — ne fait quasi rien
apiVersion: apps/v1
kind: Deployment
metadata: { name: idle-app, namespace: workloads, labels: { app: idle-app } }
spec:
  replicas: 1
  selector: { matchLabels: { app: idle-app } }
  template:
    metadata: { labels: { app: idle-app, profile: idle } }
    spec:
      containers:
        - name: app
          image: busybox:1.36
          command: ["sh", "-c", "while true; do sleep 30; done"]
          resources:
            requests: { cpu: "50m", memory: "32Mi" }
---
# Workload 2 : CPU-INTENSIVE — boucle Python qui fait des matmul
apiVersion: apps/v1
kind: Deployment
metadata: { name: cpu-intensive, namespace: workloads, labels: { app: cpu-intensive } }
spec:
  replicas: 1
  selector: { matchLabels: { app: cpu-intensive } }
  template:
    metadata: { labels: { app: cpu-intensive, profile: heavy } }
    spec:
      containers:
        - name: app
          image: python:3.11-slim
          command: ["python", "-c"]
          args:
            - |
              import time, random
              # CPU constant ~70%
              while True:
                  start = time.time()
                  # Pi par méthode Monte Carlo (CPU-bound, pas de math optimisé)
                  inside = 0
                  for _ in range(1_000_000):
                      x, y = random.random(), random.random()
                      if x*x + y*y < 1: inside += 1
                  print("pi ≈", 4 * inside / 1_000_000, flush=True)
                  # Petite pause pour ne pas tout cramer
                  time.sleep(0.1)
          resources:
            requests: { cpu: "500m", memory: "128Mi" }
            limits:   { cpu: "1000m", memory: "256Mi" }
---
# Workload 3 : CACHE-FRIENDLY — même algo mais avec optimisation (math.tau, vectorisation)
apiVersion: apps/v1
kind: Deployment
metadata: { name: cache-friendly, namespace: workloads, labels: { app: cache-friendly } }
spec:
  replicas: 1
  selector: { matchLabels: { app: cache-friendly } }
  template:
    metadata: { labels: { app: cache-friendly, profile: optimized } }
    spec:
      containers:
        - name: app
          image: python:3.11-slim
          command: ["sh", "-c"]
          args:
            - |
              pip install --quiet numpy
              python -c "
              import time
              import numpy as np
              while True:
                  # Même résultat, mais vectorisé (plus efficient)
                  pts = np.random.rand(1_000_000, 2)
                  inside = (pts[:,0]**2 + pts[:,1]**2 < 1).sum()
                  print('pi ≈', 4 * inside / 1_000_000, flush=True)
                  time.sleep(0.5)
              "
          resources:
            requests: { cpu: "500m", memory: "128Mi" }
            limits:   { cpu: "1000m", memory: "256Mi" }
EOF

echo "==> Workloads déployés. Attendre 20 min puis observer Grafana."
kubectl -n workloads get pods

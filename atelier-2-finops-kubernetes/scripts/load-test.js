// Atelier 2 — Test de charge progressif sur le frontend pour déclencher l'HPA.
// Lancer : kubectl port-forward -n boutique svc/frontend 8080:80 (dans un autre terminal)
//          puis : k6 run scripts/load-test.js

import http from 'k6/http';
import { check, sleep } from 'k6';

export const options = {
  stages: [
    { duration: '1m', target: 20 },    // montée à 20 VU
    { duration: '2m', target: 100 },   // montée à 100 VU
    { duration: '3m', target: 100 },   // tenir 100 VU
    { duration: '1m', target: 200 },   // pic à 200 VU
    { duration: '2m', target: 0 },     // redescente
  ],
  thresholds: {
    http_req_failed: ['rate<0.05'],         // <5% d'erreurs
    http_req_duration: ['p(95)<1000'],      // p95 < 1s
  },
};

const BASE_URL = __ENV.TARGET_URL || 'http://localhost:8080';

export default function () {
  // Endpoint qui consomme du CPU (calcul d'un nombre premier)
  const res = http.get(`${BASE_URL}/api/info`);
  check(res, { 'status 200': (r) => r.status === 200 });
  sleep(Math.random() * 0.5);
}

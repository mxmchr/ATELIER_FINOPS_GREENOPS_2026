"""
Génère un dataset CUR (Cost and Usage Report) synthétique pour l'atelier 1.
Le dataset simule 90 jours de consommation d'une entreprise fictive avec :
- 4 comptes (prod, staging, dev, sandbox)
- 8 services AWS
- 4 équipes
- Anomalies réalistes (pic, gaspillage, ressources orphelines)
"""

import csv
import random
import datetime as dt
from pathlib import Path

random.seed(42)

OUT = Path(__file__).parent / "cur_sample.csv"

SERVICES = {
    "AmazonEC2": (0.45, ["BoxUsage:t3.medium", "BoxUsage:t3.large", "BoxUsage:m5.xlarge", "BoxUsage:c5.2xlarge"]),
    "AmazonS3":  (0.10, ["TimedStorage-ByteHrs", "Requests-Tier1", "DataTransfer-Out-Bytes"]),
    "AmazonRDS": (0.18, ["InstanceUsage:db.t3.medium", "InstanceUsage:db.m5.large", "RDS:StorageUsage"]),
    "AWSLambda": (0.04, ["Lambda-GB-Second", "Lambda-Request"]),
    "AmazonEBS": (0.06, ["VolumeUsage.gp3", "VolumeUsage.gp2", "SnapshotUsage"]),
    "AmazonCloudWatch": (0.05, ["DataProcessing-Bytes", "LogStorage"]),
    "AmazonVPC": (0.07, ["PublicIPv4:InUseAddress", "NatGateway-Hours", "DataTransfer-Regional-Bytes"]),
    "AmazonEKS": (0.05, ["AmazonEKS-Hours-Cluster"]),
}

ACCOUNTS = {
    "111111111111": "prod",
    "222222222222": "staging",
    "333333333333": "dev",
    "444444444444": "sandbox",
}

REGIONS = ["eu-west-1", "eu-west-3", "us-east-1"]
REGION_WEIGHTS = [0.6, 0.25, 0.15]

TEAMS = ["payments", "platform", "data", "frontend"]
PROJECTS = ["checkout", "customer-portal", "analytics", "internal-tools", "growth"]


def maybe(value, prob):
    """Retourne value avec prob, sinon chaîne vide (tags manquants)."""
    return value if random.random() < prob else ""


def base_cost_for(service: str, usage_type: str, env: str) -> float:
    """Coût horaire de base avant aléatoire."""
    base = {
        "BoxUsage:t3.medium": 0.0416,
        "BoxUsage:t3.large": 0.0832,
        "BoxUsage:m5.xlarge": 0.192,
        "BoxUsage:c5.2xlarge": 0.34,
        "InstanceUsage:db.t3.medium": 0.068,
        "InstanceUsage:db.m5.large": 0.171,
        "RDS:StorageUsage": 0.0023,
        "TimedStorage-ByteHrs": 0.000023,
        "Requests-Tier1": 0.000005,
        "DataTransfer-Out-Bytes": 0.09,
        "Lambda-GB-Second": 0.0000166667,
        "Lambda-Request": 0.0000002,
        "VolumeUsage.gp3": 0.08,
        "VolumeUsage.gp2": 0.10,
        "SnapshotUsage": 0.05,
        "DataProcessing-Bytes": 0.50,
        "LogStorage": 0.03,
        "PublicIPv4:InUseAddress": 0.005,
        "NatGateway-Hours": 0.045,
        "DataTransfer-Regional-Bytes": 0.01,
        "AmazonEKS-Hours-Cluster": 0.10,
    }.get(usage_type, 0.05)
    if env == "prod":
        return base * random.uniform(0.95, 1.05)
    if env == "staging":
        return base * random.uniform(0.4, 0.6)
    if env == "dev":
        return base * random.uniform(0.2, 0.4)
    return base * random.uniform(0.05, 0.15)  # sandbox


def generate():
    start = dt.date(2025, 1, 1)
    rows = []
    headers = [
        "usage_date", "account_id", "service", "region", "usage_type",
        "usage_amount", "unblended_cost", "tag_team", "tag_env", "tag_project"
    ]

    for day_offset in range(90):
        date = start + dt.timedelta(days=day_offset)
        is_weekend = date.weekday() >= 5
        # Pic sur le jour 45 (incident de production / runaway)
        is_incident = day_offset == 45
        # Tendance croissante S3 (+1% par jour, simule croissance des logs)
        s3_growth = 1 + day_offset * 0.012

        for account_id, env in ACCOUNTS.items():
            # Le sandbox est presque vide en week-end
            activity_factor = 1.0
            if env != "prod" and is_weekend:
                activity_factor = 0.95  # devrait être ~0.3 si bien optimisé !

            for service, (base_share, usage_types) in SERVICES.items():
                if random.random() > base_share * 4:  # densité réaliste
                    continue
                for usage_type in usage_types:
                    if random.random() > 0.7:
                        continue

                    region = random.choices(REGIONS, weights=REGION_WEIGHTS, k=1)[0]
                    usage_amount = random.uniform(10, 500) * activity_factor

                    cost = base_cost_for(service, usage_type, env) * usage_amount
                    # Variation
                    cost *= random.uniform(0.8, 1.2)
                    # Croissance S3
                    if service == "AmazonS3":
                        cost *= s3_growth

                    # Incident sur EC2 prod jour 45
                    if is_incident and service == "AmazonEC2" and env == "prod":
                        cost *= 4

                    # Tagging imparfait (volontaire)
                    team_tag_prob = {"prod": 0.95, "staging": 0.85, "dev": 0.60, "sandbox": 0.20}[env]
                    env_tag_prob = {"prod": 0.98, "staging": 0.90, "dev": 0.70, "sandbox": 0.25}[env]
                    project_tag_prob = {"prod": 0.85, "staging": 0.70, "dev": 0.45, "sandbox": 0.15}[env]

                    rows.append([
                        date.isoformat(),
                        account_id,
                        service,
                        region,
                        usage_type,
                        round(usage_amount, 2),
                        round(cost, 4),
                        maybe(random.choice(TEAMS), team_tag_prob),
                        maybe(env, env_tag_prob),
                        maybe(random.choice(PROJECTS), project_tag_prob),
                    ])

    # Ajouter quelques volumes EBS orphelins (sans EC2 le même jour-compte)
    for _ in range(30):
        day_offset = random.randint(0, 89)
        date = start + dt.timedelta(days=day_offset)
        rows.append([
            date.isoformat(),
            "333333333333",  # dev
            "AmazonEBS",
            "eu-west-1",
            "VolumeUsage.gp2",
            random.uniform(50, 200),
            round(random.uniform(5, 25), 4),
            "",  # pas de tag équipe
            "",
            "",
        ])

    with OUT.open("w", newline="") as f:
        writer = csv.writer(f)
        writer.writerow(headers)
        writer.writerows(rows)

    print(f"Généré : {OUT} ({len(rows)} lignes)")
    total = sum(r[6] for r in rows)
    print(f"Coût total simulé : ${total:,.2f}")


if __name__ == "__main__":
    generate()

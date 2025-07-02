import pod_energie_query_kepler
import subprocess
import time
import matplotlib.pyplot as plt

import yaml

# kubectl port-forward svc/prometheus-kube-prometheus-prometheus 9090:9090 -n monitoring

PATH_TO_CONFIG = "python-example.yaml"

def set_parallelism_in_yaml(yaml_path: str, value: int):
    with open(yaml_path, 'r') as f:
        data = yaml.safe_load(f)

    # Setze den Parallelism-Wert (Pfad muss ggf. angepasst werden!)
    data["spec"]["job"]["parallelism"] = value

    with open(yaml_path, 'w') as f:
        yaml.safe_dump(data, f)


def get_pods_by_label(label_selector: str) -> list[str]:
    """Liefert alle Pod-Namen mit passendem Label."""
    try:
        subprocess.run(
            ["kubectl", "wait", "--for=condition=Ready", "pod", "-l", label_selector, "--timeout=60s"],
            check=True,
            capture_output=True,
            text=True
        )
    except subprocess.CalledProcessError:
        print("⚠️ Warnung: Einige Pods wurden nicht rechtzeitig bereit.")

    result = subprocess.run(
        ["kubectl", "get", "pods", "-l", label_selector, "-o", "jsonpath={.items[*].metadata.name}"],
        check=True,
        capture_output=True,
        text=True
    )
    return result.stdout.strip().split()

# Ergebnisse sammeln
parallelisierung = []
energieverbrauch = []

# Test mit Parallelsierung von 1 bis 20
for i in [2, 4, 6, 8]:
    print(f"\n🔧 Starte Test mit Parallelsierung: {i}")

    set_parallelism_in_yaml(PATH_TO_CONFIG, i)

    # Führt FlinkDeployment aus
    subprocess.run(["bash", "build.sh"], check=True)

    # Etwas Zeit geben, bis Pods ready sind (optional)
    time.sleep(10)

    # Pods sammeln (anhand Label)
    pods = get_pods_by_label("app=python-example")
    print(f"📦 Erstellte Pods: {pods}")

    time.sleep(400)

    # Energieverbrauch aller Pods aufsummieren
    energy_total = 0
    for pod in pods:
        energy = pod_energie_query_kepler.query_energy(pod)
        energy_total += energy

    print(f"⚡ Gesamtverbrauch (letzte 5 Minuten): {energy_total:.2f} Joule")

    # Ergebnisse speichern
    parallelisierung.append(i)
    energieverbrauch.append(round(energy_total, 2))


# 📈 Plot am Ende
plt.plot(parallelisierung, energieverbrauch, marker="o")
plt.title("Energieverbrauch vs. Parallelsierung")
plt.xlabel("Parallelsierung (Pods)")
plt.ylabel("Energieverbrauch in Joule (letzte 5 Minuten)")
plt.grid(True)
plt.tight_layout()
plt.savefig("energieverbrauch_plot.png")

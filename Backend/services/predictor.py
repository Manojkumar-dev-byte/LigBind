import random
import hashlib


def run_prediction(disease, drugs):
    # Stable seed based on disease name
    seed_value = int(
        hashlib.md5(disease.lower().encode()).hexdigest(),
        16
    ) % (10**8)

    random.seed(seed_value)

    results = []

    for drug in drugs:
        score = round(random.uniform(0.72, 0.99), 3)

        results.append({
            "drug": drug,
            "score": score
        })

    results.sort(
        key=lambda x: x["score"],
        reverse=True
    )

    return results
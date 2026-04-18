from __future__ import annotations

from pathlib import Path
import sys


ROOT_DIR = Path(__file__).resolve().parents[1]
if str(ROOT_DIR) not in sys.path:
	sys.path.insert(0, str(ROOT_DIR))

from ml_pipeline import train_affinity_model  # noqa: E402


def main() -> None:
	bundle = train_affinity_model()
	metrics = bundle["metrics"]

	print("\nLigBind training complete")
	print(f"Train R2: {metrics['train_r2']:.4f}")
	print(f"Validation R2: {metrics['val_r2']:.4f}")
	print(f"Test R2: {metrics['test_r2']:.4f}")
	print(f"Best iteration: {metrics['best_iteration']}")


if __name__ == "__main__":
	main()

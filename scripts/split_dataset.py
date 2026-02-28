"""Split training data into train/valid/test sets (80/10/10).

Reads data/training/all.jsonl and produces:
- data/training/train.jsonl
- data/training/valid.jsonl
- data/training/test.jsonl
"""

import json
import random
import sys
from pathlib import Path


TRAINING_DIR = Path("data/training")
INPUT_PATH = TRAINING_DIR / "all.jsonl"
SEED = 42


def main():
    if not INPUT_PATH.exists():
        print(f"{INPUT_PATH} not found. Run build_training_data.py first.")
        sys.exit(1)

    # Load all examples
    examples = []
    with open(INPUT_PATH, "r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if line:
                examples.append(json.loads(line))

    print(f"Loaded {len(examples)} examples from {INPUT_PATH}")

    if len(examples) < 10:
        print("Warning: Very few examples. Consider adding more training data.")

    # Shuffle deterministically
    random.seed(SEED)
    random.shuffle(examples)

    # Split 80/10/10
    n = len(examples)
    train_end = int(n * 0.8)
    valid_end = int(n * 0.9)

    splits = {
        "train": examples[:train_end],
        "valid": examples[train_end:valid_end],
        "test": examples[valid_end:],
    }

    for name, data in splits.items():
        output_path = TRAINING_DIR / f"{name}.jsonl"
        with open(output_path, "w", encoding="utf-8") as f:
            for example in data:
                f.write(json.dumps(example, ensure_ascii=False) + "\n")
        print(f"  {name}: {len(data)} examples → {output_path}")

    print(f"\nDone. Training data is ready for MLX fine-tuning.")
    print(f"Next step: python -m mlx_lm.lora --config configs/lora_config.yaml")


if __name__ == "__main__":
    main()

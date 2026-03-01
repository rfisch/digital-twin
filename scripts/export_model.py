#!/usr/bin/env python3
"""
Export pipeline: LoRA adapter → fused model → GGUF → Ollama

Takes the trained LoRA adapter and the base model, then:
1. Fuses adapter into base model (with dequantize to fp16)
2. Converts fp16 safetensors to GGUF via llama.cpp
3. Quantizes GGUF to Q4_K_M for efficient serving
4. Imports into Ollama

Usage:
    python scripts/export_model.py
    python scripts/export_model.py --adapter-path adapters/jacq-v2 --name jacq-v2
    python scripts/export_model.py --quantization Q5_K_M
    python scripts/export_model.py --skip-ollama  # just produce the GGUF
"""

import argparse
import os
import shutil
import subprocess
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent
MODELS_DIR = PROJECT_ROOT / "models" / "fused"
LLAMA_CPP_CONVERTER = Path("/tmp/llama.cpp/convert_hf_to_gguf.py")
LLAMA_CPP_QUANTIZE = Path("/tmp/llama.cpp/build/bin/llama-quantize")
MODELFILE_PATH = PROJECT_ROOT / "Modelfile"

DEFAULT_BASE_MODEL = "mlx-community/Meta-Llama-3.1-8B-Instruct-4bit"
DEFAULT_ADAPTER_PATH = PROJECT_ROOT / "adapters" / "jacq-v1"
DEFAULT_QUANTIZATION = "Q4_K_M"


def run(cmd: list[str], desc: str) -> subprocess.CompletedProcess:
    """Run a command with clear status output."""
    print(f"\n{'='*60}")
    print(f"  {desc}")
    print(f"{'='*60}")
    print(f"  $ {' '.join(str(c) for c in cmd)}\n")
    result = subprocess.run(cmd, capture_output=False, text=True)
    if result.returncode != 0:
        print(f"\nERROR: {desc} failed (exit code {result.returncode})")
        sys.exit(1)
    return result


def check_dependencies():
    """Verify required tools are available."""
    missing = []
    if not LLAMA_CPP_CONVERTER.exists():
        missing.append(f"llama.cpp converter not found at {LLAMA_CPP_CONVERTER}")
    if not LLAMA_CPP_QUANTIZE.exists():
        missing.append(f"llama.cpp quantize not found at {LLAMA_CPP_QUANTIZE}")
    try:
        subprocess.run([sys.executable, "-m", "mlx_lm", "fuse", "--help"],
                       capture_output=True, timeout=10)
    except (FileNotFoundError, subprocess.TimeoutExpired):
        missing.append("mlx_lm not available (pip install mlx-lm)")

    if missing:
        print("Missing dependencies:")
        for m in missing:
            print(f"  - {m}")
        print("\nTo build llama.cpp:")
        print("  cd /tmp && git clone https://github.com/ggml-org/llama.cpp")
        print("  cd llama.cpp && pip install -r requirements.txt")
        print("  mkdir build && cd build && cmake .. -DGGML_METAL=ON")
        print("  cmake --build . --target llama-quantize -j$(sysctl -n hw.ncpu)")
        sys.exit(1)


def step1_fuse_and_dequantize(base_model: str, adapter_path: Path,
                               fp16_dir: Path):
    """Fuse LoRA adapter into base model, dequantizing to fp16."""
    if fp16_dir.exists():
        print(f"Removing existing fp16 directory: {fp16_dir}")
        shutil.rmtree(fp16_dir)

    run([
        sys.executable, "-m", "mlx_lm", "fuse",
        "--model", base_model,
        "--adapter-path", str(adapter_path),
        "--save-path", str(fp16_dir),
        "--dequantize",
    ], "Step 1: Fuse adapter + dequantize to fp16")


def step2_convert_to_gguf(fp16_dir: Path, f16_gguf: Path):
    """Convert fp16 safetensors to GGUF format."""
    if f16_gguf.exists():
        print(f"Removing existing f16 GGUF: {f16_gguf}")
        f16_gguf.unlink()

    run([
        sys.executable, str(LLAMA_CPP_CONVERTER),
        str(fp16_dir),
        "--outfile", str(f16_gguf),
    ], "Step 2: Convert fp16 safetensors → GGUF")


def step3_quantize(f16_gguf: Path, quantized_gguf: Path,
                    quantization: str):
    """Quantize fp16 GGUF to target quantization level."""
    if quantized_gguf.exists():
        print(f"Removing existing quantized GGUF: {quantized_gguf}")
        quantized_gguf.unlink()

    run([
        str(LLAMA_CPP_QUANTIZE),
        str(f16_gguf),
        str(quantized_gguf),
        quantization,
    ], f"Step 3: Quantize GGUF ({quantization})")


def step4_import_ollama(quantized_gguf: Path, model_name: str):
    """Update Modelfile and import into Ollama."""
    # Update Modelfile to point to the quantized GGUF
    gguf_relative = os.path.relpath(quantized_gguf, PROJECT_ROOT)
    modelfile_content = MODELFILE_PATH.read_text()

    # Replace the FROM line
    lines = modelfile_content.splitlines()
    new_lines = []
    for line in lines:
        if line.startswith("FROM "):
            new_lines.append(f"FROM ./{gguf_relative}")
        else:
            new_lines.append(line)
    MODELFILE_PATH.write_text("\n".join(new_lines) + "\n")

    # Start Ollama if needed
    result = subprocess.run(["pgrep", "-x", "ollama"], capture_output=True)
    started_ollama = False
    if result.returncode != 0:
        print("Starting Ollama...")
        subprocess.Popen(["ollama", "serve"],
                         stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        import time
        time.sleep(3)
        started_ollama = True

    run([
        "ollama", "create", f"{model_name}", "-f", str(MODELFILE_PATH),
    ], f"Step 4: Import into Ollama as '{model_name}'")

    # Verify
    subprocess.run(["ollama", "list"], capture_output=False)

    if started_ollama:
        print("\nNote: Ollama was started for import. Stop it with: pkill ollama")


def main():
    parser = argparse.ArgumentParser(
        description="Export fine-tuned model: adapter → GGUF → Ollama")
    parser.add_argument("--base-model", default=DEFAULT_BASE_MODEL,
                        help=f"Base model path or HF repo (default: {DEFAULT_BASE_MODEL})")
    parser.add_argument("--adapter-path", type=Path, default=DEFAULT_ADAPTER_PATH,
                        help=f"Path to adapter weights (default: {DEFAULT_ADAPTER_PATH})")
    parser.add_argument("--name", default="jacq:8b",
                        help="Ollama model name (default: jacq:8b)")
    parser.add_argument("--quantization", default=DEFAULT_QUANTIZATION,
                        help=f"GGUF quantization type (default: {DEFAULT_QUANTIZATION})")
    parser.add_argument("--skip-ollama", action="store_true",
                        help="Skip Ollama import step")
    parser.add_argument("--keep-intermediates", action="store_true",
                        help="Keep fp16 intermediate files")
    args = parser.parse_args()

    # Derived paths
    name_slug = args.name.replace(":", "-").replace("/", "-")
    fp16_dir = MODELS_DIR / f"{name_slug}-fp16"
    f16_gguf = MODELS_DIR / f"{name_slug}-f16.gguf"
    quant_suffix = args.quantization.lower().replace("_", "")
    quantized_gguf = MODELS_DIR / f"{name_slug}-{quant_suffix}.gguf"

    print(f"Export pipeline for: {args.name}")
    print(f"  Base model:    {args.base_model}")
    print(f"  Adapter:       {args.adapter_path}")
    print(f"  Quantization:  {args.quantization}")
    print(f"  Output GGUF:   {quantized_gguf}")

    check_dependencies()

    MODELS_DIR.mkdir(parents=True, exist_ok=True)

    step1_fuse_and_dequantize(args.base_model, args.adapter_path, fp16_dir)
    step2_convert_to_gguf(fp16_dir, f16_gguf)
    step3_quantize(f16_gguf, quantized_gguf, args.quantization)

    if not args.skip_ollama:
        step4_import_ollama(quantized_gguf, args.name)

    # Cleanup intermediates
    if not args.keep_intermediates:
        print(f"\nCleaning up intermediates...")
        if fp16_dir.exists():
            shutil.rmtree(fp16_dir)
            print(f"  Removed {fp16_dir}")
        if f16_gguf.exists():
            f16_gguf.unlink()
            print(f"  Removed {f16_gguf}")

    size_gb = quantized_gguf.stat().st_size / (1024**3)
    print(f"\nDone! Final model: {quantized_gguf} ({size_gb:.1f} GB)")
    if not args.skip_ollama:
        print(f"Run with: ollama run {args.name}")


if __name__ == "__main__":
    main()

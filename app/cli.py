"""CLI interface for the writing assistant.

Usage:
    python app/cli.py blog "Write about morning routines"
    python app/cli.py email "Follow up with a client" --recipient "Sarah"
    python app/cli.py copywriting "Product launch announcement"
    python app/cli.py freeform "Write a reflection on creativity"

Options:
    --model         Model to use (default: jacq:8b)
    --temperature   Generation temperature (default: 0.7)
    --no-rag        Disable RAG context retrieval
    --max-tokens    Maximum response tokens (default: 2048)
"""

import argparse
import sys
from pathlib import Path

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from app.assistant import WritingAssistant


def main():
    parser = argparse.ArgumentParser(
        description="Jacq's Writing Assistant",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=__doc__,
    )
    parser.add_argument(
        "task_type",
        choices=WritingAssistant.TASK_TYPES,
        help="Type of writing to generate",
    )
    parser.add_argument("topic", help="The topic or writing request")
    parser.add_argument("--model", default="jacq:8b", help="Model to use")
    parser.add_argument("--temperature", type=float, default=0.7)
    parser.add_argument("--max-tokens", type=int, default=2048)
    parser.add_argument("--no-rag", action="store_true", help="Disable RAG context")

    # Email-specific options
    parser.add_argument("--recipient", default="")
    parser.add_argument("--purpose", default="")
    parser.add_argument("--email-type", default="professional")

    # Copywriting-specific options
    parser.add_argument("--medium", default="")
    parser.add_argument("--audience", default="")
    parser.add_argument("--message", default="")
    parser.add_argument("--tone", default="")

    args = parser.parse_args()

    assistant = WritingAssistant(model=args.model)

    try:
        print(f"\nGenerating {args.task_type} with model {args.model}...\n")
        print("-" * 60)

        result = assistant.generate(
            task_type=args.task_type,
            topic=args.topic,
            use_rag=not args.no_rag,
            temperature=args.temperature,
            max_tokens=args.max_tokens,
            recipient=args.recipient,
            purpose=args.purpose,
            email_type=args.email_type,
            medium=args.medium,
            audience=args.audience,
            message=args.message,
            tone=args.tone,
        )

        print(result)
        print("-" * 60)
    finally:
        assistant.shutdown()


if __name__ == "__main__":
    main()

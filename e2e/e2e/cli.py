"""
Command-line interface for E2E Topic Modeling.
"""

import argparse
import os
import sys

import pandas as pd


def main():
    parser = argparse.ArgumentParser(
        prog="e2e",
        description="E2E: Embedding-to-Explanation Topic Modeling Pipeline",
    )
    subparsers = parser.add_subparsers(dest="command", help="Available commands")

    # --- run command ---
    run_parser = subparsers.add_parser("run", help="Run the full pipeline on a corpus")
    run_parser.add_argument("input", help="Path to input CSV file")
    run_parser.add_argument("--text-column", default="text", help="Name of the text column (default: text)")
    run_parser.add_argument("--output-dir", default="e2e_output", help="Output directory")
    run_parser.add_argument("--domain-context", default="a text corpus", help="Domain context for LLM prompts")
    run_parser.add_argument("--n-iterations", type=int, default=50, help="Hyperparameter search iterations")
    run_parser.add_argument("--n-votes", type=int, default=100, help="LLM naming votes per topic")
    run_parser.add_argument("--topic-min", type=int, default=2, help="Minimum topics to evaluate")
    run_parser.add_argument("--topic-max", type=int, default=26, help="Maximum topics to evaluate")
    run_parser.add_argument("--embedding-model", default="all-MiniLM-L6-v2", help="SentenceTransformer model")
    run_parser.add_argument("--llm-model", default="gpt-4o", help="OpenAI model for naming/classification")
    run_parser.add_argument("--stopwords-file", help="Path to custom stopwords file (comma-separated)")
    run_parser.add_argument("--seed", type=int, help="Random seed")
    run_parser.add_argument("--no-preprocess", action="store_true", help="Skip preprocessing")

    # --- classify command ---
    classify_parser = subparsers.add_parser("classify", help="Classify a corpus using discovered themes")
    classify_parser.add_argument("input", help="Path to input CSV file")
    classify_parser.add_argument("--text-column", default="text", help="Name of the text column")
    classify_parser.add_argument("--themes", required=True, nargs="+", help="Theme names to classify into")
    classify_parser.add_argument("--output", default="classified_output.csv", help="Output CSV path")
    classify_parser.add_argument("--domain-context", default="a text corpus", help="Domain context for LLM")
    classify_parser.add_argument("--llm-model", default="gpt-4o", help="OpenAI model")

    args = parser.parse_args()

    if args.command is None:
        parser.print_help()
        sys.exit(1)

    if args.command == "run":
        _run(args)
    elif args.command == "classify":
        _classify(args)


def _run(args):
    from e2e.pipeline import E2EPipeline
    from e2e.preprocessing import load_custom_stopwords

    df = pd.read_csv(args.input)
    if args.text_column not in df.columns:
        print(f"Error: Column '{args.text_column}' not found in {args.input}")
        sys.exit(1)

    documents = df[args.text_column].dropna().tolist()
    print(f"Loaded {len(documents)} documents from {args.input}")

    custom_stopwords = None
    if args.stopwords_file:
        custom_stopwords = load_custom_stopwords(args.stopwords_file)
        print(f"Loaded {len(custom_stopwords)} custom stopwords")

    pipeline = E2EPipeline(
        domain_context=args.domain_context,
        llm_model=args.llm_model,
        embedding_model=args.embedding_model,
        n_votes=args.n_votes,
        topic_range=(args.topic_min, args.topic_max),
        n_iterations=args.n_iterations,
        custom_stopwords=custom_stopwords,
        random_seed=args.seed,
    )

    pipeline.run(documents, preprocess=not args.no_preprocess)
    pipeline.save(args.output_dir)

    # Also classify the input corpus
    print("\nClassifying input corpus...")
    df_classified = pipeline.classify_dataframe(df, args.text_column)
    df_classified.to_csv(os.path.join(args.output_dir, "classified_corpus.csv"), index=False)
    print(f"Classified corpus saved to {args.output_dir}/classified_corpus.csv")


def _classify(args):
    from e2e.classifier import TopicClassifier

    df = pd.read_csv(args.input)
    if args.text_column not in df.columns:
        print(f"Error: Column '{args.text_column}' not found in {args.input}")
        sys.exit(1)

    classifier = TopicClassifier(
        themes=args.themes,
        model=args.llm_model,
        domain_context=args.domain_context,
    )

    df = classifier.classify_dataframe(df, args.text_column)
    df.to_csv(args.output, index=False)
    print(f"Classification complete. Output saved to {args.output}")


if __name__ == "__main__":
    main()

"""
E2E end-to-end pipeline.

Orchestrates the three stages:
  1. BERTopic modeling with hyperparameter optimization
  2. LLM-based democratic topic naming
  3. LLM-based corpus classification
"""

import json
import os
from typing import Dict, List, Optional, Set, Tuple

import pandas as pd

from e2e.modeling import TopicModeler, OptimizationResult
from e2e.naming import TopicNamer
from e2e.classifier import TopicClassifier
from e2e.preprocessing import preprocess_corpus


class E2EPipeline:
    """
    End-to-end E2E pipeline.

    Usage:
        pipeline = E2EPipeline(
            domain_context="tweets about health policy",
            openai_api_key="sk-...",
        )
        results = pipeline.run(documents)
        results = pipeline.classify(all_documents)

    Args:
        domain_context: Description of the corpus domain for LLM prompts.
        openai_api_key: OpenAI API key. If None, reads from env.
        llm_model: OpenAI model for naming and classification. Default: "gpt-4o".
        embedding_model: SentenceTransformer model. Default: "all-MiniLM-L6-v2".
        n_votes: Number of LLM votes per topic for naming. Default: 100.
        topic_range: (min, max) topic count range. Default: (2, 26).
        n_iterations: Number of hyperparameter search iterations. Default: 50.
        custom_stopwords: Optional set of domain-specific stopwords.
        random_seed: Seed for reproducibility. Default: None.
    """

    def __init__(
        self,
        domain_context: str = "a text corpus",
        openai_api_key: Optional[str] = None,
        llm_model: str = "gpt-4o",
        embedding_model: str = "all-MiniLM-L6-v2",
        n_votes: int = 100,
        topic_range: Tuple[int, int] = (2, 26),
        n_iterations: int = 50,
        custom_stopwords: Optional[Set[str]] = None,
        random_seed: Optional[int] = None,
    ):
        self.domain_context = domain_context
        self.openai_api_key = openai_api_key
        self.llm_model = llm_model
        self.custom_stopwords = custom_stopwords

        self.modeler = TopicModeler(
            embedding_model=embedding_model,
            stopwords=list(custom_stopwords) if custom_stopwords else None,
            topic_range=topic_range,
            n_iterations=n_iterations,
            random_seed=random_seed,
        )

        self.namer = TopicNamer(
            model=llm_model,
            n_votes=n_votes,
            api_key=openai_api_key,
            domain_context=domain_context,
        )

        # Populated after run()
        self.optimization_result: Optional[OptimizationResult] = None
        self.topic_names: Optional[Dict[int, Dict]] = None
        self.theme_names: Optional[List[str]] = None
        self._classifier: Optional[TopicClassifier] = None

    def run(
        self,
        documents: List[str],
        preprocess: bool = True,
        verbose: bool = True,
    ) -> Dict:
        """
        Execute the full pipeline: model -> name -> prepare classifier.

        Args:
            documents: List of raw or preprocessed text documents.
            preprocess: Whether to preprocess documents first.
            verbose: Print progress.

        Returns:
            Dict with keys:
                'optimization': OptimizationResult
                'topic_names': Dict[topic_id, naming_result]
                'theme_list': List of theme name strings
                'topic_info': DataFrame of topic info
        """
        # Stage 1: Preprocess
        if preprocess:
            if verbose:
                print("=" * 60)
                print("STAGE 0: Preprocessing")
                print("=" * 60)
            docs = preprocess_corpus(documents, self.custom_stopwords, show_progress=verbose)
        else:
            docs = documents

        # Stage 2: Topic Modeling
        if verbose:
            print("\n" + "=" * 60)
            print("STAGE 1: BERTopic Modeling with Hyperparameter Optimization")
            print("=" * 60)
        self.optimization_result = self.modeler.optimize(docs, verbose=verbose)

        # Extract topic words
        model = self.optimization_result.best_model
        topic_words = {}
        for tid in model.get_topics():
            if tid != -1:
                words = model.get_topic(tid)
                if words:
                    topic_words[tid] = [w for w, _ in words]

        # Stage 3: LLM Topic Naming
        if verbose:
            print("\n" + "=" * 60)
            print("STAGE 2: LLM Democratic Topic Naming")
            print("=" * 60)
        self.topic_names = self.namer.name_all_topics(topic_words, show_progress=verbose)

        # Prepare theme list
        self.theme_names = [self.topic_names[tid]["name"] for tid in sorted(self.topic_names.keys())]

        # Initialize classifier
        self._classifier = TopicClassifier(
            themes=self.theme_names,
            model=self.llm_model,
            api_key=self.openai_api_key,
            domain_context=self.domain_context,
        )

        if verbose:
            print("\n" + "=" * 60)
            print("PIPELINE COMPLETE")
            print("=" * 60)
            print(f"Topics found: {len(self.theme_names)}")
            for tid, name_result in self.topic_names.items():
                print(f"  Topic {tid}: {name_result['name']} "
                      f"({name_result['votes']}/{name_result['total_votes']} votes)")
            print(f"\nClassifier ready. Call pipeline.classify(documents) to classify a corpus.")

        return {
            "optimization": self.optimization_result,
            "topic_names": self.topic_names,
            "theme_list": self.theme_names,
            "topic_info": self.optimization_result.topic_info,
        }

    def classify(
        self,
        documents: List[str],
        show_progress: bool = True,
    ) -> List[str]:
        """
        Classify documents into the discovered themes.

        Must call run() first to discover themes.

        Args:
            documents: List of text documents to classify.
            show_progress: Show progress bar.

        Returns:
            List of theme labels.
        """
        if self._classifier is None:
            raise RuntimeError("Must call run() before classify(). No themes have been discovered yet.")
        return self._classifier.classify_corpus(documents, show_progress=show_progress)

    def classify_dataframe(
        self,
        df: pd.DataFrame,
        text_column: str,
        output_column: str = "theme",
        show_progress: bool = True,
    ) -> pd.DataFrame:
        """Classify a DataFrame column. Must call run() first."""
        if self._classifier is None:
            raise RuntimeError("Must call run() before classify_dataframe().")
        return self._classifier.classify_dataframe(df, text_column, output_column, show_progress)

    def validate_classifier(
        self,
        documents: List[str],
        human_labels: List[str],
        threshold: float = 0.85,
        show_progress: bool = True,
    ) -> Dict:
        """
        Validate classifier against human-labeled samples.

        Args:
            documents: Sample texts.
            human_labels: Human-assigned labels.
            threshold: Minimum agreement rate to pass. Default: 0.85.
            show_progress: Show progress bar.

        Returns:
            Validation result dict with 'passed' key.
        """
        if self._classifier is None:
            raise RuntimeError("Must call run() before validate_classifier().")
        result = self._classifier.validate(documents, human_labels, show_progress)
        result["threshold"] = threshold
        result["passed"] = result["agreement_rate"] >= threshold
        return result

    def save(self, output_dir: str):
        """Save all pipeline results to a directory."""
        os.makedirs(output_dir, exist_ok=True)

        if self.optimization_result:
            self.modeler.save_results(self.optimization_result, output_dir)

        if self.topic_names:
            names_data = {
                str(tid): {
                    "name": r["name"],
                    "votes": r["votes"],
                    "total_votes": r["total_votes"],
                    "top_candidates": dict(r["all_candidates"].most_common(10)),
                }
                for tid, r in self.topic_names.items()
            }
            with open(os.path.join(output_dir, "topic_names.json"), "w") as f:
                json.dump(names_data, f, indent=2)

        if self.theme_names:
            with open(os.path.join(output_dir, "themes.json"), "w") as f:
                json.dump(self.theme_names, f, indent=2)

        print(f"Pipeline results saved to {output_dir}/")

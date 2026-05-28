"""
BERTopic modeling module with hyperparameter optimization.

Implements the core topic modeling pipeline:
  - SentenceTransformer embeddings
  - UMAP dimensionality reduction
  - HDBSCAN clustering
  - Class-based TF-IDF topic extraction
  - Random search hyperparameter optimization scored by c_v coherence
"""

import json
import os
from dataclasses import dataclass, field
from typing import Dict, List, Optional, Tuple

import numpy as np
import pandas as pd
from bertopic import BERTopic
from gensim.corpora import Dictionary
from gensim.models.coherencemodel import CoherenceModel
from hdbscan import HDBSCAN
from sentence_transformers import SentenceTransformer
from sklearn.feature_extraction.text import CountVectorizer
from umap import UMAP


@dataclass
class TopicModelResult:
    """Container for a single model evaluation result."""
    n_topics: int
    coherence: float
    umap_params: Dict
    hdbscan_params: Dict
    iteration: int
    topic_words: Optional[List[List[str]]] = None
    model: Optional[BERTopic] = None


@dataclass
class OptimizationResult:
    """Container for the full optimization output."""
    best_result: TopicModelResult
    all_results: List[TopicModelResult]
    best_model: Optional[BERTopic] = None
    topics: Optional[List[int]] = None
    topic_info: Optional[pd.DataFrame] = None


class TopicModeler:
    """
    BERTopic modeler with hyperparameter optimization.

    Searches over UMAP and HDBSCAN parameter spaces using random search,
    evaluating each configuration across a range of topic counts.
    The best model is selected by c_v coherence score.

    Args:
        embedding_model: SentenceTransformer model name. Default: "all-MiniLM-L6-v2".
        stopwords: List of stopwords for the CountVectorizer.
        umap_params: Dict of parameter name -> list of values to search.
        hdbscan_params: Dict of parameter name -> list of values to search.
        topic_range: Tuple of (min_topics, max_topics). Default: (2, 26).
        n_iterations: Number of random search iterations. Default: 50.
        random_seed: Random seed for reproducibility. Default: None.
    """

    DEFAULT_UMAP_PARAMS = {
        "n_neighbors": [5, 10, 15, 20, 25, 30, 35],
        "n_components": [3, 4, 5, 6, 7, 8, 9, 10],
        "min_dist": [0.01, 0.05, 0.1, 0.5],
        "metric": ["cosine"],
    }

    DEFAULT_HDBSCAN_PARAMS = {
        "min_cluster_size": [5, 10, 15, 20, 25, 30, 35],
        "metric": ["euclidean"],
        "cluster_selection_method": ["eom"],
    }

    def __init__(
        self,
        embedding_model: str = "all-MiniLM-L6-v2",
        stopwords: Optional[List[str]] = None,
        umap_params: Optional[Dict] = None,
        hdbscan_params: Optional[Dict] = None,
        topic_range: Tuple[int, int] = (2, 26),
        n_iterations: int = 50,
        random_seed: Optional[int] = None,
    ):
        self.embedding_model_name = embedding_model
        self.stopwords = stopwords or []
        self.umap_search_space = umap_params or self.DEFAULT_UMAP_PARAMS
        self.hdbscan_search_space = hdbscan_params or self.DEFAULT_HDBSCAN_PARAMS
        self.topic_range = range(topic_range[0], topic_range[1])
        self.n_iterations = n_iterations
        self.random_seed = random_seed
        if random_seed is not None:
            np.random.seed(random_seed)

    def _compute_coherence(self, topic_words: List[List[str]], texts: List[str]) -> float:
        """Compute c_v coherence score for a set of topic word lists."""
        tokenized = [text.split() for text in texts]
        dictionary = Dictionary(tokenized)
        cm = CoherenceModel(
            topics=topic_words,
            texts=tokenized,
            dictionary=dictionary,
            coherence="c_v",
        )
        return cm.get_coherence()

    def _create_model(self, umap_config: Dict, hdbscan_config: Dict, nr_topics: Optional[int] = None) -> BERTopic:
        """Create a BERTopic model with given parameters."""
        sentence_model = SentenceTransformer(self.embedding_model_name)
        umap_model = UMAP(**umap_config)
        hdbscan_model = HDBSCAN(**hdbscan_config)
        vectorizer = CountVectorizer(stop_words=self.stopwords if self.stopwords else None)

        return BERTopic(
            nr_topics=nr_topics,
            embedding_model=sentence_model,
            umap_model=umap_model,
            hdbscan_model=hdbscan_model,
            vectorizer_model=vectorizer,
            verbose=False,
        )

    def _evaluate_single(
        self,
        documents: List[str],
        umap_config: Dict,
        hdbscan_config: Dict,
        n_topics: int,
        iteration: int,
    ) -> Optional[TopicModelResult]:
        """Evaluate a single model configuration."""
        try:
            model = self._create_model(umap_config, hdbscan_config, nr_topics=n_topics)
            topics, _ = model.fit_transform(documents)

            unique_topics = set(topics) - {-1}
            if len(unique_topics) < 2:
                return None

            topic_words = []
            for topic_id in range(n_topics):
                tw = model.get_topic(topic_id)
                if tw:
                    topic_words.append([word for word, _ in tw])

            if len(topic_words) < 2:
                return None

            coherence = self._compute_coherence(topic_words, documents)
            return TopicModelResult(
                n_topics=n_topics,
                coherence=coherence,
                umap_params={k: v.item() if hasattr(v, "item") else v for k, v in umap_config.items()},
                hdbscan_params={k: v.item() if hasattr(v, "item") else v for k, v in hdbscan_config.items()},
                iteration=iteration,
                topic_words=topic_words,
                model=model,
            )
        except Exception as e:
            print(f"  Error evaluating {n_topics} topics: {e}")
            return None

    def optimize(self, documents: List[str], verbose: bool = True) -> OptimizationResult:
        """
        Run hyperparameter optimization over the search space.

        For each iteration, randomly samples UMAP and HDBSCAN parameters,
        then evaluates models across the full topic range. The model with the
        highest c_v coherence score is selected.

        Args:
            documents: List of preprocessed text documents.
            verbose: Print progress information.

        Returns:
            OptimizationResult with best model and all evaluation results.
        """
        all_results = []
        best_result = None

        for i in range(self.n_iterations):
            umap_config = {k: np.random.choice(v) for k, v in self.umap_search_space.items()}
            hdbscan_config = {k: np.random.choice(v) for k, v in self.hdbscan_search_space.items()}

            if verbose:
                print(f"Iteration {i + 1}/{self.n_iterations} | UMAP: {umap_config} | HDBSCAN: {hdbscan_config}")

            for n_topics in self.topic_range:
                result = self._evaluate_single(documents, umap_config, hdbscan_config, n_topics, i + 1)
                if result is not None:
                    all_results.append(result)
                    if best_result is None or result.coherence > best_result.coherence:
                        best_result = result
                        if verbose:
                            print(f"  New best: {n_topics} topics, coherence={result.coherence:.4f}")

        if best_result is None:
            raise RuntimeError("No valid models found. Check your data and parameter ranges.")

        # Refit best model to get final assignments
        if verbose:
            print(f"\nBest model: iteration={best_result.iteration}, "
                  f"topics={best_result.n_topics}, coherence={best_result.coherence:.4f}")
            print("Refitting best model...")

        final_model = self._create_model(best_result.umap_params, best_result.hdbscan_params)
        final_topics, _ = final_model.fit_transform(documents)

        return OptimizationResult(
            best_result=best_result,
            all_results=all_results,
            best_model=final_model,
            topics=final_topics,
            topic_info=final_model.get_topic_info(),
        )

    def save_results(self, opt_result: OptimizationResult, output_dir: str):
        """Save optimization results to disk."""
        os.makedirs(output_dir, exist_ok=True)

        # Save all results as JSON
        results_data = [
            {
                "iteration": r.iteration,
                "n_topics": r.n_topics,
                "coherence": r.coherence,
                "umap_params": r.umap_params,
                "hdbscan_params": r.hdbscan_params,
            }
            for r in opt_result.all_results
        ]
        with open(os.path.join(output_dir, "all_results.json"), "w") as f:
            json.dump(results_data, f, indent=2)

        # Save topic info
        if opt_result.topic_info is not None:
            opt_result.topic_info.to_csv(os.path.join(output_dir, "topic_info.csv"), index=False)

        # Save best parameters
        best = opt_result.best_result
        with open(os.path.join(output_dir, "best_params.json"), "w") as f:
            json.dump({
                "iteration": best.iteration,
                "n_topics": best.n_topics,
                "coherence": best.coherence,
                "umap_params": best.umap_params,
                "hdbscan_params": best.hdbscan_params,
            }, f, indent=2)

        print(f"Results saved to {output_dir}/")

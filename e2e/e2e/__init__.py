"""
E2E: Embedding-to-Explanation Topic Modeling Pipeline

A three-stage methodology for automated topic discovery in text corpora:
  1. BERTopic modeling with hyperparameter optimization
  2. LLM-based democratic topic naming
  3. LLM-based corpus classification

Reference:
  Thomas, J.E. (2025). Embedding-to-Explanation Topic Modeling: A Hybrid
  Approach for Interpretive Text Analysis. The University of Texas at Austin.
"""

__version__ = "2.0.0"
__author__ = "Jacob Edward Thomas"

from e2e.pipeline import E2EPipeline
from e2e.modeling import TopicModeler
from e2e.naming import TopicNamer
from e2e.classifier import TopicClassifier

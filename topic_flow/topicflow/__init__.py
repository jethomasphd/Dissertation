"""
TopicFlow: BERTopic + LLM Topic Modeling Pipeline

A three-stage methodology for automated topic discovery in text corpora:
  1. BERTopic modeling with hyperparameter optimization
  2. LLM-based democratic topic naming
  3. LLM-based corpus classification

Reference:
  Thomas, J.E. (2025). TopicFlow: A BERTopic and Large Language Model Pipeline
  for Topic Discovery and Classification. Preprint.
"""

__version__ = "1.0.0"
__author__ = "Jacob Edward Thomas"

from topicflow.pipeline import TopicFlowPipeline
from topicflow.modeling import TopicModeler
from topicflow.naming import TopicNamer
from topicflow.classifier import TopicClassifier

"""
Text preprocessing module for E2E Topic Modeling.

Provides cleaning, tokenization, stopword removal, and lemmatization
for preparing text corpora for topic modeling.
"""

import re
import nltk
from nltk.corpus import stopwords, wordnet
from nltk.tokenize import word_tokenize
from nltk.stem import WordNetLemmatizer
from typing import List, Optional, Set


def _ensure_nltk_data():
    """Download required NLTK data if not present."""
    for resource in ["punkt", "punkt_tab", "stopwords", "averaged_perceptron_tagger",
                     "averaged_perceptron_tagger_eng", "wordnet"]:
        try:
            nltk.data.find(f"tokenizers/{resource}" if "punkt" in resource else f"corpora/{resource}" if resource in ("stopwords", "wordnet") else f"taggers/{resource}")
        except LookupError:
            nltk.download(resource, quiet=True)


_ensure_nltk_data()
_lemmatizer = WordNetLemmatizer()


def _get_wordnet_pos(word: str):
    """Map POS tag to WordNet POS for lemmatization."""
    tag = nltk.pos_tag([word])[0][1][0].upper()
    tag_dict = {"J": wordnet.ADJ, "N": wordnet.NOUN, "V": wordnet.VERB, "R": wordnet.ADV}
    return tag_dict.get(tag, wordnet.NOUN)


def clean_text(text: str) -> str:
    """Remove non-alphabetic characters, collapse whitespace, lowercase."""
    text = re.sub(r"[^a-zA-Z]", " ", text)
    text = re.sub(r"\s+", " ", text).strip()
    return text.lower()


def preprocess_document(
    text: str,
    custom_stopwords: Optional[Set[str]] = None,
) -> str:
    """
    Full preprocessing pipeline for a single document.

    Steps:
      1. Clean text (remove non-alpha, lowercase)
      2. Tokenize
      3. Remove stopwords (NLTK English + any custom)
      4. Lemmatize with POS tagging

    Args:
        text: Raw text string.
        custom_stopwords: Optional set of additional stopwords.

    Returns:
        Preprocessed text as a single string of lemmatized tokens.
    """
    stop_words = set(stopwords.words("english"))
    if custom_stopwords:
        stop_words = stop_words.union(custom_stopwords)

    cleaned = clean_text(text)
    tokens = word_tokenize(cleaned)
    lemmatized = [
        _lemmatizer.lemmatize(token, _get_wordnet_pos(token))
        for token in tokens
        if token not in stop_words and len(token) > 1
    ]
    return " ".join(lemmatized)


def preprocess_corpus(
    documents: List[str],
    custom_stopwords: Optional[Set[str]] = None,
    show_progress: bool = True,
) -> List[str]:
    """
    Preprocess a list of documents.

    Args:
        documents: List of raw text strings.
        custom_stopwords: Optional set of additional stopwords.
        show_progress: Whether to display a progress bar.

    Returns:
        List of preprocessed text strings.
    """
    if show_progress:
        from tqdm import tqdm
        return [preprocess_document(doc, custom_stopwords) for doc in tqdm(documents, desc="Preprocessing")]
    return [preprocess_document(doc, custom_stopwords) for doc in documents]


def load_custom_stopwords(filepath: str) -> Set[str]:
    """Load custom stopwords from a comma-separated text file."""
    with open(filepath, "r") as f:
        return set(word.strip().lower() for word in f.read().split(",") if word.strip())

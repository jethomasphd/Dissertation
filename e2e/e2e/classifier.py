"""
LLM-based text classification module.

Classifies documents into identified themes using an LLM,
with validation against human-labeled samples.
"""

import time
from typing import Dict, List, Optional

import pandas as pd
from openai import OpenAI
from tqdm import tqdm


class TopicClassifier:
    """
    Classifies text documents into predefined themes using an LLM.

    Args:
        themes: List of theme names to classify into. An additional
            "Does not fit any theme" option is always included.
        model: OpenAI model name. Default: "gpt-4o".
        temperature: Sampling temperature. Default: 0.5.
        max_retries: Max retries per API call. Default: 5.
        api_key: OpenAI API key. If None, reads from OPENAI_API_KEY env var.
        domain_context: Context string describing the corpus.
    """

    def __init__(
        self,
        themes: List[str],
        model: str = "gpt-4o",
        temperature: float = 0.5,
        max_retries: int = 5,
        api_key: Optional[str] = None,
        domain_context: str = "a text corpus",
    ):
        self.client = OpenAI(api_key=api_key) if api_key else OpenAI()
        self.model = model
        self.themes = themes
        self.temperature = temperature
        self.max_retries = max_retries
        self.domain_context = domain_context
        self._options = self._build_options()

    def _build_options(self) -> str:
        """Build the numbered options string for the classification prompt."""
        options = [f"{i + 1}. {theme}" for i, theme in enumerate(self.themes)]
        options.append(f"{len(self.themes) + 1}. The text does not fit into any of these themes.")
        return "\n".join(options)

    def classify_one(self, text: str) -> str:
        """
        Classify a single document.

        Returns the theme name or "Does not fit any theme".
        """
        prompt = (
            f"Classify the following text into one of the following themes:\n"
            f"{self._options}\n\n"
            f"Text: {text}\n\n"
            f"Respond with ONLY the verbatim theme name from the list above."
        )

        retries = 0
        while retries < self.max_retries:
            try:
                response = self.client.chat.completions.create(
                    model=self.model,
                    messages=[
                        {"role": "system", "content": "You are an expert at classifying text into themes. Respond with only the theme name."},
                        {"role": "user", "content": prompt},
                    ],
                    max_tokens=50,
                    temperature=self.temperature,
                )
                result = response.choices[0].message.content.strip()
                # Normalize: strip leading numbers/dots
                for theme in self.themes:
                    if theme.lower() in result.lower():
                        return theme
                if "does not fit" in result.lower() or "not fit" in result.lower():
                    return "Does not fit any theme"
                return result
            except Exception as e:
                retries += 1
                if retries < self.max_retries:
                    time.sleep(2 ** retries)
                else:
                    print(f"Classification failed after {self.max_retries} retries: {e}")
                    return "Error"

    def classify_corpus(
        self,
        documents: List[str],
        show_progress: bool = True,
    ) -> List[str]:
        """
        Classify a list of documents.

        Args:
            documents: List of text strings to classify.
            show_progress: Show progress bar.

        Returns:
            List of theme labels, one per document.
        """
        results = []
        iterator = tqdm(documents, desc="Classifying") if show_progress else documents
        for doc in iterator:
            results.append(self.classify_one(doc))
        return results

    def classify_dataframe(
        self,
        df: pd.DataFrame,
        text_column: str,
        output_column: str = "theme",
        show_progress: bool = True,
    ) -> pd.DataFrame:
        """
        Classify a DataFrame column and add results as a new column.

        Args:
            df: Input DataFrame.
            text_column: Name of column containing text to classify.
            output_column: Name of new column for classifications.
            show_progress: Show progress bar.

        Returns:
            DataFrame with the new classification column.
        """
        df = df.copy()
        df[output_column] = self.classify_corpus(
            df[text_column].tolist(),
            show_progress=show_progress,
        )
        return df

    def validate(
        self,
        documents: List[str],
        human_labels: List[str],
        show_progress: bool = True,
    ) -> Dict:
        """
        Validate classifier against human-labeled samples.

        Args:
            documents: List of text strings.
            human_labels: Corresponding human-assigned labels.
            show_progress: Show progress bar.

        Returns:
            Dict with 'agreement_rate', 'n_total', 'n_agree', 'n_disagree',
            and 'disagreements' (list of mismatched cases).
        """
        predicted = self.classify_corpus(documents, show_progress=show_progress)
        n_agree = sum(1 for p, h in zip(predicted, human_labels) if p.lower().strip() == h.lower().strip())
        disagreements = [
            {"index": i, "text": documents[i][:100], "predicted": predicted[i], "human": human_labels[i]}
            for i, (p, h) in enumerate(zip(predicted, human_labels))
            if p.lower().strip() != h.lower().strip()
        ]

        return {
            "agreement_rate": n_agree / len(documents) if documents else 0,
            "n_total": len(documents),
            "n_agree": n_agree,
            "n_disagree": len(documents) - n_agree,
            "disagreements": disagreements,
        }

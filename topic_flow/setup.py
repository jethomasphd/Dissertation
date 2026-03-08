from setuptools import setup, find_packages

setup(
    name="topicflow",
    version="1.0.0",
    description="BERTopic + LLM Topic Modeling Pipeline: Automated topic discovery, LLM-based naming, and corpus classification.",
    long_description=open("README.md").read(),
    long_description_content_type="text/markdown",
    author="Jacob Edward Thomas",
    author_email="jacob.thomas@utexas.edu",
    url="https://github.com/jethomasphd/topicflow",
    packages=find_packages(),
    python_requires=">=3.9",
    install_requires=[
        "bertopic>=0.15.0",
        "sentence-transformers>=2.2.0",
        "umap-learn>=0.5.0",
        "hdbscan>=0.8.0",
        "gensim>=4.0.0",
        "nltk>=3.8.0",
        "scikit-learn>=1.0.0",
        "openai>=1.0.0",
        "pandas>=1.5.0",
        "numpy>=1.21.0",
        "matplotlib>=3.5.0",
        "tqdm>=4.60.0",
    ],
    entry_points={
        "console_scripts": [
            "topicflow=topicflow.cli:main",
        ],
    },
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Science/Research",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Topic :: Scientific/Engineering :: Artificial Intelligence",
        "Topic :: Text Processing :: Linguistic",
    ],
    license="MIT",
)

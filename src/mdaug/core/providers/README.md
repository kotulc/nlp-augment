# Core Service Modules
The core natural language service components include text sentiment and related *metrics*, Content *summarization* and heading generation, and *tagging* and keyword extraction utilities. Each package in this directory contains a module with the name of the package (e.g. `appp.core.summary.summary.py`) that contains the primary get_* functions for that subpackage. These primary functions are leveraged by the related API endpoints found in `


## Structure
The following components make up the core language modeling (AI) functionality of the service.  
- models: language models and utilities
- metrics: text style and scoring functions
- summary: content summarization
- tags: content keyword extraction


### models
Low-level language helpers and model utilities: embedding and keyword models, semantic-similarity/MMR routines, and small sample helpers. Provides the algorithms and model calls that power tagging and summarization.

This package includes shared utilities and model loader wrappers: centralized model initialization, caching, debug/remote routing, and lightweight fallbacks for heavy dependencies. Keeps resource management and common helpers consistent across subpackages.

### metrics
Computes text quality and content metrics: diction/genre/mode/tone, sentiment and polarity scores, spam/toxicity detection. Returns numeric or categorical assessments used by the /metrics endpoint.

### summary
Generates concise content summaries and headings: titles, subtitles, descriptions, and outlines. Used to produce human-readable summaries and structured outlines from input text.

### tags
Extracts topic tags from text: named entities, keywords, and model-generated related concepts. Used by the `/tags` endpoint to return tag lists and relevance scores.

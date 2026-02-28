# nlp-mdaug
A CLI-first NLP augmentation toolkit for structured text content.

`nlp-mdaug` analyzes text, generates summaries/headings, extracts tags, and returns JSON.


## Purpose
This application is intended to augment collections of text content with AI and NLP-derived relational and semantic information with a simple and direct JSON input and output format.

## Refactor Status
The project is in active refactor to align implementation with `SPEC.md` and this README.
During early phases, CLI command stubs and smoke tests are the primary stability targets.

General Workflow:
```text
JSON content -> compute metrics, summarize, extract tags -> JSON results
```


## Features
- **AI summarization** - Generate content summaries, titles, and headings
- **Keyword extraction** - Extract entities, keywords, and related tags
- **Relevance ranking** - Compare text-based content with MMR and composite scoring
- **Semantic similarity** - Evaluate similarity between content blocks
- **Sentiment analysis** - Compute content polarity and class membership scores
- **Spam detection** - Detect spam and score toxicity
- **Style scoring** - Evaluate content linguistic attributes


## Commands
Each command takes input in the same shape (defined below) and returns results based on the type of operation. Most commands return a single result (as defined in the `Output` section below) for each supplied request item with the exception of `compare` and `rank`.

| Command | Purpose | Output Shape (Default) |
|---------|---------|------------------------|
| `mdaug analyze` | Compute metrics (sentiment, toxicity, etc.) |  `{metric: value, ...}` |
| `mdaug compare` | Compare one or more text inputs | `{item_or_id: score, ...}` |
| `mdaug extract` | Extract entities/keywords from the supplied content | `{entities: {...}, keywords: {...}}` |
| `mdaug outline` | Generate an outline of the supplied content | `{point: score, ...}` |
| `mdaug rank` | Rank items against query text | `{item_or_id: score, ...}` |
| `mdaug summarize` | Generate one or more summaries | `{summary: score, ...}` |
| `mdaug tag` | Generate tags related to the supplied content | `{tag: score, ...}` |
| `mdaug title` | Generate one or more titles or subtitles | `{title: score, ...}` |


## Configuration
All settings follow a four-tier priority: **CLI option -> env -> `config.yaml` -> default**.
Place a `config.yaml` in your working directory to set application-wide defaults; pass CLI options
to override on a per-run basis or set environment variables when deploying as part of a service.

| Setting | Default | Description |
|---------|---------|-------------|
| `transformers` | `None` | configuration settings for the `Transformers` library |


## Quickstart

### Install
```bash
python -m venv .venv
source .venv/bin/activate
pip install -e .
```


### Input

### Source
Each command accepts JSON from exactly one source:

- JSON from `stdin` by default
- `--file <path>` reads JSON from a file


### Format
All commands expect JSON in the same basic format, a list or dictionary of content for the
requested operation. The only difference between the two is how results are returned: for a list,
results preserve input order; for a dictionary, results reference input keys (ids).

Ordered list input:
```json
[
  "first content chunk to process",
  "second content chunk to process"
]
```

Keyed dictionary input:
```json
{
  "content-id1": "first content value",
  "content-id2": "second content value"
}
```

Supplied JSON with a single level of nesting is also acceptable and interpreted as groups of
individual requests. Each parent-level collection is processed in isolation from other groups.

List-of-groups input:
```json
[
  ["request 1 item 1", "request 1 item 2"],
  ["request 2 item 1", "request 2 item 2"]
]
```

Dictionary-of-groups input:
```json
{
  "group1": {
    "content-id1": "request 1 content"
  },
  "group2": {
    "content-id2": "request 2 content"
  }
}
```


### Output

### Destination
Each command directs output JSON to the defined output stream:

- JSON to `stdout` by default
- `--out <path>` writes JSON to a file
- Detailed logs/progress goes to `stderr`


### Format
All commands return JSON with the same top-level structure as the supplied request. If an ordered
list of content is provided, results are returned as an ordered list. If a dictionary is provided,
results are returned as a dictionary with matching keys.

The examples below illustrate default output shapes for each command.


#### `mdaug analyze`
The `analyze` command computes the scores of a set of pre-defined metrics customizable via `config.yaml`.

Request:
```json
["Natural language processing can enrich text with summaries and tags."]
```

Result:
```json
[
  {
    "negative": 0.03,
    "neutral": 0.22,
    "positive": 0.75,
    "polarity": 0.68,
    "toxicity": 0.01
  }
]
```


#### `mdaug compare`
The `compare` command evaluates semantic similarity between the first content item and all
remaining items. Results contain `N-1` scores because similarity against itself is always `1.00`.

Request:
```json
[
  "Natural language processing can enrich text with summaries and tags.",
  "NLP can enrich text with generated summaries and tags.",
  "Text augmentation adds summary and tagging metadata.",
  "Content can be transformed into structured NLP outputs."
]
```

Result:
```json
{
  "NLP can enrich text with generated summaries and tags.": 0.93,
  "Content can be transformed into structured NLP outputs.": 0.78,
  "Text augmentation adds summary and tagging metadata.": 0.71
}
```


#### `mdaug extract`
`extract` simply extracts keywords and entities from the supplied text and returns a dictionary of extracted keys and similarity score values.

Request:
```json
["Natural language processing can enrich text with summaries and tags."]
```

Result:
```json
[
  {
    "entities": {},
    "keywords": {
      "Natural": 0.78,
      "language": 0.65,
      "text": 0.62
    }
  }
]
```


#### `mdaug outline`
The `outline` command generates a list of high-level summary points and their scores for a given body of text.

Request:
```json
[
  "Natural language processing tools such as these can enrich text based on the defined operations. Available operations for this tool include summarization and tagging."
]
```

Result:
```json
[
  {
    "Natural language operations": 0.85,
    "Summarization and tagging": 0.83
  }
]

```


#### `mdaug rank`
The `rank` command returns ordered results and scores from a composite similarity metric that includes linguistic acceptability, ranking candidates in terms of completeness and not just similarity.

Request:
```json
[
  "Natural language processing can enrich text with summaries and tags.",
  "NLP can enrich text with generated summaries and tags.",
  "Text augmentation adds summary and tagging metadata.",
  "Content can be transformed into structured NLP outputs."
]
```

Result:
```json
{
  "NLP can enrich text with generated summaries and tags.": 0.93,
  "Text augmentation adds summary and tagging metadata.": 0.79,
  "Content can be transformed into structured NLP outputs.": 0.65
}
```


#### `mdaug summarize`
The `summarize` command generates a list of summaries of the supplied content with the number of results configurable via `config.yaml`.

Request:
```json
[
  "Natural language processing tools such as these can enrich text based on the defined operations. Available operations for this tool include summarization and tagging."
]
```

Result:
```json
[
  {
    "Natural language processing": 0.89,
    "Available operations for this tool": 0.82,
    "Operations to enrich text": 0.77
  }
]
```


#### `mdaug tag`
The `tag` command generates a list of related words or concepts relating to the supplied content with the number of results configurable via `config.yaml`.

Request:
```json
[
  "Natural language processing tools such as these can enrich text based on the defined operations. Available operations for this tool include summarization and tagging."
]
```

Result:
```json
[
  {
    "natural language": 0.92,
    "text": 0.90,
    "operations": 87,
    "tool": 0.85
  }
]
```


#### `mdaug title`
The `title` command generates a list of potential headings for the supplied content with the number of results configurable via `config.yaml`.

Request:
```json
[
  "Natural language processing tools such as these can enrich text based on the defined operations. Available operations for this tool include summarization and tagging."
]
```

Result:
```json
[
  {
    "NLP Operations and Tools": 0.97,
    "Natural Language Operations": 0.95,
    "Language Processing Tools": 0.89
  }
]
```


## Architecture
The general flow of dependency is `cli -> service -> core -> providers`:

```text
nlp-mdaug/
  src/mdaug/        # Main package source
    cli/            # Command-line interface
    common/         # Configuration and shared utilities
    core/           # Operational logic
    providers/      # Provider adapter layer
    service/        # Runtime and orchestration
    schemas/        # Shared requests and responses
  tests/            # Test suite (pytest)
  examples/         # Sample input & output
  config.yaml       # Default app-level configuration
  README.md         # User documentation
```


### cli
The command line interface package contains all modules that define the CLI app, its available commands, options, flags, and interfaces to the `core` logic layer. 

```
cli/                
  cli.py              # CLI interface entrypoint (Typer command based)
  commands.py         # Defines available commands (e.g. init, extract, commit, export)
```


### common
The common package simply contains shared modules and utilities leveraged throughout the application.

```
common/
  sample.py           # Sample text for operation demonstrations
  config.py           # User configuration loading and validation
```


### core
The core package contains all of the internal operational logic leveraged by the CLI commands. This includes content summarization, generation, keyword extraction, and analysis.

[NOTE: This structure is currently emerging and in development -- subject to change]
```
core/
  analysis/           # Sentiment analysis utilities (analyze operation)
  extraction/         # Keyword extraction and tagging (tag operation)
  generation/         # Content generation (summarize operation)
  relevance/          # Semantic comparison and ranking (compare and rank operations)
```


## Development
```bash
pytest          # run tests
ruff check .    # lint
mypy src/       # type check
```

### Contributing
This repository is currently in early development but feel free to submit PRs as long as all of your updates align with the following conventions...


#### Development Conventions
Focus on building readable, concise, minimal functional blocks organized by purpose. Project maintainability and interpretability is the primary goal, everything else is secondary.

The most important rule is to keep modules and code blocks simple and purposeful: Each module, class, function, block or call should have a single well-defined (and commented) purpose. DO NOT re-create the wheel, DO NOT add custom code when a common package will suffice. Add only the MINIMAL amount of code to implement the modules documented purpose.

#### Do's
- Be consistent with the style of the project and its conventions
- Simple elegant terse lines and declarations are the goal; optimize for readability
- Keep module, variable, class, and function names short (1-4 words) but distinct
- Function and variable names are snake case and class names are camel case
- Try to keep lines to 100 columns/characters or less (this is a soft limit)
- Include single returns (white space) to separate lines WITHIN logical blocks of code
- Include double returns (white space) BETWEEN logical blocks of code (e.g. after imports)
- Include a description of each module in a triple quoted comment at the top before imports
- Order module functions alphabetically or otherwise logically, be consistent.
- When vertically listing function arguments, indent the closing ) to match 
the argument indent (one level in from def), not back to the def column.

#### Dont's
- DO NOT list arguments vertically unless completely necessary.
- DO NOT vertically align function arguments if they can reasonably fit on a single line.
- DO NOT * import ANYTHING. Always explicitly import at the top of the module only.
- DO NOT add any functionality outside the defined scope of a given module.


### Testing
- Use pytest: Organize by folder and module mirroring the structure of the source
- Add fixtures when multiple tests require them and define them at the top of the test module or in a conftest file when shared between modules.
- Define tests with the user's input prior to implementing a new feature (TDD)
- Keep unit and integration tests separate, short, and isolated
- Unit tests should test a single function with names like `test_<function>_<case>`
- Tests should be able to be described in a single line with triple quote docstrings
- Use parameterized tests when possible to avoid test sprawl

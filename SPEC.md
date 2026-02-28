# nlp-mdaug Specifications
This document is intended to serve as a whiteboard for the early specifications for this application.


## Design Goals
- Simple JSON in / JSON out
- Friendly defaults for CLI users
- Input from `stdin` or `--file` only
- No directory/path scanning in v1
- Extensible provider layer for swapping model backends


## Philosophy: Simple Public I/O
The CLI should be easy to use without learning a complex schema, both input and output. The user may optionally configure advanced behavior via env variables of the local `config.yaml` file.

Default behavior:
- Generic JSON input format via stdin (small and readable)
- Command-specific JSON output via stdout (small and readable)

Advanced behavior (optional, later):
- Rich envelopes for batch jobs, tracing, partial failures, and provider metadata
- This keeps the public CLI friendly while still allowing a stronger internal data model.


## Commands
Each command takes input in the same shape (defined below) and returns results based on the type
of operation. Most commands return one result per supplied content item. `compare` and `rank`
return set-level scored results derived from all supplied content items.

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


## Input

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


## Output

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


## CLI Examples
Each command defaults to stdin input streams but can optionally read from a file using the `--file` option. Similarly, output defaults to stdout but the `--out` option supports writing to a file instead.

Read from file:
```bash
mdaug analyze --file examples/text.json
```

Pipe JSON via stdin:
```bash
cat examples/text.json | mdaug summarize
```

Write response to a file:
```bash
mdaug tag --file examples/text.json --out tagged.json
```


## Errors
Error behavior:
- Validation errors return non-zero exit code
- Runtime/model errors return non-zero exit code
- Error JSON goes to `stdout` (if command is in JSON mode)
- Logs/details go to `stderr`

Example:
```json
{
  "error": "missing_input",
  "message": "No JSON input found. Provide input via stdin or --file."
}
```


## Optional Advanced Format (Later)
If needed, add an optional richer output mode for debugging and pipelines:
- `--format full`
- `--debug`

This mode can include:
- request IDs
- provider/model metadata
- timing info
- partial failures
- scored candidates for summaries/tags

Important:
- Keep simple mode as the default
- Do not require envelope-based JSON for normal usage


## Configuration
All command options may also be set as environment variables or configured through the local `config.yaml` file. The order of priority for these configurations always follows the pattern below:
```text
CLI option -> environment variable -> config.yaml -> built-in default
```

Configuration groups:
- `providers` (backend selection)
- `generation` (prompt templates, token limits, temperature)
- `service` (runtime logging, cache, device)
- `operations` (settings for each command, e.g. analyze, compare, extract, etc.)

Example (conceptual):
```yaml
providers:
  generative: huggingface
  embeddings: sentence_transformers
  nlp: spacy

generation:
  model: google/gemma-3-1b-it
  max_new_tokens: 128
  temperature: 0.7
```


## Architecture (Simple, Extensible)
```text
src/mdaug/
  cli/                # CLI commands and input/output handling
  common/             # config, schemas, errors, shared utilities
  core/               # command/operation logic
    analysis/         # metric scoring operations
    extraction/       # entity and keyword extraction operations
    generation/       # summarize, title, outline, tag operations
    relevance/        # compare and rank operations
  providers/          # model/provider interfaces and adapters
  service/            # application runtime and orchestration
  schemas/            # shared request and response models
```

### `cli`
Responsibilities:
- Parse command options
- Load JSON from `stdin` or `--file`
- Validate user-friendly request shape
- Call core operation
- Emit JSON to `stdout` / `--out`

### `common`
Responsibilities:
- Config loading and validation
- Shared error types
- Shared schema helpers (simple public schemas + optional internal normalized schemas)

### `core`
Responsibilities:
- Implement command logic
- Use provider interfaces instead of provider SDKs directly
- Normalize outputs into simple default JSON


## Provider / Interface Layer (Extensibility)
The provider layer allows core operations to work with different backends without changing command
logic.

The primary purpose of this layer is to support a diverse set of local and remote generative models via the Transformers library, Ollama or through an existing service API.

This layer provides the ability to swap generative model backends (local HF, remote API, mock provider) while keeping `title`, `outline`, `summarize`, `tag` and related command module behavior stable.

### Provider design goals
- Interface-first (operations depend on protocols, not SDKs)
- Lazy loading (avoid loading heavy models at import time)
- Configurable selection (choose provider/model via config)
- Normalized outputs (providers return plain Python types)

### Suggested provider structure (planned)
Build to the follow structure as necessary, start with the core modules required for a flexible provider interface and adapt existing models and modules as needed.

```text
core/providers/
  registry.py              # names -> provider classes
  factory.py               # build providers from config
  errors.py                # provider-specific exceptions
  default/                 # default provider logic (generate, sentiment, etc.)
  interfaces/
    generative.py          # generate(prompt, ...) -> list[str]
    embeddings.py          # embed(texts) -> vectors
    nlp.py                 # parse/entities/sentence splitting (spacy)
    keyword.py             # keyword extraction interface (keybert)
  generative/
    huggingface.py
    openai.py              
  embeddings/
    sentence_transformers.py
```

### Example interface (conceptual)
```python
class GenerativeProvider(Protocol):
    def generate(self, prompt: str, **kwargs) -> list[str]:
        ...
```

### Dependency direction
```text
cli -> common
cli -> core
core/* -> core/providers/interfaces
core/providers/* -> external SDKs
```

Avoid:
- CLI importing provider SDKs directly
- Core operations returning provider-specific objects
- Model initialization during module import


## Development
```bash
pytest
ruff check .
mypy src/
```


## Contributing
Follow the project conventions in `AGENTS.md` and keep modules simple, focused, and easy to read.

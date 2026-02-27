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
- Command-specific JSON output vis stdout (small and readable)

Advanced behavior (optional, later):
- Rich envelopes for batch jobs, tracing, partial failures, and provider metadata
- This keeps the public CLI friendly while still allowing a stronger internal data model.


## Commands
Each command takes input in the same shape (defined below) and returns results based on the type of operation. Analysis and generation commands such as `analyze`, `extract`, `outline`, `summarize`, `tag`, and `title` will return one or more results for each supplied content item.

| Command | Purpose | Output Shape (Default) |
|---------|---------|------------------------|
| `mdaug analyze` | Compute metrics (sentiment, toxicity, etc.) |  `{metric: value, ...}` |
| `mdaug compare` | Compare one or more text inputs | `{input: score, ...}` |
| `mdaug extract` | Extract entities/keywords from the supplied content | `{entities: [...], ...}` |
| `mdaug outline` | Generate an outline of the supplied conent | `{outline: "...", ...}` |
| `mdaug rank` | Rank items against query text | `[most_relevant, ..., least_relevant]` |
| `mdaug summarize` | Generate one or more sumamries | `{summary: "...", ...}` |
| `mdaug tag` | Generate tags related to the supplied content | `{tags: [...], ...}` |
| `mdaug title` | Generate one or more titles or subtitles | `{title: "...", ...}` |


## Input

### Source
Each command accepts JSON from exactly one source:

- JSON from `stdin` by default
- `--file <path>` reads JSON from a file


### Format
All commands expect JSON in the same basic format, a list or dictionary of the content to be supplied to the requested operation. The only difference between the two is in how results are returned: for a list results are ordered respective to the source content. If a dictionary is supplied the results will reference the keys (ids) of the content.

```json
# Input provided as an ordered list of content strings (no key/ids to reference)
["first content chunk to process", "second content chunk", ...]

# Input provided as key-value pairs where results will reference the supplied keys
{"content-id1": "content value1", "content-id2": "content value2", ...}
```

Supplied JSON with a single level of nesting is also acceptable and interpreted as groups of individual requests. Each parent level collection will be processed in isolation from all other groups in a batch fashion. 

```json
# Input groups may be provided as a list of lists, or list of dicts
[{"content-id": "content value", ...}, {"content-id": "content value", ...}]

# Input provided as key-value pairs return results that reference the supplied keys
{"group1": {"content-id": "request1 content", ...}, "group2": {"content-id": "request2 content", ...}]
```


## Output

### Destination
Each command directs output json to the defined output stream:

- JSON to `stdout` by default
- `--out <path>` writes JSON to a file
- Detailed logs/progress goes to `stderr`


### Format
All commands return JSON with the same item structure as the supplied request. If an ordered list of content is provided the results will be returned as a list of results with the same relative order. If a dictionary is provided the results will be returned as a dictionary with item keys matching each request.

The examples below illustrate a single result for a given content item.


#### `mdaug analyze`
The `analyze` command computes the scores of a set of pre-defined (customizable via `config.yaml`) metrics.

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
The `compare` command evaluate the semantic similarity between the first content item and all remaining items. The results will always contain N-1 scores since evaluating the semantic similarity of text against itself always yeilds 1.00.

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
[
  0.93, 
  0.71, 
  0.78
]
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
  "Natural language processing tools such as these can enrich text based on the defined 
  operations. Available operations for this tool include summarization and tagging."
]
```

Result:
```json
{
  "Natural language operations": 0.85,
  "Summarization and tagging": 0.83
}
```


#### `mdaug rank`
The `rank` command returns results in order of a composite similarity metric along with the computed scores.

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


#### `mdaug summarize`
The `summarize` command generates a list of summaries of the supplied content with the number of results configurable via `config.yaml`.

Request:
```json
[
  "Natural language processing tools such as these can enrich text based on the defined 
  operations. Available operations for this tool include summarization and tagging."
]
```

Result:
```json
{
  "Natural language processing": 0.89,
  "Available operations for this tool": 0.82,
  "Operations to enrich text": 0.77,
}
```


#### `mdaug tag`
The `tag` command generates a list of related words or concepts relating to the supplied content with the number of results configurable via `config.yaml`.

Request:
```json
[
  "Natural language processing tools such as these can enrich text based on the defined 
  operations. Available operations for this tool include summarization and tagging."
]
```

Result:
```json
{
  "natural language": 0.92,
  "text": 0.90,
  "operations": 87,
  "tool": 0.85
}
```


#### `mdaug title`
The `title` command generates a list of potential headings for the supplied content with the number of results configurable via `config.yaml`.

Request:
```json
[
  "Natural language processing tools such as these can enrich text based on the defined 
  operations. Available operations for this tool include summarization and tagging."
]
```

Result:
```json
{
  "NLP Operations and Tools": 0.97,
  "Natural Language Operations": 0.95,
  "Language Processing Tools": 0.89,
}
```


# TODO: Finish revising CLI examples using the above input/output format
## CLI Examples

Read from file:

```bash
mdaug analyze --file examples/analyze.json
```

Pipe JSON via stdin:

```bash
cat examples/summarize.json | mdaug summarize
```

Write response to a file:

```bash
mdaug compute --file examples/compute.json --out output.json
```


## Errors (Simple Default)

Default CLI errors should be understandable and small.

Example:

```json
{
  "error": "missing_field",
  "message": "Required field 'content' is missing."
}
```

Suggested error behavior:

- Validation errors return non-zero exit code
- Runtime/model errors return non-zero exit code
- Error JSON goes to `stdout` (if command is in JSON mode)
- Logs/details go to `stderr`


## Optional Advanced Format (Later)

If needed, add an optional richer output mode for debugging and pipelines:

- `--format full`
- `--debug-meta`

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

Priority order:

```text
CLI option -> environment variable -> config.yaml -> built-in default
```

Suggested config groups:

- `providers` (backend selection)
- `models` (model names per operation)
- `generation` (prompt templates, token limits, temperature)
- `analysis` (enabled metrics / thresholds)
- `relevance` (ranking defaults)
- `runtime` (logging, cache, device)

Example (conceptual):

```yaml
providers:
  generative: huggingface
  embeddings: sentence_transformers
  nlp: spacy

models:
  generative:
    model: google/gemma-3-1b-it

generation:
  max_new_tokens: 128
  temperature: 0.7
```


## Architecture (Simple, Extensible)

```text
src/mdaug/
  cli/                  # CLI commands and input/output handling
  common/               # config, schemas, errors, shared utilities
  core/
    analysis/           # analyze operation
    extraction/         # tag operation
    generation/         # summarize operation
    relevance/          # compare and rank operations
    providers/          # model/provider interfaces and adapters
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

Primary use case:

- Swap generative model backends (local HF, remote API, mock provider) while keeping
  `summarize`/`compute` behavior stable.

### Provider design goals

- Interface-first (operations depend on protocols, not SDKs)
- Lazy loading (avoid loading heavy models at import time)
- Configurable selection (choose provider/model via config or CLI)
- Normalized outputs (providers return plain Python types)

### Suggested provider structure

```text
core/providers/
  registry.py              # names -> provider classes
  factory.py               # build providers from config
  errors.py                # provider-specific exceptions

  interfaces/
    generative.py          # generate(prompt, ...) -> list[str]
    embeddings.py          # embed(texts) -> vectors
    nlp.py                 # parse/entities/sentence splitting
    keyword.py             # keyword extraction interface

  generative/
    huggingface.py
    openai.py              # optional
    mock.py                # tests/dev

  embeddings/
    sentence_transformers.py
    mock.py

  nlp/
    spacy.py
    mock.py

  keyword/
    keybert.py
    mock.py
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

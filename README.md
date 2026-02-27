# nlp-mdaug
A CLI-first NLP augmentation toolkit for structured text content.

`nlp-mdaug` analyzes text, generates summaries/headings, extracts tags, and returns JSON.


## Purpose
This application is intended to augment collections of textcontent with AI and NLP-derived relational and semantic information with a simple and direct JSON input and output format.

General Workflow:
```
JSON content → compute metrics, summarize, extract tags → JSON results 
```


## Features
- **AI summarization** — Generate content summaries, titles, and headings
- **Keyword extraction** — Extract entities, keywords, and related tags
- **Relevance ranking** —  Compare text-based content with MMR and composite scoring
- **Semantic similarity** —  Evaluate similarity between content blocks
- **Sentiment analysis** — Compute content polarity and class membership scores
- **Spam detection** — Detect spam and score toxicity
- **Style scoring** — Evaluate content linguistic attributes


## Commands
Each command takes input in the same shape (defined below) and returns results based on the type of operation. All commands return a single result (as defined in the `Output` section below) for each supplied request item. 

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


## Configuration
All settings follow a four-tier priority: **CLI option → env → `config.yaml` → default**.
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
Each command can take a json string as input via stdin:
```
[
  {"id": "doc-001:0", "slug": "my-doc.md"},
  {"id": "doc-001:1", "title": "Example doc"},
  {"id": "doc-001:2", "content": "First text block."},
  {"id": "doc-001:3", "content": "Second text block."}
]
```
NOTE: The value of the "id" key is used as a reference for comparison and ranking operations


### Output
For a given input all commands return json via stdout: 
```
{
  "command": "analyze",
  "results": {...},
  "status": "ok",
  "errors": [],
}
```

Results may optionally be returned as a json file with the `--out <file>` option:

| File | Description |
|------|-------------|
| `<slug>.json` | All requested metrics, summaries, tags and results


## Architecture
```
nlp-mdaug/
├── src/mdaug/        # Main package source
│   ├── cli/          # Command-line interface
│   ├── common/       # Config and shared modules and utils
│   └── core/         # Operational logic 
├── tests/            # Test suite (pytest)
├── examples/         # Sample input & output
├── config.yaml       # Default app-level configurations
└── README.md         # User documentation
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
  analysis/           # Sentiment analysis utilties (analyze operation)
  extraction/         # Keyword extraction and tagging (tag operation)
  generation/         # Content generation (summarize operation)
  providers/          # Default models and provider adapter layer
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
- Use paramaterized tests when possible to avoid test sprawl

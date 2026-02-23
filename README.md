# nlp-mdaug
A CLI-first tool for AI-powered NLP toolbox and augmentation engine for structured text data automatically extracting configurable metrics, generating summaries, headings and extracting tags.


## Purpose
This application is intended to augment ordered blocks of text-based content with natural language-based  relational and semantic information.

General Workflow:
```
content → compute metrics, summarize, extract tags → relational JSON 
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
[High-level description of interface commands go here, what form does user inputs take?]

```
mdaug analyze         # Compute spam, toxicity, style and sentiment metrics
mdaug compare         # run the entire pipeline (all of the following commands)
mdaug rank            # initialize database schema and optionally clears stored data
mdaug summarize       # recursively extract blocks, frontmatter, and content hash
mdaug tag             # initialize database schema and optionally clears stored data
```

`<path>` is a single directory (recursively scanned)


## Configuration
All settings follow a three-tier priority: **CLI option → `config.yaml` → built-in default**.
Place a `config.yaml` in your working directory to set project-wide defaults; pass CLI options
to override on a per-run basis.

| Setting | Default | Description |
|---------|---------|-------------|
| `transformers` | `None` | configuration settings for the `Transformers` library |


## Quickstart

### Install
```bash
python -m venv .venv
source .venv/bin/activate
pip install -U pip
pip install -e ".[dev]"
```

### Output
For each input document, all commands produce:

| File | Description |
|------|-------------|
| `<slug>.json` | All requested metrics, summaries, tags and results


## Architecture
```
nlp-mdaug/
├── src/mdaug/        # Main package source
│   ├── cli/          # Command-line interface
│   ├── core/         # Operational logic
│   └── utils/        # Common and shared app utilities
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


### core
The core package contains all of the internal operational logic leveraged by the CLI commands. This includes content summarization, generation, keyword extraction, and analysis.

[NOTE: This structure is currently emerging and in development -- subject to change]
```
core/
  operations/         # Implementation for compare, rank, summarize, etc.
  relevance/          # Semantic similarity and relevance support
  analysis/           # Sentiment analysis utilties
  generation/         # Content generation and summarization
  extraction/         # Keyword extraction and tagging
```


### utils
The utils package simply contains common utilities leveraged throughout the application.

```
utils/
  config.py           # User configuration loading and validation
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
- DO NOT vertically space lines of code unless completely necessary.
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

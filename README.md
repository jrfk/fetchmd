> [!NOTE]
> ⚡ Note: This is a vibe coding project. The code is experimental and may evolve rapidly.
> 

# fetchmd

Fetch web pages and convert them to Markdown.

This CLI tool allows you to fetch one or more URLs concurrently, extract the main content, convert it to Markdown, and save it locally. It uses `httpx` for asynchronous HTTP requests and `readability-lxml` for content extraction.

## Installation

**Prerequisites:**

*   Python >= 3.10
*   [uv](https://github.com/astral-sh/uv): A fast Python package installer and resolver (used in the Makefile). You can install it via pip, brew, etc.

**Steps:**

1.  Clone the repository:
    ```bash
    git clone https://github.com/jrfk/fetchmd.git
    cd fetchmd
    ```
2.  Install dependencies using the Makefile (which utilizes `uv`):
    ```bash
    make install
    ```
    This command installs the package in editable mode along with all optional and development dependencies defined in `pyproject.toml`.

## Usage

There are several ways to run `fetchmd`:

**1. Using the Makefile:**

This is the recommended way for simple runs. Set the `URL` environment variable (space-separated for multiple URLs).

```bash
make run URL="https://example.com"
# Multiple URLs
make run URL="https://example.com https://another-site.org/page"
# Specify output directory (defaults to ./out)
make run URL="https://example.com" OUT=./markdown_files
```

**2. Directly via Python module:**

You can also invoke the CLI directly.

```bash
fetchmd https://example.com https://another-site.org/page --out ./output --concurrency 10
```


```bash
uvx fetchmd https://example.com https://another-site.org/page --out ./output --concurrency 10
```


**3. Using the VS Code Task:**

If you are using Visual Studio Code, you can use the predefined task:

1.  Open the Command Palette (Cmd+Shift+P or Ctrl+Shift+P).
2.  Type "Tasks: Run Task" and select it.
3.  Choose "Run fetchmd".
4.  You will be prompted to enter the URL(s).

**Output:**

Markdown files will be saved in the specified output directory (default: `./out`), organized by domain name:

```
out/
└── example.com/
    └── example-domain.md
└── another-site.org/
    └── page.md
```

Each Markdown file includes YAML front-matter with the title (derived from the slug), date, and source URL.

## CLI Options

```
Usage: python -m fetchmd [OPTIONS] URLS...

Arguments:
  URLS...  List of URLs to fetch.  [required]

Options:
  -o, --out TEXT       Output directory for Markdown files.  [default: out]
  -c, --concurrency INTEGER
                       Number of concurrent fetch requests.  [default: 5]
  -t, --timeout INTEGER  Request timeout in seconds.  [default: 20]
  -ua, --user-agent TEXT
                       Custom User-Agent string.
  --help               Show this message and exit.
```

## Development

*   **Run tests:** `make test` (uses `pytest`)

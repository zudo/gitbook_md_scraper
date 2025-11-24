# gitbook_md_scraper

A simple tool to download GitBook documentation as Markdown files. It preserves the directory structure, creating a tree of markdown files perfect for feeding into AI/LLM agents for context.

It is also useful for version tracking documentation to easily see changes over time.

## Usage

1. **Clone this repo**:

   ```bash
   git clone https://github.com/zudo/gitbook_md_scraper
   cd gitbook_md_scraper
   ```

2. **Install** (requires [uv](https://github.com/astral-sh/uv)):

   ```bash
   uv tool install .
   ```

3. **Run**:

   ```bash
   gitbook-md-scraper <URL>
   ```

   Example:

   ```bash
   gitbook-md-scraper https://gitbook.com/docs
   ```

Files are saved to the `docs/` folder.

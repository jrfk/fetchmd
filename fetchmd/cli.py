import asyncio
import logging
from typing import List, Optional

import typer

from .converter import html2md
from .extractor import extract_main

# 相対インポートで他のモジュールを読み込む
from .fetcher import _DEFAULT_CONCURRENCY, _DEFAULT_TIMEOUT, Fetcher
from .writer import save_markdown

# 基本的なロギング設定
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Typerアプリケーションインスタンスを作成
# pyproject.toml の [project.scripts] で "fetchmd:app" と指定されているため、
# この 'app' インスタンスが参照される
app = typer.Typer(help="Fetch web pages and convert them to Markdown.")

async def process_url(url: str, fetcher: Fetcher, out_dir: str):
    """単一のURLを処理する非同期関数"""
    try:
        logger.info(f"Fetching: {url}")
        html = await fetcher.get(url)
        if not html:
            logger.warning(f"No content fetched for {url}")
            return

        logger.info(f"Extracting main content from: {url}")
        main_html = extract_main(html, url)
        if not main_html:
            logger.warning(f"Could not extract main content from {url}")
            # 元のHTMLをそのまま使うか、スキップするか選択できる。ここではスキップ。
            return

        logger.info(f"Converting HTML to Markdown for: {url}")
        markdown = html2md(main_html)
        if not markdown:
            logger.warning(f"Could not convert content to Markdown for {url}")
            return

        logger.info(f"Saving Markdown for: {url}")
        await save_markdown(markdown, url, out_dir)

    except Exception as e:
        # トレースバックは冗長なのでFalse
        logger.error(f"Failed to process {url}: {e}", exc_info=False)

@app.command()
def run(
    urls: List[str] = typer.Argument(..., help="List of URLs to fetch."),
    out_dir: str = typer.Option("out", "--out", "-o", help="Output directory for Markdown files."),
    concurrency: int = typer.Option(
        _DEFAULT_CONCURRENCY, "--concurrency", "-c",
        help="Number of concurrent fetch requests."
    ),
    timeout: int = typer.Option(
        _DEFAULT_TIMEOUT, "--timeout", "-t",
        help="Request timeout in seconds."
    ),
    user_agent: Optional[str] = typer.Option(
        None, "--user-agent", "-ua",
        help="Custom User-Agent string."
    ),
):
    """
    Fetches content from URLs, extracts main articles, converts to Markdown, and saves them.
    """
    logger.info("Starting fetchmd run...")
    logger.info(f"Output directory: {out_dir}")
    logger.info(f"Concurrency: {concurrency}")
    logger.info(f"Timeout: {timeout}")
    if user_agent:
        logger.info(f"Using custom User-Agent: {user_agent}")

    # Fetcherインスタンスを作成
    fetcher_args = {"concurrency": concurrency, "timeout": timeout}
    if user_agent:
        fetcher_args["user_agent"] = user_agent
    fetcher = Fetcher(**fetcher_args)

    # 各URLに対する処理タスクを作成
    tasks = [process_url(url, fetcher, out_dir) for url in urls]

    # asyncio.gatherでタスクを並行実行
    # ここで asyncio.run を使うと Typer の async サポートと競合する可能性があるため、
    # Typer が内部でイベントループを管理するのに任せる。
    # Typer はデコレートされた関数が async def の場合、自動的に asyncio.run を呼び出す。
    async def main():
        await asyncio.gather(*tasks)

    asyncio.run(main())
    logger.info("fetchmd run finished.")

# スクリプトとして直接実行された場合（主にデバッグ用）
if __name__ == "__main__":
    app()

import logging

import html_to_markdown

logger = logging.getLogger(__name__)

def html2md(html: str) -> str:
    """
    HTML 文字列を Markdown に変換します。

    Args:
        html: 変換対象の HTML 文字列。

    Returns:
        変換された Markdown 文字列。変換に失敗した場合は空文字列を返します。
    """
    if not html:
        logger.warning("Empty HTML provided for conversion.")
        return ""

    try:
        # html-to-markdown ライブラリを使用して変換
        markdown_content = html_to_markdown.markdownify(html)
        return markdown_content
    except Exception as e:
        logger.error(f"Failed to convert HTML to Markdown: {e}", exc_info=True)
        return ""

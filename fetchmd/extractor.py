from readability import Document
import logging

logger = logging.getLogger(__name__)

def extract_main(html: str, url: str) -> str:
    """
    readability-lxml を使用して、HTML 文字列から主要な記事コンテンツを抽出します。

    Args:
        html: 抽出対象の HTML 文字列。
        url: HTML の取得元 URL。相対リンクの解決などに使用されることがあります。

    Returns:
        抽出された主要コンテンツの HTML 文字列。抽出に失敗した場合は空文字列を返します。
    """
    if not html:
        logger.warning(f"Empty HTML provided for URL: {url}")
        return ""

    try:
        doc = Document(html, url=url)
        # summary() は主要なコンテンツの HTML を返す
        # html=True を指定しないとプレーンテキストになる
        main_content_html = doc.summary(html_partial=True)
        return main_content_html
    except Exception as e:
        # readability-lxml は様々な内部エラーを出す可能性があるため、広めに捕捉
        logger.error(f"Failed to extract main content from {url}: {e}", exc_info=True)
        return ""
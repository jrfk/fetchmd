import asyncio
import re  # 正規表現モジュールをインポート
from typing import Final

import httpx

# デフォルトのユーザーエージェント文字列
_DEFAULT_UA: Final = "fetchmd/0.1 (+https://github.com/jrfk/fetchmd)"
# デフォルトの並行処理数
_DEFAULT_CONCURRENCY: Final = 5
# デフォルトのタイムアウト（秒）
_DEFAULT_TIMEOUT: Final = 20

class Fetcher:
    """
    指定されたURLから非同期にコンテンツを取得するクラス。
    asyncio.Semaphore を使用して同時接続数を制御します。
    """
    def __init__(
        self,
        concurrency: int = _DEFAULT_CONCURRENCY,
        timeout: int = _DEFAULT_TIMEOUT,
        user_agent: str = _DEFAULT_UA,
    ):
        """
        Fetcherを初期化します。

        Args:
            concurrency: 最大同時接続数。
            timeout: HTTPリクエストのタイムアウト（秒）。
            user_agent: HTTPリクエストで使用するUser-Agentヘッダー。
        """
        if concurrency <= 0:
            raise ValueError("Concurrency must be a positive integer.")
        if timeout <= 0:
            raise ValueError("Timeout must be a positive integer.")

        self._sem = asyncio.Semaphore(concurrency)
        self._timeout = timeout
        self._headers = {"User-Agent": user_agent}

    async def get(self, url: str) -> str:
        """
        指定されたURLからコンテンツを非同期に取得します。

        Args:
            url: 取得対象のURL。

        Returns:
            取得したコンテンツのテキスト。

        Raises:
            httpx.HTTPStatusError: HTTPリクエストが失敗した場合 (4xx or 5xx)。
            httpx.RequestError: ネットワーク関連のエラーが発生した場合。
            ValueError: URLが無効な場合。
        """
        # 正規表現で http:// または https:// の後にホスト名が続くかチェック
        # 簡単なチェックであり、完全なURLバリデーションではない点に注意
        if not url or not re.match(r"^https?://.+", url):
            # URLの検証エラーメッセージ
            msg = "Invalid URL provided (must start with http:// or https:// followed by a host)"
            raise ValueError(f"{msg}: {url}")

        # 同時実行数を制限し、HTTPクライアントを生成
        async with self._sem, httpx.AsyncClient(
            timeout=self._timeout,
            follow_redirects=True,  # リダイレクトを追跡
            headers=self._headers,  # カスタムヘッダーを設定
            http2=True,             # HTTP/2 を有効化 (可能な場合)
        ) as client:
                try:
                    response = await client.get(url)
                    response.raise_for_status()  # 4xx/5xxエラーがあれば例外を送出
                    # エンコーディングを推測させるために .text を使用
                    return response.text
                except httpx.HTTPStatusError as e:
                    print(f"HTTP error occurred for {url}: {e}")
                    raise
                except httpx.RequestError as e:
                    print(f"Request error occurred for {url}: {e}")
                    raise
                except Exception as e: # 予期せぬエラー
                    print(f"An unexpected error occurred for {url}: {e}")
                    raise

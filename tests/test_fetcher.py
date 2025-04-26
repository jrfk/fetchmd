import pytest

from fetchmd.fetcher import Fetcher


# pytest-asyncio が非同期テスト関数を認識するためのマーカー
@pytest.mark.asyncio
async def test_fetcher_example_com():
    """
    Fetcher クラスが https://example.com からコンテンツを正常に取得できるかテストする。
    """
    # Fetcher インスタンスを作成 (テスト用に小さな値を設定)
    fetcher = Fetcher(concurrency=2, timeout=10)

    try:
        # https://example.com からコンテンツを取得
        html = await fetcher.get("https://example.com")

        # 取得した HTML に期待される文字列が含まれているか確認
        assert "<h1>Example Domain</h1>" in html
        assert "<p>This domain is for use in illustrative examples in documents." in html

    except Exception as e:
        # テストが失敗した場合、エラー内容を表示
        pytest.fail(f"Fetcher failed to get content from https://example.com: {e}")

@pytest.mark.asyncio
async def test_fetcher_invalid_url():
    """
    Fetcher クラスが無効な URL に対して適切に ValueError を送出するかテストする。
    """
    fetcher = Fetcher()
    invalid_urls = [
        "example.com",          # スキームなし
        "ftp://example.com",    # サポート外スキーム
        "",                     # 空文字列
        "http://",              # ホスト名なし
    ]

    for url in invalid_urls:
        with pytest.raises(ValueError, match="Invalid URL provided"):
            await fetcher.get(url)

@pytest.mark.asyncio
async def test_fetcher_not_found():
    """
    Fetcher クラスが存在しない URL (404) に対して httpx.HTTPStatusError を送出するかテストする。
    """
    fetcher = Fetcher(timeout=5)
    # 確実に 404 を返すであろう URL
    url = "https://httpbin.org/status/404"

    # httpx.HTTPStatusError が発生することを期待
    # pytest.raises をコンテキストマネージャとして使用
    with pytest.raises(pytest.importorskip("httpx").HTTPStatusError) as excinfo:
        await fetcher.get(url)

    # エラーオブジェクトのステータスコードが 404 であることを確認
    assert excinfo.value.response.status_code == 404

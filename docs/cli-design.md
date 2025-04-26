
# 📑 **Agent 作業指示書**
*(CLI「fetchmd」を **httpx.AsyncClient + asyncio** でゼロから設計・実装する)*  

---

## 1. ゴール / Goal  

- **指定 URL**（複数可）を並列に取得し、本文を抽出して **Markdown** ファイルとして保存できる CLI を完成させる。  
- すべて **httpx.AsyncClient** を用いた非同期 I/O で実装する。  
- `make run URL=...` または VS Code/Copilot-Agent の **Run fetchmd** タスクからワンコマンド実行できることを確認。  

---

## 2. プロジェクト構成 / Layout  

```
fetchmd/
├─ fetchmd/
│  ├─ __init__.py
│  ├─ cli.py          # Typer エントリ
│  ├─ fetcher.py      # httpx + asyncio
│  ├─ extractor.py    # readability-lxml ラッパ
│  ├─ converter.py    # html-to-markdown
│  └─ writer.py       # aiofiles
├─ tests/
│  └─ test_fetcher.py
├─ Makefile
├─ .vscode/
│  └─ tasks.json
├─ pyproject.toml
└─ README.md
```

---

## 3. 主要ライブラリ / Tech Stack  

| 目的 | ライブラリ | 備考 |
|------|-----------|------|
| CLI | **Typer** | Click 互換で `async` 関数呼び出ししやすい |
| HTTP | **httpx[http2]** | HTTP/2 も有効化 |
| 本文抽出 | **readability-lxml** + BeautifulSoup4 | 広告除去 |
| HTML→MD | **html-to-markdown** (デフォルト) <br> 任意で **markitdown** 切替可 | Strategy pattern |
| 非同期ファイル | **aiofiles** | 画像も将来 DL 可能 |
| テスト | pytest + **pytest-asyncio** | CI ready |

| パッケージ管理 | **uv** | 依存解決とビルドを高速化 |


---

## 4. 実装タスク / Tasks for the Agent  

| # | 内容 | 成否判定 |
|---|------|---------|
| **1** | `pyproject.toml` 作成：Python ≥ 3.10、依存を `[project.optional-dependencies] all = [...]` へ定義 | `uv uv pip install -e .[all]` が完走 |
| **2** | `fetcher.py`: `class Fetcher` を **httpx.AsyncClient** + `asyncio.Semaphore` で実装<br>‐ 引数 `concurrency=5`, `timeout=20` を持つ | `await Fetcher().get("https://example.com")` が `<h1>Example` を含む |
| **3** | `extractor.py`: readability で主要記事 HTML を返す `extract_main(html, url)` 関数 | 単体テストで非 None |
| **4** | `converter.py`: `html2md(html: str) -> str` を実装。<br>Strategy で `"backend"` を切替えられるようにする | デフォルト backend で見出し `#` が含まれる |
| **5** | `writer.py`: `save_markdown(md, url, out_dir)` で<br>``out/<domain>/<slug>.md`` へ保存。YAML front-matterを付与 | ファイルが生成され、タイトルと date が入る |
| **6** | `cli.py`: Typer で `fetchmd run URL... --out out --concurrency 8` を実装 | `python -m fetchmd.run https://example.com` が成功 |
| **7** | テスト: `tests/test_fetcher.py` を pytest-asyncio で作成 | `pytest -q` が緑 |
| **8** | **Makefile**: `install`, `test`, `run` ターゲットを用意 | `make run URL=https://example.com` が md 生成 |
| **9** | **.vscode/tasks.json**: `Run fetchmd` で `make run` を実行 | コマンドパレットから実行可 |
| **10** | **README.md**: セットアップ～使用例を記載 | mdlint パス |
| **11** | GitHub Actions (optional): `pytest` と `make run URL=https://example.com` を確認する CI | CI が green |

---

## 5. サンプルコード断片 / Code Snippets  

### fetcher.py
```python
import asyncio, httpx
from typing import Final

_DEFAULT_UA: Final = "fetchmd/0.1 (+https://github.com/yourorg/fetchmd)"

class Fetcher:
    def __init__(self, concurrency: int = 5, timeout: int = 20):
        self._sem = asyncio.Semaphore(concurrency)
        self._timeout = timeout
        self._headers = {"User-Agent": _DEFAULT_UA}

    async def get(self, url: str) -> str:
        async with self._sem:
            async with httpx.AsyncClient(
                timeout=self._timeout,
                follow_redirects=True,
                headers=self._headers,
                http2=True,
            ) as client:
                r = await client.get(url)
                r.raise_for_status()
                return r.text
```

### tests/test_fetcher.py
```python
import pytest, asyncio
from fetchmd.fetcher import Fetcher

@pytest.mark.asyncio
async def test_fetcher_example():
    html = await Fetcher(concurrency=2, timeout=10).get("https://example.com")
    assert "<h1>Example Domain</h1>" in html
```

### Makefile
```make
PY=python -m

install:
	uv uv pip install -e .[all]

test:
	pytest -q

run:
	$(PY) fetchmd.cli run $(URL) --out out
```

---

## 6. コミットルール / Commit Guidelines  

| Prefix | 用途 | 例 |
|--------|------|----|
| `feat:` | 機能追加 | `feat: add httpx fetcher` |
| `fix:` | バグ修正 | `fix: handle invalid url scheme` |
| `docs:` | 文書 | `docs: add README quickstart` |
| `chore:` | CI・設定・Makefile | `chore: add vscode tasks` |
| `test:` | テスト追加 | `test: cover extractor edge cases` |

**1タスク = 1コミット** を推奨。  

---

## 7. 開発フロー / Step-by-Step  

1. **Fork / Clone** リポジトリ  
2. `make install  # uses uv` で依存を入れる  
3. タスク **#2-5** を順番に実装 → 各ステップで `pytest -q`  
4. **#6** で CLI を完成 → `make run URL=https://example.com` 動作確認  
5. **#7-9** を追加して DX 改善  
6. **#10** README 更新 → `mdlint`  
7. (任意) **#11** GitHub Actions で CI を確立  
8. 全テスト・CI グリーンを確認してプルリク作成  

---

## 8. Definition of Done  

- `make run URL=https://example.com` → `out/example.com/example-domain.md` が生成され、本文が Markdown 化されている  
- `pytest -q` で **0 失敗**  
- VS Code **Run fetchmd** が同じ成果物を出力  
- 依存は **httpx** 系のみで **aiohttp** は含まれない  
- すべてのコミットがルールに従い、README が最新  

---

> **備考**  
> - 今後の拡張（クローラー、画像ダウンロード、i18n など）は `converter` / `writer` に Strategy を噛ませるだけで対応可能。  
> - HTTP/2 有効化により一部サイトでヘッダー圧縮・多重化のメリットを享受できる。  
> - 大量 URL でも `concurrency` を絞れば帯域を枯渇させずに済む。  

Happy coding & scraping!

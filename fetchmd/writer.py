import logging
import os
import re
from datetime import datetime
from pathlib import Path
from urllib.parse import urlparse

import aiofiles

logger = logging.getLogger(__name__)

def _sanitize_filename(name: str) -> str:
    """ファイル名として安全な文字列に変換する"""
    # スラッシュをハイフンに置換
    name = name.replace('/', '-')
    # ファイル名に使えない文字を除去 (英数字、ハイフン、アンダースコア以外を除去)
    name = re.sub(r'[^\w\-_\.]', '', name)
    # 先頭と末尾のハイフンやアンダースコアを除去
    name = name.strip('-_')
    # 連続するハイフンやアンダースコアを1つにまとめる
    name = re.sub(r'[-_]{2,}', '-', name)
    # 長すぎるファイル名を切り詰める (例: 100文字)
    return name[:100]

async def save_markdown(md: str, url: str, out_dir: str):
    """
    Markdown コンテンツを YAML front-matter 付きでファイルに非同期で保存します。

    Args:
        md: 保存する Markdown 文字列。
        url: コンテンツの取得元 URL。ドメイン名とファイルパスの生成に使用します。
        out_dir: 保存先のベースディレクトリ。
    """
    if not md:
        logger.warning(f"Empty markdown content provided for URL: {url}. Skipping save.")
        return

    try:
        parsed_url = urlparse(url)
        domain = parsed_url.netloc
        path = parsed_url.path.strip('/') # 先頭と末尾のスラッシュを除去

        # パスからファイル名を生成
        if not path:
            slug = "index"
        else:
            # パスの最後の部分をファイル名候補とする
            filename_candidate = path.split('/')[-1]
            # 拡張子を除去 (例: .html, .php)
            filename_base = os.path.splitext(filename_candidate)[0]
            slug = _sanitize_filename(filename_base)
            if not slug: # サニタイズ後に空になった場合
                slug = _sanitize_filename(path) # パス全体をサニタイズ
                if not slug: # それでも空なら index
                    slug = "index"

        # 出力ディレクトリとファイルパスを構築
        output_path = Path(out_dir) / domain / f"{slug}.md"

        # 出力ディレクトリを作成 (親ディレクトリも含む)
        # これは非同期である必要はない
        output_path.parent.mkdir(parents=True, exist_ok=True)

        # YAML front-matter を作成
        # スラッグから簡易的なタイトル生成
        title = slug.replace('-', ' ').replace('_', ' ').capitalize()
        current_date = datetime.now().strftime('%Y-%m-%d')
        front_matter = f"---\ntitle: {title}\ndate: {current_date}\nsource: {url}\n---\n\n"

        # ファイルに非同期で書き込み
        async with aiofiles.open(output_path, mode='w', encoding='utf-8') as f:
            await f.write(front_matter + md)

        logger.info(f"Successfully saved markdown for {url} to {output_path}")

    except Exception as e:
        logger.error(f"Failed to save markdown for {url}: {e}", exc_info=True)

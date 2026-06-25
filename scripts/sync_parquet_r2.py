# -*- coding: utf-8 -*-
"""
腳本名稱: scripts/sync_parquet_r2
功能說明: 獨立的 Cloudflare R2 Parquet 歷史資料湖同步 CLI 工具。
          支援下載 (download)、上傳 (upload)、清單 (list) 與驗證 (verify) 操作。
          本地端未設定時會友善提示，但在嚴格模式 (Actions / R2_REQUIRED) 下若 Secrets 不全將直接失敗。
"""
from __future__ import annotations

import argparse
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from src.data.r2_sync import (
    is_r2_configured,
    check_r2_strict_mode,
    download_parquet_from_r2,
    upload_parquet_to_r2,
    verify_r2_upload,
    list_r2_parquet_objects,
)

def run_sync() -> int:
    parser = argparse.ArgumentParser(description="Cloudflare R2 Parquet 歷史資料湖同步工具")
    parser.add_argument(
        "action",
        type=str,
        choices=["download", "upload", "list", "verify"],
        help="執行的操作：download (下載)、upload (上傳)、list (列出物件)、verify (上傳驗證)",
    )
    args = parser.parse_args()

    # 1. 嚴格模式安全檢查
    try:
        check_r2_strict_mode()
    except Exception as e:
        print(f"[Error] {e}", file=sys.stderr)
        return 1

    # 2. 友善提示 (本機且未設定時)
    if not is_r2_configured():
        print("【提示】Cloudflare R2 環境變數設定不完整。跳過 R2 同步流程。")
        print("若需要啟用 R2，請設定 R2_ACCESS_KEY_ID、R2_SECRET_ACCESS_KEY、R2_BUCKET_NAME 與 R2_ENDPOINT_URL 等環境變數。")
        return 0

    action = args.action

    try:
        if action == "list":
            objects = list_r2_parquet_objects()
            print(f"\n--- R2 Bucket 中的 Parquet 物件列表 (共 {len(objects)} 筆) ---")
            for obj in objects:
                print(f"- Key: {obj['Key']} | 大小: {obj['Size']} bytes | 修改時間: {obj['LastModified']}")
            print("----------------------------------------------------------------\n")
            
        elif action == "download":
            download_parquet_from_r2()
            
        elif action == "upload":
            upload_parquet_to_r2()
            
        elif action == "verify":
            verify_r2_upload()

    except Exception as exc:
        print(f"[Error] 執行 {action} 失敗！錯誤: {exc}", file=sys.stderr)
        return 1

    return 0

if __name__ == "__main__":
    sys.exit(run_sync())

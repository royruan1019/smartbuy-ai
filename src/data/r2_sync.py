"""
模組名稱: src.data.r2_sync
功能說明: 提供 Cloudflare R2（S3 相容）資料湖的下載、上傳、清單列出與上傳驗證功能。
          支援 GitHub Actions 嚴格模式，確保 CI/CD 環境下 credential 缺失時能直接拋出例外阻斷流程。

【相關元件 (Related Components)】
- 被依賴: scripts/sync_parquet_r2.py
- 被依賴: scripts/update_agri_price_daily.py
- 被依賴: scripts/backfill_agri_price_history.py
"""
from __future__ import annotations

import os
import boto3
from botocore.config import Config
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[2]
LOCAL_PARQUET_DIR = PROJECT_ROOT / "data" / "history_parquet"

def get_r2_config() -> dict[str, str | None]:
    """
    從環境變數讀取 R2 連線所需設定。
    """
    account_id = os.getenv("R2_ACCOUNT_ID")
    access_key_id = os.getenv("R2_ACCESS_KEY_ID")
    secret_access_key = os.getenv("R2_SECRET_ACCESS_KEY")
    bucket_name = os.getenv("R2_BUCKET_NAME")
    endpoint_url = os.getenv("R2_ENDPOINT_URL")
    parquet_prefix = os.getenv("R2_PARQUET_PREFIX", "history_parquet/agri_price/")

    # 若無 endpoint_url 但有 account_id，自動拼湊 endpoint_url
    if not endpoint_url and account_id:
        endpoint_url = f"https://{account_id}.r2.cloudflarestorage.com"

    return {
        "access_key_id": access_key_id,
        "secret_access_key": secret_access_key,
        "bucket_name": bucket_name,
        "endpoint_url": endpoint_url,
        "parquet_prefix": parquet_prefix,
    }

def is_r2_configured() -> bool:
    """
    判斷 R2 所需之必要連線設定是否齊全。
    """
    config = get_r2_config()
    return bool(
        config["access_key_id"]
        and config["secret_access_key"]
        and config["bucket_name"]
        and config["endpoint_url"]
    )

def check_r2_strict_mode() -> None:
    """
    檢查是否為嚴格模式。
    若 GITHUB_ACTIONS=true 或 R2_REQUIRED=true，則 R2 連線設定必須完整，否則拋出例外。
    """
    is_github_actions = os.getenv("GITHUB_ACTIONS") == "true"
    is_r2_required = os.getenv("R2_REQUIRED") == "true"

    if (is_github_actions or is_r2_required) and not is_r2_configured():
        raise ValueError(
            "【錯誤】目前處於嚴格模式 (GITHUB_ACTIONS=true 或 R2_REQUIRED=true)，"
            "但 Cloudflare R2 的連線 Secrets 設定不完整。請檢查環境變數配置。"
        )

def _get_r2_client():
    """
    建立並回傳 boto3 S3 client。
    """
    config = get_r2_config()
    if not is_r2_configured():
        raise ValueError("R2 設定不完整，無法建立 R2 客戶端。")

    # Cloudflare R2 要求 s3v4 簽名
    s3_config = Config(signature_version="s3v4")

    return boto3.client(
        "s3",
        endpoint_url=config["endpoint_url"],
        aws_access_key_id=config["access_key_id"],
        aws_secret_access_key=config["secret_access_key"],
        config=s3_config,
    )

def list_r2_parquet_objects() -> list[dict]:
    """
    列出 R2 Bucket 中所有符合 Prefix 前綴的 Parquet 物件資訊。

    回傳:
        list[dict]: 包含 Key、Size、LastModified 的清單。
    """
    check_r2_strict_mode()
    if not is_r2_configured():
        print("R2 未配置，跳過列出 R2 物件。")
        return []

    config = get_r2_config()
    bucket_name = config["bucket_name"]
    prefix = config["parquet_prefix"]

    client = _get_r2_client()
    try:
        response = client.list_objects_v2(Bucket=bucket_name, Prefix=prefix)
        objects = response.get("Contents", [])
        # 只保留 .parquet 結尾的物件
        return [obj for obj in objects if obj["Key"].endswith(".parquet")]
    except Exception as e:
        print(f"列出 R2 物件失敗: {e}")
        raise

def download_parquet_from_r2() -> bool:
    """
    從 Cloudflare R2 下載所有已存在的 Parquet 歷史資料檔案至本地。

    回傳:
        bool: 是否下載成功（或無可下載檔案）。
    """
    check_r2_strict_mode()
    if not is_r2_configured():
        print("R2 未配置，跳過從 R2 下載 Parquet 歷史資料。")
        return False

    config = get_r2_config()
    bucket_name = config["bucket_name"]
    prefix = config["parquet_prefix"]

    print("開始從 Cloudflare R2 下載 Parquet 歷史檔案...", flush=True)
    client = _get_r2_client()
    
    LOCAL_PARQUET_DIR.mkdir(parents=True, exist_ok=True)
    objects = list_r2_parquet_objects()

    if not objects:
        print("R2 儲存桶中目前無任何 Parquet 歷史檔案（這可能是全新 Bucket），跳過下載。", flush=True)
        return True

    for obj in objects:
        key = obj["Key"]
        filename = Path(key).name
        local_path = LOCAL_PARQUET_DIR / filename
        
        print(f"正在下載: {key} -> {local_path} ({obj['Size']} bytes)...", flush=True)
        try:
            client.download_file(bucket_name, key, str(local_path))
        except Exception as e:
            print(f"下載檔案 {key} 失敗: {e}")
            raise

    print("R2 Parquet 歷史資料下載完成。", flush=True)
    return True

def upload_parquet_to_r2() -> bool:
    """
    將本地所有的 Parquet 歷史資料檔案上傳並同步至 Cloudflare R2。

    回傳:
        bool: 是否上傳成功。
    """
    check_r2_strict_mode()
    if not is_r2_configured():
        print("R2 未配置，跳過上傳 Parquet 至 R2。")
        return False

    config = get_r2_config()
    bucket_name = config["bucket_name"]
    prefix = config["parquet_prefix"]

    if not LOCAL_PARQUET_DIR.exists():
        print("本地無 Parquet 歷史資料目錄，無須上傳。")
        return True

    parquet_files = list(LOCAL_PARQUET_DIR.glob("*.parquet"))
    if not parquet_files:
        print("本地無任何 .parquet 檔案，無須上傳。")
        return True

    print("開始將本地 Parquet 歷史檔案上傳至 Cloudflare R2...", flush=True)
    client = _get_r2_client()

    for local_path in parquet_files:
        filename = local_path.name
        key = f"{prefix}{filename}"
        
        print(f"正在上傳: {local_path} -> {key} ({local_path.stat().st_size} bytes)...", flush=True)
        try:
            client.upload_file(str(local_path), bucket_name, key)
        except Exception as e:
            print(f"上傳檔案 {filename} 失敗: {e}")
            raise

    print("R2 Parquet 歷史資料上傳完成。", flush=True)
    return True

def verify_r2_upload() -> bool:
    """
    驗證 R2 上已上傳的 Parquet 檔案大小是否與本地端一致。

    回傳:
        bool: 驗證是否完全通過。若不一致或找不到檔案則會拋出例外。
    """
    check_r2_strict_mode()
    if not is_r2_configured():
        print("R2 未配置，跳過上傳驗證。")
        return False

    config = get_r2_config()
    bucket_name = config["bucket_name"]
    prefix = config["parquet_prefix"]

    if not LOCAL_PARQUET_DIR.exists():
        print("本地無 Parquet 歷史資料，無可驗證內容。")
        return True

    parquet_files = list(LOCAL_PARQUET_DIR.glob("*.parquet"))
    if not parquet_files:
        print("本地無任何 .parquet 檔案，無可驗證內容。")
        return True

    print("開始驗證 R2 上傳完整性...", flush=True)
    client = _get_r2_client()

    for local_path in parquet_files:
        filename = local_path.name
        key = f"{prefix}{filename}"
        local_size = local_path.stat().st_size

        try:
            response = client.head_object(Bucket=bucket_name, Key=key)
            r2_size = response.get("ContentLength", 0)

            if local_size != r2_size:
                raise ValueError(
                    f"【驗證失敗】檔案 {filename} 大小不一致！"
                    f"本地端大小: {local_size} bytes，R2 端大小: {r2_size} bytes"
                )
            print(f"驗證通過: {filename} (大小: {r2_size} bytes 一致)", flush=True)
        except Exception as e:
            print(f"驗證檔案 {filename} 時發生錯誤或找不到該 R2 物件: {e}")
            raise

    print("R2 上傳完整性驗證全部通過！", flush=True)
    return True

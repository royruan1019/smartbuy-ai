"""
模組名稱: tests.test_r2_sync
功能說明: 測試 Cloudflare R2 同步客戶端功能。
          使用 unittest.mock 模擬 boto3.client 以驗證嚴格模式、下載、上傳與 Content-Length 大小比對驗證。

【相關元件 (Related Components)】
- 依賴: src.data.r2_sync
"""
from __future__ import annotations

import os
from datetime import date
from pathlib import Path
import pytest
from unittest.mock import MagicMock, patch

import src.data.r2_sync as r2_sync


@pytest.fixture
def clean_r2_env(monkeypatch):
    """確保測試開始時環境變數是乾淨的。"""
    for var in [
        "R2_ACCOUNT_ID",
        "R2_ACCESS_KEY_ID",
        "R2_SECRET_ACCESS_KEY",
        "R2_BUCKET_NAME",
        "R2_ENDPOINT_URL",
        "R2_PARQUET_PREFIX",
        "R2_REQUIRED",
        "GITHUB_ACTIONS",
    ]:
        monkeypatch.delenv(var, raising=False)


@pytest.fixture
def mock_r2_config(monkeypatch):
    """模擬合法的 R2 設定。"""
    monkeypatch.setattr(r2_sync, "get_r2_config", lambda: {
        "access_key_id": "mock_id",
        "secret_access_key": "mock_secret",
        "bucket_name": "mock_bucket",
        "endpoint_url": "https://mock.r2.cloudflarestorage.com",
        "parquet_prefix": "history_parquet/agri_price/",
    })
    monkeypatch.setattr(r2_sync, "is_r2_configured", lambda: True)


def test_is_r2_configured_success(monkeypatch, clean_r2_env):
    """測試當環境變數齊全時，is_r2_configured 傳回 True。"""
    monkeypatch.setattr(r2_sync, "get_r2_config", lambda: {
        "access_key_id": "mock_id",
        "secret_access_key": "mock_secret",
        "bucket_name": "mock_bucket",
        "endpoint_url": "https://mock.r2.cloudflarestorage.com",
        "parquet_prefix": "history_parquet/",
    })
    assert r2_sync.is_r2_configured() is True


def test_is_r2_configured_missing(monkeypatch, clean_r2_env):
    """測試當環境變數缺失時，is_r2_configured 傳回 False。"""
    monkeypatch.setattr(r2_sync, "get_r2_config", lambda: {
        "access_key_id": None,
        "secret_access_key": None,
        "bucket_name": "mock_bucket",
        "endpoint_url": None,
        "parquet_prefix": "history_parquet/",
    })
    assert r2_sync.is_r2_configured() is False


def test_check_r2_strict_mode_github_actions(monkeypatch, clean_r2_env):
    """測試在 GITHUB_ACTIONS 嚴格模式下，若設定不全，check_r2_strict_mode 會拋出例外。"""
    monkeypatch.setenv("GITHUB_ACTIONS", "true")
    # 設定不全
    monkeypatch.setattr(r2_sync, "is_r2_configured", lambda: False)
    with pytest.raises(ValueError, match="嚴格模式"):
        r2_sync.check_r2_strict_mode()


def test_check_r2_strict_mode_r2_required(monkeypatch, clean_r2_env):
    """測試在 R2_REQUIRED 嚴格模式下，若設定不全，check_r2_strict_mode 會拋出例外。"""
    monkeypatch.setenv("R2_REQUIRED", "true")
    # 設定不全
    monkeypatch.setattr(r2_sync, "is_r2_configured", lambda: False)
    with pytest.raises(ValueError, match="嚴格模式"):
        r2_sync.check_r2_strict_mode()


def test_check_r2_strict_mode_local_dev(monkeypatch, clean_r2_env):
    """測試在本機非嚴格模式下，若設定不全，check_r2_strict_mode 應優雅通過不拋出例外。"""
    # 確保兩者皆為 False
    monkeypatch.setenv("GITHUB_ACTIONS", "false")
    monkeypatch.setenv("R2_REQUIRED", "false")
    monkeypatch.setattr(r2_sync, "is_r2_configured", lambda: False)
    
    # 預期不應拋出例外
    r2_sync.check_r2_strict_mode()


@patch("src.data.r2_sync.boto3.client")
def test_download_parquet_from_r2_empty(mock_boto_client, clean_r2_env, mock_r2_config):
    """測試當 R2 Bucket 中無 Parquet 物件時，download_parquet_from_r2 回傳 True。"""
    # Mock S3 Client
    mock_s3 = MagicMock()
    mock_s3.list_objects_v2.return_value = {}  # 傳回空的
    mock_boto_client.return_value = mock_s3

    res = r2_sync.download_parquet_from_r2()
    assert res is True
    mock_s3.list_objects_v2.assert_called_once()
    mock_s3.download_file.assert_not_called()


@patch("src.data.r2_sync.boto3.client")
def test_download_parquet_from_r2_success(mock_boto_client, clean_r2_env, mock_r2_config, monkeypatch, tmp_path):
    """測試從 R2 下載多個 Parquet 檔案成功之流程。"""
    monkeypatch.setattr(r2_sync, "LOCAL_PARQUET_DIR", tmp_path)

    # Mock S3 Client
    mock_s3 = MagicMock()
    mock_s3.list_objects_v2.return_value = {
        "Contents": [
            {"Key": "history_parquet/agri_price/agri_price_2026-05.parquet", "Size": 1200, "LastModified": "date"},
            {"Key": "history_parquet/agri_price/agri_price_2026-06.parquet", "Size": 2500, "LastModified": "date"},
        ]
    }
    mock_boto_client.return_value = mock_s3

    res = r2_sync.download_parquet_from_r2()
    assert res is True
    assert mock_s3.download_file.call_count == 2
    
    # 驗證下載檔案的路徑是否有呼叫
    download_calls = mock_s3.download_file.call_args_list
    assert "agri_price_2026-05.parquet" in download_calls[0][0][2]
    assert "agri_price_2026-06.parquet" in download_calls[1][0][2]


@patch("src.data.r2_sync.boto3.client")
def test_upload_parquet_to_r2_success(mock_boto_client, clean_r2_env, mock_r2_config, monkeypatch, tmp_path):
    """測試將本機 Parquet 檔案成功上傳至 R2。"""
    monkeypatch.setattr(r2_sync, "LOCAL_PARQUET_DIR", tmp_path)

    # 建立本機虛擬的 Parquet 檔案
    file1 = tmp_path / "agri_price_2026-05.parquet"
    file1.write_text("dummy content 1")
    file2 = tmp_path / "agri_price_2026-06.parquet"
    file2.write_text("dummy content 2")

    mock_s3 = MagicMock()
    mock_boto_client.return_value = mock_s3

    res = r2_sync.upload_parquet_to_r2()
    assert res is True
    assert mock_s3.upload_file.call_count == 2


@patch("src.data.r2_sync.boto3.client")
def test_verify_r2_upload_success(mock_boto_client, clean_r2_env, mock_r2_config, monkeypatch, tmp_path):
    """測試比對檔案大小一致時，驗證成功。"""
    monkeypatch.setattr(r2_sync, "LOCAL_PARQUET_DIR", tmp_path)

    # 建立一個測試檔案
    file1 = tmp_path / "agri_price_2026-05.parquet"
    content = "dummy text"
    file1.write_text(content)
    file_size = file1.stat().st_size

    mock_s3 = MagicMock()
    # Mock head_object 返回 ContentLength 一致
    mock_s3.head_object.return_value = {"ContentLength": file_size}
    mock_boto_client.return_value = mock_s3

    res = r2_sync.verify_r2_upload()
    assert res is True
    mock_s3.head_object.assert_called_once_with(
        Bucket="mock_bucket",
        Key="history_parquet/agri_price/agri_price_2026-05.parquet"
    )


@patch("src.data.r2_sync.boto3.client")
def test_verify_r2_upload_failed(mock_boto_client, clean_r2_env, mock_r2_config, monkeypatch, tmp_path):
    """測試比對檔案大小不一致時，驗證失敗並拋出例外。"""
    monkeypatch.setattr(r2_sync, "LOCAL_PARQUET_DIR", tmp_path)

    # 建立一個測試檔案
    file1 = tmp_path / "agri_price_2026-05.parquet"
    file1.write_text("dummy text")

    mock_s3 = MagicMock()
    # Mock head_object 返回不同的 ContentLength
    mock_s3.head_object.return_value = {"ContentLength": 99999}
    mock_boto_client.return_value = mock_s3

    with pytest.raises(ValueError, match="大小不一致"):
        r2_sync.verify_r2_upload()

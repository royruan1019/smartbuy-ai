# -*- coding: utf-8 -*-
"""
單元測試: tests.test_generate_baseline_predictions
功能說明: 測試 scripts/generate_baseline_predictions.py 的 CLI 解析與執行，確保 mock 資料庫寫入。
"""
from __future__ import annotations

import sys
from datetime import date, timedelta
from pathlib import Path
import pandas as pd
import pytest

PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

import scripts.generate_baseline_predictions as script


def test_cli_dry_run_single_mode(monkeypatch):
    """測試單一作物模式下的 dry-run 執行，且 mock 資料庫載入與寫入。"""
    # 1. Mock 歷史資料載入
    fake_history = pd.DataFrame({
        "trans_date": [date(2026, 6, 1) + timedelta(days=i) for i in range(10)],
        "avg_price": [10.0] * 10
    })
    
    monkeypatch.setattr(script, "load_historical_prices_for_ml", lambda **k: fake_history)
    monkeypatch.setattr(script, "load_price_history", lambda **k: pd.DataFrame())
    
    # 2. Mock 寫入 Supabase (不應被呼叫，因為是 dry-run)
    save_called = False
    def mock_save(df):
        nonlocal save_called
        save_called = True
        return len(df)
    monkeypatch.setattr(script, "save_predictions_to_supabase", mock_save)
    
    # 3. 執行 CLI main
    test_args = [
        "generate_baseline_predictions.py",
        "--crop-code", "001",
        "--market-code", "109",
        "--days", "5",
        "--dry-run",
        "--forecast-start-date", "2026-06-23"
    ]
    monkeypatch.setattr(sys, "argv", test_args)
    
    exit_code = script.main()
    
    assert exit_code == 0
    assert not save_called  # 乾跑模式下不應進行資料庫寫入


def test_cli_batch_mode_dry_run(monkeypatch):
    """測試批次 Top N 模式下的 dry-run 執行。"""
    # 1. Mock 最新價格行情
    fake_latest = pd.DataFrame([
        {"crop_code": "001", "crop_name": "高麗菜", "market_code": "109", "market_name": "台北一", "volume": 1000},
        {"crop_code": "002", "crop_name": "小白菜", "market_code": "109", "market_name": "台北一", "volume": 800},
    ])
    monkeypatch.setattr(script, "load_latest_prices", lambda limit: fake_latest)
    
    # 2. Mock 歷史資料 (兩組各有 10 筆資料)
    fake_history = pd.DataFrame({
        "trans_date": [date(2026, 6, 1) + timedelta(days=i) for i in range(10)],
        "avg_price": [15.0] * 10
    })
    
    monkeypatch.setattr(script, "load_historical_prices_for_ml", lambda **k: fake_history)
    
    # 3. 執行批次 CLI
    test_args = [
        "generate_baseline_predictions.py",
        "--top-n", "2",
        "--days", "3",
        "--dry-run",
        "--forecast-start-date", "2026-06-23"
    ]
    monkeypatch.setattr(sys, "argv", test_args)
    
    exit_code = script.main()
    
    assert exit_code == 0


def test_data_update_logs_warning_only(monkeypatch):
    """測試當 data_update_logs 寫入失敗時只列印 warning，不中斷預測寫入流程。"""
    # 模擬 database_url 存在以使 safe_write_update_log 開始連線程序
    monkeypatch.setattr(script, "_load_database_url", lambda: "postgresql://user:pass@localhost/db")
    
    # Mock create_engine 使其拋出例外，模擬資料庫連線失敗
    def mock_create_engine(*args, **kwargs):
        raise RuntimeError("Connection failed")
    monkeypatch.setattr(script, "create_engine", mock_create_engine)
    
    # 確保 safe_write_update_log 被調用時能優雅處理 DB 異常，不拋出 crash
    try:
        script.safe_write_update_log(status="success", rows_inserted=5)
    except Exception as e:
        pytest.fail(f"safe_write_update_log should handle DB errors gracefully, but crashed: {e}")

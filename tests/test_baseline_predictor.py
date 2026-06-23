# -*- coding: utf-8 -*-
"""
單元測試: tests.test_baseline_predictor
功能說明: 測試 baseline_predictor 模組的預測計算、足夠與不足資料處理、三種狀態分類與日期過濾。
"""
from __future__ import annotations

import warnings
from datetime import date, timedelta
import pandas as pd
import pytest

from src.ml.baseline_predictor import predict_next_5_days


def test_predict_insufficient_data():
    """測試當歷史資料少於 7 筆時，跳過預測且回傳空 DataFrame，並發出 warning。"""
    # 建立 6 筆測試資料
    dates = [date(2026, 6, 1) + timedelta(days=i) for i in range(6)]
    prices = [10.0, 12.0, 11.0, 9.0, 10.5, 11.0]
    history_df = pd.DataFrame({"trans_date": dates, "avg_price": prices})
    
    with pytest.warns(UserWarning, match="無法計算 MA7"):
        df_pred = predict_next_5_days(
            history_df=history_df,
            crop_code="001",
            crop_name="高麗菜",
            market_code="109",
            market_name="台北一",
            forecast_start_date=date(2026, 6, 10),
            days=5,
        )
        
    assert df_pred.empty
    assert list(df_pred.columns) == [
        "predict_date", "crop_code", "crop_name", "market_code", "market_name",
        "predicted_price", "predicted_status"
    ]


def test_predict_with_7_to_29_records():
    """測試有效歷史紀錄在 7~29 筆時，使用全體均值作為比較基準。"""
    # 建立 10 筆測試資料
    dates = [date(2026, 6, 1) + timedelta(days=i) for i in range(10)]
    # 平均價格為 10.0
    prices = [10.0] * 10
    # 最近 7 筆價格設為 8.0（比全體均值 10.0 低 20% => cheap 便宜）
    # prices: [10.0, 10.0, 10.0, 8.0, 8.0, 8.0, 8.0, 8.0, 8.0, 8.0]
    prices[3:] = [8.0] * 7
    
    history_df = pd.DataFrame({"trans_date": dates, "avg_price": prices})
    
    df_pred = predict_next_5_days(
        history_df=history_df,
        crop_code="001",
        crop_name="高麗菜",
        market_code="109",
        market_name="台北一",
        forecast_start_date=date(2026, 6, 23),
        days=5,
    )
    
    assert len(df_pred) == 5
    assert (df_pred["predicted_price"] == 8.0).all()
    # 全體均值 = (10*3 + 8*7) / 10 = 8.6
    # 預測價格 8.0 / 8.6 = 0.93 (正常區間 0.9~1.1 內) -> 應為 normal
    assert (df_pred["predicted_status"] == "normal").all()

    # 調整最近 7 筆為 5.0，全體均值 = (10*3 + 5*7)/10 = 6.5
    # 預測價格 5.0 / 6.5 = 0.76 (< 0.9) -> 應為 cheap
    prices[3:] = [5.0] * 7
    history_df_cheap = pd.DataFrame({"trans_date": dates, "avg_price": prices})
    df_pred_cheap = predict_next_5_days(
        history_df=history_df_cheap,
        crop_code="001",
        crop_name="高麗菜",
        market_code="109",
        market_name="台北一",
        forecast_start_date=date(2026, 6, 23),
        days=5,
    )
    assert (df_pred_cheap["predicted_status"] == "cheap").all()


def test_predict_with_30_plus_records():
    """測試有效歷史紀錄在 30 筆以上時，使用最近 30 筆均值作為比較基準。"""
    # 建立 40 筆測試資料
    dates = [date(2026, 6, 1) + timedelta(days=i) for i in range(40)]
    
    # 前 10 筆為極高價格 100.0 (應該被 30 天移動平均排除)
    # 後 30 筆價格為 10.0，最近 7 筆為 12.0
    prices = [100.0] * 10 + [10.0] * 23 + [12.0] * 7
    
    history_df = pd.DataFrame({"trans_date": dates, "avg_price": prices})
    
    df_pred = predict_next_5_days(
        history_df=history_df,
        crop_code="001",
        crop_name="高麗菜",
        market_code="109",
        market_name="台北一",
        forecast_start_date=date(2026, 6, 23),
        days=5,
    )
    
    # MA7 = 12.0
    # MA30 = (10.0 * 23 + 12.0 * 7) / 30 = 10.46
    # 12.0 / 10.46 = 1.147 (> 1.1) -> 應為 expensive 偏貴
    assert len(df_pred) == 5
    assert (df_pred["predicted_price"] == 12.0).all()
    assert (df_pred["predicted_status"] == "expensive").all()


def test_predict_invalid_records_handling():
    """測試自動排除 avg_price 為 NULL 或小於等於 0 的異常數據。"""
    # 建立含有 NULL、0、負數的 10 筆資料
    dates = [date(2026, 6, 1) + timedelta(days=i) for i in range(10)]
    prices = [10.0, None, -5.0, 10.0, 0.0, 10.0, 10.0, 10.0, 10.0, 10.0]
    # 清理後只剩下 10.0 的 7 筆有效紀錄
    history_df = pd.DataFrame({"trans_date": dates, "avg_price": prices})
    
    df_pred = predict_next_5_days(
        history_df=history_df,
        crop_code="001",
        crop_name="高麗菜",
        market_code="109",
        market_name="台北一",
        forecast_start_date=date(2026, 6, 23),
        days=5,
    )
    
    assert len(df_pred) == 5
    assert (df_pred["predicted_price"] == 10.0).all()
    assert (df_pred["predicted_status"] == "normal").all()


def test_predict_date_bounds():
    """測試產生的預測日期不早於今日。"""
    # 測試 forecast_start_date 早於今日的情況下，應自動推遲到今日開始
    dates = [date(2026, 6, 1) + timedelta(days=i) for i in range(10)]
    prices = [10.0] * 10
    history_df = pd.DataFrame({"trans_date": dates, "avg_price": prices})
    
    past_date = date.today() - timedelta(days=5)
    
    df_pred = predict_next_5_days(
        history_df=history_df,
        crop_code="001",
        crop_name="高麗菜",
        market_code="109",
        market_name="台北一",
        forecast_start_date=past_date,
        days=3,
    )
    
    # 預期預測日期從今日開始
    pred_dates = df_pred["predict_date"].tolist()
    assert len(pred_dates) == 3
    assert pred_dates[0] == date.today()
    assert pred_dates[1] == date.today() + timedelta(days=1)
    assert pred_dates[2] == date.today() + timedelta(days=2)

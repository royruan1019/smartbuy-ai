from src.data.report_store import add_price_report, classify_price_gap


def test_gap_labels():
    assert classify_price_gap(0.05) == "接近行情"
    assert classify_price_gap(0.20) == "稍高"
    assert classify_price_gap(0.40) == "可能買貴"


def test_report_is_appended(tmp_path):
    path = tmp_path / "reports.csv"
    result = add_price_report("高麗菜", 60, "測試市場", path=path)
    assert path.exists()
    assert result["status"] == "待確認"
    assert "高麗菜" in path.read_text(encoding="utf-8-sig")


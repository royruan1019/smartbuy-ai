from src.calendar.solar_terms import get_today_solar_term_advice


def test_summer_solstice_boundary():
    assert get_today_solar_term_advice("2026-06-20")["term_name"] == "芒種"
    assert get_today_solar_term_advice("2026-06-21")["term_name"] == "夏至"


def test_early_january_wraps_to_previous_last_term():
    assert get_today_solar_term_advice("2026-01-01")["term_name"] == "冬至"


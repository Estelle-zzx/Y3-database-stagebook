from streamlit.testing.v1 import AppTest


def test_trip_page_controls_missing_route_and_conflicts(tmp_path):
    script = '''
import pandas as pd
from unittest.mock import patch
import app
events = pd.DataFrame([
    dict(performance_id=1, title="测试剧目甲", version="original", category="话剧", language="普通话", district="黄浦区",
         theater_id=1, theater_name="剧场甲", start_time=pd.Timestamp("2026-12-01 19:30"), end_time=pd.Timestamp("2026-12-01 21:30"),
         restaurant_name=None, restaurant_category=None, price_tier=None, avg_price=None, distance_m=None,
         transport_type="subway", estimated_time=30, estimated_cost=5, suitable_district="静安区"),
    dict(performance_id=2, title="测试剧目乙", version="original", category="话剧", language="普通话", district="徐汇区",
         theater_id=2, theater_name="剧场乙", start_time=pd.Timestamp("2026-12-01 21:00"), end_time=pd.Timestamp("2026-12-01 23:00"),
         restaurant_name=None, restaurant_category=None, price_tier=None, avg_price=None, distance_m=None,
         transport_type=None, estimated_time=None, estimated_cost=None, suitable_district=None),
])
with patch.object(app, "query_df", side_effect=[pd.DataFrame(), events]):
    app.page_trip_assistance(None, 1)
'''
    script_path = tmp_path / "trip_page.py"
    script_path.write_text(script, encoding="utf-8")
    at = AppTest.from_file(str(script_path)).run()
    assert not at.exception
    assert len(at.warning) == 1
    assert "时间重叠" in at.warning[0].value
    assert any("无法估算" in node.value for node in at.markdown)
    assert any("18:45" in node.value for node in at.markdown)
    at.number_input[0].set_value(30).run()
    assert not at.exception
    assert any("18:15" in node.value for node in at.markdown)
    assert len(at.get("download_button")) == 1


def test_empty_trip_page():
    at = AppTest.from_string('''
import pandas as pd
from unittest.mock import patch
import app
with patch.object(app, "query_df", return_value=pd.DataFrame()):
    app.page_trip_assistance(None, 1)
''').run()
    assert not at.exception
    assert len(at.info) == 1
    assert len(at.get("download_button")) == 0

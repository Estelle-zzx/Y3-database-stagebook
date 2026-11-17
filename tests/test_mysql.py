"""Set STAGEBOOK_TEST_URL only to a disposable database loaded with demo SQL."""
import os
from concurrent.futures import ThreadPoolExecutor
from uuid import uuid4

import pytest
from sqlalchemy import create_engine, event, text
from services import set_calendar_status, refresh_profile_recommendations, delete_catalog_item

pytestmark = pytest.mark.mysql


@pytest.fixture
def db():
    url = os.environ.get("STAGEBOOK_TEST_URL")
    if not url:
        pytest.skip("STAGEBOOK_TEST_URL is not set")
    engine = create_engine(url, pool_pre_ping=True)
    with engine.begin() as conn:
        uid = conn.execute(text("INSERT INTO `User`(username,nickname,city) VALUES(:name,'test','上海')"),
                           {"name": f"test_{uuid4().hex}"}).lastrowid
        pid = conn.execute(text("INSERT INTO Performance(production_id,theater_id,start_time,end_time,price_min,price_max) "
                                "SELECT production_id,theater_id,NOW()+INTERVAL 2 DAY,NOW()+INTERVAL 2 DAY+INTERVAL 2 HOUR,100,200 "
                                "FROM Performance LIMIT 1")).lastrowid
    yield engine, int(uid), int(pid)
    with engine.begin() as conn:
        conn.execute(text("DELETE FROM Profile_Recommendation_Result WHERE user_id=:uid OR performance_id=:pid"), {"uid": uid, "pid": pid})
        conn.execute(text("DELETE FROM `User` WHERE user_id=:uid"), {"uid": uid})
        conn.execute(text("DELETE FROM Performance WHERE performance_id=:pid"), {"pid": pid})
    engine.dispose()


def state(engine, uid, pid):
    with engine.connect() as conn:
        plan = conn.execute(text("SELECT status FROM Planned_Performance WHERE user_id=:uid AND performance_id=:pid"), {"uid": uid, "pid": pid}).scalar()
        watch = conn.execute(text("SELECT score FROM Watch_Record WHERE user_id=:uid AND performance_id=:pid"), {"uid": uid, "pid": pid}).scalars().all()
    return plan, watch


def finish(engine, pid):
    with engine.begin() as conn:
        conn.execute(text("UPDATE Performance SET start_time=NOW()-INTERVAL 3 HOUR,end_time=NOW()-INTERVAL 1 HOUR WHERE performance_id=:pid"), {"pid": pid})


def test_calendar_lifecycle_and_user_isolation(db):
    engine, uid, pid = db
    set_calendar_status(engine, uid, pid, "planned", add_only=True)
    with pytest.raises(ValueError, match="已经"):
        set_calendar_status(engine, uid, pid, "planned", add_only=True)
    set_calendar_status(engine, uid, pid, "booked")
    assert state(engine, uid, pid) == ("booked", [])
    with pytest.raises(ValueError, match="结束后"):
        set_calendar_status(engine, uid, pid, "watched", 8)
    finish(engine, pid)
    set_calendar_status(engine, uid, pid, "watched", 8)
    set_calendar_status(engine, uid, pid, "watched", 9)
    assert state(engine, uid, pid) == (None, [9])
    with pytest.raises(ValueError, match="已开始"):
        set_calendar_status(engine, uid, pid, "planned")
    assert state(engine, uid, pid) == (None, [9])
    set_calendar_status(engine, 1, pid, "canceled")
    assert state(engine, uid, pid) == (None, [9])
    set_calendar_status(engine, uid, pid, "canceled")
    assert state(engine, uid, pid) == (None, [])


def test_failure_rolls_back_both_tables(db):
    engine, uid, pid = db
    finish(engine, pid)
    set_calendar_status(engine, uid, pid, "watched", 8)
    def fail_after_watch_delete(conn, cursor, statement, parameters, context, executemany):
        if statement.startswith("DELETE FROM Planned_Performance"):
            raise RuntimeError("simulated second-statement failure")
    event.listen(engine, "before_cursor_execute", fail_after_watch_delete)
    try:
        with pytest.raises(RuntimeError):
            set_calendar_status(engine, uid, pid, "canceled")
    finally:
        event.remove(engine, "before_cursor_execute", fail_after_watch_delete)
    assert state(engine, uid, pid) == (None, [8])


def test_concurrent_adds_create_one_plan(db):
    engine, uid, pid = db
    def add():
        try:
            set_calendar_status(engine, uid, pid, "planned", add_only=True)
            return "added"
        except ValueError:
            return "duplicate"
    with ThreadPoolExecutor(max_workers=2) as pool:
        results = list(pool.map(lambda _: add(), range(2)))
    assert sorted(results) == ["added", "duplicate"]
    assert state(engine, uid, pid) == ("planned", [])


def test_recommendation_cache_commits_and_connection_is_reusable(db):
    engine, uid, pid = db
    result = refresh_profile_recommendations(engine, uid)
    assert not result.empty
    with engine.connect() as conn:
        count = conn.execute(text("SELECT COUNT(*) FROM Profile_Recommendation_Result WHERE user_id=:uid"), {"uid": uid}).scalar()
        assert count == len(result)
        assert conn.execute(text("SELECT 1")).scalar() == 1
    again = refresh_profile_recommendations(engine, uid)
    assert len(again) == len(result)


@pytest.mark.parametrize("status,score", [("invalid", None), ("watched", -1), ("watched", float("nan"))])
def test_invalid_input_does_not_write(db, status, score):
    engine, uid, pid = db
    with pytest.raises(ValueError):
        set_calendar_status(engine, uid, pid, status, score)
    assert state(engine, uid, pid) == (None, [])


def test_demo_account_rerun_preserves_profile_and_password(db):
    import app
    engine, _, _ = db
    app.ensure_auth_table(engine)
    app.ensure_teacher_test_accounts(engine)
    with engine.begin() as conn:
        conn.execute(text("UPDATE `User` SET price_preference='premium',home_district='徐汇区' WHERE username='Estelle'"))
        before = conn.execute(text("SELECT a.password_hash FROM StageBook_App_Account a JOIN `User` u ON a.user_id=u.user_id WHERE u.username='Estelle'")).scalar_one()
    app.ensure_teacher_test_accounts(engine)
    with engine.connect() as conn:
        after = conn.execute(text("SELECT u.price_preference,u.home_district,a.password_hash FROM StageBook_App_Account a JOIN `User` u ON a.user_id=u.user_id WHERE u.username='Estelle'")).one()
    assert tuple(after) == ("premium", "徐汇区", before)


def test_account_deletion_after_recommendation_refresh(db):
    import app
    engine, uid, _ = db
    refresh_profile_recommendations(engine, uid)
    app.delete_current_account(engine, uid)
    with engine.connect() as conn:
        assert conn.execute(text("SELECT COUNT(*) FROM `User` WHERE user_id=:uid"), {"uid": uid}).scalar() == 0
        assert conn.execute(text("SELECT COUNT(*) FROM Profile_Recommendation_Result WHERE user_id=:uid"), {"uid": uid}).scalar() == 0


def test_recommendation_and_trip_pages_with_mysql(db):
    from streamlit.testing.v1 import AppTest
    engine, uid, pid = db
    set_calendar_status(engine, uid, pid, "planned")
    for page in ("page_recommendations", "page_trip_assistance"):
        at = AppTest.from_string(f'''
import os
from sqlalchemy import create_engine
import app
engine = create_engine(os.environ["STAGEBOOK_TEST_URL"])
try:
    app.{page}(engine, {uid})
finally:
    engine.dispose()
''').run(timeout=20)
        assert not at.exception
        assert not at.error
        if page == "page_trip_assistance":
            assert len(at.get("download_button")) == 1


def test_delete_performance_cleans_recommendation_cache(db):
    engine, uid, pid = db
    result = refresh_profile_recommendations(engine, uid)
    assert pid in result["performance_id"].tolist()
    delete_catalog_item(engine, "Performance", pid)
    with engine.connect() as conn:
        assert conn.execute(text("SELECT COUNT(*) FROM Performance WHERE performance_id=:pid"), {"pid": pid}).scalar() == 0
        assert conn.execute(text("SELECT COUNT(*) FROM Profile_Recommendation_Result WHERE performance_id=:pid"), {"pid": pid}).scalar() == 0

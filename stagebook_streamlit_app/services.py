"""Transactional calendar operations, independent of Streamlit rendering."""
from math import isfinite

import pandas as pd
from sqlalchemy import text
from sqlalchemy.engine import Engine


def delete_catalog_item(engine: Engine, table: str, item_id: int) -> None:
    """Remove derived recommendation rows before deleting a show/production."""
    keys = {"Performance": "performance_id", "Production": "production_id"}
    if table not in keys:
        raise ValueError("不支持的删除对象。")
    column = keys[table]
    with engine.begin() as conn:
        conn.execute(text(
            "DELETE FROM Profile_Recommendation_Result WHERE performance_id IN "
            f"(SELECT performance_id FROM Performance WHERE {column}=:id)"
        ), {"id": item_id})
        conn.execute(text(f"DELETE FROM {table} WHERE {column}=:id"), {"id": item_id})


def set_calendar_status(engine: Engine, user_id: int, performance_id: int,
                        status: str, score: float | None = None,
                        *, add_only: bool = False) -> None:
    """Serialize one user's edits and commit both calendar tables together."""
    if status not in {"planned", "booked", "watched", "canceled"}:
        raise ValueError("不支持的观演状态。")
    if score is not None and (not isfinite(float(score)) or not 0 <= score <= 10):
        raise ValueError("评分必须在 0 到 10 之间。")
    params = {"uid": int(user_id), "pid": int(performance_id), "status": status, "score": score}
    with engine.begin() as conn:
        # Every calendar write in the application takes this lock first. This
        # also serializes inserts when neither calendar table has a row yet.
        user = conn.execute(text("SELECT user_id FROM `User` WHERE user_id=:uid FOR UPDATE"), params).first()
        if user is None:
            raise ValueError("用户不存在。")
        performance = conn.execute(text(
            "SELECT start_time, end_time, NOW() AS db_now FROM Performance "
            "WHERE performance_id=:pid FOR UPDATE"), params).mappings().first()
        if performance is None:
            raise ValueError("场次不存在。")
        planned = conn.execute(text("SELECT 1 FROM Planned_Performance WHERE user_id=:uid AND performance_id=:pid"), params).first()
        watched = conn.execute(text("SELECT 1 FROM Watch_Record WHERE user_id=:uid AND performance_id=:pid"), params).first()
        if add_only and (planned or watched):
            raise ValueError("这个场次已经在你的计划或记录中，请使用状态管理修改。")
        if status in {"planned", "booked"} and performance["start_time"] <= performance["db_now"]:
            raise ValueError("已开始的场次不能加入计划。")
        if status == "watched" and performance["end_time"] > performance["db_now"]:
            raise ValueError("演出结束后才能记录为已观看。")

        if status == "watched":
            params["watch_date"] = performance["start_time"].date()
            if watched:
                conn.execute(text("UPDATE Watch_Record SET watch_date=:watch_date, score=:score "
                                  "WHERE user_id=:uid AND performance_id=:pid"), params)
            else:
                conn.execute(text("INSERT INTO Watch_Record(user_id, performance_id, watch_date, score) "
                                  "VALUES(:uid, :pid, :watch_date, :score)"), params)
            conn.execute(text("DELETE FROM Planned_Performance WHERE user_id=:uid AND performance_id=:pid"), params)
        else:
            conn.execute(text("DELETE FROM Watch_Record WHERE user_id=:uid AND performance_id=:pid"), params)
            if status == "canceled":
                conn.execute(text("DELETE FROM Planned_Performance WHERE user_id=:uid AND performance_id=:pid"), params)
            elif planned:
                conn.execute(text("UPDATE Planned_Performance SET status=:status WHERE user_id=:uid AND performance_id=:pid"), params)
            else:
                conn.execute(text("INSERT INTO Planned_Performance(user_id, performance_id, status) "
                                  "VALUES(:uid, :pid, :status)"), params)


def refresh_profile_recommendations(engine: Engine, user_id: int) -> pd.DataFrame:
    """Drain CALL results before committing its cache writes (mysqlconnector)."""
    connection = engine.raw_connection()
    cursor = None
    try:
        cursor = connection.cursor()
        cursor.execute("SELECT user_id FROM `User` WHERE user_id=%s FOR UPDATE", (int(user_id),))
        if cursor.fetchone() is None:
            raise ValueError("用户不存在。")
        cursor.execute("CALL sp_recommend_by_profile(%s)", (int(user_id),))
        frame = pd.DataFrame()
        while True:
            if cursor.description is not None:
                frame = pd.DataFrame(cursor.fetchall(), columns=cursor.column_names)
            if not cursor.nextset():
                break
        connection.commit()
        return frame
    except Exception:
        connection.rollback()
        raise
    finally:
        if cursor is not None:
            cursor.close()
        connection.close()

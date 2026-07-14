# -*- coding: utf-8 -*-
"""
StageBook 可视化展示界面
运行方式：
    streamlit run app.py

前提：
1. MySQL 已启动；
2. 已依次执行 main_code.sql 和 StageBook_insert_data.sql；
3. 已安装 requirements.txt 中的依赖。
"""

from __future__ import annotations

from dataclasses import dataclass
from datetime import date, datetime, time
import calendar
import html
from typing import Any
import hashlib
import hmac
import os
import time as _time

import altair as alt
import pandas as pd
import streamlit as st
from sqlalchemy import create_engine, text
from sqlalchemy.engine import Engine, URL
from sqlalchemy.exc import SQLAlchemyError


# =========================
# 页面基础设置
# =========================

st.set_page_config(
    page_title="StageBook 观剧记录与推荐系统",
    page_icon="🎭",
    layout="wide",
    initial_sidebar_state="expanded",
)

CUSTOM_CSS = """
<style>
:root {
    --stagebook-bg: #f8f5f0;
    --stagebook-card: #ffffff;
    --stagebook-text-soft: #6b6258;
    --stagebook-main: #6d3b47;
    --stagebook-accent: #b08b57;
}
.block-container {
    padding-top: 1.3rem;
    padding-bottom: 2rem;
}
.stage-title {
    font-size: 2.2rem;
    font-weight: 800;
    letter-spacing: -0.03em;
    margin: 0 0 0.35rem 0;
    line-height: 1.45;
    padding-top: 0.5rem;
    padding-bottom: 0.15rem;
    overflow: visible !important;
}
.stage-subtitle {
    color: #6b6258;
    font-size: 1.02rem;
    margin-bottom: 1.1rem;
}
.card {
    background: #ffffff;
    border: 1px solid rgba(109, 59, 71, 0.12);
    border-radius: 18px;
    padding: 1.05rem 1.15rem;
    box-shadow: 0 8px 22px rgba(49, 37, 29, 0.045);
    margin-bottom: 0.8rem;
}
.card h3 {
    margin-top: 0;
    margin-bottom: 0.4rem;
}
.soft {
    color: #6b6258;
}
.badge {
    display: inline-block;
    padding: 0.18rem 0.48rem;
    border-radius: 999px;
    background: rgba(176, 139, 87, 0.16);
    color: #6d3b47;
    font-size: 0.78rem;
    font-weight: 700;
    margin-right: 0.25rem;
}
.badge-red {
    background: rgba(109, 59, 71, 0.14);
    color: #6d3b47;
}
.badge-green {
    background: rgba(60, 128, 94, 0.14);
    color: #2d6c4c;
}
.small-note {
    font-size: 0.86rem;
    color: #6b6258;
}
hr {
    margin-top: 0.8rem;
    margin-bottom: 0.8rem;
}

.perf-grid {display:grid; grid-template-columns: repeat(auto-fit, minmax(280px, 1fr)); gap: 1rem; margin-top: .75rem;}
.perf-card {background: linear-gradient(145deg, #fff, #fbf6ed); border: 1px solid rgba(109,59,71,.14); border-radius: 20px; padding: 1rem 1.05rem; box-shadow: 0 10px 24px rgba(49,37,29,.06);}
.perf-card h3 {margin:0 0 .4rem 0; font-size:1.16rem;}
.perf-meta {color:#6b6258; font-size:.92rem; line-height:1.75;}
.calendar-wrap {background:#fff; border:1px solid rgba(109,59,71,.12); border-radius:22px; padding:1rem; box-shadow:0 8px 22px rgba(49,37,29,.045);}
.week-head {font-weight:800; text-align:center; color:#6d3b47; padding:.3rem 0;}
.day-cell {min-height:118px; border-radius:18px; padding:.55rem; background:linear-gradient(180deg,#fff,#faf7f1); border:1px solid rgba(176,139,87,.20); margin-bottom:.45rem;}
.day-muted {opacity:.38; background:#f7f4ef;}
.day-num {font-size:1.05rem; font-weight:800; color:#6d3b47;}
.event-pill {display:block; margin-top:.32rem; padding:.28rem .42rem; border-radius:10px; font-size:.78rem; line-height:1.25; white-space:nowrap; overflow:hidden; text-overflow:ellipsis;}
.event-watched {background:rgba(60,128,94,.16); color:#235d41;}
.event-planned {background:rgba(75,117,184,.14); color:#244f87;}
.event-booked {background:rgba(176,139,87,.20); color:#75562a;}
.event-canceled {background:rgba(145,75,75,.13); color:#7b3030;}
.action-hint {background:rgba(176,139,87,.12); border:1px dashed rgba(109,59,71,.25); border-radius:16px; padding:.8rem; color:#6b6258;}
.trip-title {font-size:1.12rem; font-weight:850; color:#6d3b47;}

.hero-card {background: linear-gradient(135deg, #fff8ed 0%, #ffffff 52%, #f8eef1 100%); border:1px solid rgba(109,59,71,.13); border-radius:26px; padding:1.35rem 1.5rem; box-shadow:0 12px 30px rgba(49,37,29,.06); margin-bottom:1rem;}
.hero-kicker {font-size:.88rem; font-weight:800; color:#b08b57; letter-spacing:.08em; text-transform:uppercase;}
.hero-name {font-size:1.95rem; font-weight:900; color:#6d3b47; margin:.15rem 0 .25rem 0;}
.home-grid {display:grid; grid-template-columns:repeat(auto-fit, minmax(250px,1fr)); gap: .85rem;}
.timeline-card {background:#fff; border:1px solid rgba(176,139,87,.18); border-left:6px solid rgba(176,139,87,.55); border-radius:18px; padding:.8rem .95rem; margin-bottom:.65rem; box-shadow:0 8px 18px rgba(49,37,29,.04);}
.timeline-card b {color:#6d3b47;}
.status-strip {display:flex; flex-wrap:wrap; gap:.5rem; margin:.4rem 0 .8rem 0;}
.status-chip {display:inline-flex; align-items:center; gap:.35rem; padding:.4rem .65rem; border-radius:999px; background:rgba(176,139,87,.14); color:#6d3b47; font-weight:750; font-size:.86rem;}
.preference-row {display:flex; justify-content:space-between; align-items:center; gap:.75rem; padding:.55rem .65rem; border:1px solid rgba(109,59,71,.1); border-radius:14px; background:#fff; margin:.35rem 0;}
.clean-detail {font-size:.86rem; color:#6b6258; line-height:1.65;}
.perform-time-card {background:#fff; border:1px solid rgba(109,59,71,.10); border-radius:18px; padding:.85rem .95rem; margin-bottom:.75rem; box-shadow:0 8px 18px rgba(49,37,29,.035);}

</style>
"""
st.markdown(CUSTOM_CSS, unsafe_allow_html=True)


# =========================
# 数据库连接
# =========================

@dataclass(frozen=True)
class DBConfig:
    host: str
    port: int
    user: str
    password: str
    database: str


def _secret_or_default(path: list[str], default: Any) -> Any:
    """从 st.secrets 读取配置，失败则返回默认值。"""
    try:
        value: Any = st.secrets
        for key in path:
            value = value[key]
        return value
    except Exception:
        return default


def sidebar_db_config() -> DBConfig:
    """侧边栏数据库配置。优先显示 secrets 中的默认值，也允许现场修改。"""
    st.sidebar.markdown("### 数据库连接")

    default_host = _secret_or_default(["mysql", "host"], "localhost")
    default_port = int(_secret_or_default(["mysql", "port"], 3306))
    default_user = _secret_or_default(["mysql", "user"], "root")
    default_password = _secret_or_default(["mysql", "password"], "")
    default_database = _secret_or_default(["mysql", "database"], "StageBook")

    # 方案 C：本地有 secrets.toml 时自动带入；没有 secrets.toml 时展开连接参数，便于老师现场输入 MySQL 密码。
    with st.sidebar.expander("连接参数", expanded=(default_password == "")):
        if default_password == "":
            st.caption("未检测到 .streamlit/secrets.toml，可在这里填写本机 MySQL 连接信息。")
        else:
            st.caption("已从 .streamlit/secrets.toml 读取默认连接信息，也可在这里临时修改。")
        host = st.text_input("Host", value=default_host)
        port = st.number_input("Port", min_value=1, max_value=65535, value=default_port, step=1)
        user = st.text_input("User", value=default_user)
        password = st.text_input("Password", value=default_password, type="password")
        database = st.text_input("Database", value=default_database)

    return DBConfig(
        host=host.strip(),
        port=int(port),
        user=user.strip(),
        password=password,
        database=database.strip(),
    )


@st.cache_resource(show_spinner=False)
def get_engine(host: str, port: int, user: str, password: str, database: str) -> Engine:
    # 用 URL.create 而不是手动拼接字符串，可正确处理密码里的 @/#/% 等特殊字符。
    url = URL.create(
        drivername="mysql+mysqlconnector",
        username=user,
        password=password,
        host=host,
        port=port,
        database=database,
        query={"charset": "utf8mb4"},
    )
    return create_engine(url, pool_pre_ping=True, pool_recycle=3600, future=True)


def engine_from_config(config: DBConfig) -> Engine | None:
    try:
        engine = get_engine(config.host, config.port, config.user, config.password, config.database)
        with engine.connect() as conn:
            conn.execute(text("SELECT 1"))
        return engine
    except Exception as exc:
        st.error("数据库连接失败。请确认 MySQL 已启动，并且已执行 main_code.sql。")
        st.caption(str(exc))
        return None


def query_df(engine: Engine, sql: str, params: dict[str, Any] | None = None) -> pd.DataFrame:
    with engine.connect() as conn:
        return pd.read_sql(text(sql), conn, params=params or {})


def execute_sql(engine: Engine, sql: str, params: dict[str, Any] | None = None) -> None:
    with engine.begin() as conn:
        conn.execute(text(sql), params or {})


def call_profile_recommendation(engine: Engine, user_id: int) -> pd.DataFrame:
    # MySQL CALL 会返回结果集；这里用 read_sql 直接拿存储过程返回的推荐表。
    with engine.connect() as conn:
        return pd.read_sql(text("CALL sp_recommend_by_profile(:uid)"), conn, params={"uid": user_id})



# =========================
# 登录注册与账号体系
# =========================

AUTH_TABLE = "StageBook_App_Account"


def ensure_auth_table(engine: Engine) -> None:
    """创建前端登录账号表。业务用户仍然存在 User 表中，本表只保存密码哈希和登录状态。"""
    create_sql = f"""
    CREATE TABLE IF NOT EXISTS {AUTH_TABLE} (
        account_id INT AUTO_INCREMENT PRIMARY KEY,
        user_id INT NOT NULL UNIQUE,
        password_salt VARCHAR(64) NOT NULL,
        password_hash VARCHAR(128) NOT NULL,
        is_active TINYINT(1) NOT NULL DEFAULT 1,
        created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
        last_login DATETIME NULL,
        CONSTRAINT fk_stagebook_app_account_user
            FOREIGN KEY (user_id) REFERENCES `User`(user_id)
            ON DELETE CASCADE
    ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;
    """
    execute_sql(engine, create_sql)


def hash_password(password: str, salt_hex: str | None = None) -> tuple[str, str]:
    """PBKDF2-HMAC-SHA256 密码哈希。返回 salt_hex, hash_hex。"""
    if salt_hex is None:
        salt = os.urandom(16)
        salt_hex = salt.hex()
    else:
        salt = bytes.fromhex(salt_hex)

    digest = hashlib.pbkdf2_hmac(
        "sha256",
        password.encode("utf-8"),
        salt,
        200_000,
    )
    return salt_hex, digest.hex()


def verify_password(password: str, salt_hex: str, expected_hash: str) -> bool:
    _, actual_hash = hash_password(password, salt_hex=salt_hex)
    return hmac.compare_digest(actual_hash, expected_hash)


def login_user(engine: Engine, username: str, password: str) -> tuple[bool, str]:
    """校验账号密码，成功后写入 st.session_state。"""
    df = query_df(
        engine,
        f"""
        SELECT
            a.user_id,
            a.password_salt,
            a.password_hash,
            a.is_active,
            u.username,
            u.nickname,
            u.city,
            u.role,
            u.price_preference,
            u.time_preference,
            u.home_district
        FROM {AUTH_TABLE} a
        JOIN `User` u ON a.user_id = u.user_id
        WHERE u.username = :username
        LIMIT 1
        """,
        {"username": username.strip()},
    )

    if df.empty:
        return False, "账号不存在，或尚未初始化登录账号。"

    row = df.iloc[0]
    if int(row["is_active"]) != 1:
        return False, "该账号已被停用。"

    if not verify_password(password, row["password_salt"], row["password_hash"]):
        return False, "密码错误。"

    execute_sql(
        engine,
        f"UPDATE {AUTH_TABLE} SET last_login = NOW() WHERE user_id = :uid",
        {"uid": int(row["user_id"])},
    )

    st.session_state["auth_user"] = {
        "user_id": int(row["user_id"]),
        "username": str(row["username"]),
        "nickname": str(row["nickname"]),
        "city": str(row["city"]),
        "role": str(row["role"]),
        "price_preference": str(row["price_preference"]),
        "time_preference": str(row["time_preference"]),
        "home_district": str(row["home_district"]),
    }
    return True, "登录成功。"


def logout_user() -> None:
    st.session_state.pop("auth_user", None)


def register_user(
    engine: Engine,
    username: str,
    nickname: str,
    password: str,
    city: str,
    price_preference: str,
    time_preference: str,
    home_district: str,
) -> tuple[bool, str]:
    """注册普通用户。管理员账号不通过注册入口创建。"""
    username = username.strip()
    nickname = nickname.strip()
    city = city.strip() or "上海"

    if not username or not nickname or not password:
        return False, "用户名、昵称和密码不能为空。"
    if len(password) < 6:
        return False, "密码至少需要 6 位。"

    exists = query_df(
        engine,
        "SELECT user_id FROM `User` WHERE username = :username LIMIT 1",
        {"username": username},
    )
    if not exists.empty:
        return False, "用户名已存在。"

    salt_hex, password_hash = hash_password(password)

    try:
        with engine.begin() as conn:
            result = conn.execute(
                text(
                    """
                    INSERT INTO `User`(
                        username, nickname, city,
                        price_preference, time_preference, home_district, role
                    )
                    VALUES(
                        :username, :nickname, :city,
                        :price_preference, :time_preference, :home_district, 'user'
                    )
                    """
                ),
                {
                    "username": username,
                    "nickname": nickname,
                    "city": city,
                    "price_preference": price_preference,
                    "time_preference": time_preference,
                    "home_district": home_district,
                },
            )
            user_id = int(result.lastrowid)
            conn.execute(
                text(
                    f"""
                    INSERT INTO {AUTH_TABLE}(user_id, password_salt, password_hash)
                    VALUES(:user_id, :salt, :hash)
                    """
                ),
                {"user_id": user_id, "salt": salt_hex, "hash": password_hash},
            )
        return True, "注册成功，请使用新账号登录。"
    except SQLAlchemyError as exc:
        return False, f"注册失败：{exc}"


def demo_account_count(engine: Engine) -> int:
    df = query_df(engine, f"SELECT COUNT(*) AS cnt FROM {AUTH_TABLE}")
    return int(df.iloc[0]["cnt"])


def initialize_demo_accounts(engine: Engine, default_password: str = "StageBook123!") -> int:
    """
    为 User 表中已有用户创建演示登录账号。
    只在账号表没有对应 user_id 时插入；密码统一为 default_password。
    """
    users = query_df(engine, "SELECT user_id FROM `User` ORDER BY user_id")
    inserted = 0
    for row in users.itertuples():
        salt_hex, password_hash = hash_password(default_password)
        try:
            execute_sql(
                engine,
                f"""
                INSERT IGNORE INTO {AUTH_TABLE}(user_id, password_salt, password_hash)
                VALUES(:uid, :salt, :hash)
                """,
                {"uid": int(row.user_id), "salt": salt_hex, "hash": password_hash},
            )
            inserted += 1
        except SQLAlchemyError:
            pass
    return inserted


def ensure_teacher_test_accounts(engine: Engine) -> None:
    """确保登录页提示的两个测试账号可直接使用。"""
    accounts = [
        {
            "username": "Estelle",
            "nickname": "Estelle",
            "password": "123456",
            "role": "user",
            "price_preference": "mid",
            "time_preference": "weekend_evening",
            "home_district": "静安区",
        },
        {
            "username": "admin",
            "nickname": "管理员",
            "password": "StageBook123!",
            "role": "admin",
            "price_preference": "mid",
            "time_preference": "weekend_evening",
            "home_district": "黄浦区",
        },
    ]
    for account in accounts:
        user_df = query_df(engine, "SELECT user_id FROM `User` WHERE username = :username LIMIT 1", {"username": account["username"]})
        if user_df.empty:
            with engine.begin() as conn:
                result = conn.execute(
                    text(
                        """
                        INSERT INTO `User`(username, nickname, city, price_preference, time_preference, home_district, role)
                        VALUES(:username, :nickname, '上海', :price_preference, :time_preference, :home_district, :role)
                        """
                    ),
                    account,
                )
                user_id = int(result.lastrowid)
        else:
            user_id = int(user_df.iloc[0]["user_id"])
            execute_sql(
                engine,
                """
                UPDATE `User`
                SET nickname = :nickname, role = :role,
                    price_preference = :price_preference,
                    time_preference = :time_preference,
                    home_district = :home_district
                WHERE user_id = :user_id
                """,
                {**account, "user_id": user_id},
            )
        salt_hex, password_hash = hash_password(account["password"])
        execute_sql(
            engine,
            f"""
            INSERT INTO {AUTH_TABLE}(user_id, password_salt, password_hash, is_active)
            VALUES(:user_id, :salt, :hash, 1)
            ON DUPLICATE KEY UPDATE password_salt = VALUES(password_salt),
                                    password_hash = VALUES(password_hash),
                                    is_active = 1
            """,
            {"user_id": user_id, "salt": salt_hex, "hash": password_hash},
        )


def page_auth(engine: Engine) -> None:
    st.title("🎭 StageBook")
    st.markdown(
        "<div class='stage-subtitle'>登录后即可进入 StageBook，查看演出、维护剧历和管理推荐。</div>",
        unsafe_allow_html=True,
    )

    st.info("测试账号：普通用户 Estelle / 123456；管理员 admin / StageBook123!", icon="🔑")

    tab_login, tab_register = st.tabs(["登录", "注册"])

    with tab_login:
        with st.form("login_form"):
            username = st.text_input("用户名", placeholder="例如 alice 或 admin")
            password = st.text_input("密码", type="password")
            submitted = st.form_submit_button("登录", type="primary")
            if submitted:
                ok, msg = login_user(engine, username, password)
                if ok:
                    st.success(msg)
                    st.rerun()
                else:
                    st.error(msg)

    with tab_register:
        with st.form("register_form"):
            username = st.text_input("新用户名")
            nickname = st.text_input("昵称")
            password = st.text_input("设置密码", type="password")
            confirm = st.text_input("确认密码", type="password")
            city = st.text_input("城市", value="上海")
            price_preference = st.selectbox("价格偏好", ["economy", "mid", "premium"], index=1)
            time_preference = st.selectbox(
                "时间偏好",
                ["weekday_evening", "weekend_evening", "weekend_matinee"],
                index=1,
            )
            home_district = st.selectbox(
                "出发区域",
                ["黄浦区", "徐汇区", "静安区", "长宁区", "浦东新区", "普陀区"],
                index=2,
            )
            submitted = st.form_submit_button("注册普通用户")
            if submitted:
                if password != confirm:
                    st.error("两次输入的密码不一致。")
                else:
                    ok, msg = register_user(
                        engine,
                        username=username,
                        nickname=nickname,
                        password=password,
                        city=city,
                        price_preference=price_preference,
                        time_preference=time_preference,
                        home_district=home_district,
                    )
                    if ok:
                        st.success(msg)
                    else:
                        st.error(msg)

def current_user() -> dict[str, Any]:
    return st.session_state.get("auth_user", {})


def delete_current_account(engine: Engine, user_id: int) -> None:
    """删除当前普通用户账号；User 外键会级联清理其登录、计划、记录和偏好。"""
    execute_sql(engine, "DELETE FROM `User` WHERE user_id = :uid AND role = 'user'", {"uid": user_id})


def render_user_sidebar(engine: Engine, user: dict[str, Any]) -> None:
    st.sidebar.markdown("### 当前登录")
    st.sidebar.markdown(
        f"""
        <div class="card">
            <b>{user.get('nickname', '-')}</b><br>
            <span class="soft">@{user.get('username', '-')} · {user.get('role', '-')}</span><br>
            <span class="soft">出发区：{user.get('home_district', '-')}</span>
        </div>
        """,
        unsafe_allow_html=True,
    )
    if st.sidebar.button("退出登录"):
        logout_user()
        st.rerun()

    if user.get("role") == "user":
        with st.sidebar.expander("注销账号", expanded=False):
            st.caption("注销后会删除当前普通用户账号及其观剧记录、计划和偏好。")
            confirm = st.text_input("输入当前用户名确认", key="delete_account_confirm")
            if st.button("确认注销当前账号", key="delete_account_btn", type="secondary"):
                if confirm.strip() != str(user.get("username", "")):
                    st.warning("用户名不一致，未执行注销。")
                else:
                    delete_current_account(engine, int(user["user_id"]))
                    logout_user()
                    st.success("账号已注销。")
                    st.rerun()


def page_user_home(engine: Engine, user: dict[str, Any]) -> None:
    user_id = int(user["user_id"])
    nickname = safe_html(user.get("nickname", "StageBook 用户"))
    username = safe_html(user.get("username", "-"))
    home_district = safe_html(user.get("home_district", "-"))

    st.markdown(
        f"""
        <div class="hero-card">
            <div class="hero-kicker">StageBook Personal Hub</div>
            <div class="hero-name">欢迎回来，{nickname}</div>
            <div class="soft">@{username} · 出发区：{home_district} · 你的观剧计划、记录、偏好和行程建议会在这里汇总。</div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    stats = query_df(
        engine,
        """
        SELECT
            (SELECT COUNT(*) FROM Watch_Record WHERE user_id = :uid) AS watched_count,
            (SELECT COUNT(*) FROM Planned_Performance WHERE user_id = :uid AND status IN ('planned', 'booked')) AS active_plan_count,
            (SELECT COUNT(*) FROM Favorite_Actor WHERE user_id = :uid) AS fav_actor_count,
            (SELECT fn_audience_type(:uid)) AS audience_type
        """,
        {"uid": user_id},
    ).iloc[0]

    c1, c2, c3, c4 = st.columns(4)
    c1.metric("已看场次", int(stats["watched_count"]))
    c2.metric("有效计划", int(stats["active_plan_count"]))
    c3.metric("喜欢演员", int(stats["fav_actor_count"]))
    c4.metric("观众类型", stats["audience_type"])

    left, right = st.columns([1.15, 1])

    with left:
        st.markdown("### 最近/即将观看")
        cal = query_df(
            engine,
            """
            SELECT title, theater_name, start_time, calendar_status, score
            FROM v_user_calendar
            WHERE user_id = :uid AND calendar_status <> 'canceled'
            ORDER BY ABS(TIMESTAMPDIFF(HOUR, NOW(), start_time))
            LIMIT 6
            """,
            {"uid": user_id},
        )
        if cal.empty:
            st.info("暂无观剧记录或计划，可以去「演出信息汇总」或「混合推荐引擎」看看适合你的场次。")
        else:
            for r in cal.itertuples():
                score_text = "" if pd.isna(r.score) else f" · 评分 {safe_html(r.score)}"
                st.markdown(
                    f"""
                    <div class="timeline-card">
                        <b>{safe_html(r.title)}</b><br>
                        {tag_badge(r.calendar_status, 'badge-green' if r.calendar_status == 'watched' else '')}
                        <span class="soft">{safe_html(r.theater_name)} · {fmt_dt(r.start_time)}{score_text}</span>
                    </div>
                    """,
                    unsafe_allow_html=True,
                )

    with right:
        st.markdown("### 我的画像摘要")
        profile = query_df(
            engine,
            """
            SELECT favorite_actors, favorite_categories, favorite_languages,
                   favorite_districts, most_watched_category, most_visited_theater
            FROM v_user_preference_profile
            WHERE user_id = :uid
            """,
            {"uid": user_id},
        )
        if profile.empty:
            st.info("暂无画像数据。")
        else:
            row = profile.iloc[0]
            chips = "".join(
                tag_badge(x)
                for x in [row["favorite_categories"], row["favorite_languages"], row["favorite_districts"]]
                if pd.notna(x) and str(x)
            )
            st.markdown(
                f"""
                <div class="card">
                    <h3>偏好概览</h3>
                    <div class="status-strip">{chips or '<span class="soft">暂无主动偏好，去「用户偏好画像」添加吧。</span>'}</div>
                    <b>喜欢演员：</b>{safe_html(row['favorite_actors'], '暂无')}<br>
                    <b>最常剧种：</b>{safe_html(row['most_watched_category'], '暂无')}<br>
                    <b>常去剧院：</b>{safe_html(row['most_visited_theater'], '暂无')}
                </div>
                """,
                unsafe_allow_html=True,
            )

    st.markdown("### 快捷入口")
    q1, q2, q3 = st.columns(3)
    with q1:
        st.markdown("<div class='card'><h3>📅 观剧日历</h3><div class='soft'>你的计划、已订票与已观看演出都汇在这里。</div></div>", unsafe_allow_html=True)
        if st.button("进入我的观剧管理", use_container_width=True):
            st.session_state["nav_page"] = "我的观剧管理"
            st.rerun()
    with q2:
        st.markdown("<div class='card'><h3>✨ 个性推荐</h3><div class='soft'>从画像和相似用户中发现更适合你的演出。</div></div>", unsafe_allow_html=True)
        if st.button("查看混合推荐", use_container_width=True):
            st.session_state["nav_page"] = "混合推荐引擎"
            st.rerun()
    with q3:
        st.markdown("<div class='card'><h3>🧳 行程辅助</h3><div class='soft'>围绕已计划场次查看餐饮、交通与出发建议。</div></div>", unsafe_allow_html=True)
        if st.button("查看行程辅助", use_container_width=True):
            st.session_state["nav_page"] = "场景化行程辅助"
            st.rerun()


# =========================
# 通用数据读取
# =========================

def load_users(engine: Engine, include_admin: bool = False) -> pd.DataFrame:
    where = "" if include_admin else "WHERE role = 'user'"
    return query_df(
        engine,
        f"""
        SELECT user_id, username, nickname, city, price_preference,
               time_preference, home_district, role
        FROM `User`
        {where}
        ORDER BY user_id
        """,
    )


def load_user_options(engine: Engine, include_admin: bool = False) -> dict[str, int]:
    users = load_users(engine, include_admin=include_admin)
    return {
        f"{row.nickname} / {row.username}": int(row.user_id)
        for row in users.itertuples()
    }


def label_value_options(df: pd.DataFrame, label_cols: list[str], value_col: str) -> dict[str, Any]:
    if df.empty:
        return {}
    options: dict[str, Any] = {}
    for row in df.to_dict("records"):
        label = " / ".join(str(row[col]) for col in label_cols)
        options[label] = row[value_col]
    return options


def price_label(price_min: Any, price_max: Any) -> str:
    try:
        return f"¥{float(price_min):.0f}–{float(price_max):.0f}"
    except Exception:
        return "票价未定"


def fmt_dt(value: Any) -> str:
    if pd.isna(value):
        return "-"
    if isinstance(value, str):
        value = pd.to_datetime(value)
    return pd.to_datetime(value).strftime("%Y-%m-%d %H:%M")


def safe_html(value: Any, default: str = "-") -> str:
    """转义数据库文本，避免卡片展示时把内容误渲染成 HTML/源码。"""
    if value is None or pd.isna(value):
        return default
    text_value = str(value)
    if text_value == "":
        return default
    return html.escape(text_value, quote=True)


def tag_badge(text_value: Any, color: str = "") -> str:
    if text_value is None or pd.isna(text_value) or text_value == "":
        return ""
    cls = "badge"
    if color:
        cls += f" {color}"
    return f"<span class='{cls}'>{safe_html(text_value, '')}</span>"


def performance_label(row: Any, include_price: bool = False) -> str:
    """用户侧下拉框使用的场次标签；不在剧名后拼 #编号。"""
    base = f"{row.title} / {row.theater_name} / {fmt_dt(row.start_time)}"
    if include_price:
        base += f" / {price_label(row.price_min, row.price_max)}"
    return base



def plain_text(value: Any, default: str = "-") -> str:
    """用于 Streamlit 原生组件的纯文本清洗，避免把 SQL/HTML 段落当源码展示。"""
    if value is None or pd.isna(value):
        return default
    text_value = str(value).strip()
    return text_value if text_value else default


def get_cast_by_performance(engine: Engine, perf_ids: list[int]) -> dict[int, str]:
    """批量读取场次演员信息，返回适合页面展示的纯文本。"""
    clean_ids = sorted({int(pid) for pid in perf_ids if pid is not None})
    if not clean_ids:
        return {}
    id_sql = ",".join(str(pid) for pid in clean_ids)
    cast_df = query_df(
        engine,
        f"""
        SELECT pc.performance_id, a.actor_name, r.role_name, pc.cast_type, pc.cast_group
        FROM Performance_Cast pc
        JOIN Actor a ON pc.actor_id = a.actor_id
        JOIN Role r ON pc.role_id = r.role_id
        WHERE pc.performance_id IN ({id_sql})
        ORDER BY pc.performance_id, pc.cast_group, pc.cast_type, a.actor_name
        """,
    )
    result: dict[int, str] = {}
    if cast_df.empty:
        return result
    for pid, g in cast_df.groupby("performance_id"):
        parts: list[str] = []
        for x in g.head(12).itertuples():
            role = plain_text(x.role_name, "角色未定")
            actor = plain_text(x.actor_name, "演员未定")
            cast_type = plain_text(x.cast_type, "")
            group = plain_text(x.cast_group, "")
            extra = " / ".join(v for v in [cast_type, f"{group}组" if group else ""] if v)
            parts.append(f"{actor} 饰 {role}" + (f"（{extra}）" if extra else ""))
        result[int(pid)] = "；".join(parts)
    return result


def admin_log(engine: Engine, admin_id: int, action_type: str, target_table: str, target_id: int | None, description: str) -> None:
    execute_sql(
        engine,
        """
        INSERT INTO Admin_Log(admin_user_id, action_type, target_table, target_id, description)
        VALUES(:admin_id, :action_type, :target_table, :target_id, :description)
        """,
        {
            "admin_id": admin_id,
            "action_type": action_type,
            "target_table": target_table,
            "target_id": target_id,
            "description": description[:255],
        },
    )


def show_dataframe(df: pd.DataFrame, height: int = 420) -> None:
    st.dataframe(df, use_container_width=True, hide_index=True, height=height)


# =========================
# 页面：总览
# =========================

def page_dashboard(engine: Engine) -> None:
    st.title("🎭 StageBook 总览")
    st.markdown(
        "<div class='stage-subtitle'>基于观剧记录、偏好画像、混合推荐与行程辅助的数据库系统展示界面。</div>",
        unsafe_allow_html=True,
    )

    count_sql = """
    SELECT '用户' AS item, COUNT(*) AS cnt FROM `User`
    UNION ALL SELECT '剧目', COUNT(*) FROM Production
    UNION ALL SELECT '演出场次', COUNT(*) FROM Performance
    UNION ALL SELECT '演员', COUNT(*) FROM Actor
    UNION ALL SELECT '观剧记录', COUNT(*) FROM Watch_Record
    UNION ALL SELECT '计划观看', COUNT(*) FROM Planned_Performance
    UNION ALL SELECT '餐厅方案', COUNT(*) FROM Nearby_Restaurant
    UNION ALL SELECT '交通方案', COUNT(*) FROM Transport_Option
    """
    counts = query_df(engine, count_sql)
    count_map = dict(zip(counts["item"], counts["cnt"]))

    cols = st.columns(4)
    for col, item in zip(cols, ["用户", "剧目", "演出场次", "观剧记录"]):
        col.metric(item, int(count_map.get(item, 0)))
    cols = st.columns(4)
    for col, item in zip(cols, ["计划观看", "演员", "餐厅方案", "交通方案"]):
        col.metric(item, int(count_map.get(item, 0)))

    st.markdown("### 功能覆盖情况")
    c1, c2, c3 = st.columns([1.1, 1, 1])

    with c1:
        profile = query_df(
            engine,
            """
            SELECT audience_type, COUNT(*) AS user_count
            FROM v_user_preference_profile
            GROUP BY audience_type
            ORDER BY user_count DESC
            """,
        )
        st.markdown("**用户画像分布**")
        if not profile.empty:
            chart = alt.Chart(profile).mark_bar().encode(
                x=alt.X("user_count:Q", title="用户数"),
                y=alt.Y("audience_type:N", title="画像类型", sort="-x"),
                tooltip=["audience_type", "user_count"],
            )
            st.altair_chart(chart, use_container_width=True)
        else:
            st.info("暂无用户画像数据。")

    with c2:
        perf_by_category = query_df(
            engine,
            """
            SELECT category, COUNT(*) AS performance_count
            FROM v_public_performance_info
            GROUP BY category
            ORDER BY performance_count DESC
            """,
        )
        st.markdown("**场次剧种分布**")
        if not perf_by_category.empty:
            chart = alt.Chart(perf_by_category).mark_bar().encode(
                x=alt.X("performance_count:Q", title="场次数"),
                y=alt.Y("category:N", title="剧种", sort="-x"),
                tooltip=["category", "performance_count"],
            )
            st.altair_chart(chart, use_container_width=True)
        else:
            st.info("暂无演出数据。")

    with c3:
        calendar_count = query_df(
            engine,
            """
            SELECT calendar_status, COUNT(*) AS cnt
            FROM v_user_calendar
            GROUP BY calendar_status
            ORDER BY cnt DESC
            """,
        )
        st.markdown("**观剧状态分布**")
        if not calendar_count.empty:
            chart = alt.Chart(calendar_count).mark_bar().encode(
                x=alt.X("cnt:Q", title="数量"),
                y=alt.Y("calendar_status:N", title="状态", sort="-x"),
                tooltip=["calendar_status", "cnt"],
            )
            st.altair_chart(chart, use_container_width=True)
        else:
            st.info("暂无日历数据。")

    st.markdown("### 推荐来源概览")
    try:
        rec_source = query_df(
            engine,
            """
            SELECT recommendation_source, COUNT(*) AS cnt
            FROM v_hybrid_recommendation
            GROUP BY recommendation_source
            ORDER BY cnt DESC
            """,
        )
        if rec_source.empty:
            st.info("暂无混合推荐结果。可以先完善偏好画像，或检查是否存在未来可推荐场次。")
        else:
            st.altair_chart(
                alt.Chart(rec_source).mark_bar().encode(
                    x=alt.X("cnt:Q", title="推荐条数"),
                    y=alt.Y("recommendation_source:N", title="推荐来源", sort="-x"),
                    tooltip=["recommendation_source", "cnt"],
                ),
                use_container_width=True,
            )
    except SQLAlchemyError as exc:
        st.warning("推荐视图暂不可用，请确认存储过程和视图已成功创建。")
        st.caption(str(exc))


# =========================
# 页面：公开演出
# =========================

def page_public_performances(engine: Engine) -> None:
    st.title("🎟️ 演出信息汇总")
    st.markdown("<div class='stage-subtitle'>汇总当前剧目、场次、剧院与卡司信息，帮助你快速了解近期演出安排。</div>", unsafe_allow_html=True)

    df = query_df(engine, "SELECT * FROM v_public_performance_info ORDER BY title, start_time")
    if df.empty:
        st.info("暂无演出数据。")
        return

    col1, col2, col3, col4 = st.columns([1.4, 1, 1, 1])
    keyword = col1.text_input("搜索剧目/剧院", "")
    categories = sorted(df["category"].dropna().astype(str).unique().tolist())
    districts = sorted(df["district"].dropna().astype(str).unique().tolist())
    category = col2.selectbox("剧种", ["全部"] + categories)
    district = col3.selectbox("区域", ["全部"] + districts)
    only_future = col4.toggle("只看未来场次", value=False)
    special_only = st.toggle("只看特殊场次", value=False)

    view = df.copy()
    if keyword:
        mask = (
            view["title"].astype(str).str.contains(keyword, case=False, na=False)
            | view["theater_name"].astype(str).str.contains(keyword, case=False, na=False)
        )
        view = view[mask]
    if category != "全部":
        view = view[view["category"].astype(str) == category]
    if district != "全部":
        view = view[view["district"].astype(str) == district]
    if only_future:
        view = view[pd.to_datetime(view["start_time"]) > pd.Timestamp.now()]
    if special_only:
        view = view[view["special_tag"].notna() & (view["special_tag"].astype(str).str.strip() != "")]

    st.caption(f"共 {view['title'].nunique()} 个剧目 / {len(view)} 个场次")
    if view.empty:
        st.info("当前筛选条件下没有演出。")
        return

    perf_ids = [int(x) for x in view["performance_id"].dropna().unique().tolist()]
    cast_by_perf = get_cast_by_performance(engine, perf_ids)

    grouped = view.groupby(["title", "version", "category", "language"], dropna=False)
    for (title, version, cat, lang), g in grouped:
        title_text = plain_text(title, "未命名剧目")
        cat_text = plain_text(cat, "未分类")
        header = f"{title_text}｜{cat_text}｜{len(g)} 场"
        with st.expander(header, expanded=False):
            time_min = fmt_dt(g["start_time"].min())
            time_max = fmt_dt(g["start_time"].max())
            theaters = "、".join(plain_text(x, "") for x in g["theater_name"].dropna().astype(str).unique()[:4]) or "-"
            c_title, c_meta = st.columns([1.4, 2])
            c_title.subheader(title_text)
            c_title.caption(" / ".join(x for x in [plain_text(version, ""), cat_text, plain_text(lang, "")] if x))
            c_meta.markdown(f"**演出范围：** {time_min} 至 {time_max}")
            c_meta.markdown(f"**涉及剧院：** {theaters}")
            c_meta.markdown(f"**票价区间：** {price_label(g['price_min'].min(), g['price_max'].max())}")

            for r in g.sort_values("start_time").itertuples():
                cast_text = plain_text(cast_by_perf.get(int(r.performance_id), "暂无卡司信息"), "暂无卡司信息")
                with st.container(border=True):
                    c_time, c_place, c_price = st.columns([1.35, 1.3, 0.75])
                    c_time.markdown(f"**{fmt_dt(r.start_time)} — {fmt_dt(r.end_time)}**")
                    c_place.markdown(f"{plain_text(r.theater_name)} · {plain_text(r.district)}")
                    c_price.markdown(f"**{price_label(r.price_min, r.price_max)}**")
                    if pd.notna(r.special_tag) and str(r.special_tag).strip():
                        st.caption(f"特殊场次：{plain_text(r.special_tag)}")
                    st.markdown("**演员信息**")
                    st.text(cast_text)


# =========================
# 页面：我的观剧管理
# =========================

def _calendar_event_class(status: Any) -> str:
    status = str(status or "planned")
    if status == "watched":
        return "event-watched"
    if status == "booked":
        return "event-booked"
    if status == "canceled":
        return "event-canceled"
    return "event-planned"


@st.dialog("日期观剧管理")
def _day_management_dialog(engine: Engine, user_id: int, selected_day: date) -> None:
    st.markdown(f"### {selected_day.strftime('%Y-%m-%d')} 的观剧安排")
    day_events = query_df(
        engine,
        """
        SELECT performance_id, title, version_name, theater_name, start_time, end_time, calendar_status, score
        FROM v_user_calendar
        WHERE user_id = :uid AND DATE(start_time) = :day AND calendar_status <> 'canceled'
        ORDER BY start_time
        """,
        {"uid": user_id, "day": selected_day},
    )
    if day_events.empty:
        st.info("这一天还没有计划或记录，可以在下面直接添加。")
    else:
        for r in day_events.itertuples():
            st.markdown(
                f"""
                <div class="card">
                    <b>{safe_html(r.title)}</b><br>
                    {tag_badge(r.calendar_status, 'badge-green' if r.calendar_status == 'watched' else '')}
                    <span class="soft">{safe_html(r.theater_name)} · {fmt_dt(r.start_time)}</span><br>
                    <span class="soft">评分：{'-' if pd.isna(r.score) else safe_html(r.score)}</span>
                </div>
                """,
                unsafe_allow_html=True,
            )

    t1, t2, t3 = st.tabs(["添加计划", "新增观剧记录", "状态管理"])

    with t1:
        future_df = query_df(
            engine,
            """
            SELECT v.performance_id, v.title, v.theater_name, v.start_time, v.price_min, v.price_max, v.special_tag
            FROM v_public_performance_info v
            WHERE DATE(v.start_time) = :day
              AND v.start_time > NOW()
              AND NOT EXISTS (SELECT 1 FROM Planned_Performance pp WHERE pp.user_id = :uid AND pp.performance_id = v.performance_id)
              AND NOT EXISTS (SELECT 1 FROM Watch_Record wr WHERE wr.user_id = :uid AND wr.performance_id = v.performance_id)
            ORDER BY v.start_time
            """,
            {"uid": user_id, "day": selected_day},
        )
        if future_df.empty:
            st.info("这一天暂无可添加的未来场次，或对应场次已经在计划/记录中。")
        else:
            options = {
                performance_label(r, include_price=True): int(r.performance_id)
                for r in future_df.itertuples()
            }
            with st.form(f"calendar_add_plan_{selected_day}"):
                perf_label = st.selectbox("选择场次", list(options.keys()))
                status = st.selectbox("状态", ["planned", "booked", "watched"], index=0)
                watched_score = st.slider("watched 评分", min_value=0.0, max_value=10.0, value=8.0, step=0.5)
                st.caption("选择 watched 时会直接写入观剧记录；planned/booked 会写入计划。")
                if st.form_submit_button("加入日历"):
                    pid = options[perf_label]
                    dup_df = query_df(
                        engine,
                        """
                        SELECT
                            EXISTS(SELECT 1 FROM Planned_Performance WHERE user_id = :uid AND performance_id = :pid) AS has_plan,
                            EXISTS(SELECT 1 FROM Watch_Record WHERE user_id = :uid AND performance_id = :pid) AS has_watch
                        """,
                        {"uid": user_id, "pid": pid},
                    ).iloc[0]
                    if int(dup_df["has_plan"]) or int(dup_df["has_watch"]):
                        st.warning("该剧目的这个场次已经在你的计划或记录中，不能重复添加。")
                    else:
                        try:
                            if status == "watched":
                                execute_sql(
                                    engine,
                                    "INSERT INTO Watch_Record(user_id, performance_id, watch_date, score) VALUES(:uid, :pid, :watch_date, :score)",
                                    {"uid": user_id, "pid": pid, "watch_date": selected_day, "score": watched_score},
                                )
                            else:
                                execute_sql(
                                    engine,
                                    "INSERT INTO Planned_Performance(user_id, performance_id, status) VALUES(:uid, :pid, :status)",
                                    {"uid": user_id, "pid": pid, "status": status},
                                )
                            st.toast("添加成功", icon="✅")
                            st.rerun()
                        except SQLAlchemyError as exc:
                            st.error("添加失败，可能是场次已结束、已重复添加或触发器拦截。")
                            st.caption(str(exc))

    with t2:
        perf_df = query_df(
            engine,
            """
            SELECT v.performance_id, v.title, v.theater_name, v.start_time, v.end_time
            FROM v_public_performance_info v
            WHERE DATE(v.start_time) = :day
              AND NOT EXISTS (SELECT 1 FROM Watch_Record wr WHERE wr.user_id = :uid AND wr.performance_id = v.performance_id)
            ORDER BY v.start_time DESC
            """,
            {"uid": user_id, "day": selected_day},
        )
        if perf_df.empty:
            st.info("这一天暂无可新增的观剧记录，或对应场次已经记录过。")
        else:
            options = {
                performance_label(r): int(r.performance_id)
                for r in perf_df.itertuples()
            }
            with st.form(f"calendar_add_watch_{selected_day}"):
                perf_label = st.selectbox("选择已观看场次", list(options.keys()))
                score = st.slider("评分", min_value=0.0, max_value=10.0, value=8.0, step=0.5)
                if st.form_submit_button("保存观剧记录"):
                    pid = options[perf_label]
                    dup_df = query_df(
                        engine,
                        "SELECT COUNT(*) AS cnt FROM Watch_Record WHERE user_id = :uid AND performance_id = :pid",
                        {"uid": user_id, "pid": pid},
                    ).iloc[0]
                    if int(dup_df["cnt"]):
                        st.warning("该剧目的这个场次已经记录过，不能重复添加。")
                    else:
                        try:
                            execute_sql(
                                engine,
                                "INSERT INTO Watch_Record(user_id, performance_id, watch_date, score) VALUES(:uid, :pid, :watch_date, :score)",
                                {"uid": user_id, "pid": pid, "watch_date": selected_day, "score": score},
                            )
                            st.toast("添加成功", icon="✅")
                            st.rerun()
                        except SQLAlchemyError as exc:
                            st.error("保存失败。")
                            st.caption(str(exc))

    with t3:
        status_df = query_df(
            engine,
            """
            SELECT performance_id, title, theater_name, start_time, calendar_status, score
            FROM v_user_calendar
            WHERE user_id = :uid AND DATE(start_time) = :day AND calendar_status <> 'canceled'
            ORDER BY start_time
            """,
            {"uid": user_id, "day": selected_day},
        )
        if status_df.empty:
            st.info("这一天暂无可修改状态的计划或记录。")
        else:
            options = {
                f"{r.title} / {fmt_dt(r.start_time)} / 当前：{r.calendar_status}": int(r.performance_id)
                for r in status_df.itertuples()
            }
            current_status = {int(r.performance_id): str(r.calendar_status) for r in status_df.itertuples()}
            current_score = {int(r.performance_id): (None if pd.isna(r.score) else float(r.score)) for r in status_df.itertuples()}
            with st.form(f"calendar_update_status_{selected_day}"):
                label = st.selectbox("选择场次", list(options.keys()))
                pid = options[label]
                current = current_status.get(pid, "planned")
                choices = ["planned", "booked", "watched", "canceled"]
                new_status = st.selectbox("新状态", choices, index=choices.index(current) if current in choices else 0)
                score_default = current_score.get(pid) if current_score.get(pid) is not None else 8.0
                score = st.slider("watched 评分", min_value=0.0, max_value=10.0, value=float(score_default), step=0.5)
                st.caption("改为 canceled 会从日历移除；改为 watched 会进入观剧记录。")
                if st.form_submit_button("更新状态"):
                    try:
                        if new_status == "canceled":
                            execute_sql(engine, "DELETE FROM Planned_Performance WHERE user_id = :uid AND performance_id = :pid", {"uid": user_id, "pid": pid})
                            execute_sql(engine, "DELETE FROM Watch_Record WHERE user_id = :uid AND performance_id = :pid", {"uid": user_id, "pid": pid})
                            st.toast("已取消并从日历中移除", icon="🗑️")
                        elif new_status == "watched":
                            exists = query_df(
                                engine,
                                "SELECT COUNT(*) AS cnt FROM Watch_Record WHERE user_id = :uid AND performance_id = :pid",
                                {"uid": user_id, "pid": pid},
                            ).iloc[0]
                            if int(exists["cnt"]):
                                execute_sql(
                                    engine,
                                    "UPDATE Watch_Record SET watch_date = :watch_date, score = :score WHERE user_id = :uid AND performance_id = :pid",
                                    {"uid": user_id, "pid": pid, "watch_date": selected_day, "score": score},
                                )
                                execute_sql(engine, "DELETE FROM Planned_Performance WHERE user_id = :uid AND performance_id = :pid", {"uid": user_id, "pid": pid})
                            else:
                                execute_sql(
                                    engine,
                                    "INSERT INTO Watch_Record(user_id, performance_id, watch_date, score) VALUES(:uid, :pid, :watch_date, :score)",
                                    {"uid": user_id, "pid": pid, "watch_date": selected_day, "score": score},
                                )
                            st.toast("已标记为 watched", icon="✅")
                        else:
                            execute_sql(
                                engine,
                                """
                                INSERT INTO Planned_Performance(user_id, performance_id, status)
                                VALUES(:uid, :pid, :status)
                                ON DUPLICATE KEY UPDATE status = VALUES(status)
                                """,
                                {"status": new_status, "uid": user_id, "pid": pid},
                            )
                            execute_sql(engine, "DELETE FROM Watch_Record WHERE user_id = :uid AND performance_id = :pid", {"uid": user_id, "pid": pid})
                            st.toast("更新成功", icon="✅")
                        st.rerun()
                    except SQLAlchemyError as exc:
                        st.error("状态更新失败。")
                        st.caption(str(exc))


def page_user_management(engine: Engine, user_id: int) -> None:
    st.title("📅 我的观剧管理")
    st.markdown("<div class='stage-subtitle'>把计划、订票和已观看演出汇成一张个人剧历，清楚呈现你的观演节奏。</div>", unsafe_allow_html=True)

    user_df = query_df(engine, "SELECT username, nickname FROM `User` WHERE user_id = :uid", {"uid": user_id})
    if not user_df.empty:
        st.caption(f"当前账号：{user_df.iloc[0]['nickname']} / {user_df.iloc[0]['username']}")

    today = date.today()
    c1, c2, c3 = st.columns([1, 1, 2])
    year = int(c1.number_input("年份", min_value=2000, max_value=2100, value=today.year, step=1))
    month = int(c2.selectbox("月份", list(range(1, 13)), index=today.month - 1, format_func=lambda x: f"{x} 月"))
    c3.markdown("<div class='action-hint'>提示：每个日期按钮都可点击；彩色标签表示 watched / planned / booked。状态改为 canceled 时会直接从日历移除；改为 watched 会进入观剧记录。</div>", unsafe_allow_html=True)

    month_start = date(year, month, 1)
    month_end = date(year, month, calendar.monthrange(year, month)[1])
    df = query_df(
        engine,
        """
        SELECT performance_id, title, version_name, theater_name, start_time, end_time, calendar_status, score
        FROM v_user_calendar
        WHERE user_id = :uid AND DATE(start_time) BETWEEN :start_day AND :end_day
          AND calendar_status <> 'canceled'
        ORDER BY start_time
        """,
        {"uid": user_id, "start_day": month_start, "end_day": month_end},
    )
    if not df.empty:
        df["day"] = pd.to_datetime(df["start_time"]).dt.date

    st.markdown(f"### {year} 年 {month} 月观剧日历")
    st.markdown("<div class='calendar-wrap'>", unsafe_allow_html=True)
    week_names = ["周一", "周二", "周三", "周四", "周五", "周六", "周日"]
    cols = st.columns(7)
    for i, name in enumerate(week_names):
        cols[i].markdown(f"<div class='week-head'>{name}</div>", unsafe_allow_html=True)

    for week in calendar.Calendar(firstweekday=0).monthdatescalendar(year, month):
        cols = st.columns(7)
        for i, d in enumerate(week):
            day_df = df[df["day"] == d] if not df.empty else pd.DataFrame()
            muted = " day-muted" if d.month != month else ""
            pills = ""
            for r in day_df.head(3).itertuples():
                cls = _calendar_event_class(r.calendar_status)
                pills += f"<span class='event-pill {cls}'>{safe_html(r.calendar_status, '')} · {safe_html(r.title, '')}</span>"
            more = "" if len(day_df) <= 3 else f"<span class='event-pill event-planned'>+{len(day_df)-3} 更多</span>"
            with cols[i]:
                st.markdown(f"<div class='day-cell{muted}'><div class='day-num'>{d.day}</div>{pills}{more}</div>", unsafe_allow_html=True)
                if st.button("管理", key=f"day_btn_{year}_{month}_{d.isoformat()}", use_container_width=True, disabled=(d.month != month)):
                    st.session_state["calendar_selected_day"] = d
                    _day_management_dialog(engine, user_id, d)
    st.markdown("</div>", unsafe_allow_html=True)

    if df.empty:
        st.info("本月暂无观剧记录或计划。点击某个日期仍可添加当天场次。")
    else:
        status_count = df.groupby("calendar_status", as_index=False).size().rename(columns={"size": "cnt"})
        st.altair_chart(
            alt.Chart(status_count).mark_arc(innerRadius=48).encode(
                theta=alt.Theta("cnt:Q", title="数量"),
                color=alt.Color("calendar_status:N", title="状态"),
                tooltip=["calendar_status", "cnt"],
            ),
            use_container_width=True,
        )


# =========================
# 页面：用户画像
# =========================

def page_profiles(engine: Engine, user_id: int) -> None:
    st.title("🧭 用户偏好画像")
    st.markdown("<div class='stage-subtitle'>用喜欢的演员、剧种、语言和区域描绘你的观剧口味，让推荐更贴近你。</div>", unsafe_allow_html=True)
    if st.session_state.pop("profile_added_success", False):
        st.toast("添加成功", icon="✅")
    if st.session_state.pop("profile_deleted_success", False):
        st.toast("删除成功", icon="🗑️")

    user_df = query_df(
        engine,
        "SELECT username, nickname FROM `User` WHERE user_id = :uid",
        {"uid": user_id},
    )
    if not user_df.empty:
        st.caption(f"当前账号：{user_df.iloc[0]['nickname']} / {user_df.iloc[0]['username']}")

    profile = query_df(
        engine,
        "SELECT * FROM v_user_preference_profile WHERE user_id = :uid",
        {"uid": user_id},
    )
    if profile.empty:
        st.info("该用户暂无画像。")
        return

    row = profile.iloc[0]
    c1, c2, c3, c4 = st.columns(4)
    c1.metric("观众类型", row["audience_type"])
    c2.metric("已看场次", int(row["total_watched"] or 0))
    c3.metric("平均评分", "-" if pd.isna(row["avg_score"]) else row["avg_score"])
    c4.metric("最常剧种", "-" if pd.isna(row["most_watched_category"]) else row["most_watched_category"])

    st.markdown(
        f"""
        <div class="card">
            <h3>{safe_html(row['username'])} 的画像摘要</h3>
            {tag_badge(row['price_preference'])}
            {tag_badge(row['time_preference'])}
            {tag_badge(row['audience_type'], 'badge-red')}
            <hr>
            <b>喜欢演员：</b>{safe_html(row['favorite_actors'], '暂无')}<br>
            <b>喜欢剧种：</b>{safe_html(row['favorite_categories'], '暂无')}<br>
            <b>喜欢语言：</b>{safe_html(row['favorite_languages'], '暂无')}<br>
            <b>喜欢区域：</b>{safe_html(row['favorite_districts'], '暂无')}<br>
            <b>最常观看演员：</b>{safe_html(row['most_watched_actor'], '暂无')}<br>
            <b>最常去剧院：</b>{safe_html(row['most_visited_theater'], '暂无')}
        </div>
        """,
        unsafe_allow_html=True,
    )

    st.markdown("### 主动偏好维护")
    t_actor, t_category, t_language, t_district = st.tabs(["喜欢演员", "喜欢剧种", "喜欢语言", "喜欢区域"])

    with t_actor:
        actors = query_df(engine, "SELECT actor_id, actor_name FROM Actor ORDER BY actor_name")
        options = label_value_options(actors, ["actor_name"], "actor_id")
        current = query_df(
            engine,
            """
            SELECT fa.actor_id, a.actor_name
            FROM Favorite_Actor fa
            JOIN Actor a ON fa.actor_id = a.actor_id
            WHERE fa.user_id = :uid
            ORDER BY a.actor_name
            """,
            {"uid": user_id},
        )
        add_col, del_col = st.columns(2)
        with add_col:
            st.markdown("**添加喜欢演员**")
            if options:
                with st.form("add_fav_actor"):
                    labels = st.multiselect("选择演员", list(options.keys()))
                    submitted = st.form_submit_button("添加")
                    if submitted:
                        try:
                            for label in labels:
                                execute_sql(
                                    engine,
                                    "INSERT IGNORE INTO Favorite_Actor(user_id, actor_id) VALUES(:uid, :aid)",
                                    {"uid": user_id, "aid": options[label]},
                                )
                            st.session_state["profile_added_success"] = True
                            st.rerun()
                        except SQLAlchemyError as exc:
                            st.error("添加失败。")
                            st.caption(str(exc))
        with del_col:
            st.markdown("**删除已选演员**")
            if current.empty:
                st.info("暂无已添加演员。")
            else:
                del_options = {str(r.actor_name): int(r.actor_id) for r in current.itertuples()}
                with st.form("delete_fav_actor"):
                    labels = st.multiselect("选择要删除的演员", list(del_options.keys()))
                    submitted = st.form_submit_button("删除")
                    if submitted:
                        for label in labels:
                            execute_sql(
                                engine,
                                "DELETE FROM Favorite_Actor WHERE user_id = :uid AND actor_id = :aid",
                                {"uid": user_id, "aid": del_options[label]},
                            )
                        st.session_state["profile_deleted_success"] = True
                        st.rerun()

    with t_category:
        categories = query_df(engine, "SELECT DISTINCT category FROM Production ORDER BY category")
        category_list = categories["category"].dropna().tolist()
        current = query_df(
            engine,
            "SELECT category FROM Favorite_Category WHERE user_id = :uid ORDER BY category",
            {"uid": user_id},
        )
        add_col, del_col = st.columns(2)
        with add_col:
            st.markdown("**添加喜欢剧种**")
            with st.form("add_fav_category"):
                selected_categories = st.multiselect("选择剧种", category_list)
                submitted = st.form_submit_button("添加")
                if submitted:
                    for cat in selected_categories:
                        execute_sql(
                            engine,
                            "INSERT IGNORE INTO Favorite_Category(user_id, category) VALUES(:uid, :cat)",
                            {"uid": user_id, "cat": cat},
                        )
                    st.session_state["profile_added_success"] = True
                    st.rerun()
        with del_col:
            st.markdown("**删除已选剧种**")
            current_list = current["category"].dropna().tolist() if not current.empty else []
            if not current_list:
                st.info("暂无已添加剧种。")
            else:
                with st.form("delete_fav_category"):
                    selected = st.multiselect("选择要删除的剧种", current_list)
                    submitted = st.form_submit_button("删除")
                    if submitted:
                        for cat in selected:
                            execute_sql(
                                engine,
                                "DELETE FROM Favorite_Category WHERE user_id = :uid AND category = :cat",
                                {"uid": user_id, "cat": cat},
                            )
                        st.session_state["profile_deleted_success"] = True
                        st.rerun()

    with t_language:
        languages = query_df(engine, "SELECT DISTINCT language FROM Production ORDER BY language")
        language_list = languages["language"].dropna().tolist()
        current = query_df(
            engine,
            "SELECT language FROM Favorite_Language WHERE user_id = :uid ORDER BY language",
            {"uid": user_id},
        )
        add_col, del_col = st.columns(2)
        with add_col:
            st.markdown("**添加喜欢语言**")
            with st.form("add_fav_language"):
                selected_languages = st.multiselect("选择语言", language_list)
                submitted = st.form_submit_button("添加")
                if submitted:
                    for lang in selected_languages:
                        execute_sql(
                            engine,
                            "INSERT IGNORE INTO Favorite_Language(user_id, language) VALUES(:uid, :lang)",
                            {"uid": user_id, "lang": lang},
                        )
                    st.session_state["profile_added_success"] = True
                    st.rerun()
        with del_col:
            st.markdown("**删除已选语言**")
            current_list = current["language"].dropna().tolist() if not current.empty else []
            if not current_list:
                st.info("暂无已添加语言。")
            else:
                with st.form("delete_fav_language"):
                    selected = st.multiselect("选择要删除的语言", current_list)
                    submitted = st.form_submit_button("删除")
                    if submitted:
                        for lang in selected:
                            execute_sql(
                                engine,
                                "DELETE FROM Favorite_Language WHERE user_id = :uid AND language = :lang",
                                {"uid": user_id, "lang": lang},
                            )
                        st.session_state["profile_deleted_success"] = True
                        st.rerun()

    with t_district:
        districts = query_df(
            engine,
            "SELECT DISTINCT city, district FROM Theater ORDER BY city, district",
        )
        opts = {
            f"{r.city}-{r.district}": (r.city, r.district)
            for r in districts.itertuples()
        }
        current = query_df(
            engine,
            "SELECT city, district FROM Favorite_District WHERE user_id = :uid ORDER BY city, district",
            {"uid": user_id},
        )
        add_col, del_col = st.columns(2)
        with add_col:
            st.markdown("**添加喜欢区域**")
            with st.form("add_fav_district"):
                selected_districts = st.multiselect("选择区域", list(opts.keys()))
                submitted = st.form_submit_button("添加")
                if submitted:
                    for label in selected_districts:
                        city, district = opts[label]
                        execute_sql(
                            engine,
                            "INSERT IGNORE INTO Favorite_District(user_id, city, district) VALUES(:uid, :city, :district)",
                            {"uid": user_id, "city": city, "district": district},
                        )
                    st.session_state["profile_added_success"] = True
                    st.rerun()
        with del_col:
            st.markdown("**删除已选区域**")
            if current.empty:
                st.info("暂无已添加区域。")
            else:
                del_options = {f"{r.city}-{r.district}": (r.city, r.district) for r in current.itertuples()}
                with st.form("delete_fav_district"):
                    selected = st.multiselect("选择要删除的区域", list(del_options.keys()))
                    submitted = st.form_submit_button("删除")
                    if submitted:
                        for label in selected:
                            city, district = del_options[label]
                            execute_sql(
                                engine,
                                "DELETE FROM Favorite_District WHERE user_id = :uid AND city = :city AND district = :district",
                                {"uid": user_id, "city": city, "district": district},
                            )
                        st.session_state["profile_deleted_success"] = True
                        st.rerun()


# =========================
# 页面：混合推荐
# =========================

def page_recommendations(engine: Engine, user_id: int) -> None:
    st.title("✨ 混合推荐引擎")
    st.markdown(
        "<div class='stage-subtitle'>结合你的偏好与相似观众，整理值得关注的演出场次。</div>",
        unsafe_allow_html=True,
    )

    user_df = query_df(
        engine,
        "SELECT username, nickname FROM `User` WHERE user_id = :uid",
        {"uid": user_id},
    )
    if not user_df.empty:
        st.caption(f"当前账号：{user_df.iloc[0]['nickname']} / {user_df.iloc[0]['username']}")

    c1, c2 = st.columns([1, 3])
    if c1.button("查看最相似用户"):
        sim = query_df(
            engine,
            "SELECT fn_most_similar_user(:uid) AS similar_user_id",
            {"uid": user_id},
        )
        sim_id = sim.iloc[0]["similar_user_id"] if not sim.empty else None
        if pd.isna(sim_id) or sim_id is None:
            st.warning("暂无可计算的相似用户。")
        else:
            sim_user = query_df(
                engine,
                "SELECT user_id, username, nickname FROM `User` WHERE user_id = :sid",
                {"sid": int(sim_id)},
            )
            st.info(f"最相似用户：{sim_user.iloc[0]['nickname']} / {sim_user.iloc[0]['username']}")
    c2.markdown("<div class='action-hint'>推荐结果来自数据库视图；点击加入计划后，状态固定为 planned，并与日历和行程辅助联动。</div>", unsafe_allow_html=True)

    rec_df = query_df(
        engine,
        """
        SELECT *
        FROM v_hybrid_recommendation
        WHERE user_id = :uid
        ORDER BY
            CASE recommendation_source
                WHEN 'profile_based' THEN 1
                WHEN 'similar_user' THEN 2
                WHEN 'rule_based' THEN 3
                ELSE 9
            END,
            start_time
        """,
        {"uid": user_id},
    )

    if rec_df.empty:
        st.info("暂无推荐结果。请检查是否有未来场次或画像推荐结果。")
        return

    source_count = rec_df.groupby("recommendation_source", as_index=False).size().rename(columns={"size": "cnt"})
    st.altair_chart(
        alt.Chart(source_count).mark_bar().encode(
            x=alt.X("cnt:Q", title="推荐条数"),
            y=alt.Y("recommendation_source:N", title="来源", sort="-x"),
            tooltip=["recommendation_source", "cnt"],
        ),
        use_container_width=True,
    )

    st.markdown("### 推荐列表")
    source_filter = st.multiselect(
        "筛选推荐来源",
        sorted(rec_df["recommendation_source"].dropna().unique().tolist()),
        default=sorted(rec_df["recommendation_source"].dropna().unique().tolist()),
    )
    view = rec_df[rec_df["recommendation_source"].isin(source_filter)].copy()

    for row in view.itertuples():
        special = tag_badge(row.tag_label, "badge-red")
        source = tag_badge(row.recommendation_source)
        profile = tag_badge(row.matched_profile_type, "badge-green")
        st.markdown(
            f"""
            <div class="card">
                <h3>{safe_html(row.production_title)}</h3>
                {source}{profile}{special}
                <br>
                <span class="soft">{safe_html(row.version_name)} / {safe_html(row.category)} / {safe_html(row.language)}</span><br>
                <b>{fmt_dt(row.start_time)}</b> · {safe_html(row.theater_name)} · {safe_html(row.district)}<br>
                <b>{price_label(row.price_min, row.price_max)}</b><br>
                <span class="soft">推荐理由：{safe_html(row.recommendation_reason)}</span>
            </div>
            """,
            unsafe_allow_html=True,
        )

        add_key = f"add_recommend_{user_id}_{row.recommended_performance_id}"
        if st.button("加入计划", key=add_key):
            pid = int(row.recommended_performance_id)
            dup_df = query_df(
                engine,
                """
                SELECT
                    EXISTS(SELECT 1 FROM Planned_Performance WHERE user_id = :uid AND performance_id = :pid) AS has_plan,
                    EXISTS(SELECT 1 FROM Watch_Record WHERE user_id = :uid AND performance_id = :pid) AS has_watch
                """,
                {"uid": user_id, "pid": pid},
            ).iloc[0]
            if int(dup_df["has_plan"]) or int(dup_df["has_watch"]):
                st.warning("该剧目的这个场次已经在你的计划或记录中，不能重复加入。")
            else:
                try:
                    execute_sql(
                        engine,
                        """
                        INSERT INTO Planned_Performance(user_id, performance_id, status)
                        VALUES(:uid, :pid, 'planned')
                        """,
                        {"uid": user_id, "pid": pid},
                    )
                    st.success("已加入计划，并会同步显示在观剧日历与场景化行程辅助中。")
                    st.rerun()
                except SQLAlchemyError as exc:
                    st.error("加入计划失败。")
                    st.caption(str(exc))


# =========================
# 页面：行程辅助
# =========================

def page_trip_assistance(engine: Engine, user_id: int) -> None:
    st.title("🧳 场景化行程辅助")
    st.markdown(
        "<div class='stage-subtitle'>围绕已计划的演出场次，呈现剧院、餐饮、交通和出发参考。</div>",
        unsafe_allow_html=True,
    )

    user_df = query_df(engine, "SELECT username, nickname FROM `User` WHERE user_id = :uid", {"uid": user_id})
    if not user_df.empty:
        st.caption(f"当前账号：{user_df.iloc[0]['nickname']} / {user_df.iloc[0]['username']}")

    df = query_df(
        engine,
        """
        SELECT t.*, v.title, v.version, v.category, v.language, v.district
        FROM v_planned_trip_assistance t
        JOIN v_public_performance_info v ON t.performance_id = v.performance_id
        WHERE t.user_id = :uid
        ORDER BY t.start_time
        """,
        {"uid": user_id},
    )

    if df.empty:
        st.info("暂无 planned/booked 状态的计划观看记录，或暂无匹配的行程辅助数据。")
        return

    st.caption(f"共 {len(df)} 条场次行程建议")
    for row in df.itertuples():
        restaurant = row.restaurant_name if pd.notna(row.restaurant_name) else "暂无匹配餐厅"
        transport = row.transport_type if pd.notna(row.transport_type) else "暂无匹配交通"
        depart = fmt_dt(row.suggested_departure_time)
        st.markdown(
            f"""
            <div class="card">
                <div class="trip-title">{safe_html(row.title)}</div>
                {tag_badge(row.version)}{tag_badge(row.category, 'badge-red')}{tag_badge('计划行程')}{tag_badge(row.price_tier if pd.notna(row.price_tier) else '')}
                <hr>
                <b>对应场次：</b>{fmt_dt(row.start_time)} — {fmt_dt(row.end_time)}<br>
                <b>演出地点：</b>{safe_html(row.theater_name)} · {safe_html(row.district)}<br>
                <b>推荐餐厅：</b>{safe_html(restaurant)}
                <span class="soft">（{safe_html(row.restaurant_category if pd.notna(row.restaurant_category) else '-')}，
                人均 {row.avg_price if pd.notna(row.avg_price) else '-'}，
                距离 {row.distance_m if pd.notna(row.distance_m) else '-'} m）</span><br>
                <b>推荐交通：</b>{safe_html(transport)}
                <span class="soft">（预计 {row.estimated_time if pd.notna(row.estimated_time) else '-'} 分钟，
                ¥{row.estimated_cost if pd.notna(row.estimated_cost) else '-'}，
                出发区：{safe_html(row.suitable_district if pd.notna(row.suitable_district) else '-')}）</span><br>
                <b>建议出发：</b>{depart}
            </div>
            """,
            unsafe_allow_html=True,
        )


# =========================
# 页面：管理员后台
# =========================

@st.dialog("剧目日历详情")
def _admin_day_performance_dialog(engine: Engine, selected_day: date) -> None:
    st.markdown(f"### {selected_day.strftime('%Y-%m-%d')} 全部演出")
    df = query_df(
        engine,
        """
        SELECT performance_id, title, version, category, language, theater_name, district,
               start_time, end_time, price_min, price_max, special_tag
        FROM v_public_performance_info
        WHERE DATE(start_time) = :day
        ORDER BY start_time, title
        """,
        {"day": selected_day},
    )
    if df.empty:
        st.info("这一天没有演出。")
        return
    cast_by_perf = get_cast_by_performance(engine, [int(x) for x in df["performance_id"].tolist()])
    for r in df.itertuples():
        with st.container(border=True):
            st.markdown(f"**{plain_text(r.title)}**")
            st.caption(f"{plain_text(r.category)} / {plain_text(r.language)} / {plain_text(r.version)}")
            st.write(f"{fmt_dt(r.start_time)} — {fmt_dt(r.end_time)}")
            st.write(f"{plain_text(r.theater_name)} · {plain_text(r.district)} · {price_label(r.price_min, r.price_max)}")
            if pd.notna(r.special_tag) and str(r.special_tag).strip():
                st.caption(f"特殊场次：{plain_text(r.special_tag)}")
            st.write(f"演员信息：{cast_by_perf.get(int(r.performance_id), '暂无卡司信息')}")


def _admin_option_maps(engine: Engine) -> tuple[dict[str, int], dict[str, int], dict[str, int]]:
    productions = query_df(engine, "SELECT production_id, title, version FROM Production ORDER BY title, production_id")
    theaters = query_df(engine, "SELECT theater_id, theater_name, district FROM Theater ORDER BY theater_name, theater_id")
    actors = query_df(engine, "SELECT actor_id, actor_name FROM Actor ORDER BY actor_name, actor_id")
    prod_options = {f"{r.title} / {r.version}": int(r.production_id) for r in productions.itertuples()}
    theater_options = {f"{r.theater_name} / {r.district}": int(r.theater_id) for r in theaters.itertuples()}
    actor_options = {str(r.actor_name): int(r.actor_id) for r in actors.itertuples()}
    return prod_options, theater_options, actor_options


def _insert_performance_with_cast(
    conn: Any,
    production_id: int,
    theater_id: int,
    start_dt: datetime,
    end_dt: datetime,
    price_min: float,
    price_max: float,
    special_tag: str,
    actor_role_pairs: list[tuple[int, str]],
    cast_type: str,
    cast_group: str,
) -> int:
    perf_result = conn.execute(
        text(
            """
            INSERT INTO Performance(
                production_id, theater_id, start_time, end_time,
                price_min, price_max, special_tag
            )
            VALUES(:production_id, :theater_id, :start_time, :end_time,
                   :price_min, :price_max, NULLIF(:special_tag, ''))
            """
        ),
        {
            "production_id": production_id,
            "theater_id": theater_id,
            "start_time": start_dt,
            "end_time": end_dt,
            "price_min": price_min,
            "price_max": price_max,
            "special_tag": special_tag.strip(),
        },
    )
    performance_id = int(perf_result.lastrowid)
    for actor_id, role_name in actor_role_pairs:
        role_name = role_name.strip() or "角色未定"
        conn.execute(
            text(
                """
                INSERT IGNORE INTO Role(production_id, role_name)
                VALUES(:production_id, :role_name)
                """
            ),
            {"production_id": production_id, "role_name": role_name},
        )
        role_df = pd.read_sql(
            text("SELECT role_id FROM Role WHERE production_id = :production_id AND role_name = :role_name LIMIT 1"),
            conn,
            params={"production_id": production_id, "role_name": role_name},
        )
        if not role_df.empty:
            conn.execute(
                text(
                    """
                    INSERT IGNORE INTO Performance_Cast(performance_id, actor_id, role_id, cast_type, cast_group)
                    VALUES(:performance_id, :actor_id, :role_id, :cast_type, :cast_group)
                    """
                ),
                {
                    "performance_id": performance_id,
                    "actor_id": actor_id,
                    "role_id": int(role_df.iloc[0]["role_id"]),
                    "cast_type": cast_type,
                    "cast_group": cast_group.strip() or "A",
                },
            )
    return performance_id


def page_admin(engine: Engine) -> None:
    st.title("🛠️ 演出信息管理")
    st.markdown("<div class='stage-subtitle'>集中维护剧目、场次、剧院、餐馆、演员和交通信息，并通过日历查看整体排期。</div>", unsafe_allow_html=True)

    admins = load_users(engine, include_admin=True)
    admins = admins[admins["role"] == "admin"]
    if admins.empty:
        st.warning("暂无管理员用户。")
        return

    admin_options = {f"{row.nickname} / {row.username}": int(row.user_id) for row in admins.itertuples()}
    admin_label = st.selectbox("当前管理员", list(admin_options.keys()))
    admin_id = admin_options[admin_label]

    def _existing_values(table: str, column: str) -> list[str]:
        df = query_df(engine, f"SELECT DISTINCT {column} AS value FROM {table} WHERE {column} IS NOT NULL AND {column} <> '' ORDER BY {column}")
        return df["value"].dropna().astype(str).tolist() if not df.empty else []

    def _custom_or_existing(label: str, values: list[str], default: str = "", key: str = "") -> str:
        values = sorted({v for v in values if str(v).strip()})
        if values:
            options = values + ["新增自定义..."]
            default_index = options.index(default) if default in options else 0
            selected = st.selectbox(label, options, index=default_index, key=f"{key}_select")
            if selected != "新增自定义...":
                return selected
        return st.text_input(label, value=default if default not in values else "", key=f"{key}_text").strip()

    tab_calendar, tab_prod, tab_perf, tab_edit, tab_basic, tab_delete, tab_log = st.tabs([
        "剧目日历", "新增剧目", "新增场次", "修改信息", "基础数据", "批量删除", "管理员日志"
    ])

    with tab_calendar:
        today = date.today()
        c1, c2, c3 = st.columns([1, 1, 2])
        year = int(c1.number_input("年份", min_value=2000, max_value=2100, value=today.year, step=1, key="admin_cal_year"))
        month = int(c2.selectbox("月份", list(range(1, 13)), index=today.month - 1, format_func=lambda x: f"{x} 月", key="admin_cal_month"))
        c3.markdown("<div class='action-hint'>所有公开场次会显示在日历格子中；日期详情包含场次、剧院与演员信息。</div>", unsafe_allow_html=True)

        month_start = date(year, month, 1)
        month_end = date(year, month, calendar.monthrange(year, month)[1])
        df = query_df(
            engine,
            """
            SELECT performance_id, title, theater_name, start_time, end_time, category, special_tag
            FROM v_public_performance_info
            WHERE DATE(start_time) BETWEEN :start_day AND :end_day
            ORDER BY start_time, title
            """,
            {"start_day": month_start, "end_day": month_end},
        )
        if not df.empty:
            df["day"] = pd.to_datetime(df["start_time"]).dt.date

        st.markdown(f"### {year} 年 {month} 月全部剧目日历")
        st.markdown("<div class='calendar-wrap'>", unsafe_allow_html=True)
        cols = st.columns(7)
        for i, name in enumerate(["周一", "周二", "周三", "周四", "周五", "周六", "周日"]):
            cols[i].markdown(f"<div class='week-head'>{name}</div>", unsafe_allow_html=True)
        for week in calendar.Calendar(firstweekday=0).monthdatescalendar(year, month):
            cols = st.columns(7)
            for i, d in enumerate(week):
                day_df = df[df["day"] == d] if not df.empty else pd.DataFrame()
                muted = " day-muted" if d.month != month else ""
                pills = ""
                for r in day_df.head(4).itertuples():
                    time_text = fmt_dt(r.start_time)[11:16] if fmt_dt(r.start_time) != "-" else ""
                    pills += f"<span class='event-pill event-booked'>{safe_html(r.title, '')} · {time_text}</span>"
                more = "" if len(day_df) <= 4 else f"<span class='event-pill event-planned'>+{len(day_df)-4} 更多</span>"
                with cols[i]:
                    st.markdown(f"<div class='day-cell{muted}'><div class='day-num'>{d.day}</div>{pills}{more}</div>", unsafe_allow_html=True)
                    if st.button("查看", key=f"admin_day_btn_{year}_{month}_{d.isoformat()}", use_container_width=True, disabled=(d.month != month)):
                        _admin_day_performance_dialog(engine, d)
        st.markdown("</div>", unsafe_allow_html=True)

    with tab_prod:
        st.markdown("### 新增剧目")
        st.caption("这里只维护剧目本身；场次、剧院和演员卡司请到「新增场次」中添加。")
        with st.form("add_production_only"):
            title = st.text_input("剧目名称")
            category = _custom_or_existing("剧种", _existing_values("Production", "category"), default="音乐剧", key="prod_add_category")
            duration_min = st.number_input("时长/分钟", min_value=1, value=120)
            language = _custom_or_existing("语言", _existing_values("Production", "language"), default="普通话", key="prod_add_language")
            version = st.selectbox("版本", ["original", "revival", "tour", "limited"])
            submitted = st.form_submit_button("新增剧目", type="primary")
            if submitted:
                title_clean = title.strip()
                if not title_clean:
                    st.error("剧目名称不能为空。")
                elif not category or not language:
                    st.error("剧种和语言不能为空。")
                else:
                    duplicate = query_df(engine, "SELECT COUNT(*) AS cnt FROM Production WHERE title = :title", {"title": title_clean}).iloc[0]
                    if int(duplicate["cnt"]):
                        st.error("同一剧目已经存在，不能重复添加。")
                    else:
                        try:
                            execute_sql(
                                engine,
                                "INSERT INTO Production(title, category, duration_min, language, version) VALUES(:title, :category, :duration, :language, :version)",
                                {"title": title_clean, "category": category, "duration": int(duration_min), "language": language, "version": version},
                            )
                            admin_log(engine, admin_id, "INSERT", "Production", None, f"新增剧目：{title_clean}")
                            st.success("剧目已新增。")
                            st.rerun()
                        except SQLAlchemyError as exc:
                            st.error("新增剧目失败。")
                            st.caption(str(exc))

        st.markdown("### 批量新增剧目")
        st.caption("格式：剧目名称 | 剧种 | 时长分钟 | 语言 | 版本。已有同名剧目会自动跳过。")
        batch_text = st.text_area("批量内容", height=140, placeholder="夜色将明|话剧|120|普通话|original\n城市回声|音乐剧|135|普通话|tour", key="batch_add_productions")
        if st.button("批量新增剧目", key="batch_add_productions_btn"):
            inserted, skipped = 0, []
            for raw_line in batch_text.splitlines():
                line = raw_line.strip()
                if not line:
                    continue
                parts = [x.strip() for x in line.split("|")]
                if len(parts) != 5:
                    skipped.append(f"格式错误：{line}")
                    continue
                title, category, duration, language, version = parts
                if version not in ["original", "revival", "tour", "limited"]:
                    skipped.append(f"版本错误：{line}")
                    continue
                duplicate = query_df(engine, "SELECT COUNT(*) AS cnt FROM Production WHERE title = :title", {"title": title}).iloc[0]
                if int(duplicate["cnt"]):
                    skipped.append(f"已存在：{title}")
                    continue
                try:
                    execute_sql(
                        engine,
                        "INSERT INTO Production(title, category, duration_min, language, version) VALUES(:title, :category, :duration, :language, :version)",
                        {"title": title, "category": category, "duration": int(duration), "language": language, "version": version},
                    )
                    inserted += 1
                except Exception as exc:
                    skipped.append(f"失败：{title}（{exc}）")
            if inserted:
                admin_log(engine, admin_id, "BATCH_INSERT", "Production", None, f"批量新增剧目 {inserted} 个")
            st.success(f"批量新增完成：成功 {inserted} 个，跳过/失败 {len(skipped)} 个。")
            if skipped:
                st.caption("；".join(skipped[:10]))
            st.rerun()

    with tab_perf:
        prod_options, theater_options, actor_options = _admin_option_maps(engine)
        st.markdown("### 新增场次")
        if not prod_options or not theater_options:
            st.info("请先保证剧目和剧院有数据。")
        else:
            with st.form("add_performance"):
                prod_label = st.selectbox("剧目", list(prod_options.keys()), key="single_perf_prod")
                theater_label = st.selectbox("剧院", list(theater_options.keys()), key="single_perf_theater")
                perf_date = st.date_input("演出日期", value=date.today(), key="single_perf_date")
                start_t = st.time_input("开始时间", value=time(19, 30), key="single_perf_start")
                end_t = st.time_input("结束时间", value=time(21, 30), key="single_perf_end")
                price_min = st.number_input("最低票价", min_value=0.0, value=180.0, step=10.0, key="single_perf_price_min")
                price_max = st.number_input("最高票价", min_value=0.0, value=680.0, step=10.0, key="single_perf_price_max")
                tag_values = _existing_values("Performance", "special_tag")
                tag_options = ["无"] + tag_values + ["新增自定义..."]
                tag_choice = st.selectbox("特殊标签", tag_options, key="single_perf_tag_select")
                special_tag = "" if tag_choice == "无" else tag_choice
                if tag_choice == "新增自定义...":
                    special_tag = st.text_input("自定义特殊标签", value="", key="single_perf_tag_text").strip()
                selected_actors = st.multiselect("演员", list(actor_options.keys()), key="single_perf_actors")
                role_names = st.text_input("角色名", placeholder="按演员选择顺序填写，用逗号分隔", key="single_perf_roles")
                cast_type = st.selectbox("演员类型", ["leading", "supporting", "ensemble", "guest"], key="single_perf_cast_type")
                cast_group = st.text_input("卡司组别", value="A", key="single_perf_cast_group")
                submitted = st.form_submit_button("新增场次", type="primary")

                if submitted:
                    start_dt = datetime.combine(perf_date, start_t)
                    end_dt = datetime.combine(perf_date, end_t)
                    role_list = [x.strip() for x in role_names.replace("，", ",").split(",") if x.strip()]
                    actor_role_pairs = []
                    for idx, actor_label in enumerate(selected_actors):
                        actor_role_pairs.append((actor_options[actor_label], role_list[idx] if idx < len(role_list) else "角色未定"))
                    try:
                        with engine.begin() as conn:
                            performance_id = _insert_performance_with_cast(
                                conn,
                                production_id=prod_options[prod_label],
                                theater_id=theater_options[theater_label],
                                start_dt=start_dt,
                                end_dt=end_dt,
                                price_min=float(price_min),
                                price_max=float(price_max),
                                special_tag=special_tag,
                                actor_role_pairs=actor_role_pairs,
                                cast_type=cast_type,
                                cast_group=cast_group,
                            )
                        admin_log(engine, admin_id, "INSERT", "Performance", performance_id, f"新增场次：{prod_label} @ {theater_label}")
                        st.success("场次已新增，并写入管理员日志。")
                        st.rerun()
                    except SQLAlchemyError as exc:
                        st.error("新增失败，可能违反时间或票价 CHECK 约束。")
                        st.caption(str(exc))

            st.markdown("### 批量新增场次")
            st.caption("格式：剧目名称 | 剧院名称 | 日期YYYY-MM-DD | 开始HH:MM | 结束HH:MM | 最低票价 | 最高票价 | 特殊标签。特殊标签可留空。")
            batch_perf_text = st.text_area("批量场次内容", height=150, placeholder="时间旅人|上海大剧院|2026-06-01|19:30|21:30|180|680|首演", key="batch_add_performances")
            if st.button("批量新增场次", key="batch_add_performances_btn"):
                productions = query_df(engine, "SELECT production_id, title FROM Production")
                theaters = query_df(engine, "SELECT theater_id, theater_name FROM Theater")
                prod_by_title = {str(r.title).strip(): int(r.production_id) for r in productions.itertuples()}
                theater_by_name = {str(r.theater_name).strip(): int(r.theater_id) for r in theaters.itertuples()}
                inserted, skipped = 0, []
                for raw_line in batch_perf_text.splitlines():
                    line = raw_line.strip()
                    if not line:
                        continue
                    parts = [x.strip() for x in line.split("|")]
                    if len(parts) < 7:
                        skipped.append(f"格式错误：{line}")
                        continue
                    if len(parts) == 7:
                        parts.append("")
                    title, theater_name, day_str, start_str, end_str, p_min, p_max, tag = parts[:8]
                    if title not in prod_by_title:
                        skipped.append(f"剧目不存在：{title}")
                        continue
                    if theater_name not in theater_by_name:
                        skipped.append(f"剧院不存在：{theater_name}")
                        continue
                    try:
                        perf_date = datetime.strptime(day_str, "%Y-%m-%d").date()
                        start_t = datetime.strptime(start_str, "%H:%M").time()
                        end_t = datetime.strptime(end_str, "%H:%M").time()
                        with engine.begin() as conn:
                            _insert_performance_with_cast(
                                conn,
                                production_id=prod_by_title[title],
                                theater_id=theater_by_name[theater_name],
                                start_dt=datetime.combine(perf_date, start_t),
                                end_dt=datetime.combine(perf_date, end_t),
                                price_min=float(p_min),
                                price_max=float(p_max),
                                special_tag=tag,
                                actor_role_pairs=[],
                                cast_type="leading",
                                cast_group="A",
                            )
                        inserted += 1
                    except Exception as exc:
                        skipped.append(f"失败：{line}（{exc}）")
                if inserted:
                    admin_log(engine, admin_id, "BATCH_INSERT", "Performance", None, f"批量新增场次 {inserted} 个")
                st.success(f"批量新增场次完成：成功 {inserted} 个，跳过/失败 {len(skipped)} 个。")
                if skipped:
                    st.caption("；".join(skipped[:10]))
                st.rerun()

    with tab_edit:
        st.markdown("### 修改演出信息")
        edit_prod_tab, edit_perf_tab = st.tabs(["修改剧目", "修改场次"])
        with edit_prod_tab:
            productions = query_df(engine, "SELECT production_id, title, category, duration_min, language, version FROM Production ORDER BY title")
            if productions.empty:
                st.info("暂无可修改剧目。")
            else:
                prod_options = {f"{r.title} / {r.version}": int(r.production_id) for r in productions.itertuples()}
                selected_label = st.selectbox("选择剧目", list(prod_options.keys()), key="edit_prod_select")
                selected_id = prod_options[selected_label]
                current = productions[productions["production_id"] == selected_id].iloc[0]
                categories = _existing_values("Production", "category")
                languages = _existing_values("Production", "language")
                if str(current["category"]) not in categories:
                    categories.append(str(current["category"]))
                if str(current["language"]) not in languages:
                    languages.append(str(current["language"]))
                with st.form("edit_production_form"):
                    new_title = st.text_input("剧目名称", value=str(current["title"]))
                    new_category = st.selectbox("剧种", sorted(categories), index=sorted(categories).index(str(current["category"])), key="edit_prod_category")
                    new_duration = st.number_input("时长/分钟", min_value=1, value=int(current["duration_min"]))
                    new_language = st.selectbox("语言", sorted(languages), index=sorted(languages).index(str(current["language"])), key="edit_prod_language")
                    versions = ["original", "revival", "tour", "limited"]
                    new_version = st.selectbox("版本", versions, index=versions.index(str(current["version"])) if str(current["version"]) in versions else 0)
                    if st.form_submit_button("保存剧目修改", type="primary"):
                        duplicate = query_df(
                            engine,
                            "SELECT COUNT(*) AS cnt FROM Production WHERE title = :title AND production_id <> :pid",
                            {"title": new_title.strip(), "pid": selected_id},
                        ).iloc[0]
                        if not new_title.strip():
                            st.error("剧目名称不能为空。")
                        elif int(duplicate["cnt"]):
                            st.error("同名剧目已存在，不能保存。")
                        else:
                            execute_sql(
                                engine,
                                """
                                UPDATE Production
                                SET title = :title, category = :category, duration_min = :duration,
                                    language = :language, version = :version
                                WHERE production_id = :pid
                                """,
                                {"title": new_title.strip(), "category": new_category, "duration": int(new_duration), "language": new_language, "version": new_version, "pid": selected_id},
                            )
                            admin_log(engine, admin_id, "UPDATE", "Production", selected_id, f"修改剧目：{new_title.strip()}")
                            st.success("剧目信息已更新。")
                            st.rerun()

        with edit_perf_tab:
            perf_df = query_df(engine, "SELECT performance_id, title, theater_name, start_time, end_time, price_min, price_max, special_tag FROM v_public_performance_info ORDER BY start_time DESC")
            prod_options, theater_options, _ = _admin_option_maps(engine)
            if perf_df.empty:
                st.info("暂无可修改场次。")
            else:
                perf_options = {f"{r.title} / {r.theater_name} / {fmt_dt(r.start_time)}": int(r.performance_id) for r in perf_df.itertuples()}
                perf_label = st.selectbox("选择场次", list(perf_options.keys()), key="edit_perf_select")
                perf_id = perf_options[perf_label]
                current = perf_df[perf_df["performance_id"] == perf_id].iloc[0]
                raw = query_df(engine, "SELECT production_id, theater_id, start_time, end_time, price_min, price_max, special_tag FROM Performance WHERE performance_id = :pid", {"pid": perf_id}).iloc[0]
                theater_labels = list(theater_options.keys())
                current_theater_label = next((label for label, val in theater_options.items() if val == int(raw["theater_id"])), theater_labels[0]) if theater_labels else None
                tag_values = _existing_values("Performance", "special_tag")
                tag_options = ["无"] + tag_values
                current_tag = "无" if pd.isna(raw["special_tag"]) or str(raw["special_tag"]).strip() == "" else str(raw["special_tag"])
                if current_tag not in tag_options:
                    tag_options.append(current_tag)
                with st.form("edit_performance_form"):
                    st.caption(f"剧目：{plain_text(current['title'])}")
                    theater_label = st.selectbox("剧院", theater_labels, index=theater_labels.index(current_theater_label), key="edit_perf_theater")
                    start_dt_current = pd.to_datetime(raw["start_time"]).to_pydatetime()
                    end_dt_current = pd.to_datetime(raw["end_time"]).to_pydatetime()
                    perf_date = st.date_input("演出日期", value=start_dt_current.date(), key="edit_perf_date")
                    start_t = st.time_input("开始时间", value=start_dt_current.time(), key="edit_perf_start")
                    end_t = st.time_input("结束时间", value=end_dt_current.time(), key="edit_perf_end")
                    price_min = st.number_input("最低票价", min_value=0.0, value=float(raw["price_min"]), step=10.0, key="edit_perf_price_min")
                    price_max = st.number_input("最高票价", min_value=0.0, value=float(raw["price_max"]), step=10.0, key="edit_perf_price_max")
                    special_tag = st.selectbox("特殊标签", tag_options, index=tag_options.index(current_tag), key="edit_perf_tag")
                    if st.form_submit_button("保存场次修改", type="primary"):
                        execute_sql(
                            engine,
                            """
                            UPDATE Performance
                            SET theater_id = :theater_id, start_time = :start_time, end_time = :end_time,
                                price_min = :price_min, price_max = :price_max, special_tag = :special_tag
                            WHERE performance_id = :pid
                            """,
                            {
                                "theater_id": theater_options[theater_label],
                                "start_time": datetime.combine(perf_date, start_t),
                                "end_time": datetime.combine(perf_date, end_t),
                                "price_min": float(price_min),
                                "price_max": float(price_max),
                                "special_tag": None if special_tag == "无" else special_tag,
                                "pid": perf_id,
                            },
                        )
                        admin_log(engine, admin_id, "UPDATE", "Performance", perf_id, f"修改场次：{perf_label}")
                        st.success("场次信息已更新。")
                        st.rerun()

    with tab_basic:
        b1, b2, b3, b4 = st.tabs(["剧院", "餐馆", "演员", "交通"])
        with b1:
            with st.form("add_theater"):
                theater_name = st.text_input("剧院名称")
                city_values = _existing_values("Theater", "city")
                city = _custom_or_existing("城市", city_values, default="上海", key="theater_add_city")
                district_values = _existing_values("Theater", "district")
                district = _custom_or_existing("区域", district_values, default="黄浦区", key="theater_add_district")
                address = st.text_input("地址")
                submitted = st.form_submit_button("新增剧院")
                if submitted:
                    if not theater_name.strip() or not address.strip():
                        st.error("剧院名称和地址不能为空。")
                    else:
                        try:
                            execute_sql(engine, "INSERT INTO Theater(theater_name, city, district, address) VALUES(:name, :city, :district, :address)", {"name": theater_name.strip(), "city": city, "district": district, "address": address.strip()})
                            admin_log(engine, admin_id, "INSERT", "Theater", None, f"新增剧院：{theater_name.strip()}")
                            st.success("剧院已新增。")
                            st.rerun()
                        except SQLAlchemyError as exc:
                            st.error("新增剧院失败。")
                            st.caption(str(exc))
            theaters = query_df(engine, "SELECT theater_id, theater_name, city, district, address FROM Theater ORDER BY theater_id DESC")
            show_dataframe(theaters, height=220)
            theater_del_options = {f"{r.theater_name} / {r.district}": int(r.theater_id) for r in theaters.itertuples()}
            selected = st.multiselect("删除剧院", list(theater_del_options.keys()), key="basic_delete_theaters")
            if st.button("删除选中剧院", key="basic_delete_theaters_btn"):
                try:
                    for label in selected:
                        execute_sql(engine, "DELETE FROM Theater WHERE theater_id = :id", {"id": theater_del_options[label]})
                        admin_log(engine, admin_id, "DELETE", "Theater", theater_del_options[label], f"删除剧院：{label}")
                    st.success(f"已删除 {len(selected)} 个剧院。")
                    st.rerun()
                except SQLAlchemyError as exc:
                    st.error("删除剧院失败，通常是因为仍有关联场次或餐馆/交通方案。")
                    st.caption(str(exc))

        with b2:
            theaters = query_df(engine, "SELECT theater_id, theater_name, district FROM Theater ORDER BY theater_name")
            theater_options = {f"{r.theater_name} / {r.district}": int(r.theater_id) for r in theaters.itertuples()}
            if not theater_options:
                st.info("请先新增剧院。")
            else:
                with st.form("add_restaurant"):
                    theater_label = st.selectbox("所属剧院", list(theater_options.keys()))
                    restaurant_name = st.text_input("餐馆名称")
                    category = _custom_or_existing("餐馆类型", _existing_values("Nearby_Restaurant", "category"), default="简餐", key="restaurant_add_category")
                    avg_price = st.number_input("人均价格", min_value=0.0, value=80.0, step=5.0)
                    distance_m = st.number_input("到剧院距离/米", min_value=0, value=500, step=50)
                    price_tier = st.selectbox("价格档位", ["low", "mid", "high"], index=1)
                    submitted = st.form_submit_button("新增餐馆")
                    if submitted:
                        if not restaurant_name.strip():
                            st.error("餐馆名称不能为空。")
                        else:
                            try:
                                execute_sql(
                                    engine,
                                    """
                                    INSERT INTO Nearby_Restaurant(theater_id, restaurant_name, category, avg_price, distance_m, price_tier)
                                    VALUES(:theater_id, :name, :category, :avg_price, :distance_m, :price_tier)
                                    """,
                                    {"theater_id": theater_options[theater_label], "name": restaurant_name.strip(), "category": category, "avg_price": float(avg_price), "distance_m": int(distance_m), "price_tier": price_tier},
                                )
                                admin_log(engine, admin_id, "INSERT", "Nearby_Restaurant", None, f"新增餐馆：{restaurant_name.strip()}")
                                st.success("餐馆已新增。")
                                st.rerun()
                            except SQLAlchemyError as exc:
                                st.error("新增餐馆失败。")
                                st.caption(str(exc))
            restaurants = query_df(engine, "SELECT nr.restaurant_id, nr.restaurant_name, nr.category, nr.avg_price, nr.distance_m, nr.price_tier, t.theater_name FROM Nearby_Restaurant nr JOIN Theater t ON nr.theater_id = t.theater_id ORDER BY nr.restaurant_id DESC")
            show_dataframe(restaurants, height=220)
            restaurant_del_options = {f"{r.restaurant_name} / {r.theater_name}": int(r.restaurant_id) for r in restaurants.itertuples()}
            selected = st.multiselect("删除餐馆", list(restaurant_del_options.keys()), key="basic_delete_restaurants")
            if st.button("删除选中餐馆", key="basic_delete_restaurants_btn"):
                try:
                    for label in selected:
                        execute_sql(engine, "DELETE FROM Nearby_Restaurant WHERE restaurant_id = :id", {"id": restaurant_del_options[label]})
                        admin_log(engine, admin_id, "DELETE", "Nearby_Restaurant", restaurant_del_options[label], f"删除餐馆：{label}")
                    st.success(f"已删除 {len(selected)} 个餐馆。")
                    st.rerun()
                except SQLAlchemyError as exc:
                    st.error("删除餐馆失败。")
                    st.caption(str(exc))

        with b3:
            with st.form("add_actor"):
                actor_name = st.text_input("演员姓名")
                gender = st.selectbox("性别", ["other", "male", "female"])
                submitted = st.form_submit_button("新增演员")
                if submitted:
                    if not actor_name.strip():
                        st.error("演员姓名不能为空。")
                    else:
                        try:
                            execute_sql(engine, "INSERT INTO Actor(actor_name, gender) VALUES(:name, :gender)", {"name": actor_name.strip(), "gender": gender})
                            admin_log(engine, admin_id, "INSERT", "Actor", None, f"新增演员：{actor_name.strip()}")
                            st.success("演员已新增。")
                            st.rerun()
                        except SQLAlchemyError as exc:
                            st.error("新增演员失败。")
                            st.caption(str(exc))
            actors = query_df(engine, "SELECT actor_id, actor_name, gender FROM Actor ORDER BY actor_id DESC")
            show_dataframe(actors, height=220)
            actor_del_options = {str(r.actor_name): int(r.actor_id) for r in actors.itertuples()}
            selected = st.multiselect("删除演员", list(actor_del_options.keys()), key="basic_delete_actors")
            if st.button("删除选中演员", key="basic_delete_actors_btn"):
                try:
                    for label in selected:
                        execute_sql(engine, "DELETE FROM Actor WHERE actor_id = :id", {"id": actor_del_options[label]})
                        admin_log(engine, admin_id, "DELETE", "Actor", actor_del_options[label], f"删除演员：{label}")
                    st.success(f"已删除 {len(selected)} 个演员。")
                    st.rerun()
                except SQLAlchemyError as exc:
                    st.error("删除演员失败。")
                    st.caption(str(exc))

        with b4:
            theaters = query_df(engine, "SELECT theater_id, theater_name, district FROM Theater ORDER BY theater_name")
            theater_options = {f"{r.theater_name} / {r.district}": int(r.theater_id) for r in theaters.itertuples()}
            if not theater_options:
                st.info("请先新增剧院。")
            else:
                with st.form("add_transport"):
                    theater_label = st.selectbox("所属剧院", list(theater_options.keys()))
                    transport_type = st.selectbox("交通方式", ["subway", "bus", "taxi", "walk"])
                    estimated_time = st.number_input("预计时间/分钟", min_value=0, value=30, step=5)
                    estimated_cost = st.number_input("预计费用", min_value=0.0, value=6.0, step=1.0)
                    suitable_values = _existing_values("Transport_Option", "suitable_district") or _existing_values("Theater", "district")
                    suitable_district = st.selectbox("适合出发区", sorted(set(suitable_values + ["黄浦区", "徐汇区", "静安区", "长宁区", "浦东新区", "普陀区"])))
                    submitted = st.form_submit_button("新增交通方案")
                    if submitted:
                        try:
                            execute_sql(
                                engine,
                                """
                                INSERT INTO Transport_Option(theater_id, transport_type, estimated_time, estimated_cost, suitable_district)
                                VALUES(:theater_id, :transport_type, :estimated_time, :estimated_cost, :suitable_district)
                                """,
                                {"theater_id": theater_options[theater_label], "transport_type": transport_type, "estimated_time": int(estimated_time), "estimated_cost": float(estimated_cost), "suitable_district": suitable_district},
                            )
                            admin_log(engine, admin_id, "INSERT", "Transport_Option", None, f"新增交通方案：{theater_label} / {transport_type}")
                            st.success("交通方案已新增。")
                            st.rerun()
                        except SQLAlchemyError as exc:
                            st.error("新增交通方案失败。")
                            st.caption(str(exc))
            transports = query_df(engine, "SELECT tr.transport_id, tr.transport_type, tr.estimated_time, tr.estimated_cost, tr.suitable_district, t.theater_name FROM Transport_Option tr JOIN Theater t ON tr.theater_id = t.theater_id ORDER BY tr.transport_id DESC")
            show_dataframe(transports, height=220)
            transport_del_options = {f"{r.transport_type} / {r.theater_name} / {r.suitable_district}": int(r.transport_id) for r in transports.itertuples()}
            selected = st.multiselect("删除交通方案", list(transport_del_options.keys()), key="basic_delete_transports")
            if st.button("删除选中交通方案", key="basic_delete_transports_btn"):
                try:
                    for label in selected:
                        execute_sql(engine, "DELETE FROM Transport_Option WHERE transport_id = :id", {"id": transport_del_options[label]})
                        admin_log(engine, admin_id, "DELETE", "Transport_Option", transport_del_options[label], f"删除交通方案：{label}")
                    st.success(f"已删除 {len(selected)} 个交通方案。")
                    st.rerun()
                except SQLAlchemyError as exc:
                    st.error("删除交通方案失败。")
                    st.caption(str(exc))

    with tab_delete:
        st.markdown("### 批量删除")
        st.caption("这里按数据类型批量撤销；有关联数据时，数据库会按外键规则级联或拒绝删除。")
        d1, d2 = st.columns(2)
        with d1:
            productions = query_df(engine, "SELECT production_id, title, version FROM Production ORDER BY title")
            prod_del_options = {f"{r.title} / {r.version}": int(r.production_id) for r in productions.itertuples()}
            selected_prod = st.multiselect("按剧目批量删除", list(prod_del_options.keys()))
            if st.button("删除选中剧目", type="primary"):
                try:
                    for label in selected_prod:
                        execute_sql(engine, "DELETE FROM Production WHERE production_id = :id", {"id": prod_del_options[label]})
                        admin_log(engine, admin_id, "DELETE", "Production", prod_del_options[label], f"删除剧目：{label}")
                    st.success(f"已删除 {len(selected_prod)} 个剧目。")
                    st.rerun()
                except SQLAlchemyError as exc:
                    st.error("删除剧目失败。")
                    st.caption(str(exc))

            performances = query_df(engine, "SELECT performance_id, title, theater_name, start_time FROM v_public_performance_info ORDER BY start_time DESC")
            perf_del_options = {f"{r.title} / {r.theater_name} / {fmt_dt(r.start_time)}": int(r.performance_id) for r in performances.itertuples()}
            selected_perf = st.multiselect("批量删除场次", list(perf_del_options.keys()))
            if st.button("删除选中场次"):
                try:
                    for label in selected_perf:
                        execute_sql(engine, "DELETE FROM Performance WHERE performance_id = :id", {"id": perf_del_options[label]})
                        admin_log(engine, admin_id, "DELETE", "Performance", perf_del_options[label], f"删除场次：{label}")
                    st.success(f"已删除 {len(selected_perf)} 个场次。")
                    st.rerun()
                except SQLAlchemyError as exc:
                    st.error("删除场次失败。")
                    st.caption(str(exc))
        with d2:
            theaters = query_df(engine, "SELECT theater_id, theater_name, district FROM Theater ORDER BY theater_name")
            theater_del_options = {f"{r.theater_name} / {r.district}": int(r.theater_id) for r in theaters.itertuples()}
            selected_theater = st.multiselect("批量删除剧院", list(theater_del_options.keys()))
            if st.button("删除选中剧院"):
                try:
                    for label in selected_theater:
                        execute_sql(engine, "DELETE FROM Theater WHERE theater_id = :id", {"id": theater_del_options[label]})
                        admin_log(engine, admin_id, "DELETE", "Theater", theater_del_options[label], f"删除剧院：{label}")
                    st.success(f"已删除 {len(selected_theater)} 个剧院。")
                    st.rerun()
                except SQLAlchemyError as exc:
                    st.error("删除剧院失败，通常是因为该剧院仍有关联场次。请先删除相关场次。")
                    st.caption(str(exc))

            restaurants = query_df(engine, "SELECT nr.restaurant_id, nr.restaurant_name, t.theater_name FROM Nearby_Restaurant nr JOIN Theater t ON nr.theater_id = t.theater_id ORDER BY nr.restaurant_name")
            restaurant_del_options = {f"{r.restaurant_name} / {r.theater_name}": int(r.restaurant_id) for r in restaurants.itertuples()}
            selected_restaurant = st.multiselect("批量删除餐馆", list(restaurant_del_options.keys()))
            if st.button("删除选中餐馆"):
                try:
                    for label in selected_restaurant:
                        execute_sql(engine, "DELETE FROM Nearby_Restaurant WHERE restaurant_id = :id", {"id": restaurant_del_options[label]})
                        admin_log(engine, admin_id, "DELETE", "Nearby_Restaurant", restaurant_del_options[label], f"删除餐馆：{label}")
                    st.success(f"已删除 {len(selected_restaurant)} 个餐馆。")
                    st.rerun()
                except SQLAlchemyError as exc:
                    st.error("删除餐馆失败。")
                    st.caption(str(exc))

            actors = query_df(engine, "SELECT actor_id, actor_name FROM Actor ORDER BY actor_name")
            actor_del_options = {str(r.actor_name): int(r.actor_id) for r in actors.itertuples()}
            selected_actor = st.multiselect("批量删除演员", list(actor_del_options.keys()))
            if st.button("删除选中演员"):
                try:
                    for label in selected_actor:
                        execute_sql(engine, "DELETE FROM Actor WHERE actor_id = :id", {"id": actor_del_options[label]})
                        admin_log(engine, admin_id, "DELETE", "Actor", actor_del_options[label], f"删除演员：{label}")
                    st.success(f"已删除 {len(selected_actor)} 个演员。")
                    st.rerun()
                except SQLAlchemyError as exc:
                    st.error("删除演员失败。")
                    st.caption(str(exc))

            transports = query_df(engine, "SELECT tr.transport_id, tr.transport_type, tr.suitable_district, t.theater_name FROM Transport_Option tr JOIN Theater t ON tr.theater_id = t.theater_id ORDER BY tr.transport_id DESC")
            transport_del_options = {f"{r.transport_type} / {r.theater_name} / {r.suitable_district}": int(r.transport_id) for r in transports.itertuples()}
            selected_transport = st.multiselect("批量删除交通方案", list(transport_del_options.keys()))
            if st.button("删除选中交通方案"):
                try:
                    for label in selected_transport:
                        execute_sql(engine, "DELETE FROM Transport_Option WHERE transport_id = :id", {"id": transport_del_options[label]})
                        admin_log(engine, admin_id, "DELETE", "Transport_Option", transport_del_options[label], f"删除交通方案：{label}")
                    st.success(f"已删除 {len(selected_transport)} 个交通方案。")
                    st.rerun()
                except SQLAlchemyError as exc:
                    st.error("删除交通方案失败。")
                    st.caption(str(exc))

    with tab_log:
        logs = query_df(
            engine,
            """
            SELECT l.log_id, u.username AS admin_username, l.action_type,
                   l.target_table, l.target_id, l.action_time, l.description
            FROM Admin_Log l
            JOIN `User` u ON l.admin_user_id = u.user_id
            ORDER BY l.action_time DESC, l.log_id DESC
            LIMIT 100
            """,
        )
        show_dataframe(logs, height=420)


# =========================
# 页面：SQL 展示台
# =========================

def page_sql_console(engine: Engine) -> None:
    st.title("🔎 SQL 展示台")
    st.markdown("<div class='stage-subtitle'>内置常用数据库检测与展示语句，便于快速查看视图、统计、约束结果和推荐过程输出。</div>", unsafe_allow_html=True)

    samples = {
        "基础表行数检测": """SELECT 'User' AS table_name, COUNT(*) AS rows_count FROM `User`
UNION ALL SELECT 'Production', COUNT(*) FROM Production
UNION ALL SELECT 'Performance', COUNT(*) FROM Performance
UNION ALL SELECT 'Theater', COUNT(*) FROM Theater
UNION ALL SELECT 'Actor', COUNT(*) FROM Actor
UNION ALL SELECT 'Watch_Record', COUNT(*) FROM Watch_Record
UNION ALL SELECT 'Planned_Performance', COUNT(*) FROM Planned_Performance;""",
        "重复剧目名称检测": "SELECT title, COUNT(*) AS duplicate_count FROM Production GROUP BY title HAVING COUNT(*) > 1 ORDER BY duplicate_count DESC;",
        "未来场次缺少卡司检测": """SELECT v.performance_id, v.title, v.theater_name, v.start_time
FROM v_public_performance_info v
LEFT JOIN Performance_Cast pc ON v.performance_id = pc.performance_id
WHERE v.start_time >= NOW()
GROUP BY v.performance_id, v.title, v.theater_name, v.start_time
HAVING COUNT(pc.actor_id) = 0
ORDER BY v.start_time;""",
        "剧院配套完整性检测": """SELECT t.theater_id, t.theater_name, t.district,
       COUNT(DISTINCT nr.restaurant_id) AS restaurant_count,
       COUNT(DISTINCT tr.transport_id) AS transport_count
FROM Theater t
LEFT JOIN Nearby_Restaurant nr ON t.theater_id = nr.theater_id
LEFT JOIN Transport_Option tr ON t.theater_id = tr.theater_id
GROUP BY t.theater_id, t.theater_name, t.district
ORDER BY restaurant_count, transport_count, t.theater_name;""",
        "用户观剧日历": "SELECT * FROM v_user_calendar ORDER BY user_id, start_time;",
        "演出信息汇总": "SELECT * FROM v_public_performance_info ORDER BY start_time;",
        "用户画像视图": "SELECT * FROM v_user_preference_profile ORDER BY user_id;",
        "混合推荐视图": "SELECT * FROM v_hybrid_recommendation ORDER BY user_id, start_time;",
        "行程辅助视图": "SELECT * FROM v_planned_trip_assistance ORDER BY user_id, start_time;",
        "观众类型函数": "SELECT user_id, username, fn_audience_type(user_id) AS audience_type FROM `User` ORDER BY user_id;",
        "推荐来源统计": "SELECT recommendation_source, COUNT(*) AS cnt FROM v_hybrid_recommendation GROUP BY recommendation_source ORDER BY cnt DESC;",
        "计划状态统计": "SELECT status, COUNT(*) AS cnt FROM Planned_Performance GROUP BY status ORDER BY cnt DESC;",
        "管理员操作日志": "SELECT * FROM Admin_Log ORDER BY action_time DESC, log_id DESC LIMIT 100;",
    }
    choice = st.selectbox("选择展示 SQL", list(samples.keys()))
    sql = st.text_area("SQL", value=samples[choice], height=160)

    if st.button("执行查询", type="primary"):
        stripped = sql.strip().lower()
        if not (stripped.startswith("select") or stripped.startswith("with") or stripped.startswith("call sp_recommend_by_profile")):
            st.error("为了避免误操作，此处只允许 SELECT/WITH 查询，或 CALL sp_recommend_by_profile。")
            return
        try:
            df = query_df(engine, sql)
            show_dataframe(df, height=480)
        except SQLAlchemyError as exc:
            st.error("执行失败。")
            st.caption(str(exc))


# =========================
# 主程序
# =========================

def main() -> None:
    config = sidebar_db_config()
    engine = engine_from_config(config)
    if engine is None:
        st.stop()

    try:
        ensure_auth_table(engine)
        ensure_teacher_test_accounts(engine)
    except SQLAlchemyError as exc:
        st.error("登录账号表初始化失败。请确认当前数据库用户有 CREATE TABLE 权限。")
        st.caption(str(exc))
        st.stop()

    st.sidebar.success("已连接 StageBook 数据库")

    user = current_user()
    if not user:
        page_auth(engine)
        return

    st.sidebar.markdown("---")
    render_user_sidebar(engine, user)
    st.sidebar.markdown("---")

    role = user.get("role", "user")

    requested_page = st.session_state.pop("nav_page", None)

    if role == "admin":
        admin_pages = ["管理员总览", "演出信息汇总", "演出信息管理", "SQL 展示台"]
        page = st.sidebar.radio(
            "功能导航",
            admin_pages,
            index=admin_pages.index(requested_page) if requested_page in admin_pages else 0,
        )
        st.sidebar.caption("管理员视角：维护基础数据、查看全局统计和审计日志。")
    else:
        user_pages = ["我的首页", "演出信息汇总", "我的观剧管理", "用户偏好画像", "混合推荐引擎", "场景化行程辅助"]
        page = st.sidebar.radio(
            "功能导航",
            user_pages,
            index=user_pages.index(requested_page) if requested_page in user_pages else 0,
        )
        st.sidebar.caption("用户视角：只管理当前账号自己的观剧、偏好、推荐和行程。")

    try:
        if page == "我的首页":
            page_user_home(engine, user)
        elif page == "管理员总览":
            page_dashboard(engine)
        elif page == "演出信息汇总":
            page_public_performances(engine)
        elif page == "我的观剧管理":
            page_user_management(engine, int(user["user_id"]))
        elif page == "用户偏好画像":
            page_profiles(engine, int(user["user_id"]))
        elif page == "混合推荐引擎":
            page_recommendations(engine, int(user["user_id"]))
        elif page == "场景化行程辅助":
            page_trip_assistance(engine, int(user["user_id"]))
        elif page == "演出信息管理":
            if role != "admin":
                st.error("当前账号没有管理员权限。")
            else:
                page_admin(engine)
        elif page == "SQL 展示台":
            if role != "admin":
                st.error("当前账号没有 SQL 展示台权限。")
            else:
                page_sql_console(engine)
    except SQLAlchemyError as exc:
        st.error("数据库操作失败。")
        st.caption(str(exc))
    except Exception as exc:
        st.error("页面运行出错。")
        st.caption(str(exc))


if __name__ == "__main__":
    main()

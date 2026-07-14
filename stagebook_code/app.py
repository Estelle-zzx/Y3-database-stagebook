import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime, date
import random
import json

# ─── Page Config ──────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="StageBook · 观剧手记",
    page_icon="🎭",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ─── Custom CSS ───────────────────────────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Noto+Serif+SC:wght@400;600;700;900&family=DM+Mono:wght@400;500&family=Cormorant+Garamond:ital,wght@0,400;0,600;1,400;1,600&display=swap');

:root {
    --ink:       #1a1008;
    --parchment: #f5efe4;
    --cream:     #faf6ef;
    --gold:      #c9933a;
    --gold-lt:   #e8c97a;
    --crimson:   #8b1a2a;
    --sage:      #4a6741;
    --mist:      #8a9ba8;
    --card-bg:   rgba(255,253,248,0.92);
    --border:    rgba(201,147,58,0.25);
    --shadow:    0 4px 24px rgba(26,16,8,0.12);
}

html, body, [class*="css"] {
    font-family: 'Noto Serif SC', serif;
    color: var(--ink);
}

/* Hide Streamlit chrome */
#MainMenu, footer, header { display: none !important; }
.block-container { padding: 0 !important; max-width: 100% !important; }

/* ── Background ── */
.stApp {
    background: var(--cream);
    background-image:
        radial-gradient(circle at 15% 20%, rgba(201,147,58,0.06) 0%, transparent 50%),
        radial-gradient(circle at 85% 80%, rgba(139,26,42,0.05) 0%, transparent 50%),
        url("data:image/svg+xml,%3Csvg width='60' height='60' viewBox='0 0 60 60' xmlns='http://www.w3.org/2000/svg'%3E%3Cg fill='none' fill-rule='evenodd'%3E%3Cg fill='%23c9933a' fill-opacity='0.03'%3E%3Cpath d='M36 34v-4h-2v4h-4v2h4v4h2v-4h4v-2h-4zm0-30V0h-2v4h-4v2h4v4h2V6h4V4h-4zM6 34v-4H4v4H0v2h4v4h2v-4h4v-2H6zM6 4V0H4v4H0v2h4v4h2V6h4V4H6z'/%3E%3C/g%3E%3C/g%3E%3C/svg%3E");
}

/* ── Sidebar ── */
[data-testid="stSidebar"] {
    background: var(--ink) !important;
    border-right: 1px solid rgba(201,147,58,0.3);
}
[data-testid="stSidebar"] * { color: var(--parchment) !important; }
[data-testid="stSidebar"] .stSelectbox label,
[data-testid="stSidebar"] .stRadio label { color: var(--gold-lt) !important; font-size: 0.8rem; letter-spacing: 0.1em; text-transform: uppercase; }
[data-testid="stSidebar"] select,
[data-testid="stSidebar"] [data-baseweb="select"] { background: rgba(201,147,58,0.1) !important; border: 1px solid rgba(201,147,58,0.3) !important; color: var(--parchment) !important; }

/* Sidebar nav buttons */
.nav-btn {
    display: flex; align-items: center; gap: 12px;
    padding: 12px 20px; margin: 4px 0;
    border-radius: 6px; cursor: pointer;
    transition: all 0.2s;
    font-size: 0.95rem; letter-spacing: 0.03em;
    color: rgba(245,239,228,0.7);
    border: 1px solid transparent;
}
.nav-btn:hover { background: rgba(201,147,58,0.15); color: var(--gold-lt); border-color: rgba(201,147,58,0.2); }
.nav-btn.active { background: rgba(201,147,58,0.2); color: var(--gold); border-color: rgba(201,147,58,0.4); font-weight: 600; }
.nav-icon { font-size: 1.2rem; }

/* ── Page header ── */
.page-header {
    padding: 48px 56px 32px;
    border-bottom: 1px solid var(--border);
    margin-bottom: 0;
}
.page-title {
    font-family: 'Cormorant Garamond', serif;
    font-size: 2.8rem; font-weight: 600;
    color: var(--ink); line-height: 1;
    letter-spacing: -0.01em;
}
.page-title em { color: var(--gold); font-style: italic; }
.page-subtitle { font-size: 0.85rem; color: var(--mist); margin-top: 6px; letter-spacing: 0.08em; text-transform: uppercase; }

/* ── Content area ── */
.content-area { padding: 36px 56px 56px; }

/* ── Cards ── */
.card {
    background: var(--card-bg);
    border: 1px solid var(--border);
    border-radius: 12px;
    padding: 28px 32px;
    box-shadow: var(--shadow);
    backdrop-filter: blur(8px);
    margin-bottom: 20px;
    position: relative;
    overflow: hidden;
}
.card::before {
    content: '';
    position: absolute; top: 0; left: 0;
    width: 3px; height: 100%;
    background: linear-gradient(to bottom, var(--gold), var(--crimson));
}
.card-title {
    font-family: 'Cormorant Garamond', serif;
    font-size: 1.3rem; font-weight: 600;
    color: var(--ink); margin-bottom: 4px;
}
.card-meta { font-size: 0.8rem; color: var(--mist); font-family: 'DM Mono', monospace; }

/* ── Stat boxes ── */
.stat-row { display: flex; gap: 20px; margin-bottom: 28px; flex-wrap: wrap; }
.stat-box {
    flex: 1; min-width: 130px;
    background: var(--card-bg);
    border: 1px solid var(--border);
    border-radius: 10px; padding: 20px 22px;
    box-shadow: var(--shadow);
    text-align: center;
}
.stat-num {
    font-family: 'Cormorant Garamond', serif;
    font-size: 2.4rem; font-weight: 700;
    color: var(--gold); line-height: 1;
}
.stat-label { font-size: 0.78rem; color: var(--mist); margin-top: 6px; letter-spacing: 0.06em; }

/* ── Tags / badges ── */
.tag {
    display: inline-block;
    padding: 3px 10px; border-radius: 20px;
    font-size: 0.75rem; font-family: 'DM Mono', monospace;
    letter-spacing: 0.04em; margin: 2px;
}
.tag-gold    { background: rgba(201,147,58,0.15);  color: var(--gold);    border: 1px solid rgba(201,147,58,0.3); }
.tag-crimson { background: rgba(139,26,42,0.12);   color: var(--crimson); border: 1px solid rgba(139,26,42,0.25); }
.tag-sage    { background: rgba(74,103,65,0.12);   color: var(--sage);    border: 1px solid rgba(74,103,65,0.25); }
.tag-mist    { background: rgba(138,155,168,0.15); color: var(--mist);    border: 1px solid rgba(138,155,168,0.25); }

/* ── Score star ── */
.score-display {
    font-family: 'Cormorant Garamond', serif;
    font-size: 1.6rem; font-weight: 700; color: var(--gold);
}

/* ── Rec card ── */
.rec-card {
    background: var(--card-bg);
    border: 1px solid var(--border);
    border-radius: 10px; padding: 22px 26px;
    box-shadow: var(--shadow);
    margin-bottom: 14px;
    display: flex; align-items: flex-start; gap: 20px;
    position: relative;
}
.rec-score-badge {
    width: 52px; height: 52px; border-radius: 50%;
    background: linear-gradient(135deg, var(--gold), var(--crimson));
    display: flex; align-items: center; justify-content: center;
    flex-shrink: 0;
    font-family: 'Cormorant Garamond', serif;
    font-size: 1.25rem; font-weight: 700; color: white;
}
.rec-info { flex: 1; }
.rec-title { font-size: 1.1rem; font-weight: 600; color: var(--ink); margin-bottom: 4px; }
.rec-meta { font-size: 0.78rem; color: var(--mist); font-family: 'DM Mono', monospace; }
.rec-reason {
    font-size: 0.82rem; color: var(--sage);
    margin-top: 8px; padding: 6px 10px;
    background: rgba(74,103,65,0.08); border-radius: 4px;
    border-left: 2px solid var(--sage);
    font-style: italic;
}
.rec-price { font-size: 0.9rem; color: var(--crimson); font-weight: 600; font-family: 'DM Mono', monospace; }

/* ── Trip card ── */
.trip-card {
    background: linear-gradient(135deg, rgba(26,16,8,0.97), rgba(60,30,10,0.95));
    border: 1px solid rgba(201,147,58,0.4);
    border-radius: 12px; padding: 28px 32px;
    color: var(--parchment); margin-bottom: 20px;
}
.trip-title { font-family: 'Cormorant Garamond', serif; font-size: 1.6rem; color: var(--gold); margin-bottom: 6px; }
.trip-info-grid { display: grid; grid-template-columns: 1fr 1fr; gap: 18px; margin-top: 18px; }
.trip-info-item label { font-size: 0.72rem; color: var(--gold-lt); text-transform: uppercase; letter-spacing: 0.1em; display: block; margin-bottom: 4px; }
.trip-info-item span { font-size: 0.95rem; color: var(--parchment); }

/* ── Calendar ── */
.cal-item {
    display: flex; align-items: center; gap: 16px;
    padding: 14px 18px; border-radius: 8px;
    border: 1px solid var(--border);
    background: var(--card-bg); margin-bottom: 10px;
}
.cal-date {
    width: 52px; text-align: center; flex-shrink: 0;
    font-family: 'Cormorant Garamond', serif;
}
.cal-date .day { font-size: 1.8rem; font-weight: 700; color: var(--gold); line-height: 1; }
.cal-date .month { font-size: 0.7rem; color: var(--mist); text-transform: uppercase; letter-spacing: 0.06em; }
.cal-info { flex: 1; }
.cal-info .title { font-size: 1rem; font-weight: 600; color: var(--ink); }
.cal-info .sub { font-size: 0.78rem; color: var(--mist); font-family: 'DM Mono', monospace; margin-top: 2px; }
.status-watched { color: var(--sage); background: rgba(74,103,65,0.12); padding: 2px 8px; border-radius: 10px; font-size: 0.72rem; font-family: 'DM Mono', monospace; }
.status-planned { color: var(--gold); background: rgba(201,147,58,0.12); padding: 2px 8px; border-radius: 10px; font-size: 0.72rem; font-family: 'DM Mono', monospace; }
.status-booked  { color: var(--crimson); background: rgba(139,26,42,0.12); padding: 2px 8px; border-radius: 10px; font-size: 0.72rem; font-family: 'DM Mono', monospace; }

/* ── Form ── */
.stTextInput input, .stSelectbox select, .stNumberInput input, .stDateInput input {
    border: 1px solid var(--border) !important;
    border-radius: 6px !important;
    background: var(--card-bg) !important;
    font-family: 'Noto Serif SC', serif !important;
}
.stTextInput input:focus, .stSelectbox select:focus {
    border-color: var(--gold) !important;
    box-shadow: 0 0 0 2px rgba(201,147,58,0.15) !important;
}

/* ── Buttons ── */
.stButton button {
    background: linear-gradient(135deg, var(--gold), #b8812e) !important;
    color: white !important; border: none !important;
    font-family: 'Noto Serif SC', serif !important;
    font-weight: 600 !important; letter-spacing: 0.04em !important;
    border-radius: 6px !important;
    padding: 8px 20px !important;
    transition: all 0.2s !important;
}
.stButton button:hover { opacity: 0.88 !important; transform: translateY(-1px) !important; box-shadow: 0 4px 16px rgba(201,147,58,0.3) !important; }

/* ── Table ── */
.dataframe { border-collapse: collapse !important; width: 100% !important; font-size: 0.88rem !important; }
.dataframe th { background: rgba(201,147,58,0.12) !important; color: var(--ink) !important; font-weight: 600 !important; padding: 10px 14px !important; border-bottom: 2px solid var(--border) !important; }
.dataframe td { padding: 9px 14px !important; border-bottom: 1px solid rgba(201,147,58,0.1) !important; }
.dataframe tr:hover td { background: rgba(201,147,58,0.04) !important; }

/* ── Divider ── */
.ornament { text-align: center; color: var(--gold); margin: 28px 0 20px; font-size: 1.2rem; letter-spacing: 0.4em; opacity: 0.6; }

/* ── Profile badge ── */
.audience-type-badge {
    display: inline-flex; align-items: center; gap: 10px;
    background: linear-gradient(135deg, var(--crimson), #6b1020);
    color: white; padding: 10px 20px; border-radius: 24px;
    font-size: 1rem; font-weight: 600;
    box-shadow: 0 4px 16px rgba(139,26,42,0.3);
    margin-bottom: 20px;
}

/* ── Success/info alerts ── */
.stSuccess, .stInfo, .stWarning {
    border-radius: 8px !important;
    border-left: 3px solid var(--gold) !important;
}

/* Plotly chart container */
.js-plotly-plot { border-radius: 10px; overflow: hidden; }

/* Section divider */
hr { border: none; border-top: 1px solid var(--border); margin: 24px 0; }

/* Scrollbar */
::-webkit-scrollbar { width: 6px; }
::-webkit-scrollbar-track { background: transparent; }
::-webkit-scrollbar-thumb { background: rgba(201,147,58,0.3); border-radius: 3px; }
</style>
""", unsafe_allow_html=True)

# ─── Mock Data ─────────────────────────────────────────────────────────────────
# 模拟数据库数据，实际使用时替换为 MySQL 连接
MOCK_USERS = {
    1: {"username": "shengge_fan", "nickname": "沪上观剧人", "city": "上海", "role": "user",
        "price_preference": "mid", "time_preference": "weekend_evening", "home_district": "静安区",
        "register_time": "2023-03-15"},
    2: {"username": "admin_001", "nickname": "后台管理员", "city": "上海", "role": "admin",
        "price_preference": "premium", "time_preference": "weekend_matinee", "home_district": "黄浦区",
        "register_time": "2022-01-01"},
}

MOCK_WATCH_RECORDS = [
    {"record_id":1, "title":"剧院魅影", "version":"original", "category":"音乐剧", "theater_name":"上海大剧院",
     "start_time":"2024-09-14 19:30", "score":9.5, "status":"watched"},
    {"record_id":2, "title":"猫", "version":"revival", "category":"音乐剧", "theater_name":"美琪大戏院",
     "start_time":"2024-11-02 19:00", "score":8.8, "status":"watched"},
    {"record_id":3, "title":"悲惨世界", "version":"tour", "category":"音乐剧", "theater_name":"上海文化广场",
     "start_time":"2024-12-20 14:30", "score":9.2, "status":"watched"},
    {"record_id":4, "title":"罗密欧与朱丽叶", "version":"original", "category":"话剧", "theater_name":"上海话剧艺术中心",
     "start_time":"2025-01-08 19:30", "score":8.0, "status":"watched"},
    {"record_id":5, "title":"狮子王", "version":"revival", "category":"音乐剧", "theater_name":"上海大剧院",
     "start_time":"2025-02-14 19:00", "score":9.0, "status":"watched"},
]

MOCK_PLANNED = [
    {"performance_id":101, "title":"汉密尔顿", "version":"original", "category":"音乐剧",
     "theater_name":"上海文化广场", "start_time":"2025-05-18 19:00", "end_time":"2025-05-18 21:30",
     "price_min":280, "price_max":880, "status":"booked"},
    {"performance_id":102, "title":"变身怪医", "version":"tour", "category":"音乐剧",
     "theater_name":"美琪大戏院", "start_time":"2025-06-07 14:00", "end_time":"2025-06-07 16:30",
     "price_min":180, "price_max":580, "status":"planned"},
    {"performance_id":103, "title":"芝加哥", "version":"revival", "category":"音乐剧",
     "theater_name":"上海大剧院", "start_time":"2025-07-12 19:30", "end_time":"2025-07-12 22:00",
     "price_min":380, "price_max":1080, "status":"planned"},
]

MOCK_RECOMMENDATIONS = [
    {"performance_id":201, "title":"歌剧院幽灵25周年纪念版", "version":"limited", "category":"音乐剧",
     "language":"中文", "theater_name":"上海文化广场", "district":"徐汇区",
     "start_time":"2025-05-25 19:00", "price_min":380, "price_max":1280,
     "special_tag":"限定版", "match_score":95, "recommendation_source":"profile_based",
     "matched_profile_type":"演员驱动型",
     "recommendation_reason":"匹配喜爱演员出演，同时符合音乐剧剧种偏好"},
    {"performance_id":202, "title":"西区故事", "version":"revival", "category":"音乐剧",
     "language":"中文", "theater_name":"美琪大戏院", "district":"静安区",
     "start_time":"2025-06-14 19:30", "price_min":280, "price_max":780,
     "special_tag":None, "match_score":82, "recommendation_source":"similar_user",
     "matched_profile_type":None,
     "recommendation_reason":"相似用户高度好评，与您观影口味高度契合"},
    {"performance_id":203, "title":"妈妈咪呀！", "version":"tour", "category":"音乐剧",
     "language":"中文", "theater_name":"上海大剧院", "district":"黄浦区",
     "start_time":"2025-06-28 14:00", "price_min":180, "price_max":580,
     "special_tag":"加场", "match_score":74, "recommendation_source":"rule_based",
     "matched_profile_type":None,
     "recommendation_reason":"符合周末场次时间偏好，且为特别加场"},
    {"performance_id":204, "title":"摇滚年代", "version":"original", "category":"音乐剧",
     "language":"中文", "theater_name":"上海文化广场", "district":"徐汇区",
     "start_time":"2025-07-05 19:30", "price_min":280, "price_max":680,
     "special_tag":None, "match_score":68, "recommendation_source":"profile_based",
     "matched_profile_type":"剧种探索型",
     "recommendation_reason":"拓展剧种多样性，偏好区域内场次"},
    {"performance_id":205, "title":"铸魂：亚瑟王传说", "version":"original", "category":"音乐剧",
     "language":"中文", "theater_name":"美琪大戏院", "district":"静安区",
     "start_time":"2025-08-02 19:00", "price_min":360, "price_max":960,
     "special_tag":"首演", "match_score":61, "recommendation_source":"rule_based",
     "matched_profile_type":None,
     "recommendation_reason":"新剧首演特别标签，值得关注"},
]

MOCK_TRIP = {
    "theater_name": "上海文化广场",
    "start_time": "2025-05-18 19:00",
    "end_time": "2025-05-18 21:30",
    "restaurant_name": "精品粤菜楼",
    "restaurant_category": "粤菜",
    "price_tier": "mid",
    "avg_price": 158.0,
    "distance_m": 320,
    "transport_type": "subway",
    "estimated_time": 22,
    "estimated_cost": 6.0,
    "suitable_district": "静安区",
    "suggested_departure_time": "2025-05-18 18:23",
}

MOCK_PREFERENCE = {
    "favorite_actors": "王凯、刘令飞、郑棋元",
    "favorite_categories": "音乐剧、话剧",
    "favorite_languages": "中文、英文",
    "favorite_districts": "上海-静安区、上海-徐汇区",
    "price_preference": "mid",
    "time_preference": "weekend_evening",
    "most_watched_category": "音乐剧",
    "most_watched_actor": "郑棋元",
    "most_visited_theater": "上海文化广场",
    "avg_score": 8.9,
    "total_watch_count": 5,
    "audience_type": "演员驱动型",
}

CATEGORY_STATS = {
    "音乐剧": 4, "话剧": 1,
}

SCORE_DIST = {9.5:1, 8.8:1, 9.2:1, 8.0:1, 9.0:1}

# ─── Session State Init ────────────────────────────────────────────────────────
if "page" not in st.session_state:
    st.session_state.page = "首页"
if "user_id" not in st.session_state:
    st.session_state.user_id = 1
if "logged_in" not in st.session_state:
    st.session_state.logged_in = True

# ─── Helpers ───────────────────────────────────────────────────────────────────
def price_label(p):
    return {"economy":"经济型 · ¥","mid":"中档 · ¥¥","premium":"高端 · ¥¥¥"}.get(p, p)

def time_label(t):
    return {"weekday_evening":"工作日晚场","weekend_evening":"周末晚场","weekend_matinee":"周末日场"}.get(t, t)

def transport_icon(t):
    return {"subway":"🚇","bus":"🚌","taxi":"🚕","walk":"🚶"}.get(t, "🚗")

def score_stars(s):
    filled = int(s / 2)
    return "★" * filled + "☆" * (5 - filled)

def fmt_datetime(dt_str):
    try:
        dt = datetime.strptime(dt_str, "%Y-%m-%d %H:%M")
        weekdays = ["周一","周二","周三","周四","周五","周六","周日"]
        wd = weekdays[dt.weekday()]
        return dt.strftime(f"%Y年%m月%d日 {wd} %H:%M")
    except:
        return dt_str

# ─── Sidebar ───────────────────────────────────────────────────────────────────
with st.sidebar:
    # Logo / brand
    st.markdown("""
    <div style="padding: 32px 24px 20px; text-align: center;">
        <div style="font-family:'Cormorant Garamond',serif; font-size:2rem; font-weight:700;
                    color:#c9933a; letter-spacing:0.08em;">🎭 StageBook</div>
        <div style="font-size:0.72rem; color:rgba(245,239,228,0.5); letter-spacing:0.14em;
                    text-transform:uppercase; margin-top:4px;">观剧手记 · 行程助手</div>
    </div>
    """, unsafe_allow_html=True)

    # User selector
    uid = st.selectbox("当前用户", options=[1, 2],
                        format_func=lambda x: f"#{x} {MOCK_USERS[x]['nickname']}  {'👑' if MOCK_USERS[x]['role']=='admin' else ''}",
                        key="uid_select")
    st.session_state.user_id = uid
    user = MOCK_USERS[uid]

    st.markdown("<hr style='border-color:rgba(201,147,58,0.15); margin:16px 0;'>", unsafe_allow_html=True)

    # Navigation
    pages = [
        ("首页", "✦", "个人主页"),
        ("发现演出", "◈", "浏览全部场次"),
        ("观剧记录", "◉", "我看过的演出"),
        ("计划观演", "◎", "待看清单"),
        ("智能推荐", "✧", "专属推荐"),
        ("行程助手", "⊹", "出行规划"),
    ]
    if user["role"] == "admin":
        pages.append(("管理后台", "⬡", "数据管理"))

    for page_name, icon, desc in pages:
        is_active = st.session_state.page == page_name
        cls = "nav-btn active" if is_active else "nav-btn"
        if st.button(f"{icon}  {page_name}", key=f"nav_{page_name}", use_container_width=True):
            st.session_state.page = page_name
            st.rerun()

    st.markdown("<div style='flex:1'></div>", unsafe_allow_html=True)
    st.markdown(f"""
    <div style="padding: 20px 24px; border-top: 1px solid rgba(201,147,58,0.15); margin-top:auto;">
        <div style="font-size:0.72rem; color:rgba(245,239,228,0.4); letter-spacing:0.06em;">
        登录账户 · {user['username']}<br>注册于 {user['register_time']}
        </div>
    </div>
    """, unsafe_allow_html=True)

# ─── Main Content ──────────────────────────────────────────────────────────────
page = st.session_state.page
user = MOCK_USERS[st.session_state.user_id]

# ══════════════════════════════════════════════════════════════════════════════
#  首页
# ══════════════════════════════════════════════════════════════════════════════
if page == "首页":
    st.markdown(f"""
    <div class="page-header">
        <div class="page-title">你好，<em>{user['nickname']}</em></div>
        <div class="page-subtitle">StageBook · 你的私人观剧档案馆</div>
    </div>
    """, unsafe_allow_html=True)

    st.markdown('<div class="content-area">', unsafe_allow_html=True)

    # Stat row
    pref = MOCK_PREFERENCE
    st.markdown(f"""
    <div class="stat-row">
        <div class="stat-box"><div class="stat-num">{pref['total_watch_count']}</div><div class="stat-label">观看场次</div></div>
        <div class="stat-box"><div class="stat-num">{len(MOCK_PLANNED)}</div><div class="stat-label">计划观演</div></div>
        <div class="stat-box"><div class="stat-num">{pref['avg_score']}</div><div class="stat-label">平均评分</div></div>
        <div class="stat-box"><div class="stat-num">2</div><div class="stat-label">喜爱剧种</div></div>
        <div class="stat-box"><div class="stat-num">3</div><div class="stat-label">关注演员</div></div>
    </div>
    """, unsafe_allow_html=True)

    col1, col2 = st.columns([3, 2])

    with col1:
        st.markdown('<div class="card">', unsafe_allow_html=True)
        st.markdown(f"""
        <div class="card-title">观众画像</div>
        <div class="card-meta">由系统根据你的行为数据自动生成</div>
        <div style="margin-top:18px;">
            <div class="audience-type-badge">🎭 {pref['audience_type']}</div>
        </div>
        <div style="display:grid; grid-template-columns:1fr 1fr; gap:14px; margin-top:10px; font-size:0.88rem;">
            <div><span style="color:var(--mist); font-size:0.75rem; display:block; margin-bottom:2px;">最常看剧种</span>{pref['most_watched_category']}</div>
            <div><span style="color:var(--mist); font-size:0.75rem; display:block; margin-bottom:2px;">最常看演员</span>{pref['most_watched_actor']}</div>
            <div><span style="color:var(--mist); font-size:0.75rem; display:block; margin-bottom:2px;">常去剧院</span>{pref['most_visited_theater']}</div>
            <div><span style="color:var(--mist); font-size:0.75rem; display:block; margin-bottom:2px;">价格偏好</span>{price_label(pref['price_preference'])}</div>
            <div><span style="color:var(--mist); font-size:0.75rem; display:block; margin-bottom:2px;">时间偏好</span>{time_label(pref['time_preference'])}</div>
            <div><span style="color:var(--mist); font-size:0.75rem; display:block; margin-bottom:2px;">常驻区域</span>{user['home_district']}</div>
        </div>
        <hr>
        <div style="font-size:0.82rem; color:var(--mist);">
            <span style="margin-right:12px;">喜爱演员</span>
            {''.join(f'<span class="tag tag-crimson">{a}</span>' for a in pref['favorite_actors'].split('、'))}
        </div>
        <div style="font-size:0.82rem; color:var(--mist); margin-top:8px;">
            <span style="margin-right:12px;">喜爱剧种</span>
            {''.join(f'<span class="tag tag-gold">{c}</span>' for c in pref['favorite_categories'].split('、'))}
        </div>
        <div style="font-size:0.82rem; color:var(--mist); margin-top:8px;">
            <span style="margin-right:12px;">偏好区域</span>
            {''.join(f'<span class="tag tag-sage">{d}</span>' for d in pref['favorite_districts'].split('、'))}
        </div>
        """, unsafe_allow_html=True)
        st.markdown('</div>', unsafe_allow_html=True)

    with col2:
        # Donut chart
        fig = go.Figure(go.Pie(
            labels=list(CATEGORY_STATS.keys()),
            values=list(CATEGORY_STATS.values()),
            hole=0.68,
            marker_colors=["#c9933a", "#8b1a2a", "#4a6741", "#8a9ba8"],
            textinfo="label+percent",
            textfont=dict(size=12, family="Noto Serif SC"),
        ))
        fig.update_layout(
            title=dict(text="剧种分布", font=dict(size=14, family="Cormorant Garamond"), x=0.5),
            paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
            margin=dict(t=40, b=10, l=10, r=10), height=240,
            showlegend=False,
            annotations=[dict(text=f"<b>{pref['total_watch_count']}</b><br><span style='font-size:10px'>场次</span>",
                              x=0.5, y=0.5, font_size=18, showarrow=False,
                              font=dict(family="Cormorant Garamond", color="#1a1008"))]
        )
        st.plotly_chart(fig, use_container_width=True, config={"displayModeBar": False})

        # Score radar-style bar
        scores = [r["score"] for r in MOCK_WATCH_RECORDS if r["score"]]
        fig2 = go.Figure(go.Bar(
            x=[r["title"][:4]+"…" if len(r["title"])>4 else r["title"] for r in MOCK_WATCH_RECORDS],
            y=scores,
            marker_color=["#c9933a","#b8812e","#d4a84e","#8b1a2a","#c9933a"],
            text=[f"{s:.1f}" for s in scores],
            textposition="outside",
            textfont=dict(size=11, color="#1a1008"),
        ))
        fig2.update_layout(
            title=dict(text="历史评分", font=dict(size=14, family="Cormorant Garamond"), x=0.5),
            paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
            margin=dict(t=40, b=10, l=10, r=10), height=200,
            yaxis=dict(range=[0,11], showgrid=True, gridcolor="rgba(201,147,58,0.1)",
                       tickfont=dict(size=10)),
            xaxis=dict(tickfont=dict(size=10)),
        )
        st.plotly_chart(fig2, use_container_width=True, config={"displayModeBar": False})

    # Latest recs preview
    st.markdown('<div class="ornament">· · ✦ · ·</div>', unsafe_allow_html=True)
    st.markdown('<div style="font-family:\'Cormorant Garamond\',serif; font-size:1.4rem; font-weight:600; margin-bottom:16px;">近期为你推荐</div>', unsafe_allow_html=True)
    for rec in MOCK_RECOMMENDATIONS[:2]:
        source_tag = {"profile_based":"画像推荐","similar_user":"协同推荐","rule_based":"规则推荐"}.get(rec["recommendation_source"],"推荐")
        special = f'<span class="tag tag-crimson">{rec["special_tag"]}</span>' if rec["special_tag"] else ""
        st.markdown(f"""
        <div class="rec-card">
            <div class="rec-score-badge">{rec['match_score']}</div>
            <div class="rec-info">
                <div class="rec-title">{rec['title']} <span class="tag tag-mist">{rec['version']}</span> {special}</div>
                <div class="rec-meta">{rec['theater_name']} · {rec['district']} &nbsp;|&nbsp; {rec['start_time'][:10]}</div>
                <div class="rec-reason">{rec['recommendation_reason']}</div>
            </div>
            <div style="text-align:right; flex-shrink:0;">
                <div class="rec-price">¥{int(rec['price_min'])}~{int(rec['price_max'])}</div>
                <div><span class="tag tag-gold">{source_tag}</span></div>
            </div>
        </div>
        """, unsafe_allow_html=True)

    st.markdown('</div>', unsafe_allow_html=True)

# ══════════════════════════════════════════════════════════════════════════════
#  发现演出
# ══════════════════════════════════════════════════════════════════════════════
elif page == "发现演出":
    st.markdown("""
    <div class="page-header">
        <div class="page-title">发现 <em>演出</em></div>
        <div class="page-subtitle">浏览全部场次 · 筛选符合偏好的演出</div>
    </div>
    """, unsafe_allow_html=True)

    st.markdown('<div class="content-area">', unsafe_allow_html=True)

    # Mock all performances
    all_perfs = [
        {"performance_id":101,"title":"汉密尔顿","version":"original","category":"音乐剧","language":"中文",
         "theater_name":"上海文化广场","city":"上海","district":"徐汇区",
         "start_time":"2025-05-18 19:00","end_time":"2025-05-18 21:30","price_min":280,"price_max":880,"special_tag":None},
        {"performance_id":102,"title":"变身怪医","version":"tour","category":"音乐剧","language":"中文",
         "theater_name":"美琪大戏院","city":"上海","district":"静安区",
         "start_time":"2025-06-07 14:00","end_time":"2025-06-07 16:30","price_min":180,"price_max":580,"special_tag":None},
        {"performance_id":103,"title":"芝加哥","version":"revival","category":"音乐剧","language":"中文",
         "theater_name":"上海大剧院","city":"上海","district":"黄浦区",
         "start_time":"2025-07-12 19:30","end_time":"2025-07-12 22:00","price_min":380,"price_max":1080,"special_tag":None},
        {"performance_id":201,"title":"歌剧院幽灵25周年","version":"limited","category":"音乐剧","language":"中文",
         "theater_name":"上海文化广场","city":"上海","district":"徐汇区",
         "start_time":"2025-05-25 19:00","end_time":"2025-05-25 22:00","price_min":380,"price_max":1280,"special_tag":"限定版"},
        {"performance_id":202,"title":"西区故事","version":"revival","category":"音乐剧","language":"中文",
         "theater_name":"美琪大戏院","city":"上海","district":"静安区",
         "start_time":"2025-06-14 19:30","end_time":"2025-06-14 22:00","price_min":280,"price_max":780,"special_tag":None},
        {"performance_id":205,"title":"铸魂：亚瑟王传说","version":"original","category":"音乐剧","language":"中文",
         "theater_name":"美琪大戏院","city":"上海","district":"静安区",
         "start_time":"2025-08-02 19:00","end_time":"2025-08-02 21:30","price_min":360,"price_max":960,"special_tag":"首演"},
        {"performance_id":301,"title":"雷雨","version":"revival","category":"话剧","language":"中文",
         "theater_name":"上海话剧艺术中心","city":"上海","district":"静安区",
         "start_time":"2025-05-30 19:30","end_time":"2025-05-30 22:00","price_min":80,"price_max":280,"special_tag":None},
        {"performance_id":302,"title":"四世同堂","version":"original","category":"话剧","language":"中文",
         "theater_name":"上海话剧艺术中心","city":"上海","district":"静安区",
         "start_time":"2025-06-22 19:00","end_time":"2025-06-22 21:30","price_min":120,"price_max":380,"special_tag":None},
    ]

    # Filters
    col_f1, col_f2, col_f3, col_f4 = st.columns(4)
    with col_f1:
        cat_filter = st.selectbox("剧种", ["全部","音乐剧","话剧","歌剧","舞剧"])
    with col_f2:
        district_filter = st.selectbox("区域", ["全部","黄浦区","徐汇区","静安区","长宁区","浦东新区"])
    with col_f3:
        price_filter = st.selectbox("价格段", ["全部","¥100以下","¥100-300","¥300-600","¥600以上"])
    with col_f4:
        special_filter = st.checkbox("仅看特别场次")

    # Apply filters
    filtered = all_perfs
    if cat_filter != "全部":
        filtered = [p for p in filtered if p["category"] == cat_filter]
    if district_filter != "全部":
        filtered = [p for p in filtered if p["district"] == district_filter]
    if special_filter:
        filtered = [p for p in filtered if p["special_tag"]]
    if price_filter == "¥100以下":
        filtered = [p for p in filtered if p["price_min"] < 100]
    elif price_filter == "¥100-300":
        filtered = [p for p in filtered if 100 <= p["price_min"] <= 300]
    elif price_filter == "¥300-600":
        filtered = [p for p in filtered if 300 <= p["price_min"] <= 600]
    elif price_filter == "¥600以上":
        filtered = [p for p in filtered if p["price_min"] > 600]

    st.markdown(f'<div style="font-size:0.82rem; color:var(--mist); margin:16px 0 8px;">共 <b>{len(filtered)}</b> 场演出</div>', unsafe_allow_html=True)

    for p in filtered:
        special_html = f'<span class="tag tag-crimson">{p["special_tag"]}</span>' if p["special_tag"] else ""
        st.markdown(f"""
        <div class="card" style="display:flex; align-items:center; gap:24px; padding:20px 28px;">
            <div style="flex:1;">
                <div style="font-family:'Cormorant Garamond',serif; font-size:1.2rem; font-weight:600;">
                    {p['title']} <span class="tag tag-mist">{p['version']}</span> {special_html}
                </div>
                <div style="font-size:0.8rem; color:var(--mist); font-family:'DM Mono',monospace; margin-top:4px;">
                    {p['theater_name']} · {p['district']} &nbsp;|&nbsp; {fmt_datetime(p['start_time'])}
                </div>
                <div style="margin-top:8px;">
                    <span class="tag tag-gold">{p['category']}</span>
                    <span class="tag tag-sage">{p['language']}</span>
                </div>
            </div>
            <div style="text-align:right; flex-shrink:0;">
                <div style="font-family:'Cormorant Garamond',serif; font-size:1.4rem; font-weight:600; color:var(--crimson);">
                    ¥{int(p['price_min'])} ~ {int(p['price_max'])}
                </div>
                <div style="font-size:0.72rem; color:var(--mist); margin-top:2px;">票价区间</div>
            </div>
        </div>
        """, unsafe_allow_html=True)

    st.markdown('</div>', unsafe_allow_html=True)

# ══════════════════════════════════════════════════════════════════════════════
#  观剧记录
# ══════════════════════════════════════════════════════════════════════════════
elif page == "观剧记录":
    st.markdown("""
    <div class="page-header">
        <div class="page-title">观剧 <em>记录</em></div>
        <div class="page-subtitle">我看过的演出 · 对应数据库 Watch_Record 表</div>
    </div>
    """, unsafe_allow_html=True)

    st.markdown('<div class="content-area">', unsafe_allow_html=True)

    # Add record form
    with st.expander("＋ 添加新观剧记录", expanded=False):
        c1, c2, c3 = st.columns(3)
        with c1:
            new_title = st.text_input("演出名称")
        with c2:
            new_date = st.date_input("观看日期", value=date.today())
        with c3:
            new_score = st.slider("我的评分", 0.0, 10.0, 8.0, 0.5)
        if st.button("确认添加"):
            st.success(f"✓ 已添加《{new_title}》的观看记录，评分 {new_score}")

    st.markdown('<div class="ornament">· · ✦ · ·</div>', unsafe_allow_html=True)

    for r in sorted(MOCK_WATCH_RECORDS, key=lambda x: x["start_time"], reverse=True):
        dt = datetime.strptime(r["start_time"], "%Y-%m-%d %H:%M")
        stars_html = f'<span style="color:var(--gold); font-size:1rem;">{"★" * int(r["score"]/2)}{"☆" * (5 - int(r["score"]/2))}</span>'
        st.markdown(f"""
        <div class="cal-item">
            <div class="cal-date">
                <div class="day">{dt.day:02d}</div>
                <div class="month">{dt.strftime('%b %Y')}</div>
            </div>
            <div class="cal-info" style="flex:1;">
                <div class="title">{r['title']} <span class="tag tag-mist">{r['version']}</span></div>
                <div class="sub">{r['theater_name']} · {r['start_time'][11:16]} 场 &nbsp;·&nbsp;
                    <span class="tag tag-gold">{r['category']}</span>
                </div>
            </div>
            <div style="text-align:right;">
                <div class="score-display">{r['score']}</div>
                <div>{stars_html}</div>
                <span class="status-watched">已观看</span>
            </div>
        </div>
        """, unsafe_allow_html=True)

    # Score trend chart
    st.markdown('<div class="ornament">· · ✦ · ·</div>', unsafe_allow_html=True)
    df = pd.DataFrame(MOCK_WATCH_RECORDS)[["title","start_time","score","category"]].copy()
    df = df.sort_values("start_time")
    fig = px.line(df, x="title", y="score", markers=True,
                  color_discrete_sequence=["#c9933a"],
                  labels={"title":"演出","score":"评分"},
                  title="评分趋势")
    fig.update_traces(marker=dict(size=10, symbol="circle", color="#8b1a2a",
                                  line=dict(width=2, color="#c9933a")),
                      line=dict(width=2))
    fig.update_layout(paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
                      title_font=dict(size=14, family="Cormorant Garamond"),
                      yaxis=dict(range=[0,11], gridcolor="rgba(201,147,58,0.1)"),
                      xaxis=dict(gridcolor="rgba(201,147,58,0.1)"),
                      margin=dict(t=40,b=10,l=10,r=10), height=280)
    st.plotly_chart(fig, use_container_width=True, config={"displayModeBar": False})

    st.markdown('</div>', unsafe_allow_html=True)

# ══════════════════════════════════════════════════════════════════════════════
#  计划观演
# ══════════════════════════════════════════════════════════════════════════════
elif page == "计划观演":
    st.markdown("""
    <div class="page-header">
        <div class="page-title">计划 <em>观演</em></div>
        <div class="page-subtitle">我的待看清单 · 对应数据库 Planned_Performance 表</div>
    </div>
    """, unsafe_allow_html=True)

    st.markdown('<div class="content-area">', unsafe_allow_html=True)

    status_map = {"planned":"待计划","booked":"已购票","canceled":"已取消"}
    status_cls  = {"planned":"status-planned","booked":"status-booked","canceled":"status-mist"}

    for p in sorted(MOCK_PLANNED, key=lambda x: x["start_time"]):
        dt = datetime.strptime(p["start_time"], "%Y-%m-%d %H:%M")
        days_left = (dt.date() - date.today()).days
        countdown_html = f'<span style="font-size:0.78rem; color:var(--crimson); font-family:\'DM Mono\',monospace;">还有 {days_left} 天</span>' if days_left > 0 else '<span style="color:var(--sage);">即将开演</span>'
        st.markdown(f"""
        <div class="card" style="display:flex; align-items:center; gap:20px; padding:20px 28px;">
            <div style="text-align:center; width:60px; flex-shrink:0;">
                <div style="font-family:'Cormorant Garamond',serif; font-size:2rem; font-weight:700; color:var(--gold); line-height:1;">{dt.day}</div>
                <div style="font-size:0.7rem; color:var(--mist); text-transform:uppercase;">{dt.strftime('%b')}</div>
                <div style="font-size:0.7rem; color:var(--mist);">{dt.year}</div>
            </div>
            <div style="flex:1;">
                <div style="font-family:'Cormorant Garamond',serif; font-size:1.2rem; font-weight:600;">
                    {p['title']} <span class="tag tag-mist">{p['version']}</span>
                </div>
                <div style="font-size:0.8rem; color:var(--mist); font-family:'DM Mono',monospace; margin-top:4px;">
                    {p['theater_name']} &nbsp;|&nbsp; {p['start_time'][11:16]} – {p['end_time'][11:16]}
                </div>
                <div style="margin-top:6px;">
                    <span class="tag tag-gold">{p['category']}</span>
                    {countdown_html}
                </div>
            </div>
            <div style="text-align:right; flex-shrink:0;">
                <div style="font-family:'Cormorant Garamond',serif; font-size:1.2rem; color:var(--crimson);">¥{int(p['price_min'])}~{int(p['price_max'])}</div>
                <div style="margin-top:6px;"><span class="{status_cls.get(p['status'],'status-planned')}">{status_map.get(p['status'],p['status'])}</span></div>
            </div>
        </div>
        """, unsafe_allow_html=True)

    # Timeline chart
    st.markdown('<div class="ornament">· · ✦ · ·</div>', unsafe_allow_html=True)
    df_p = pd.DataFrame(MOCK_PLANNED)
    df_p["start_dt"] = pd.to_datetime(df_p["start_time"])
    df_p["end_dt"] = pd.to_datetime(df_p["end_time"])
    fig_t = px.timeline(df_p, x_start="start_dt", x_end="end_dt", y="title",
                        color="status",
                        color_discrete_map={"planned":"#c9933a","booked":"#8b1a2a","canceled":"#8a9ba8"},
                        title="计划时间轴")
    fig_t.update_layout(paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
                        title_font=dict(size=14, family="Cormorant Garamond"),
                        margin=dict(t=40,b=10,l=10,r=10), height=200,
                        yaxis=dict(autorange="reversed"),
                        legend=dict(orientation="h", y=-0.15))
    st.plotly_chart(fig_t, use_container_width=True, config={"displayModeBar": False})

    st.markdown('</div>', unsafe_allow_html=True)

# ══════════════════════════════════════════════════════════════════════════════
#  智能推荐
# ══════════════════════════════════════════════════════════════════════════════
elif page == "智能推荐":
    st.markdown("""
    <div class="page-header">
        <div class="page-title">智能 <em>推荐</em></div>
        <div class="page-subtitle">融合画像推荐 · 协同过滤 · 规则引擎 · 对应 v_hybrid_recommendation 视图</div>
    </div>
    """, unsafe_allow_html=True)

    st.markdown('<div class="content-area">', unsafe_allow_html=True)

    pref = MOCK_PREFERENCE
    st.markdown(f"""
    <div class="card" style="padding:18px 28px; margin-bottom:24px;">
        <div style="display:flex; align-items:center; gap:16px; flex-wrap:wrap;">
            <div style="font-size:0.85rem; color:var(--mist);">当前画像类型</div>
            <div class="audience-type-badge" style="margin-bottom:0;">🎭 {pref['audience_type']}</div>
            <div style="font-size:0.82rem; color:var(--mist); margin-left:auto;">
                推荐基于：喜爱演员 · 剧种偏好 · 相似用户 · 时间偏好 · 价格区间
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)

    # Source legend
    col_l1, col_l2, col_l3 = st.columns(3)
    with col_l1:
        st.markdown('<div class="card" style="padding:14px 20px; text-align:center;"><div class="tag tag-gold">画像推荐</div><div style="font-size:0.78rem; color:var(--mist); margin-top:6px;">基于你的个人偏好<br>精准匹配</div></div>', unsafe_allow_html=True)
    with col_l2:
        st.markdown('<div class="card" style="padding:14px 20px; text-align:center;"><div class="tag tag-crimson">协同推荐</div><div style="font-size:0.78rem; color:var(--mist); margin-top:6px;">与你品味相近的用户<br>的高评分场次</div></div>', unsafe_allow_html=True)
    with col_l3:
        st.markdown('<div class="card" style="padding:14px 20px; text-align:center;"><div class="tag tag-sage">规则推荐</div><div style="font-size:0.78rem; color:var(--mist); margin-top:6px;">时间偏好 · 特别标签<br>智能规则引擎</div></div>', unsafe_allow_html=True)

    st.markdown('<div class="ornament">· · ✦ · ·</div>', unsafe_allow_html=True)

    source_tag_map = {"profile_based":"画像推荐","similar_user":"协同推荐","rule_based":"规则推荐"}
    source_cls_map = {"profile_based":"tag-gold","similar_user":"tag-crimson","rule_based":"tag-sage"}

    for rec in MOCK_RECOMMENDATIONS:
        src_label = source_tag_map.get(rec["recommendation_source"], "推荐")
        src_cls   = source_cls_map.get(rec["recommendation_source"], "tag-mist")
        special_html = f'<span class="tag tag-crimson">{rec["special_tag"]}</span>' if rec["special_tag"] else ""
        matched_html = f'<span class="tag tag-mist">{rec["matched_profile_type"]}</span>' if rec["matched_profile_type"] else ""
        score_pct = rec["match_score"]
        bar_color = "#c9933a" if score_pct >= 80 else ("#8b1a2a" if score_pct >= 60 else "#8a9ba8")
        st.markdown(f"""
        <div class="rec-card">
            <div class="rec-score-badge">{rec['match_score']}</div>
            <div class="rec-info">
                <div class="rec-title">
                    {rec['title']}
                    <span class="tag tag-mist">{rec['version']}</span>
                    {special_html}
                </div>
                <div class="rec-meta">
                    {rec['theater_name']} · {rec['district']} &nbsp;|&nbsp; {rec['start_time'][:10]}
                    &nbsp;|&nbsp; {rec['language']}
                </div>
                <div style="margin-top:6px; display:flex; align-items:center; gap:8px; flex-wrap:wrap;">
                    <span class="tag {src_cls}">{src_label}</span>
                    {matched_html}
                    <span class="tag tag-gold">{rec['category']}</span>
                </div>
                <div class="rec-reason">{rec['recommendation_reason']}</div>
                <div style="margin-top:8px; background:rgba(201,147,58,0.08); border-radius:4px; height:4px; overflow:hidden;">
                    <div style="height:100%; width:{score_pct}%; background:{bar_color}; border-radius:4px;"></div>
                </div>
            </div>
            <div style="text-align:right; flex-shrink:0; min-width:90px;">
                <div class="rec-price">¥{int(rec['price_min'])}~{int(rec['price_max'])}</div>
            </div>
        </div>
        """, unsafe_allow_html=True)

    st.markdown('</div>', unsafe_allow_html=True)

# ══════════════════════════════════════════════════════════════════════════════
#  行程助手
# ══════════════════════════════════════════════════════════════════════════════
elif page == "行程助手":
    st.markdown("""
    <div class="page-header">
        <div class="page-title">行程 <em>助手</em></div>
        <div class="page-subtitle">出行规划 · 餐厅推荐 · 出发时间 · 对应 v_planned_trip_assistance 视图</div>
    </div>
    """, unsafe_allow_html=True)

    st.markdown('<div class="content-area">', unsafe_allow_html=True)

    t = MOCK_TRIP
    transport_icons = {"subway":"🚇","bus":"🚌","taxi":"🚕","walk":"🚶"}
    transport_names = {"subway":"地铁","bus":"公交","taxi":"出租车","walk":"步行"}
    t_icon = transport_icons.get(t["transport_type"],"🚗")
    t_name = transport_names.get(t["transport_type"],t["transport_type"])

    st.markdown(f"""
    <div class="trip-card">
        <div class="trip-title">🎭 {MOCK_PLANNED[0]['title']}</div>
        <div style="font-size:0.82rem; color:rgba(245,239,228,0.6); font-family:'DM Mono',monospace;">
            {t['theater_name']} &nbsp;·&nbsp; {fmt_datetime(t['start_time'])} – {t['end_time'][11:16]}
        </div>
        <div class="trip-info-grid">
            <div class="trip-info-item">
                <label>建议出发时间</label>
                <span style="color:var(--gold); font-size:1.1rem; font-family:'Cormorant Garamond',serif; font-weight:600;">
                    ⏰ {t['suggested_departure_time'][11:16]}
                </span>
            </div>
            <div class="trip-info-item">
                <label>推荐交通方式</label>
                <span>{t_icon} {t_name} · 约 {t['estimated_time']} 分钟 · ¥{t['estimated_cost']:.0f}</span>
            </div>
            <div class="trip-info-item">
                <label>出发区域</label>
                <span>📍 {t['suitable_district']}</span>
            </div>
            <div class="trip-info-item">
                <label>到场建议</label>
                <span>演出前 {15 if t['transport_type']=='subway' else 20} 分钟缓冲</span>
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)

    col_r, col_m = st.columns([1, 1])

    with col_r:
        st.markdown("""
        <div class="card">
            <div class="card-title">📍 周边餐厅推荐</div>
            <div class="card-meta">基于你的价格偏好自动筛选</div>
        """, unsafe_allow_html=True)
        price_cls = {"low":"tag-sage","mid":"tag-gold","high":"tag-crimson"}
        price_name = {"low":"经济","mid":"中档","high":"高档"}
        st.markdown(f"""
            <div style="margin-top:18px; padding:16px; background:rgba(201,147,58,0.06); border-radius:8px;">
                <div style="font-size:1.05rem; font-weight:600; color:var(--ink);">{t['restaurant_name']}</div>
                <div style="font-size:0.8rem; color:var(--mist); margin-top:4px; font-family:'DM Mono',monospace;">
                    {t['restaurant_category']} &nbsp;·&nbsp; 距剧院 {t['distance_m']}m
                </div>
                <div style="margin-top:10px; display:flex; align-items:center; gap:10px; flex-wrap:wrap;">
                    <span class="tag {price_cls.get(t['price_tier'],'tag-gold')}">{price_name.get(t['price_tier'],'中档')}</span>
                    <span style="font-size:1rem; color:var(--crimson); font-weight:600; font-family:'DM Mono',monospace;">
                        人均 ¥{t['avg_price']:.0f}
                    </span>
                </div>
                <div style="font-size:0.78rem; color:var(--mist); margin-top:10px;">
                    💡 建议演出前约 90 分钟前往用餐
                </div>
            </div>
        </div>
        """, unsafe_allow_html=True)

    with col_m:
        # Timeline viz
        st.markdown("""<div class="card"><div class="card-title">🕐 行程时间轴</div><div class="card-meta">出行各阶段时间分配</div>""", unsafe_allow_html=True)
        depart_time = datetime.strptime(t["suggested_departure_time"], "%Y-%m-%d %H:%M")
        show_start  = datetime.strptime(t["start_time"], "%Y-%m-%d %H:%M")
        show_end    = datetime.strptime(t["end_time"], "%Y-%m-%d %H:%M")
        meal_start  = depart_time.replace(hour=depart_time.hour - 1, minute=depart_time.minute)

        timeline_items = [
            (meal_start.strftime("%H:%M"), "用餐", t["restaurant_name"], "tag-sage"),
            (depart_time.strftime("%H:%M"), "出发", f"{t_icon} {t_name}", "tag-gold"),
            (show_start.strftime("%H:%M"), "入场", t["theater_name"], "tag-crimson"),
            (show_end.strftime("%H:%M"), "散场", "演出结束，返程", "tag-mist"),
        ]
        items_html = ""
        for time_str, label, detail, cls in timeline_items:
            items_html += f"""
            <div style="display:flex; align-items:flex-start; gap:14px; margin-bottom:16px;">
                <div style="font-family:'DM Mono',monospace; font-size:0.88rem; color:var(--gold); width:46px; flex-shrink:0; padding-top:2px;">{time_str}</div>
                <div style="width:8px; height:8px; border-radius:50%; background:var(--gold); flex-shrink:0; margin-top:5px; box-shadow:0 0 6px rgba(201,147,58,0.4);"></div>
                <div>
                    <div style="font-size:0.9rem; font-weight:600; color:var(--ink);">{label}</div>
                    <div style="font-size:0.78rem; color:var(--mist); margin-top:2px;">{detail}</div>
                </div>
            </div>
            """
        st.markdown(f'<div style="margin-top:18px; padding-left:4px; border-left:2px solid rgba(201,147,58,0.25); margin-left:46px;">{items_html}</div></div>', unsafe_allow_html=True)

    st.markdown('</div>', unsafe_allow_html=True)

# ══════════════════════════════════════════════════════════════════════════════
#  管理后台
# ══════════════════════════════════════════════════════════════════════════════
elif page == "管理后台":
    if user["role"] != "admin":
        st.error("⚠️ 无访问权限，仅管理员可见")
    else:
        st.markdown("""
        <div class="page-header">
            <div class="page-title">管理 <em>后台</em></div>
            <div class="page-subtitle">数据管理 · Admin_Log · 角色权限 stagebook_admin</div>
        </div>
        """, unsafe_allow_html=True)

        st.markdown('<div class="content-area">', unsafe_allow_html=True)

        tab1, tab2, tab3 = st.tabs(["📊 数据概览", "🎭 演出管理", "📝 操作日志"])

        with tab1:
            col1, col2, col3, col4 = st.columns(4)
            stats = [("注册用户","2","User"),("演出场次","8","Performance"),("剧目数量","6","Production"),("剧院数量","4","Theater")]
            for col, (label, val, table) in zip([col1,col2,col3,col4], stats):
                with col:
                    st.markdown(f"""
                    <div class="stat-box">
                        <div class="stat-num">{val}</div>
                        <div class="stat-label">{label}</div>
                        <div style="font-size:0.65rem; color:var(--mist); margin-top:4px; font-family:'DM Mono',monospace;">{table}</div>
                    </div>
                    """, unsafe_allow_html=True)

            st.markdown('<div class="ornament">· · ✦ · ·</div>', unsafe_allow_html=True)
            # User table
            st.markdown('<div class="card-title" style="margin-bottom:12px;">用户列表</div>', unsafe_allow_html=True)
            df_users = pd.DataFrame([
                {"user_id":1,"username":"shengge_fan","nickname":"沪上观剧人","city":"上海","role":"user","price_preference":"mid"},
                {"user_id":2,"username":"admin_001","nickname":"后台管理员","city":"上海","role":"admin","price_preference":"premium"},
            ])
            st.dataframe(df_users, use_container_width=True, hide_index=True)

        with tab2:
            st.markdown('<div style="font-size:0.9rem; color:var(--mist); margin-bottom:16px;">对应 Production / Performance / Theater 表的增删改查</div>', unsafe_allow_html=True)
            with st.expander("＋ 新增演出场次"):
                c1,c2 = st.columns(2)
                with c1:
                    st.text_input("剧目名称", key="new_prod")
                    st.selectbox("版本类型", ["original","revival","tour","limited"], key="new_ver")
                    st.selectbox("剧种", ["音乐剧","话剧","歌剧","舞剧"], key="new_cat")
                with c2:
                    st.text_input("剧院", key="new_theater")
                    st.date_input("演出日期", key="new_date")
                    st.number_input("最低票价", value=180, key="new_pmin")
                if st.button("提交新演出"):
                    st.success("✓ 已写入 Performance 表")

            df_perf = pd.DataFrame([
                {"演出ID":101,"剧目":"汉密尔顿","剧院":"上海文化广场","日期":"2025-05-18","票价":"¥280~880","状态":"上架"},
                {"演出ID":102,"剧目":"变身怪医","剧院":"美琪大戏院","日期":"2025-06-07","票价":"¥180~580","状态":"上架"},
                {"演出ID":103,"剧目":"芝加哥","剧院":"上海大剧院","日期":"2025-07-12","票价":"¥380~1080","状态":"上架"},
            ])
            st.dataframe(df_perf, use_container_width=True, hide_index=True)

        with tab3:
            st.markdown('<div style="font-size:0.9rem; color:var(--mist); margin-bottom:16px;">对应 Admin_Log 表的操作记录</div>', unsafe_allow_html=True)
            logs = [
                {"log_id":1,"操作类型":"INSERT","目标表":"Performance","目标ID":103,"时间":"2025-04-15 10:23","备注":"新增芝加哥场次"},
                {"log_id":2,"操作类型":"UPDATE","目标表":"Production","目标ID":5,"时间":"2025-04-14 16:05","备注":"修改剧目信息"},
                {"log_id":3,"操作类型":"DELETE","目标表":"Nearby_Restaurant","目标ID":7,"时间":"2025-04-12 11:48","备注":"下线关闭餐厅"},
            ]
            st.dataframe(pd.DataFrame(logs), use_container_width=True, hide_index=True)

        st.markdown('</div>', unsafe_allow_html=True)

# ── Footer ──────────────────────────────────────────────────────────────────
st.markdown("""
<div style="text-align:center; padding:32px; font-size:0.72rem; color:rgba(138,155,168,0.5);
            font-family:'DM Mono',monospace; letter-spacing:0.06em; border-top:1px solid rgba(201,147,58,0.1); margin-top:40px;">
StageBook · 观剧记录与行程辅助数据库系统 · 数据库课程大作业
</div>
""", unsafe_allow_html=True)

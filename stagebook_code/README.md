# 🎭 StageBook 前端使用说明

## 技术栈
- **Python 3.8+**
- **Streamlit** — 前端框架
- **Plotly** — 数据可视化
- **Pandas** — 数据处理
- **mysql-connector-python** — MySQL 连接（可选）

## 快速启动

```bash
# 1. 安装依赖
pip install streamlit plotly pandas mysql-connector-python

# 2. 运行
streamlit run app.py
```

浏览器访问 `http://localhost:8501`

---

## 连接真实数据库

当前使用 **Mock 数据**，无需数据库即可预览效果。

如需连接你的 StageBook MySQL 数据库，在 `app.py` 开头添加：

```python
import mysql.connector

@st.cache_resource
def get_db():
    return mysql.connector.connect(
        host="localhost",
        user="your_user",
        password="your_password",
        database="StageBook"
    )

def query(sql, params=None):
    conn = get_db()
    cursor = conn.cursor(dictionary=True)
    cursor.execute(sql, params or [])
    return cursor.fetchall()
```

然后把各模块的 Mock 数据替换为对应 SQL 查询，例如：

### 观剧记录
```python
records = query("""
    SELECT pr.title, pr.version, th.theater_name,
           pf.start_time, wr.score
    FROM Watch_Record wr
    JOIN Performance pf ON wr.performance_id = pf.performance_id
    JOIN Production pr ON pf.production_id = pr.production_id
    JOIN Theater th ON pf.theater_id = th.theater_id
    WHERE wr.user_id = %s
    ORDER BY pf.start_time DESC
""", [user_id])
```

### 智能推荐（调用存储过程）
```python
cursor = conn.cursor(dictionary=True)
cursor.callproc('sp_recommend_by_profile', [user_id])
for result in cursor.stored_results():
    recommendations = result.fetchall()
```

### 用户偏好画像
```python
profile = query("SELECT * FROM v_user_preference_profile WHERE user_id = %s", [user_id])[0]
```

### 行程助手
```python
trip = query("SELECT * FROM v_planned_trip_assistance WHERE user_id = %s", [user_id])
```

---

## 功能模块对应关系

| 前端页面 | 对应数据库对象 |
|---------|-------------|
| 首页 · 用户画像 | `v_user_preference_profile` · `fn_audience_type()` |
| 发现演出 | `v_public_performance_info` |
| 观剧记录 | `Watch_Record` 表 |
| 计划观演 | `Planned_Performance` 表 |
| 智能推荐 | `v_hybrid_recommendation` · `sp_recommend_by_profile` |
| 行程助手 | `v_planned_trip_assistance` · `fn_suggested_departure_time()` |
| 管理后台 | `Admin_Log` · 全表 CRUD（需 stagebook_admin 角色） |

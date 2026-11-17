# StageBook 数据库版启动与验收

完整安装步骤、目录说明与验收路径见 [仓库首页](../README.md)。正式入口为本目录的 `app.py`；`stagebook_code/app.py` 是历史 Mock 原型。

## 启动

先在仓库根目录安装依赖，并在独立演示数据库中依次导入 `stagebook_code/main_code.sql`、`stagebook_code/StageBook_insert_data.sql`。建库脚本会删除同名数据库，不用于已有数据升级。

```powershell
python -m pip install -r stagebook_streamlit_app/requirements.txt
cd stagebook_streamlit_app
python -m streamlit run app.py
```

侧边栏填写 MySQL 连接信息，数据库名称为 `StageBook`。可将 `.streamlit/secrets.example.toml` 复制为 `secrets.toml`，填写后自动加载；不要提交真实密码。

## 本地演示账号

| 角色 | 用户名 | 初始密码 |
| --- | --- | --- |
| 普通用户 | Estelle | 123456 |
| 管理员 | admin | StageBook123! |

仅在用户名不存在时创建，刷新页面不会覆盖已有账号的资料或密码。此版本用于本地课程演示。

## 重点验收

1. 修改偏好后刷新页面，确认偏好保留；进入推荐页，结果自动更新。
2. 推荐加入计划后，日历和行程页同步显示，同一场次不可重复加入。
3. `planned` / `booked` 可互换；演出结束后才可标记 `watched`。更新状态整体提交，出错整体回滚。
4. 行程页显示重叠场次、跨剧院转场余量提醒；可以调整出发余量和导出 `.ics`。
5. 无交通匹配时明确提示无法估算；过去已结束的计划不再进入行程页。
6. 标记 `canceled` 后从日历与行程中移除；修改或取消后重新导出，并检查外部日历旧安排。
7. 管理员检查剧目、场次、演员、剧院、餐饮与交通维护及 SQL 展示。

交通与餐饮为演示数据，转场预留不是实时路线估算，出发时间不包含用餐。Python 3.10+、MySQL 8.0.16+；完整测试说明见仓库首页。

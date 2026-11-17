# StageBook · 剧场观演与行程规划

基于 **MySQL 8 + Streamlit** 的数据库课程项目：从演出信息、个人偏好和混合推荐，到观演日历、交通餐饮参考与行程冲突提醒。

## 功能

- 普通用户：注册登录、偏好维护、推荐场次加入计划、订票状态、已观看评分、账号注销。
- 行程辅助：显示未结束的有效计划、推荐交通/餐厅、调整出发余量、提示演出重叠和跨剧院转场时间不足、导出 `.ics` 日历。
- 管理员：剧目/场次/卡司及基础数据维护、整体排期、SQL 展示与日志。
- 数据库：关系约束、视图、存储过程、函数、触发器；观演状态变更使用事务和用户行锁，避免部分写入及并发重复添加。

## 目录与入口

```text
stagebook_streamlit_app/    # 正式数据库版，启动这里的 app.py
  app.py                   # Streamlit 页面
  services.py              # 事务与推荐缓存
  trip_planning.py          # 时间计算、冲突检查、日历导出
stagebook_code/
  main_code.sql            # 建库、表、视图、函数、存储过程与角色
  StageBook_insert_data.sql # 相对当前日期生成的教学演示数据
  app.py                   # 历史 Mock 原型，不连接数据库
tests/                     # 单元、MySQL 集成、Streamlit 页面测试
```

## 本地运行

使用 Python **3.10+**、MySQL **8.0.16+**。在仓库根目录执行：

```powershell
python -m pip install -r stagebook_streamlit_app/requirements.txt
mysql -u root -p --default-character-set=utf8mb4
```

进入 MySQL 提示符后按顺序执行（以下 `SOURCE` 使用仓库根目录的相对路径）：

```sql
SOURCE stagebook_code/main_code.sql;
SOURCE stagebook_code/StageBook_insert_data.sql;
EXIT;
```

**`main_code.sql` 会删除并重建 `StageBook` 数据库，仅用于新建演示环境；已有数据库请先备份，不要把它当升级脚本。** 需要能创建函数、角色和授权的数据库账号。启用二进制日志的开发实例若出现错误 1419，可由管理员在该开发实例设置 `log_bin_trust_function_creators=1` 后重试。

`StageBook_insert_data_v2_realistic_cast.sql` 是可选替换数据集，会清空多张表，且依赖基础演示数据中的用户；不是首次初始化的替代脚本。所有排期、交通与餐饮数据均按课程演示使用，不代表实时信息。

然后启动正式应用：

```powershell
cd stagebook_streamlit_app
python -m streamlit run app.py
```

在侧边栏填写本机 MySQL 连接信息，数据库名称为 **`StageBook`**（大小写一致）。也可复制 `.streamlit/secrets.example.toml` 为同目录 `secrets.toml` 并填写配置；真实配置已加入 Git 忽略规则。

首次启动自动创建本地验收账号：普通用户 `Estelle / 123456`，管理员 `admin / StageBook123!`。后续刷新不会重置已存在账号的密码、角色或偏好。此版本面向本地课程演示，仍包含公开演示账号和数据库连接配置界面，不应直接作为公网多用户服务部署。

## 验收路径

1. 登录普通用户 → 修改偏好 → 进入混合推荐 → 加入计划。
2. 进入观剧日历 → 切换 `planned` / `booked`，确认不会重复加入同一场次。
3. 进入行程辅助 → 调整额外预留与转场时间 → 导出并导入日历。
4. 添加同一时段的不同演出，确认重叠提示；不同剧院的相邻演出应提示转场不足。
5. 演出结束后方可标记 `watched`；评分保存在观剧记录，原计划被移除。`canceled` 从计划与记录中移除。
6. 管理员登录后检查演出维护与 SQL 展示。

无匹配交通时显示“无法估算”，不生成虚假的出发时间。转场提醒采用用户设置的余量，不含实时交通路线计算；出发建议不包含用餐。日历按上海时区导出 UTC 时间，取消或修改计划后需要重新导出并检查日历中的旧安排。

## 测试

```powershell
python -m pip install -r requirements-dev.txt
python -m pytest -q
```

未设置数据库时跳过 MySQL 集成测试。完整测试必须使用已导入上述两个 SQL 文件的**独立临时数据库**，测试会写入并清理测试记录：

```powershell
$env:STAGEBOOK_TEST_URL='mysql+mysqlconnector://用户名:密码@127.0.0.1:3306/StageBook'
python -m pytest -q
```

GitHub Actions 自动创建 MySQL 8 实例，检查初始化、状态切换、失败回滚、并发添加、推荐缓存持久化和行程导出。

## 已有数据库升级

本次核心功能不需要改表；更新 Python 文件并安装依赖即可。`main_code.sql` 的授权数据库名修正用于 Linux 上的新安装，交通函数的排序增加稳定的并列规则。应用行程页直接使用显示路线计算出发时间，不依赖重新创建函数。直接使用 SQL 写入的操作不受 Python 服务层的并发锁与时间校验保护。

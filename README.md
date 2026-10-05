# StageBook：观剧记录与推荐系统

## 项目定位

数据库课程项目，围绕剧目、演出场次、演员/角色/卡司、剧院、用户偏好、观剧记录和计划建立关系数据库，并以 Streamlit 展示个性化推荐、观剧日历和餐饮/交通辅助。

仓库有两份子目录 README，根目录原先缺少入口。`stagebook_code/app.py` 是 Mock 界面原型；`stagebook_streamlit_app/app.py` 是连接 MySQL 的版本，建议以此运行完整系统。

## 技术栈

| 层次 | 技术 |
|---|---|
| 数据库 | MySQL 8.0+；utf8mb4、外键/索引、视图、触发器、函数、存储过程、角色与授权 |
| 数据库连接版 | Python、Streamlit、Pandas、SQLAlchemy、mysql-connector-python、Altair |
| Mock 原型 | Streamlit、Pandas、Plotly；不连接真实数据库 |
| 应用登录 | 盐值与 PBKDF2 密码哈希、应用账号表、用户/管理员界面 |

连接版依赖见 `requirements.txt`，只设置版本下界，未提供锁文件。建议 Python 3.10+；本次在 Python 3.12 下完成语法检查，未验证最低兼容版本。

## 目录结构

| 路径 | 内容 |
|---|---|
| `stagebook_code/main_code.sql` | 建库建表、索引、触发器、函数、存储过程、视图、角色授权 |
| `stagebook_code/StageBook_insert_data.sql` | 使用相对当前日期的教学数据，推荐首次演示使用 |
| `stagebook_code/StageBook_insert_data_v2_realistic_cast.sql` | 另一份数据集，清理旧数据并使用固定排期 |
| `stagebook_code/StageBook_demo_queries.sql` | 查询与数据库能力演示 |
| `stagebook_code/test_1.sql`、`test_2.sql` | 旧测试/数据重置脚本 |
| `stagebook_code/StageBook_data_sources.md` | 数据来源与合成数据说明 |
| `stagebook_code/app.py`、`README.md` | Mock 原型及其说明 |
| `stagebook_streamlit_app/app.py` | 数据库连接、登录、普通用户与管理员页面 |
| `stagebook_streamlit_app/requirements.txt` | 连接版依赖 |
| `stagebook_streamlit_app/.streamlit/secrets.example.toml` | 本地数据库连接模板 |
| `stagebook_streamlit_app/README.md` | 页面验收说明；部署时优先遵循本根目录文档 |

## 编译运行方式

### 数据库连接版

Python 应用无需编译。先在仓库根目录创建虚拟环境：

```bash
python3 -m venv .venv
source .venv/bin/activate
python -m pip install -r stagebook_streamlit_app/requirements.txt
```

Windows PowerShell 激活命令为 `.venv\Scripts\Activate.ps1`。

先阅读 SQL 再在独立课程测试实例中执行。`main_code.sql` 开头会 **DROP DATABASE IF EXISTS StageBook**；v2 数据集和旧测试脚本也会删除数据，不能用于保留现有业务数据的实例。

建库名是 `StageBook`，但脚本末尾的 GRANT 使用 `stagebook`。大小写敏感的 MySQL 环境中，需在本地脚本副本中将 GRANT 的数据库前缀统一为 `StageBook`，并使用相同连接配置。创建角色/执行 GRANT 需要相应数据库管理权限。

从仓库根目录启动 MySQL 客户端：

```bash
mysql -u root -p
```

在 MySQL 提示符依次执行（SQL 路径相对启动客户端的目录）：

```sql
SOURCE stagebook_code/main_code.sql;
SOURCE stagebook_code/StageBook_insert_data.sql;
```

这里的第一条应指向已按本地大小写要求检查的脚本。使用 Workbench 等工具也可打开并依次执行这两个文件。`main_code.sql` 只定义数据库对象，不包含演示 INSERT 数据，必须另行导入数据集。

进入连接版目录运行：

```bash
cd stagebook_streamlit_app
python -m streamlit run app.py
```

访问 http://localhost:8501，在侧边栏输入本地 MySQL 连接信息；数据库名填 `StageBook`。也可复制 `.streamlit/secrets.example.toml` 为同目录的 `secrets.toml` 后填写配置。应用启动会创建 `StageBook_App_Account` 并初始化演示账号，因此连接账户需要对应建表及读写权限。

普通用户与管理员演示账号由应用初始化，可在本地登录页面查看提示；它们不是 MySQL 登录账号。代码在启动时会重设这两组演示账号的认证信息。应用角色判断与 SQL 角色授权是两个层次，不能据此声称已验证数据库层的逐用户隔离。

### Mock 原型

独立使用原型时，从仓库根目录安装其额外依赖并运行：

```bash
python -m pip install streamlit pandas plotly
cd stagebook_code
python -m streamlit run app.py
```

原型只用于展示界面；不能用它验证 SQL、事务或真实数据持久化。

## 测试方法

1. 在独立测试库导入结构和推荐的相对日期数据集。
2. 在 MySQL 中执行 `SOURCE stagebook_code/StageBook_demo_queries.sql;`，检查公开演出、用户画像、日历、相似用户函数、画像推荐缓存、混合推荐与行程辅助。
3. 按连接版子目录 README 的页面验收路径测试：登录、偏好更新、加入计划、观剧记录、取消计划、管理员维护与查询。
4. 在测试库逐条检查演示查询脚本中默认注释的触发器案例：已结束场次拒绝加入计划、卡司角色与剧目一致、插入记录后清理对应计划。按实际数据选择合法 ID，预期失败的语句不要当作批量导入语句运行。

`test_1.sql`、`test_2.sql` 含数据删除和固定 2026 年 5 月日期；截至本次整理这些日期已过期，会影响计划触发器和未来演出推荐。v2 也包含固定排期，且与默认数据集不能简单叠加导入。旧测试脚本的清理顺序与推荐缓存/应用账号表依赖需重新检查，不将其列为已验证的一键测试。

本次只完成两个 Python 入口的语法检查与 SQL/配置静态核对；环境没有 MySQL，未进行数据库导入、依赖安装或浏览器端到端验收。仓库未提供自动断言式测试套件。

## 个人贡献说明

可确认：初始提交由 Git 提交作者 `Estelle-zzx` 于 2026-07-14 整体导入。仓库展示了数据库设计、SQL 业务逻辑、样例数据、Mock 界面和连接版应用，但无法从一次整体提交证明各部分均由本人独立完成。

**待本人确认：**本人负责的表/视图/过程/触发器、推荐逻辑、数据整理、登录与界面模块，以及合作成员分工。确认前不填写“独立完成全栈系统”等描述。

## 无法确认与验证边界

- 未验证完整初始化脚本在具体 MySQL 权限和大小写配置下成功执行。
- 未确认部署版本、最低 Python/依赖版本、完整权限隔离和自动化测试结果。
- 教学合成数据不能作为实时演出、真实用户行为或真实推荐效果证据，详见数据来源说明。

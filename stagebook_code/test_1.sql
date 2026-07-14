SET SQL_SAFE_UPDATES = 0;
USE StageBook;
SET NAMES utf8mb4;
-- =========================
-- 1. 清空旧测试数据（按外键依赖顺序）
-- 如果你是第一次插入，也可以直接整段运行
-- =========================

DELETE FROM Watch_Record;
DELETE FROM Planned_Performance;
DELETE FROM Favorite_Actor;
DELETE FROM Favorite_Category;
DELETE FROM Favorite_Language;
DELETE FROM Favorite_District;
DELETE FROM Performance_Cast;
DELETE FROM Nearby_Restaurant;
DELETE FROM Transport_Option;
DELETE FROM Role;
DELETE FROM Performance;
DELETE FROM Actor;
DELETE FROM Theater;
DELETE FROM Production;
DELETE FROM User;

ALTER TABLE User AUTO_INCREMENT = 1;
ALTER TABLE Production AUTO_INCREMENT = 1;
ALTER TABLE Theater AUTO_INCREMENT = 1;
ALTER TABLE Performance AUTO_INCREMENT = 1;
ALTER TABLE Actor AUTO_INCREMENT = 1;
ALTER TABLE Role AUTO_INCREMENT = 1;
ALTER TABLE Nearby_Restaurant AUTO_INCREMENT = 1;
ALTER TABLE Transport_Option AUTO_INCREMENT = 1;
ALTER TABLE Watch_Record AUTO_INCREMENT = 1;

-- =========================
-- 2. 插入基础测试数据
-- =========================

-- 2.1 用户
INSERT INTO User (username, nickname, city, price_preference, time_preference, home_district)
VALUES
('u001', '小林', '上海', 'mid', 'weekend_evening', '黄浦区'),
('u002', '小周', '上海', 'economy', 'weekday_evening', '徐汇区'),
('u003', '阿青', '上海', 'premium', 'weekend_matinee', '静安区');

-- 2.2 剧院
INSERT INTO Theater (theater_name, city, district, address)
VALUES
('上海大剧院', '上海', '黄浦区', '人民大道300号'),
('美琪大戏院', '上海', '静安区', '江宁路66号'),
('上音歌剧院', '上海', '徐汇区', '汾阳路6号');

-- 2.3 剧目
INSERT INTO Production (title, category, duration_min, language, version)
VALUES
('剧目A', '音乐剧', 150, '普通话', 'original'),
('剧目B', '话剧', 120, '普通话', 'revival'),
('剧目C', '舞剧', 100, '英语', 'tour');

-- 2.4 角色
INSERT INTO Role (production_id, role_name)
VALUES
(1, '男主'),
(1, '女主'),
(1, '配角'),
(2, '主角'),
(2, '朋友'),
(3, '舞者A'),
(3, '舞者B');

-- 2.5 演员
INSERT INTO Actor (actor_name, gender)
VALUES
('演员甲', 'male'),
('演员乙', 'female'),
('演员丙', 'male'),
('演员丁', 'female'),
('演员戊', 'other');

-- 2.6 场次
-- 注意：都用未来时间，避免触发“已结束场次不能加入计划观看”
INSERT INTO Performance (production_id, theater_id, start_time, end_time, price_min, price_max, special_tag)
VALUES
(1, 1, '2026-05-10 19:30:00', '2026-05-10 22:00:00', 280, 680, '首演卡'),
(1, 1, '2026-05-11 14:00:00', '2026-05-11 16:30:00', 180, 580, NULL),
(1, 3, '2026-05-16 19:30:00', '2026-05-16 22:00:00', 380, 880, '特别返场'),
(2, 2, '2026-05-12 19:30:00', '2026-05-12 21:30:00', 100, 380, '毕业卡'),
(2, 2, '2026-05-17 14:30:00', '2026-05-17 16:30:00', 120, 420, NULL),
(3, 3, '2026-05-18 14:00:00', '2026-05-18 15:40:00', 220, 520, '限定场');

-- 2.7 场次卡司
INSERT INTO Performance_Cast (performance_id, actor_id, role_id, cast_type, cast_group)
VALUES
(1, 1, 1, 'leading', 'A'),
(1, 2, 2, 'leading', 'A'),
(1, 5, 3, 'supporting', 'A'),

(2, 1, 1, 'leading', 'A'),
(2, 2, 2, 'leading', 'A'),
(2, 5, 3, 'supporting', 'A'),

(3, 3, 1, 'leading', 'B'),
(3, 4, 2, 'leading', 'B'),
(3, 5, 3, 'supporting', 'B'),

(4, 3, 4, 'leading', 'A'),
(4, 4, 5, 'supporting', 'A'),

(5, 3, 4, 'leading', 'B'),
(5, 1, 5, 'supporting', 'B'),

(6, 4, 6, 'leading', 'A'),
(6, 5, 7, 'leading', 'A');

-- 2.8 用户偏好
INSERT INTO Favorite_Actor (user_id, actor_id)
VALUES
(1, 1),
(1, 2),
(1, 5),
(2, 3),
(3, 4),
(3, 5);

INSERT INTO Favorite_Category (user_id, category)
VALUES
(1, '音乐剧'),
(2, '话剧'),
(3, '舞剧');

INSERT INTO Favorite_Language (user_id, language)
VALUES
(1, '普通话'),
(2, '普通话'),
(3, '英语');

INSERT INTO Favorite_District (user_id, city, district)
VALUES
(1, '上海', '黄浦区'),
(1, '上海', '徐汇区'),
(2, '上海', '静安区'),
(3, '上海', '徐汇区');

-- 2.9 餐厅
INSERT INTO Nearby_Restaurant (theater_id, restaurant_name, category, avg_price, distance_m, price_tier)
VALUES
(1, '餐厅A', '中餐', 120, 300, 'mid'),
(1, '餐厅B', '西餐', 260, 450, 'high'),
(1, '餐厅C', '轻食', 70, 200, 'low'),

(2, '餐厅D', '简餐', 65, 180, 'low'),
(2, '餐厅E', '本帮菜', 150, 350, 'mid'),

(3, '餐厅F', '日料', 280, 400, 'high'),
(3, '餐厅G', '咖啡简餐', 90, 220, 'mid');

-- 2.10 交通方案
INSERT INTO Transport_Option (theater_id, transport_type, estimated_time, estimated_cost, suitable_district)
VALUES
(1, 'subway', 35, 4, '黄浦区'),
(1, 'taxi', 20, 35, '黄浦区'),
(1, 'subway', 40, 5, '徐汇区'),

(2, 'bus', 40, 2, '徐汇区'),
(2, 'taxi', 25, 30, '徐汇区'),
(2, 'subway', 30, 4, '静安区'),

(3, 'taxi', 18, 28, '静安区'),
(3, 'subway', 25, 4, '徐汇区'),
(3, 'walk', 15, 0, '徐汇区');

-- 2.11 已看记录
INSERT INTO Watch_Record (user_id, performance_id, watch_date, score)
VALUES
(1, 1, '2026-05-10', 9.0),
(1, 4, '2026-05-12', 8.5),
(2, 4, '2026-05-12', 9.0),
(2, 1, '2026-05-10', 8.0),
(3, 6, '2026-05-18', 9.5);

-- 2.12 计划观看
-- 注意不要和已看重复，否则会被触发器清掉
INSERT INTO Planned_Performance (user_id, performance_id, status)
VALUES
(1, 2, 'planned'),
(1, 3, 'booked'),
(2, 5, 'planned'),
(3, 3, 'planned');

-- =========================
-- 3. 基础检查
-- =========================

SHOW TABLES;

SELECT 'User' AS table_name, COUNT(*) AS row_count FROM User
UNION ALL
SELECT 'Production', COUNT(*) FROM Production
UNION ALL
SELECT 'Theater', COUNT(*) FROM Theater
UNION ALL
SELECT 'Performance', COUNT(*) FROM Performance
UNION ALL
SELECT 'Actor', COUNT(*) FROM Actor
UNION ALL
SELECT 'Role', COUNT(*) FROM Role
UNION ALL
SELECT 'Performance_Cast', COUNT(*) FROM Performance_Cast
UNION ALL
SELECT 'Watch_Record', COUNT(*) FROM Watch_Record
UNION ALL
SELECT 'Planned_Performance', COUNT(*) FROM Planned_Performance
UNION ALL
SELECT 'Favorite_Actor', COUNT(*) FROM Favorite_Actor
UNION ALL
SELECT 'Favorite_Category', COUNT(*) FROM Favorite_Category
UNION ALL
SELECT 'Favorite_Language', COUNT(*) FROM Favorite_Language
UNION ALL
SELECT 'Favorite_District', COUNT(*) FROM Favorite_District
UNION ALL
SELECT 'Nearby_Restaurant', COUNT(*) FROM Nearby_Restaurant
UNION ALL
SELECT 'Transport_Option', COUNT(*) FROM Transport_Option;

-- 查看基础数据
SELECT * FROM User;
SELECT * FROM Theater;
SELECT * FROM Production;
SELECT * FROM Performance ORDER BY performance_id;
SELECT * FROM Actor;
SELECT * FROM Role;
SELECT * FROM Performance_Cast ORDER BY performance_id, actor_id;
SELECT * FROM Watch_Record ORDER BY user_id, performance_id;
SELECT * FROM Planned_Performance ORDER BY user_id, performance_id;

-- =========================
-- 4. 测试触发器
-- =========================

-- 4.1 测试“插入观剧记录后自动删除同场次计划”
-- 先给 2 号用户插入一个计划
INSERT INTO Planned_Performance (user_id, performance_id, status)
VALUES (2, 2, 'planned');

SELECT '触发器测试-插入已看前' AS info;
SELECT * FROM Planned_Performance WHERE user_id = 2 ORDER BY performance_id;

-- 再插入观剧记录，触发 after insert trigger
INSERT INTO Watch_Record (user_id, performance_id, watch_date, score)
VALUES (2, 2, '2026-05-11', 8.0);

SELECT '触发器测试-插入已看后' AS info;
SELECT * FROM Planned_Performance WHERE user_id = 2 ORDER BY performance_id;

-- =========================
-- 5. 测试函数
-- =========================

SELECT 'fn_audience_type' AS test_name, 1 AS user_id, fn_audience_type(1) AS result
UNION ALL
SELECT 'fn_audience_type', 2, fn_audience_type(2)
UNION ALL
SELECT 'fn_audience_type', 3, fn_audience_type(3);

SELECT 'fn_most_similar_user' AS test_name, 1 AS user_id, fn_most_similar_user(1) AS result
UNION ALL
SELECT 'fn_most_similar_user', 2, fn_most_similar_user(2)
UNION ALL
SELECT 'fn_most_similar_user', 3, fn_most_similar_user(3);

SELECT 
    1 AS user_id,
    2 AS performance_id,
    fn_suggested_departure_time(1, 2) AS suggested_departure_time
UNION ALL
SELECT 
    2,
    5,
    fn_suggested_departure_time(2, 5)
UNION ALL
SELECT
    3,
    3,
    fn_suggested_departure_time(3, 3);

-- =========================
-- 6. 测试视图
-- =========================

-- 6.1 用户观剧日历
SELECT 'v_user_calendar - user 1' AS test_name;
SELECT * 
FROM v_user_calendar
WHERE user_id = 1
ORDER BY start_time;

SELECT 'v_user_calendar - user 2' AS test_name;
SELECT * 
FROM v_user_calendar
WHERE user_id = 2
ORDER BY start_time;

-- 6.2 用户偏好画像
SELECT 'v_user_preference_profile - all users' AS test_name;
SELECT * 
FROM v_user_preference_profile
ORDER BY user_id;

-- 6.3 混合推荐
SELECT 'v_hybrid_recommendation - user 1' AS test_name;
SELECT * 
FROM v_hybrid_recommendation
WHERE user_id = 1
ORDER BY start_time, recommended_performance_id;

SELECT 'v_hybrid_recommendation - user 2' AS test_name;
SELECT * 
FROM v_hybrid_recommendation
WHERE user_id = 2
ORDER BY start_time, recommended_performance_id;

SELECT 'v_hybrid_recommendation - user 3' AS test_name;
SELECT * 
FROM v_hybrid_recommendation
WHERE user_id = 3
ORDER BY start_time, recommended_performance_id;

-- 6.4 行程辅助视图
SELECT 'v_planned_trip_assistance - all users' AS test_name;
SELECT * 
FROM v_planned_trip_assistance
ORDER BY user_id, performance_id, restaurant_name, transport_type;

-- =========================
-- 7. 测试存储过程
-- =========================

CALL sp_recommend_by_profile(1);
CALL sp_recommend_by_profile(2);
CALL sp_recommend_by_profile(3);

-- =========================
-- 8. 一些适合答辩展示的查询
-- =========================

-- 8.1 哪个用户最常看什么剧种
SELECT
    wr.user_id,
    u.nickname,
    p.category,
    COUNT(*) AS watched_count
FROM Watch_Record wr
JOIN User u ON wr.user_id = u.user_id
JOIN Performance pf ON wr.performance_id = pf.performance_id
JOIN Production p ON pf.production_id = p.production_id
GROUP BY wr.user_id, u.nickname, p.category
ORDER BY wr.user_id, watched_count DESC;

-- 8.2 每个剧目的平均评分
SELECT
    p.production_id,
    p.title,
    p.version,
    ROUND(AVG(wr.score), 2) AS avg_score,
    COUNT(wr.record_id) AS score_count
FROM Production p
JOIN Performance pf ON p.production_id = pf.production_id
LEFT JOIN Watch_Record wr ON pf.performance_id = wr.performance_id
GROUP BY p.production_id, p.title, p.version
ORDER BY avg_score DESC, score_count DESC;

-- 8.3 特殊场次列表
SELECT
    pf.performance_id,
    p.title,
    p.version,
    th.theater_name,
    pf.start_time,
    pf.special_tag
FROM Performance pf
JOIN Production p ON pf.production_id = p.production_id
JOIN Theater th ON pf.theater_id = th.theater_id
WHERE pf.special_tag IS NOT NULL
ORDER BY pf.start_time;

-- 8.4 某用户喜欢演员是否参与未来特殊场次
SELECT
    u.user_id,
    u.nickname,
    a.actor_name,
    p.title,
    pf.performance_id,
    pf.start_time,
    pf.special_tag
FROM User u
JOIN Favorite_Actor fa ON u.user_id = fa.user_id
JOIN Actor a ON fa.actor_id = a.actor_id
JOIN Performance_Cast pc ON a.actor_id = pc.actor_id
JOIN Performance pf ON pc.performance_id = pf.performance_id
JOIN Production p ON pf.production_id = p.production_id
WHERE pf.start_time > NOW()
  AND pf.special_tag IS NOT NULL
ORDER BY u.user_id, pf.start_time;

-- 8.5 查看某个场次的完整卡司
SELECT
    pf.performance_id,
    p.title,
    a.actor_name,
    r.role_name,
    pc.cast_type,
    pc.cast_group
FROM Performance pf
JOIN Production p ON pf.production_id = p.production_id
JOIN Performance_Cast pc ON pf.performance_id = pc.performance_id
JOIN Actor a ON pc.actor_id = a.actor_id
JOIN Role r ON pc.role_id = r.role_id
WHERE pf.performance_id = 3
ORDER BY pc.cast_group, pc.cast_type, a.actor_name;

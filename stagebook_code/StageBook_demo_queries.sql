-- StageBook 演示查询脚本
USE StageBook;
SET NAMES utf8mb4;

-- 1. 公开演出信息
SELECT * FROM v_public_performance_info ORDER BY start_time LIMIT 20;

-- 2. 用户画像：检查五类画像是否都出现
SELECT user_id, username, favorite_actors, favorite_categories, price_preference, time_preference, total_watched, audience_type FROM v_user_preference_profile ORDER BY user_id;
SELECT audience_type, COUNT(*) AS user_count FROM v_user_preference_profile GROUP BY audience_type;

-- 3. 用户观剧日历
SELECT * FROM v_user_calendar WHERE user_id = 1 ORDER BY start_time;

-- 4. 相似用户函数
SELECT 1 AS user_id, fn_most_similar_user(1) AS most_similar_user_id;

-- 5. 刷新画像推荐缓存并查看结果
CALL sp_recommend_by_profile(1);
SELECT * FROM Profile_Recommendation_Result WHERE user_id = 1 ORDER BY match_score DESC, start_time ASC;

-- 6. 混合推荐：profile_based 和 rule_based 应该有结果；similar_user 取决于当前 A 路径实现逻辑
SELECT recommendation_source, COUNT(*) AS cnt FROM v_hybrid_recommendation GROUP BY recommendation_source;
SELECT * FROM v_hybrid_recommendation WHERE user_id = 1 ORDER BY recommendation_source, start_time LIMIT 20;

-- 7. 行程辅助：餐厅、交通、建议出发时间
SELECT * FROM v_planned_trip_assistance ORDER BY user_id, start_time;

-- 8. 触发器测试：以下语句默认注释，取消注释后应触发错误或自动清理
-- 已结束场次不能加入计划：
-- INSERT INTO Planned_Performance (user_id, performance_id, status) VALUES (1, 1, 'planned');
-- 角色所属剧目与场次所属剧目不一致：
-- INSERT INTO Performance_Cast (performance_id, actor_id, role_id, cast_type, cast_group) VALUES (3, 1, 4, 'leading', 'A');
-- 插入观剧记录后自动删除同用户同场次计划：先计划一个未来场次，再插入观剧记录，可观察计划记录被删除。
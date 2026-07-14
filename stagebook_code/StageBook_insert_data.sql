-- StageBook 教学演示数据集
-- 说明：场馆名称/地址参考公开信息；演出排期、用户、演员、角色、餐厅、交通为课程演示用合成数据。
-- 使用方式：先运行 main_code.sql 建库建表，再运行本文件。
USE StageBook;
SET NAMES utf8mb4;
SET FOREIGN_KEY_CHECKS = 1;
START TRANSACTION;

-- 1. 用户：覆盖演员驱动型、剧种探索型、高性价比型、行程敏感型、综合型和管理员
INSERT INTO `User` (user_id, username, nickname, city, price_preference, time_preference, home_district, role) VALUES
    (1, 'alice', '阿梨', '上海', 'mid', 'weekend_evening', '静安区', 'user'),
    (2, 'bob', '小博', '上海', 'mid', 'weekend_matinee', '徐汇区', 'user'),
    (3, 'cindy', '辛迪', '上海', 'economy', 'weekday_evening', '普陀区', 'user'),
    (4, 'david', '大卫', '上海', 'premium', 'weekend_evening', '浦东新区', 'user'),
    (5, 'emma', '艾玛', '上海', 'mid', 'weekday_evening', '黄浦区', 'user'),
    (6, 'frank', '方可', '上海', 'mid', 'weekend_evening', '静安区', 'user'),
    (7, 'admin_stage', '管理员', '上海', 'premium', 'weekday_evening', '黄浦区', 'admin');

-- 2. 剧院：真实场馆锚点，用于区域、餐厅、交通匹配
INSERT INTO Theater (theater_id, theater_name, city, district, address) VALUES
    (1, '上海大剧院', '上海', '黄浦区', '上海市黄浦区人民大道300号'),
    (2, '上音歌剧院', '上海', '徐汇区', '上海市徐汇区汾阳路6号'),
    (3, '大宁剧院', '上海', '静安区', '上海市静安区平型关路1222号'),
    (4, '上海虹桥艺术中心', '上海', '长宁区', '上海市长宁区天山路888号'),
    (5, '上海东方艺术中心', '上海', '浦东新区', '上海市浦东新区丁香路425号'),
    (6, '万代南梦宫上海文化中心·梦想剧场', '上海', '普陀区', '上海市普陀区宜昌路179号万代南梦宫艺术中心一层');

-- 3. 剧目：覆盖剧种、语言、版本
INSERT INTO Production (production_id, title, category, duration_min, language, version) VALUES
    (1, '星夜回声', '音乐剧', 150, '普通话', 'original'),
    (2, '雨巷来信', '话剧', 110, '普通话', 'revival'),
    (3, '海上花火', '舞剧', 95, '无对白', 'tour'),
    (4, '南城旧梦', '戏曲', 130, '普通话', 'limited'),
    (5, '双城笔记', '音乐剧', 145, '英语', 'tour'),
    (6, '时间旅人', '话剧', 120, '普通话', 'original'),
    (7, '小王子的盒子', '儿童剧', 80, '普通话', 'revival'),
    (8, '幕后即兴夜', '实验戏剧', 100, '普通话', 'limited'),
    (9, '罗密欧与朱丽叶', '话剧', 130, '英语', 'tour'),
    (10, '山海少年', '音乐剧', 125, '粤语', 'limited');

-- 4. 演员
INSERT INTO Actor (actor_id, actor_name, gender) VALUES
    (1, '林知夏', 'female'),
    (2, '周明远', 'male'),
    (3, '陈若安', 'female'),
    (4, '许一舟', 'male'),
    (5, '沈嘉树', 'male'),
    (6, '陆晚', 'female'),
    (7, '苏禾', 'female'),
    (8, '何清', 'male'),
    (9, '顾南枝', 'female'),
    (10, '叶宁', 'female'),
    (11, '唐予', 'male'),
    (12, '白芷', 'female'),
    (13, '秦越', 'male'),
    (14, '梁音', 'female'),
    (15, '莫凡', 'male'),
    (16, '季然', 'other'),
    (17, '夏栀', 'female'),
    (18, '程朗', 'male'),
    (19, '安乔', 'female'),
    (20, '宋迟', 'male'),
    (21, '闻笙', 'female'),
    (22, '裴远', 'male'),
    (23, '顾星河', 'male'),
    (24, '林鹿', 'female');

-- 5. 角色：每部剧 3 个角色
INSERT INTO `Role` (role_id, production_id, role_name) VALUES
    (1, 1, '主唱'),
    (2, 1, '旅人'),
    (3, 1, '旧友'),
    (4, 2, '作家'),
    (5, 2, '邮差'),
    (6, 2, '邻居'),
    (7, 3, '舞者A'),
    (8, 3, '舞者B'),
    (9, 3, '潮汐'),
    (10, 4, '青衣'),
    (11, 4, '书生'),
    (12, 4, '琴师'),
    (13, 5, '译者'),
    (14, 5, '旅伴'),
    (15, 5, '城市旁白'),
    (16, 6, '科学家'),
    (17, 6, '时间旅人'),
    (18, 6, '旁白'),
    (19, 7, '小王子'),
    (20, 7, '飞行员'),
    (21, 7, '狐狸'),
    (22, 8, '导演'),
    (23, 8, '即兴演员'),
    (24, 8, '灯光师'),
    (25, 9, '罗密欧'),
    (26, 9, '朱丽叶'),
    (27, 9, '神父'),
    (28, 10, '少年'),
    (29, 10, '海神'),
    (30, 10, '山灵');

-- 6. 场次：每部剧 3 场，包含过去场次、未来场次和特殊标签场次
INSERT INTO Performance (performance_id, production_id, theater_id, start_time, end_time, price_min, price_max, special_tag) VALUES
    (1, 1, 1, TIMESTAMP(DATE_SUB(CURDATE(), INTERVAL 120 DAY), '19:30:00'), DATE_ADD(TIMESTAMP(DATE_SUB(CURDATE(), INTERVAL 120 DAY), '19:30:00'), INTERVAL 150 MINUTE), 180.00, 680.00, NULL),
    (2, 1, 3, TIMESTAMP(DATE_SUB(CURDATE(), INTERVAL 60 DAY), '14:00:00'), DATE_ADD(TIMESTAMP(DATE_SUB(CURDATE(), INTERVAL 60 DAY), '14:00:00'), INTERVAL 150 MINUTE), 160.00, 580.00, '特别返场'),
    (3, 1, 1, TIMESTAMP(DATE_ADD(CURDATE(), INTERVAL 12 DAY), '19:30:00'), DATE_ADD(TIMESTAMP(DATE_ADD(CURDATE(), INTERVAL 12 DAY), '19:30:00'), INTERVAL 150 MINUTE), 220.00, 780.00, '首演卡'),
    (4, 2, 2, TIMESTAMP(DATE_SUB(CURDATE(), INTERVAL 100 DAY), '19:30:00'), DATE_ADD(TIMESTAMP(DATE_SUB(CURDATE(), INTERVAL 100 DAY), '19:30:00'), INTERVAL 110 MINUTE), 180.00, 480.00, NULL),
    (5, 2, 4, TIMESTAMP(DATE_ADD(CURDATE(), INTERVAL 10 DAY), '19:30:00'), DATE_ADD(TIMESTAMP(DATE_ADD(CURDATE(), INTERVAL 10 DAY), '19:30:00'), INTERVAL 110 MINUTE), 200.00, 520.00, NULL),
    (6, 2, 2, TIMESTAMP(DATE_ADD(CURDATE(), INTERVAL 32 DAY), '14:00:00'), DATE_ADD(TIMESTAMP(DATE_ADD(CURDATE(), INTERVAL 32 DAY), '14:00:00'), INTERVAL 110 MINUTE), 160.00, 420.00, '末场卡'),
    (7, 3, 5, TIMESTAMP(DATE_SUB(CURDATE(), INTERVAL 95 DAY), '19:30:00'), DATE_ADD(TIMESTAMP(DATE_SUB(CURDATE(), INTERVAL 95 DAY), '19:30:00'), INTERVAL 95 MINUTE), 220.00, 680.00, NULL),
    (8, 3, 5, TIMESTAMP(DATE_ADD(CURDATE(), INTERVAL 18 DAY), '14:00:00'), DATE_ADD(TIMESTAMP(DATE_ADD(CURDATE(), INTERVAL 18 DAY), '14:00:00'), INTERVAL 95 MINUTE), 260.00, 780.00, '特别返场'),
    (9, 3, 1, TIMESTAMP(DATE_ADD(CURDATE(), INTERVAL 45 DAY), '19:30:00'), DATE_ADD(TIMESTAMP(DATE_ADD(CURDATE(), INTERVAL 45 DAY), '19:30:00'), INTERVAL 95 MINUTE), 240.00, 720.00, NULL),
    (10, 4, 6, TIMESTAMP(DATE_SUB(CURDATE(), INTERVAL 80 DAY), '19:15:00'), DATE_ADD(TIMESTAMP(DATE_SUB(CURDATE(), INTERVAL 80 DAY), '19:15:00'), INTERVAL 130 MINUTE), 80.00, 380.00, NULL),
    (11, 4, 1, TIMESTAMP(DATE_ADD(CURDATE(), INTERVAL 20 DAY), '19:15:00'), DATE_ADD(TIMESTAMP(DATE_ADD(CURDATE(), INTERVAL 20 DAY), '19:15:00'), INTERVAL 130 MINUTE), 120.00, 480.00, '名家专场'),
    (12, 4, 6, TIMESTAMP(DATE_ADD(CURDATE(), INTERVAL 50 DAY), '14:00:00'), DATE_ADD(TIMESTAMP(DATE_ADD(CURDATE(), INTERVAL 50 DAY), '14:00:00'), INTERVAL 130 MINUTE), 80.00, 360.00, '毕业卡'),
    (13, 5, 4, TIMESTAMP(DATE_SUB(CURDATE(), INTERVAL 75 DAY), '19:30:00'), DATE_ADD(TIMESTAMP(DATE_SUB(CURDATE(), INTERVAL 75 DAY), '19:30:00'), INTERVAL 145 MINUTE), 280.00, 880.00, NULL),
    (14, 5, 1, TIMESTAMP(DATE_ADD(CURDATE(), INTERVAL 16 DAY), '19:30:00'), DATE_ADD(TIMESTAMP(DATE_ADD(CURDATE(), INTERVAL 16 DAY), '19:30:00'), INTERVAL 145 MINUTE), 320.00, 980.00, '巡演首站'),
    (15, 5, 4, TIMESTAMP(DATE_ADD(CURDATE(), INTERVAL 40 DAY), '14:00:00'), DATE_ADD(TIMESTAMP(DATE_ADD(CURDATE(), INTERVAL 40 DAY), '14:00:00'), INTERVAL 145 MINUTE), 260.00, 780.00, NULL),
    (16, 6, 3, TIMESTAMP(DATE_SUB(CURDATE(), INTERVAL 50 DAY), '19:30:00'), DATE_ADD(TIMESTAMP(DATE_SUB(CURDATE(), INTERVAL 50 DAY), '19:30:00'), INTERVAL 120 MINUTE), 220.00, 620.00, NULL),
    (17, 6, 2, TIMESTAMP(DATE_ADD(CURDATE(), INTERVAL 14 DAY), '19:30:00'), DATE_ADD(TIMESTAMP(DATE_ADD(CURDATE(), INTERVAL 14 DAY), '19:30:00'), INTERVAL 120 MINUTE), 240.00, 680.00, NULL),
    (18, 6, 3, TIMESTAMP(DATE_ADD(CURDATE(), INTERVAL 35 DAY), '19:30:00'), DATE_ADD(TIMESTAMP(DATE_ADD(CURDATE(), INTERVAL 35 DAY), '19:30:00'), INTERVAL 120 MINUTE), 220.00, 620.00, '特别返场'),
    (19, 7, 4, TIMESTAMP(DATE_SUB(CURDATE(), INTERVAL 30 DAY), '14:00:00'), DATE_ADD(TIMESTAMP(DATE_SUB(CURDATE(), INTERVAL 30 DAY), '14:00:00'), INTERVAL 80 MINUTE), 80.00, 280.00, NULL),
    (20, 7, 6, TIMESTAMP(DATE_ADD(CURDATE(), INTERVAL 11 DAY), '14:00:00'), DATE_ADD(TIMESTAMP(DATE_ADD(CURDATE(), INTERVAL 11 DAY), '14:00:00'), INTERVAL 80 MINUTE), 90.00, 300.00, NULL),
    (21, 7, 4, TIMESTAMP(DATE_ADD(CURDATE(), INTERVAL 38 DAY), '10:30:00'), DATE_ADD(TIMESTAMP(DATE_ADD(CURDATE(), INTERVAL 38 DAY), '10:30:00'), INTERVAL 80 MINUTE), 80.00, 260.00, '亲子场'),
    (22, 8, 6, TIMESTAMP(DATE_SUB(CURDATE(), INTERVAL 45 DAY), '19:30:00'), DATE_ADD(TIMESTAMP(DATE_SUB(CURDATE(), INTERVAL 45 DAY), '19:30:00'), INTERVAL 100 MINUTE), 120.00, 380.00, NULL),
    (23, 8, 3, TIMESTAMP(DATE_ADD(CURDATE(), INTERVAL 21 DAY), '19:30:00'), DATE_ADD(TIMESTAMP(DATE_ADD(CURDATE(), INTERVAL 21 DAY), '19:30:00'), INTERVAL 100 MINUTE), 150.00, 420.00, '实验开放场'),
    (24, 8, 2, TIMESTAMP(DATE_ADD(CURDATE(), INTERVAL 55 DAY), '19:30:00'), DATE_ADD(TIMESTAMP(DATE_ADD(CURDATE(), INTERVAL 55 DAY), '19:30:00'), INTERVAL 100 MINUTE), 150.00, 450.00, NULL),
    (25, 9, 2, TIMESTAMP(DATE_SUB(CURDATE(), INTERVAL 65 DAY), '19:30:00'), DATE_ADD(TIMESTAMP(DATE_SUB(CURDATE(), INTERVAL 65 DAY), '19:30:00'), INTERVAL 130 MINUTE), 260.00, 680.00, NULL),
    (26, 9, 1, TIMESTAMP(DATE_ADD(CURDATE(), INTERVAL 25 DAY), '19:30:00'), DATE_ADD(TIMESTAMP(DATE_ADD(CURDATE(), INTERVAL 25 DAY), '19:30:00'), INTERVAL 130 MINUTE), 300.00, 780.00, '经典复排'),
    (27, 9, 5, TIMESTAMP(DATE_ADD(CURDATE(), INTERVAL 60 DAY), '14:00:00'), DATE_ADD(TIMESTAMP(DATE_ADD(CURDATE(), INTERVAL 60 DAY), '14:00:00'), INTERVAL 130 MINUTE), 280.00, 720.00, NULL),
    (28, 10, 5, TIMESTAMP(DATE_SUB(CURDATE(), INTERVAL 40 DAY), '19:30:00'), DATE_ADD(TIMESTAMP(DATE_SUB(CURDATE(), INTERVAL 40 DAY), '19:30:00'), INTERVAL 125 MINUTE), 180.00, 520.00, NULL),
    (29, 10, 5, TIMESTAMP(DATE_ADD(CURDATE(), INTERVAL 27 DAY), '19:30:00'), DATE_ADD(TIMESTAMP(DATE_ADD(CURDATE(), INTERVAL 27 DAY), '19:30:00'), INTERVAL 125 MINUTE), 200.00, 580.00, '限定返场'),
    (30, 10, 6, TIMESTAMP(DATE_ADD(CURDATE(), INTERVAL 70 DAY), '19:30:00'), DATE_ADD(TIMESTAMP(DATE_ADD(CURDATE(), INTERVAL 70 DAY), '19:30:00'), INTERVAL 125 MINUTE), 180.00, 560.00, NULL);

-- 7. 场次卡司：每场 3 名演员，体现演员-场次-角色三元关联
INSERT INTO Performance_Cast (performance_id, actor_id, role_id, cast_type, cast_group) VALUES
    (1, 1, 1, 'leading', 'A'),
    (1, 2, 2, 'leading', 'A'),
    (1, 3, 3, 'supporting', 'A'),
    (2, 1, 1, 'leading', 'A'),
    (2, 2, 2, 'leading', 'A'),
    (2, 3, 3, 'supporting', 'A'),
    (3, 1, 1, 'leading', 'A'),
    (3, 2, 2, 'leading', 'A'),
    (3, 3, 3, 'supporting', 'A'),
    (4, 7, 4, 'leading', 'A'),
    (4, 8, 5, 'leading', 'A'),
    (4, 9, 6, 'supporting', 'A'),
    (5, 7, 4, 'leading', 'A'),
    (5, 8, 5, 'leading', 'A'),
    (5, 9, 6, 'supporting', 'A'),
    (6, 7, 4, 'leading', 'A'),
    (6, 8, 5, 'leading', 'A'),
    (6, 9, 6, 'supporting', 'A'),
    (7, 10, 7, 'leading', 'A'),
    (7, 11, 8, 'leading', 'A'),
    (7, 12, 9, 'ensemble', 'A'),
    (8, 10, 7, 'leading', 'A'),
    (8, 11, 8, 'leading', 'A'),
    (8, 12, 9, 'ensemble', 'A'),
    (9, 10, 7, 'leading', 'A'),
    (9, 11, 8, 'leading', 'A'),
    (9, 12, 9, 'ensemble', 'A'),
    (10, 13, 10, 'leading', 'A'),
    (10, 14, 11, 'leading', 'A'),
    (10, 15, 12, 'supporting', 'A'),
    (11, 13, 10, 'leading', 'A'),
    (11, 14, 11, 'leading', 'A'),
    (11, 15, 12, 'supporting', 'A'),
    (12, 13, 10, 'leading', 'A'),
    (12, 14, 11, 'leading', 'A'),
    (12, 15, 12, 'supporting', 'A'),
    (13, 1, 13, 'leading', 'A'),
    (13, 5, 14, 'leading', 'B'),
    (13, 6, 15, 'supporting', 'A'),
    (14, 1, 13, 'leading', 'A'),
    (14, 5, 14, 'leading', 'B'),
    (14, 6, 15, 'supporting', 'A'),
    (15, 1, 13, 'leading', 'A'),
    (15, 5, 14, 'leading', 'B'),
    (15, 6, 15, 'supporting', 'A'),
    (16, 2, 16, 'leading', 'A'),
    (16, 8, 17, 'leading', 'A'),
    (16, 16, 18, 'supporting', 'A'),
    (17, 2, 16, 'leading', 'A'),
    (17, 8, 17, 'leading', 'A'),
    (17, 16, 18, 'supporting', 'A'),
    (18, 2, 16, 'leading', 'A'),
    (18, 8, 17, 'leading', 'A'),
    (18, 16, 18, 'supporting', 'A'),
    (19, 17, 19, 'leading', 'A'),
    (19, 18, 20, 'leading', 'A'),
    (19, 19, 21, 'guest', '特别卡司'),
    (20, 17, 19, 'leading', 'A'),
    (20, 18, 20, 'leading', 'A'),
    (20, 19, 21, 'guest', '特别卡司'),
    (21, 17, 19, 'leading', 'A'),
    (21, 18, 20, 'leading', 'A'),
    (21, 19, 21, 'guest', '特别卡司'),
    (22, 20, 22, 'leading', 'A'),
    (22, 21, 23, 'ensemble', 'A'),
    (22, 22, 24, 'supporting', 'A'),
    (23, 20, 22, 'leading', 'A'),
    (23, 21, 23, 'ensemble', 'A'),
    (23, 22, 24, 'supporting', 'A'),
    (24, 20, 22, 'leading', 'A'),
    (24, 21, 23, 'ensemble', 'A'),
    (24, 22, 24, 'supporting', 'A'),
    (25, 23, 25, 'leading', 'A'),
    (25, 24, 26, 'leading', 'A'),
    (25, 8, 27, 'supporting', 'A'),
    (26, 23, 25, 'leading', 'A'),
    (26, 24, 26, 'leading', 'A'),
    (26, 8, 27, 'supporting', 'A'),
    (27, 23, 25, 'leading', 'A'),
    (27, 24, 26, 'leading', 'A'),
    (27, 8, 27, 'supporting', 'A'),
    (28, 4, 28, 'leading', 'A'),
    (28, 6, 29, 'leading', 'A'),
    (28, 14, 30, 'supporting', 'A'),
    (29, 4, 28, 'leading', 'A'),
    (29, 6, 29, 'leading', 'A'),
    (29, 14, 30, 'supporting', 'A'),
    (30, 4, 28, 'leading', 'A'),
    (30, 6, 29, 'leading', 'A'),
    (30, 14, 30, 'supporting', 'A');

-- 8. 主动偏好：喜欢演员
INSERT INTO Favorite_Actor (user_id, actor_id) VALUES
    (1,1),
    (1,2),
    (1,3),
    (2,10),
    (2,20),
    (3,17),
    (4,23),
    (4,4),
    (5,8),
    (6,1),
    (6,2),
    (6,5);

-- 9. 主动偏好：喜欢剧种
INSERT INTO Favorite_Category (user_id, category) VALUES
    (1,'音乐剧'),
    (1,'话剧'),
    (2,'音乐剧'),
    (2,'话剧'),
    (2,'舞剧'),
    (2,'实验戏剧'),
    (2,'儿童剧'),
    (3,'儿童剧'),
    (3,'戏曲'),
    (4,'话剧'),
    (4,'舞剧'),
    (5,'音乐剧'),
    (6,'音乐剧'),
    (6,'话剧');

-- 10. 主动偏好：喜欢语言
INSERT INTO Favorite_Language (user_id, language) VALUES
    (1,'普通话'),
    (1,'英语'),
    (2,'普通话'),
    (2,'无对白'),
    (3,'普通话'),
    (4,'普通话'),
    (4,'英语'),
    (5,'英语'),
    (6,'普通话'),
    (6,'英语');

-- 11. 主动偏好：喜欢区域
INSERT INTO Favorite_District (user_id, city, district) VALUES
    (1,'上海','黄浦区'),
    (1,'上海','静安区'),
    (2,'上海','徐汇区'),
    (2,'上海','长宁区'),
    (3,'上海','普陀区'),
    (4,'上海','浦东新区'),
    (4,'上海','黄浦区'),
    (5,'上海','黄浦区'),
    (6,'上海','黄浦区'),
    (6,'上海','静安区');

-- 12. 观剧记录：支撑画像推断、相似用户、评分统计
INSERT INTO Watch_Record (user_id, performance_id, watch_date, score) VALUES
    (1, 1, DATE((SELECT start_time FROM Performance WHERE performance_id = 1)), 9.2),
    (1, 2, DATE((SELECT start_time FROM Performance WHERE performance_id = 2)), 8.8),
    (1, 13, DATE((SELECT start_time FROM Performance WHERE performance_id = 13)), 8.6),
    (1, 16, DATE((SELECT start_time FROM Performance WHERE performance_id = 16)), 8.0),
    (2, 4, DATE((SELECT start_time FROM Performance WHERE performance_id = 4)), 8.1),
    (2, 7, DATE((SELECT start_time FROM Performance WHERE performance_id = 7)), 7.8),
    (2, 10, DATE((SELECT start_time FROM Performance WHERE performance_id = 10)), 8.5),
    (2, 19, DATE((SELECT start_time FROM Performance WHERE performance_id = 19)), 8.0),
    (2, 22, DATE((SELECT start_time FROM Performance WHERE performance_id = 22)), 8.3),
    (3, 10, DATE((SELECT start_time FROM Performance WHERE performance_id = 10)), 8.2),
    (3, 19, DATE((SELECT start_time FROM Performance WHERE performance_id = 19)), 8.0),
    (3, 22, DATE((SELECT start_time FROM Performance WHERE performance_id = 22)), 7.6),
    (4, 28, DATE((SELECT start_time FROM Performance WHERE performance_id = 28)), 8.9),
    (5, 13, DATE((SELECT start_time FROM Performance WHERE performance_id = 13)), 7.5),
    (5, 25, DATE((SELECT start_time FROM Performance WHERE performance_id = 25)), 8.1),
    (6, 1, DATE((SELECT start_time FROM Performance WHERE performance_id = 1)), 9.0),
    (6, 2, DATE((SELECT start_time FROM Performance WHERE performance_id = 2)), 8.5),
    (6, 13, DATE((SELECT start_time FROM Performance WHERE performance_id = 13)), 8.9),
    (6, 16, DATE((SELECT start_time FROM Performance WHERE performance_id = 16)), 8.2);

-- 13. 计划观看：支撑日历、行程辅助、行程敏感型画像
INSERT INTO Planned_Performance (user_id, performance_id, status) VALUES
    (1, 3, 'planned'),
    (1, 14, 'booked'),
    (2, 6, 'planned'),
    (2, 8, 'planned'),
    (3, 11, 'booked'),
    (3, 20, 'planned'),
    (3, 23, 'canceled'),
    (4, 18, 'planned'),
    (4, 21, 'booked'),
    (4, 27, 'planned'),
    (4, 29, 'booked'),
    (5, 5, 'planned'),
    (6, 15, 'booked'),
    (6, 17, 'planned');

-- 14. 周边餐厅：每个剧院 low/mid/high 三档，price_tier 为预先标注
INSERT INTO Nearby_Restaurant (restaurant_id, theater_id, restaurant_name, category, avg_price, distance_m, price_tier) VALUES
    (1, 1, '大剧院轻食站', '简餐', 68.00, 180, 'low'),
    (2, 1, '大剧院小馆', '本帮菜', 138.00, 320, 'mid'),
    (3, 1, '大剧院剧前餐厅', '西餐', 288.00, 520, 'high'),
    (4, 2, '上音歌剧院轻食站', '简餐', 68.00, 180, 'low'),
    (5, 2, '上音歌剧院小馆', '本帮菜', 138.00, 320, 'mid'),
    (6, 2, '上音歌剧院剧前餐厅', '西餐', 288.00, 520, 'high'),
    (7, 3, '大宁剧院轻食站', '简餐', 68.00, 180, 'low'),
    (8, 3, '大宁剧院小馆', '本帮菜', 138.00, 320, 'mid'),
    (9, 3, '大宁剧院剧前餐厅', '西餐', 288.00, 520, 'high'),
    (10, 4, '虹桥艺术中心轻食站', '简餐', 68.00, 180, 'low'),
    (11, 4, '虹桥艺术中心小馆', '本帮菜', 138.00, 320, 'mid'),
    (12, 4, '虹桥艺术中心剧前餐厅', '西餐', 288.00, 520, 'high'),
    (13, 5, '东方艺术中心轻食站', '简餐', 68.00, 180, 'low'),
    (14, 5, '东方艺术中心小馆', '本帮菜', 138.00, 320, 'mid'),
    (15, 5, '东方艺术中心剧前餐厅', '西餐', 288.00, 520, 'high'),
    (16, 6, '万代南梦宫文化中心轻食站', '简餐', 68.00, 180, 'low'),
    (17, 6, '万代南梦宫文化中心小馆', '本帮菜', 138.00, 320, 'mid'),
    (18, 6, '万代南梦宫文化中心剧前餐厅', '西餐', 288.00, 520, 'high');

-- 15. 交通方案：每个剧院覆盖 6 个出发区域，供 home_district 匹配
INSERT INTO Transport_Option (transport_id, theater_id, transport_type, estimated_time, estimated_cost, suitable_district) VALUES
    (1, 1, 'walk', 12, 0.00, '黄浦区'),
    (2, 1, 'subway', 31, 5.00, '徐汇区'),
    (3, 1, 'subway', 47, 7.00, '静安区'),
    (4, 1, 'subway', 53, 8.00, '长宁区'),
    (5, 1, 'taxi', 48, 88.00, '浦东新区'),
    (6, 1, 'subway', 65, 10.00, '普陀区'),
    (7, 2, 'subway', 32, 5.00, '黄浦区'),
    (8, 2, 'walk', 12, 0.00, '徐汇区'),
    (9, 2, 'subway', 32, 5.00, '静安区'),
    (10, 2, 'subway', 47, 7.00, '长宁区'),
    (11, 2, 'taxi', 44, 78.00, '浦东新区'),
    (12, 2, 'subway', 59, 9.00, '普陀区'),
    (13, 3, 'subway', 47, 7.00, '黄浦区'),
    (14, 3, 'subway', 30, 5.00, '徐汇区'),
    (15, 3, 'walk', 12, 0.00, '静安区'),
    (16, 3, 'subway', 30, 5.00, '长宁区'),
    (17, 3, 'taxi', 40, 68.00, '浦东新区'),
    (18, 3, 'subway', 53, 8.00, '普陀区'),
    (19, 4, 'subway', 53, 8.00, '黄浦区'),
    (20, 4, 'subway', 47, 7.00, '徐汇区'),
    (21, 4, 'subway', 31, 5.00, '静安区'),
    (22, 4, 'walk', 12, 0.00, '长宁区'),
    (23, 4, 'subway', 31, 5.00, '浦东新区'),
    (24, 4, 'subway', 47, 7.00, '普陀区'),
    (25, 5, 'taxi', 48, 88.00, '黄浦区'),
    (26, 5, 'taxi', 44, 78.00, '徐汇区'),
    (27, 5, 'taxi', 40, 68.00, '静安区'),
    (28, 5, 'subway', 32, 5.00, '长宁区'),
    (29, 5, 'walk', 12, 0.00, '浦东新区'),
    (30, 5, 'subway', 32, 5.00, '普陀区'),
    (31, 6, 'subway', 65, 10.00, '黄浦区'),
    (32, 6, 'subway', 59, 9.00, '徐汇区'),
    (33, 6, 'subway', 53, 8.00, '静安区'),
    (34, 6, 'subway', 47, 7.00, '长宁区'),
    (35, 6, 'subway', 30, 5.00, '浦东新区'),
    (36, 6, 'walk', 12, 0.00, '普陀区');

-- 16. 管理员日志：展示基础审计
INSERT INTO Admin_Log (admin_user_id, action_type, target_table, target_id, description) VALUES
    (7, 'INSERT', 'Production', 1, '新增剧目《星夜回声》'),
    (7, 'INSERT', 'Performance', 3, '新增《星夜回声》未来首演卡场次'),
    (7, 'INSERT', 'Nearby_Restaurant', 1, '维护上海大剧院周边餐厅数据'),
    (7, 'INSERT', 'Transport_Option', 1, '维护上海大剧院交通方案');

COMMIT;

-- 17. 生成画像推荐缓存：v_hybrid_recommendation 的 profile_based 路径依赖该缓存
CALL sp_recommend_by_profile(1);
CALL sp_recommend_by_profile(2);
CALL sp_recommend_by_profile(3);
CALL sp_recommend_by_profile(4);
CALL sp_recommend_by_profile(5);
CALL sp_recommend_by_profile(6);

-- 数据加载后建议执行：SELECT * FROM v_user_preference_profile; SELECT * FROM v_planned_trip_assistance;
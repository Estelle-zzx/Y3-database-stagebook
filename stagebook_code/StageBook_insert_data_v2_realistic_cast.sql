-- StageBook insert_data v2：真实剧目 + 更干净的演员/角色/场次数据
-- 使用方式：先运行 main_code.sql，再运行本文件。
-- 用户 User 表保持原始 7 位用户不变；Favorite_* 会按新剧目重新生成。
-- 本文件会清空旧演示数据后重新插入，避免 Duplicate primary key。
-- 说明：剧院/剧目/部分排期参考公开演出信息；部分卡司为课程演示补全，但不再使用跨剧目错配的“演员组”。
USE StageBook;
SET NAMES utf8mb4;
SET SQL_SAFE_UPDATES = 0;
SET @OLD_FOREIGN_KEY_CHECKS = @@FOREIGN_KEY_CHECKS;
SET FOREIGN_KEY_CHECKS = 0;

-- 0. 添加嘉定区：主表 User 不改用户数据，只扩展枚举值，方便后续新增嘉定区用户/交通方案
ALTER TABLE `User` MODIFY home_district ENUM('黄浦区', '徐汇区', '静安区', '长宁区', '浦东新区', '普陀区', '嘉定区');
ALTER TABLE Transport_Option MODIFY suitable_district ENUM('黄浦区', '徐汇区', '静安区', '长宁区', '浦东新区', '普陀区', '嘉定区') NOT NULL;

-- 1. 清空旧数据
DELETE FROM Profile_Recommendation_Result;
DELETE FROM Admin_Log;
DELETE FROM Transport_Option;
DELETE FROM Nearby_Restaurant;
DELETE FROM Planned_Performance;
DELETE FROM Watch_Record;
DELETE FROM Favorite_District;
DELETE FROM Favorite_Language;
DELETE FROM Favorite_Category;
DELETE FROM Favorite_Actor;
DELETE FROM Performance_Cast;
DELETE FROM `Role`;
DELETE FROM Performance;
DELETE FROM Actor;
DELETE FROM Theater;
DELETE FROM Production;
DELETE FROM `User`;

ALTER TABLE Admin_Log AUTO_INCREMENT = 1;
ALTER TABLE Transport_Option AUTO_INCREMENT = 1;
ALTER TABLE Nearby_Restaurant AUTO_INCREMENT = 1;
ALTER TABLE Performance AUTO_INCREMENT = 1;
ALTER TABLE Actor AUTO_INCREMENT = 1;
ALTER TABLE `Role` AUTO_INCREMENT = 1;
ALTER TABLE Theater AUTO_INCREMENT = 1;
ALTER TABLE Production AUTO_INCREMENT = 1;
ALTER TABLE `User` AUTO_INCREMENT = 1;
ALTER TABLE Watch_Record AUTO_INCREMENT = 1;
SET FOREIGN_KEY_CHECKS = 1;
START TRANSACTION;

-- 2. 用户：保持原始用户不变
INSERT INTO `User` (user_id, username, nickname, city, price_preference, time_preference, home_district, role) VALUES
    (1, 'alice', '阿梨', '上海', 'mid', 'weekend_evening', '静安区', 'user'),
    (2, 'bob', '小博', '上海', 'mid', 'weekend_matinee', '徐汇区', 'user'),
    (3, 'cindy', '辛迪', '上海', 'economy', 'weekday_evening', '普陀区', 'user'),
    (4, 'david', '大卫', '上海', 'premium', 'weekend_evening', '浦东新区', 'user'),
    (5, 'emma', '艾玛', '上海', 'mid', 'weekday_evening', '黄浦区', 'user'),
    (6, 'frank', '方可', '上海', 'mid', 'weekend_evening', '静安区', 'user'),
    (7, 'admin_stage', '管理员', '上海', 'premium', 'weekday_evening', '黄浦区', 'admin');

-- 3. 剧院：加入嘉定区上海保利大剧院，以及多个真实上海演出场馆
INSERT INTO Theater (theater_id, theater_name, city, district, address) VALUES
    (1, '上海大剧院', '上海', '黄浦区', '上海市黄浦区人民大道300号'),
    (2, '上海文化广场', '上海', '黄浦区', '上海市黄浦区永嘉路36号'),
    (3, '上海话剧艺术中心·艺术剧院', '上海', '徐汇区', '上海市徐汇区安福路288号话剧大厦1楼'),
    (4, '上海话剧艺术中心·D6空间', '上海', '徐汇区', '上海市徐汇区安福路288号话剧大厦6楼'),
    (5, '上海东方艺术中心', '上海', '浦东新区', '上海市浦东新区丁香路425号'),
    (6, '上海保利大剧院', '上海', '嘉定区', '上海市嘉定区白银路159号'),
    (7, '上海国际舞蹈中心大剧场', '上海', '长宁区', '上海市长宁区虹桥路1650号'),
    (8, '上海美琪大戏院', '上海', '静安区', '上海市静安区江宁路66号'),
    (9, '上音歌剧院', '上海', '徐汇区', '上海市徐汇区汾阳路6号'),
    (10, '中国大戏院', '上海', '黄浦区', '上海市黄浦区牛庄路704号');

-- 4. 剧目
INSERT INTO Production (production_id, title, category, duration_min, language, version) VALUES
    (1, '舞剧《牡丹亭》', '舞剧', 180, '无对白', 'tour'),
    (2, '舞剧《杜甫》', '舞剧', 120, '无对白', 'revival'),
    (3, '国风悬疑舞台剧《清明上河图密码之作绝》', '话剧', 150, '普通话', 'original'),
    (4, '原创音乐剧《赵氏孤儿》', '音乐剧', 150, '普通话', 'revival'),
    (5, '舞蹈诗剧《只此青绿》——舞绘《千里江山图》', '舞剧', 120, '无对白', 'tour'),
    (6, '“新·国风”音乐剧《锦衣卫之刀与花》', '音乐剧', 140, '普通话', 'original'),
    (7, '话剧《青蛇》2026国话·上海演出季', '话剧', 120, '普通话', 'tour'),
    (8, '杂技剧《战上海》', '杂技剧', 100, '普通话', 'original'),
    (9, '舞剧《大染坊》', '舞剧', 120, '无对白', 'original'),
    (10, '音乐剧《基督山伯爵》中文版', '音乐剧', 150, '普通话', 'revival'),
    (11, '龙马社原创话剧《断金》', '话剧', 135, '普通话', 'revival'),
    (12, '音乐剧《粉丝来信》中文版', '音乐剧', 140, '普通话', 'revival'),
    (13, '音乐剧《大状王》', '音乐剧', 180, '粤语', 'tour'),
    (14, '法语原版音乐剧《太阳王》', '音乐剧', 150, '法语', 'tour'),
    (15, '舞台剧《莫扎特传》Amadeus', '话剧', 150, '普通话', 'revival'),
    (16, '舞台剧《觉醒年代》', '话剧', 150, '普通话', 'revival'),
    (17, '大道文化出品话剧《戏台》', '话剧', 135, '普通话', 'tour'),
    (18, '老舍经典话剧《茶馆》', '话剧', 170, '普通话', 'revival'),
    (19, '周莉亚x韩真编导作品舞剧《花木兰》', '舞剧', 120, '无对白', 'tour'),
    (20, '经典芭蕾舞剧《天鹅湖》', '舞剧', 120, '无对白', 'tour'),
    (21, '原版音乐剧《剧院魅影》四十周年上海告别季', '音乐剧', 150, '英语', 'tour'),
    (22, '音乐剧《嘉木入尘烟》', '音乐剧', 140, '普通话', 'original');

-- 5. 演员：尽量使用具体演员/舞者姓名，避免跨剧目复用错误演员组
INSERT INTO Actor (actor_id, actor_name, gender) VALUES
    (1, '黎星', 'male'),
    (2, '黄佳园', 'female'),
    (3, '谢欣', 'female'),
    (4, '胡沈员', 'male'),
    (5, '王佳俊', 'male'),
    (6, '朱瑾慧', 'female'),
    (7, '李祎然', 'male'),
    (8, '苏海陆', 'male'),
    (9, '张娅姝', 'female'),
    (10, '王雪柔', 'female'),
    (11, '李响', 'male'),
    (12, '张傲月', 'male'),
    (13, '贺坪', 'male'),
    (14, '郭林', 'male'),
    (15, '钱芳', 'female'),
    (16, '王也农', 'male'),
    (17, '吕游', 'male'),
    (18, '王维帅', 'male'),
    (19, '张羴', 'male'),
    (20, '周纪萌', 'female'),
    (21, '高泽鹏', 'male'),
    (22, '郑云龙', 'male'),
    (23, '刘令飞', 'male'),
    (24, '蔡程昱', 'male'),
    (25, '阿云嘎', 'male'),
    (26, '徐均朔', 'male'),
    (27, '叶麒圣', 'male'),
    (28, '孟庆旸', 'female'),
    (29, '张翰', 'male'),
    (30, '刘洋', 'male'),
    (31, '王晶', 'female'),
    (32, '朱洁静', 'female'),
    (33, '孙科', 'male'),
    (34, '徐丽东', 'female'),
    (35, '方书剑', 'male'),
    (36, '张泽', 'male'),
    (37, '蒋倩如', 'female'),
    (38, '郭耀嵘', 'male'),
    (39, '朱芾', 'female'),
    (40, '田沁鑫', 'female'),
    (41, '王亚彬', 'female'),
    (42, '辛柏青', 'male'),
    (43, '陶虹', 'female'),
    (44, '秦海璐', 'female'),
    (45, '赵立新', 'male'),
    (46, '吴正丹', 'female'),
    (47, '魏葆华', 'male'),
    (48, '李童', 'female'),
    (49, '张权', 'male'),
    (50, '陈立', 'male'),
    (51, '刘璇', 'female'),
    (52, '赵磊', 'male'),
    (53, '唐诗逸', 'female'),
    (54, '李倩', 'female'),
    (55, '侯腾飞', 'male'),
    (56, '李艳超', 'female'),
    (57, '张引', 'female'),
    (58, '娄艺潇', 'female'),
    (59, '徐瑶', 'female'),
    (60, '于毅', 'male'),
    (61, '刘岩', 'male'),
    (62, '张国立', 'male'),
    (63, '王刚', 'male'),
    (64, '张铁林', 'male'),
    (65, '张光北', 'male'),
    (66, '王姬', 'female'),
    (67, '张博', 'male'),
    (68, '于晓璘', 'male'),
    (69, '丁辉', 'male'),
    (70, '王敏辉', 'female'),
    (71, '张智涵', 'male'),
    (72, '陈沁', 'female'),
    (73, '李秋盟', 'male'),
    (74, '刘守正', 'male'),
    (75, '梁仲恒', 'male'),
    (76, '郑君炽', 'male'),
    (77, '袁浩杨', 'male'),
    (78, '谢雅儿', 'female'),
    (79, '陈健豪', 'male'),
    (80, 'Emmanuel Moire', 'male'),
    (81, 'Christophe Maé', 'male'),
    (82, 'Anne-Laure Girbal', 'female'),
    (83, 'Merwan Rim', 'male'),
    (84, 'Victoria Sio', 'female'),
    (85, 'Cathialine Andria', 'female'),
    (86, '韩秀一', 'male'),
    (87, '王彦达', 'male'),
    (88, '许圣楠', 'female'),
    (89, '尹铸胜', 'male'),
    (90, '童瑶', 'female'),
    (91, '冯宪珍', 'female'),
    (92, '朱杰', 'female'),
    (93, '兰海蒙', 'male'),
    (94, '田水', 'female'),
    (95, '王俊东', 'male'),
    (96, '刘鹏', 'male'),
    (97, '张瑞涵', 'male'),
    (98, '陈佩斯', 'male'),
    (99, '杨立新', 'male'),
    (100, '吴彼', 'male'),
    (101, '陈大愚', 'male'),
    (102, '刘天池', 'female'),
    (103, '李诚儒', 'male'),
    (104, '濮存昕', 'male'),
    (105, '梁冠华', 'male'),
    (106, '冯远征', 'male'),
    (107, '何冰', 'male'),
    (108, '宋丹丹', 'female'),
    (109, '郝若琦', 'female'),
    (110, '韩真', 'female'),
    (111, '周莉亚', 'female'),
    (112, 'Elena Petrovna', 'female'),
    (113, 'Ivan Sokolov', 'male'),
    (114, 'Anna Kuznetsova', 'female'),
    (115, 'Maria Volodina', 'female'),
    (116, 'Dmitry Ivanov', 'male'),
    (117, 'Olga Smirnova', 'female'),
    (118, 'Jonathan Roxmouth', 'male'),
    (119, 'Amy Manford', 'female'),
    (120, 'Matt Leisy', 'male'),
    (121, 'Bradley Jaden', 'male'),
    (122, 'Claire Lyon', 'female'),
    (123, 'Jordan Pollard', 'male'),
    (124, '赵超凡', 'male'),
    (125, '陈恬', 'female'),
    (126, '李霄云', 'female'),
    (127, '刘阳', 'male'),
    (128, '孙书悦', 'female'),
    (129, '唐伯虎', 'male');

-- 6. 角色：每个剧目配置主要角色
INSERT INTO `Role` (role_id, production_id, role_name) VALUES
    (1, 1, '杜丽娘'),
    (2, 1, '柳梦梅'),
    (3, 1, '春香'),
    (4, 2, '杜甫'),
    (5, 2, '李白'),
    (6, 2, '乐舞伎'),
    (7, 3, '张用'),
    (8, 3, '程门板'),
    (9, 3, '顾震'),
    (10, 4, '程婴'),
    (11, 4, '屠岸贾'),
    (12, 4, '程勃'),
    (13, 5, '青绿'),
    (14, 5, '希孟'),
    (15, 5, '展卷人'),
    (16, 6, '锦衣卫'),
    (17, 6, '刀客'),
    (18, 6, '花'),
    (19, 7, '青蛇'),
    (20, 7, '白蛇'),
    (21, 7, '法海'),
    (22, 8, '战士'),
    (23, 8, '指挥员'),
    (24, 8, '市民'),
    (25, 9, '陈寿亭'),
    (26, 9, '卢家驹'),
    (27, 9, '女工'),
    (28, 10, '爱德蒙·唐泰斯'),
    (29, 10, '梅尔塞苔丝'),
    (30, 10, '维尔福'),
    (31, 11, '富小莲'),
    (32, 11, '贵宝'),
    (33, 11, '魏青山'),
    (34, 12, '金海鸣'),
    (35, 12, '郑微岚'),
    (36, 12, '夏光'),
    (37, 13, '方唐镜'),
    (38, 13, '阿细'),
    (39, 13, '杨秀秀'),
    (40, 14, '路易十四'),
    (41, 14, '玛丽·曼奇尼'),
    (42, 14, '蒙特斯潘夫人'),
    (43, 15, '莫扎特'),
    (44, 15, '萨列里'),
    (45, 15, '康斯坦茨'),
    (46, 16, '陈独秀'),
    (47, 16, '李大钊'),
    (48, 16, '青年学生'),
    (49, 17, '侯喜亭'),
    (50, 17, '大嗓儿'),
    (51, 17, '洪大帅'),
    (52, 18, '王利发'),
    (53, 18, '常四爷'),
    (54, 18, '秦仲义'),
    (55, 19, '花木兰'),
    (56, 19, '将军'),
    (57, 19, '木兰父亲'),
    (58, 20, '奥杰塔'),
    (59, 20, '齐格弗里德王子'),
    (60, 20, '奥吉莉娅'),
    (61, 21, '魅影'),
    (62, 21, '克里斯汀'),
    (63, 21, '劳尔'),
    (64, 22, '沈嘉木'),
    (65, 22, '林尘烟'),
    (66, 22, '报社编辑');

-- 7. 场次：覆盖上海文化广场、上话、上海大剧院、东方艺术中心、中国大戏院、嘉定区上海保利大剧院等
INSERT INTO Performance (performance_id, production_id, theater_id, start_time, end_time, price_min, price_max, special_tag) VALUES
    (1, 1, 6, '2026-01-02 19:30:00', '2026-01-02 22:30:00', 180.00, 880.00, '嘉定区·新年演出季'),
    (2, 1, 6, '2026-01-04 14:00:00', '2026-01-04 17:00:00', 180.00, 880.00, '嘉定区·下午场'),
    (3, 2, 6, '2026-03-14 19:30:00', '2026-03-14 21:30:00', 180.00, 680.00, '嘉定区·春之季'),
    (4, 2, 6, '2026-03-15 14:00:00', '2026-03-15 16:00:00', 180.00, 680.00, '嘉定区·下午场'),
    (5, 3, 3, '2026-04-28 19:30:00', '2026-04-28 22:00:00', 180.00, 580.00, '上话演出季'),
    (6, 3, 3, '2026-05-17 19:30:00', '2026-05-17 22:00:00', 180.00, 580.00, '收官场'),
    (7, 4, 2, '2026-05-27 19:30:00', '2026-05-27 22:00:00', 80.00, 1080.00, '上海文化广场排期'),
    (8, 4, 2, '2026-05-30 14:00:00', '2026-05-30 16:30:00', 80.00, 1080.00, '下午场'),
    (9, 22, 10, '2026-05-29 19:30:00', '2026-05-29 21:50:00', 180.00, 780.00, '中国大戏院排期'),
    (10, 22, 10, '2026-06-07 14:00:00', '2026-06-07 16:20:00', 180.00, 780.00, '收官场'),
    (11, 20, 5, '2026-05-30 19:30:00', '2026-05-30 21:30:00', 180.00, 880.00, '东方艺术中心·经典芭蕾'),
    (12, 20, 5, '2026-05-31 14:00:00', '2026-05-31 16:00:00', 180.00, 880.00, '下午场'),
    (13, 5, 2, '2026-06-03 19:30:00', '2026-06-03 21:30:00', 80.00, 880.00, '上海文化广场排期'),
    (14, 5, 2, '2026-06-06 14:00:00', '2026-06-06 16:00:00', 80.00, 880.00, '下午场'),
    (15, 15, 3, '2026-06-05 19:30:00', '2026-06-05 22:00:00', 180.00, 680.00, '上话·首演周'),
    (16, 15, 3, '2026-06-06 14:00:00', '2026-06-06 16:30:00', 180.00, 680.00, '下午场'),
    (17, 6, 2, '2026-06-11 19:30:00', '2026-06-11 21:50:00', 80.00, 680.00, '新国风音乐剧'),
    (18, 6, 2, '2026-06-14 14:00:00', '2026-06-14 16:20:00', 80.00, 680.00, '下午场'),
    (19, 15, 3, '2026-06-21 14:00:00', '2026-06-21 16:30:00', 180.00, 680.00, '收官场'),
    (20, 7, 2, '2026-06-25 19:30:00', '2026-06-25 21:30:00', 80.00, 880.00, '国话上海演出季'),
    (21, 16, 3, '2026-06-26 19:30:00', '2026-06-26 22:00:00', 180.00, 580.00, '人文之光'),
    (22, 19, 1, '2026-06-27 19:30:00', '2026-06-27 21:30:00', 180.00, 880.00, '上海大剧院排期'),
    (23, 16, 3, '2026-06-28 14:00:00', '2026-06-28 16:30:00', 180.00, 580.00, '下午场'),
    (24, 19, 1, '2026-06-28 14:00:00', '2026-06-28 16:00:00', 180.00, 880.00, '下午场'),
    (25, 7, 2, '2026-06-28 19:30:00', '2026-06-28 21:30:00', 80.00, 880.00, '收官场'),
    (26, 8, 2, '2026-07-01 19:30:00', '2026-07-01 21:10:00', 80.00, 480.00, '红色题材'),
    (27, 17, 1, '2026-07-02 19:30:00', '2026-07-02 21:45:00', 180.00, 1080.00, '陈佩斯主演'),
    (28, 9, 2, '2026-07-04 19:30:00', '2026-07-04 21:30:00', 80.00, 880.00, '上海文化广场排期'),
    (29, 16, 3, '2026-07-05 14:00:00', '2026-07-05 16:30:00', 180.00, 580.00, '收官场'),
    (30, 17, 1, '2026-07-05 14:00:00', '2026-07-05 16:15:00', 180.00, 1080.00, '下午场'),
    (31, 9, 2, '2026-07-05 14:00:00', '2026-07-05 16:00:00', 80.00, 880.00, '下午场'),
    (32, 10, 2, '2026-07-08 19:30:00', '2026-07-08 22:00:00', 80.00, 1080.00, '中文版'),
    (33, 10, 2, '2026-07-11 19:30:00', '2026-07-11 22:00:00', 80.00, 1080.00, '周末场'),
    (34, 11, 2, '2026-07-16 19:30:00', '2026-07-16 21:45:00', 280.00, 1380.00, '明星主演'),
    (35, 11, 2, '2026-07-19 19:30:00', '2026-07-19 21:45:00', 280.00, 1380.00, '收官场'),
    (36, 12, 2, '2026-07-30 19:30:00', '2026-07-30 21:50:00', 80.00, 680.00, '中文版'),
    (37, 12, 2, '2026-08-01 19:30:00', '2026-08-01 21:50:00', 80.00, 680.00, '收官场'),
    (38, 13, 2, '2026-08-14 19:30:00', '2026-08-14 22:30:00', 80.00, 880.00, '粤语音乐剧'),
    (39, 13, 2, '2026-08-16 14:00:00', '2026-08-16 17:00:00', 80.00, 880.00, '下午场'),
    (40, 13, 2, '2026-08-30 14:00:00', '2026-08-30 17:00:00', 80.00, 880.00, '收官场'),
    (41, 18, 5, '2026-09-04 19:15:00', '2026-09-04 22:05:00', 180.00, 880.00, '东方名家名剧月'),
    (42, 18, 5, '2026-09-05 14:00:00', '2026-09-05 16:50:00', 180.00, 880.00, '下午场'),
    (43, 21, 1, '2026-09-12 19:30:00', '2026-09-12 22:00:00', 280.00, 1280.00, '四十周年告别季'),
    (44, 21, 1, '2026-09-13 14:00:00', '2026-09-13 16:30:00', 280.00, 1280.00, '下午场'),
    (45, 14, 2, '2026-10-30 19:30:00', '2026-10-30 22:00:00', 80.00, 1280.00, '法语原版'),
    (46, 14, 2, '2026-11-01 14:00:00', '2026-11-01 16:30:00', 80.00, 1280.00, '下午场'),
    (47, 14, 2, '2026-11-15 14:00:00', '2026-11-15 16:30:00', 80.00, 1280.00, '收官场');

-- 8. 场次卡司：按 production_id 与 role_id 严格匹配；A/B场次卡司不同，不再出现《粉丝来信》演员混入《大状王》的情况
INSERT INTO Performance_Cast (performance_id, actor_id, role_id, cast_type, cast_group) VALUES
    (1, 1, 1, 'leading', 'A'),
    (1, 2, 2, 'leading', 'A'),
    (1, 3, 3, 'supporting', 'A'),
    (2, 6, 1, 'leading', 'B'),
    (2, 5, 2, 'leading', 'B'),
    (2, 3, 3, 'supporting', 'B'),
    (3, 7, 4, 'leading', 'A'),
    (3, 8, 5, 'leading', 'A'),
    (3, 9, 6, 'supporting', 'A'),
    (4, 11, 4, 'leading', 'B'),
    (4, 12, 5, 'leading', 'B'),
    (4, 10, 6, 'supporting', 'B'),
    (5, 13, 7, 'leading', 'A'),
    (5, 14, 8, 'leading', 'A'),
    (5, 15, 9, 'supporting', 'A'),
    (6, 16, 7, 'leading', 'B'),
    (6, 17, 8, 'leading', 'B'),
    (6, 18, 9, 'supporting', 'B'),
    (7, 22, 10, 'leading', 'A'),
    (7, 23, 11, 'leading', 'A'),
    (7, 24, 12, 'supporting', 'A'),
    (8, 25, 10, 'leading', 'B'),
    (8, 23, 11, 'leading', 'B'),
    (8, 26, 12, 'supporting', 'B'),
    (9, 124, 64, 'leading', 'A'),
    (9, 125, 65, 'leading', 'A'),
    (9, 126, 66, 'supporting', 'A'),
    (10, 127, 64, 'leading', 'B'),
    (10, 128, 65, 'leading', 'B'),
    (10, 129, 66, 'supporting', 'B'),
    (11, 112, 58, 'leading', 'A'),
    (11, 113, 59, 'leading', 'A'),
    (11, 114, 60, 'supporting', 'A'),
    (12, 115, 58, 'leading', 'B'),
    (12, 116, 59, 'leading', 'B'),
    (12, 117, 60, 'supporting', 'B'),
    (13, 28, 13, 'leading', 'A'),
    (13, 29, 14, 'leading', 'A'),
    (13, 30, 15, 'supporting', 'A'),
    (14, 32, 13, 'leading', 'B'),
    (14, 33, 14, 'leading', 'B'),
    (14, 31, 15, 'supporting', 'B'),
    (15, 86, 43, 'leading', 'A'),
    (15, 87, 44, 'leading', 'A'),
    (15, 88, 45, 'supporting', 'A'),
    (16, 86, 43, 'leading', 'B'),
    (16, 89, 44, 'leading', 'B'),
    (16, 90, 45, 'supporting', 'B'),
    (17, 35, 16, 'leading', 'A'),
    (17, 36, 17, 'leading', 'A'),
    (17, 34, 18, 'supporting', 'A'),
    (18, 38, 16, 'leading', 'B'),
    (18, 39, 17, 'leading', 'B'),
    (18, 37, 18, 'supporting', 'B'),
    (19, 86, 43, 'leading', 'B'),
    (19, 89, 44, 'leading', 'B'),
    (19, 90, 45, 'supporting', 'B'),
    (20, 41, 19, 'leading', 'A'),
    (20, 44, 20, 'leading', 'A'),
    (20, 42, 21, 'supporting', 'A'),
    (21, 93, 46, 'leading', 'A'),
    (21, 95, 47, 'leading', 'A'),
    (21, 92, 48, 'supporting', 'A'),
    (22, 109, 55, 'leading', 'A'),
    (22, 4, 56, 'leading', 'A'),
    (22, 7, 57, 'supporting', 'A'),
    (23, 96, 46, 'leading', 'B'),
    (23, 97, 47, 'leading', 'B'),
    (23, 94, 48, 'supporting', 'B'),
    (24, 41, 55, 'leading', 'B'),
    (24, 4, 56, 'leading', 'B'),
    (24, 7, 57, 'supporting', 'B'),
    (25, 43, 19, 'leading', 'B'),
    (25, 40, 20, 'leading', 'B'),
    (25, 45, 21, 'supporting', 'B'),
    (26, 47, 22, 'leading', 'A'),
    (26, 49, 23, 'leading', 'A'),
    (26, 46, 24, 'supporting', 'A'),
    (27, 98, 49, 'leading', 'A'),
    (27, 99, 50, 'leading', 'A'),
    (27, 101, 51, 'supporting', 'A'),
    (28, 52, 25, 'leading', 'A'),
    (28, 55, 26, 'leading', 'A'),
    (28, 53, 27, 'supporting', 'A'),
    (29, 96, 46, 'leading', 'B'),
    (29, 97, 47, 'leading', 'B'),
    (29, 94, 48, 'supporting', 'B'),
    (30, 98, 49, 'leading', 'B'),
    (30, 100, 50, 'leading', 'B'),
    (30, 103, 51, 'supporting', 'B'),
    (31, 55, 25, 'leading', 'B'),
    (31, 52, 26, 'leading', 'B'),
    (31, 54, 27, 'supporting', 'B'),
    (32, 27, 28, 'leading', 'A'),
    (32, 58, 29, 'leading', 'A'),
    (32, 60, 30, 'supporting', 'A'),
    (33, 25, 28, 'leading', 'B'),
    (33, 59, 29, 'leading', 'B'),
    (33, 61, 30, 'supporting', 'B'),
    (34, 62, 31, 'leading', 'A'),
    (34, 63, 32, 'leading', 'A'),
    (34, 64, 33, 'supporting', 'A'),
    (35, 62, 31, 'leading', 'B'),
    (35, 63, 32, 'leading', 'B'),
    (35, 65, 33, 'supporting', 'B'),
    (36, 69, 34, 'leading', 'A'),
    (36, 68, 35, 'leading', 'A'),
    (36, 70, 36, 'supporting', 'A'),
    (37, 71, 34, 'leading', 'B'),
    (37, 68, 35, 'leading', 'B'),
    (37, 72, 36, 'supporting', 'B'),
    (38, 74, 37, 'leading', 'A'),
    (38, 76, 38, 'leading', 'A'),
    (38, 78, 39, 'supporting', 'A'),
    (39, 75, 37, 'leading', 'B'),
    (39, 77, 38, 'leading', 'B'),
    (39, 78, 39, 'supporting', 'B'),
    (40, 74, 37, 'leading', 'A'),
    (40, 76, 38, 'leading', 'A'),
    (40, 78, 39, 'supporting', 'A'),
    (41, 104, 52, 'leading', 'A'),
    (41, 105, 53, 'leading', 'A'),
    (41, 99, 54, 'supporting', 'A'),
    (42, 107, 52, 'leading', 'B'),
    (42, 106, 53, 'leading', 'B'),
    (42, 104, 54, 'supporting', 'B'),
    (43, 118, 61, 'leading', 'A'),
    (43, 119, 62, 'leading', 'A'),
    (43, 120, 63, 'supporting', 'A'),
    (44, 121, 61, 'leading', 'B'),
    (44, 122, 62, 'leading', 'B'),
    (44, 123, 63, 'supporting', 'B'),
    (45, 80, 40, 'leading', 'A'),
    (45, 82, 41, 'leading', 'A'),
    (45, 84, 42, 'supporting', 'A'),
    (46, 83, 40, 'leading', 'B'),
    (46, 85, 41, 'leading', 'B'),
    (46, 82, 42, 'supporting', 'B'),
    (47, 80, 40, 'leading', 'A'),
    (47, 82, 41, 'leading', 'A'),
    (47, 84, 42, 'supporting', 'A');

-- 9. 用户主动偏好：喜欢演员
INSERT INTO Favorite_Actor (user_id, actor_id) VALUES
    (1, 22),
    (1, 23),
    (1, 27),
    (2, 13),
    (2, 15),
    (2, 104),
    (3, 28),
    (3, 46),
    (3, 51),
    (4, 62),
    (4, 63),
    (4, 64),
    (4, 98),
    (5, 86),
    (5, 87),
    (5, 92),
    (6, 68),
    (6, 74),
    (6, 80);

-- 10. 用户主动偏好：喜欢剧种
INSERT INTO Favorite_Category (user_id, category) VALUES
    (1, '音乐剧'),
    (1, '舞剧'),
    (2, '话剧'),
    (2, '音乐剧'),
    (2, '舞剧'),
    (3, '舞剧'),
    (3, '杂技剧'),
    (3, '音乐会'),
    (4, '话剧'),
    (4, '音乐剧'),
    (4, '舞剧'),
    (5, '话剧'),
    (5, '音乐剧'),
    (6, '音乐剧'),
    (6, '舞剧');

-- 11. 用户主动偏好：喜欢语言
INSERT INTO Favorite_Language (user_id, language) VALUES
    (1, '普通话'),
    (1, '无对白'),
    (2, '普通话'),
    (2, '粤语'),
    (3, '普通话'),
    (3, '无对白'),
    (4, '普通话'),
    (4, '英语'),
    (5, '普通话'),
    (6, '普通话'),
    (6, '法语'),
    (6, '粤语');

-- 12. 用户主动偏好：喜欢区域，加入嘉定区
INSERT INTO Favorite_District (user_id, city, district) VALUES
    (1, '上海', '黄浦区'),
    (1, '上海', '静安区'),
    (2, '上海', '徐汇区'),
    (2, '上海', '浦东新区'),
    (2, '上海', '嘉定区'),
    (3, '上海', '普陀区'),
    (3, '上海', '黄浦区'),
    (3, '上海', '嘉定区'),
    (4, '上海', '黄浦区'),
    (4, '上海', '徐汇区'),
    (4, '上海', '浦东新区'),
    (5, '上海', '黄浦区'),
    (5, '上海', '徐汇区'),
    (6, '上海', '黄浦区'),
    (6, '上海', '嘉定区');

-- 13. 观剧记录：使用已发生或近期场次，支持用户画像函数
INSERT INTO Watch_Record (user_id, performance_id, watch_date, score) VALUES
    (1, 7, DATE((SELECT start_time FROM Performance WHERE performance_id = 7)), 9.2),
    (1, 5, DATE((SELECT start_time FROM Performance WHERE performance_id = 5)), 8.8),
    (1, 1, DATE((SELECT start_time FROM Performance WHERE performance_id = 1)), 8.6),
    (2, 5, DATE((SELECT start_time FROM Performance WHERE performance_id = 5)), 8.7),
    (2, 6, DATE((SELECT start_time FROM Performance WHERE performance_id = 6)), 8.4),
    (2, 2, DATE((SELECT start_time FROM Performance WHERE performance_id = 2)), 8.0),
    (2, 3, DATE((SELECT start_time FROM Performance WHERE performance_id = 3)), 8.5),
    (3, 1, DATE((SELECT start_time FROM Performance WHERE performance_id = 1)), 8.2),
    (3, 3, DATE((SELECT start_time FROM Performance WHERE performance_id = 3)), 8.5),
    (3, 4, DATE((SELECT start_time FROM Performance WHERE performance_id = 4)), 7.9),
    (4, 5, DATE((SELECT start_time FROM Performance WHERE performance_id = 5)), 8.6),
    (4, 7, DATE((SELECT start_time FROM Performance WHERE performance_id = 7)), 9.0),
    (4, 2, DATE((SELECT start_time FROM Performance WHERE performance_id = 2)), 8.3),
    (5, 6, DATE((SELECT start_time FROM Performance WHERE performance_id = 6)), 8.4),
    (5, 5, DATE((SELECT start_time FROM Performance WHERE performance_id = 5)), 8.2),
    (5, 3, DATE((SELECT start_time FROM Performance WHERE performance_id = 3)), 7.9),
    (6, 7, DATE((SELECT start_time FROM Performance WHERE performance_id = 7)), 8.9),
    (6, 9, DATE((SELECT start_time FROM Performance WHERE performance_id = 9)), 8.4),
    (6, 10, DATE((SELECT start_time FROM Performance WHERE performance_id = 10)), 8.2);

-- 14. 计划观看：条件插入，若运行日期晚于某场次结束时间则自动跳过，避免触发器报错
INSERT INTO Planned_Performance (user_id, performance_id, status)
SELECT 1, 13, 'planned' FROM DUAL
WHERE (SELECT end_time FROM Performance WHERE performance_id = 13) > NOW();
INSERT INTO Planned_Performance (user_id, performance_id, status)
SELECT 1, 32, 'booked' FROM DUAL
WHERE (SELECT end_time FROM Performance WHERE performance_id = 32) > NOW();
INSERT INTO Planned_Performance (user_id, performance_id, status)
SELECT 1, 38, 'planned' FROM DUAL
WHERE (SELECT end_time FROM Performance WHERE performance_id = 38) > NOW();
INSERT INTO Planned_Performance (user_id, performance_id, status)
SELECT 2, 14, 'planned' FROM DUAL
WHERE (SELECT end_time FROM Performance WHERE performance_id = 14) > NOW();
INSERT INTO Planned_Performance (user_id, performance_id, status)
SELECT 2, 20, 'booked' FROM DUAL
WHERE (SELECT end_time FROM Performance WHERE performance_id = 20) > NOW();
INSERT INTO Planned_Performance (user_id, performance_id, status)
SELECT 2, 41, 'planned' FROM DUAL
WHERE (SELECT end_time FROM Performance WHERE performance_id = 41) > NOW();
INSERT INTO Planned_Performance (user_id, performance_id, status)
SELECT 3, 17, 'planned' FROM DUAL
WHERE (SELECT end_time FROM Performance WHERE performance_id = 17) > NOW();
INSERT INTO Planned_Performance (user_id, performance_id, status)
SELECT 3, 26, 'booked' FROM DUAL
WHERE (SELECT end_time FROM Performance WHERE performance_id = 26) > NOW();
INSERT INTO Planned_Performance (user_id, performance_id, status)
SELECT 3, 31, 'planned' FROM DUAL
WHERE (SELECT end_time FROM Performance WHERE performance_id = 31) > NOW();
INSERT INTO Planned_Performance (user_id, performance_id, status)
SELECT 4, 27, 'planned' FROM DUAL
WHERE (SELECT end_time FROM Performance WHERE performance_id = 27) > NOW();
INSERT INTO Planned_Performance (user_id, performance_id, status)
SELECT 4, 34, 'booked' FROM DUAL
WHERE (SELECT end_time FROM Performance WHERE performance_id = 34) > NOW();
INSERT INTO Planned_Performance (user_id, performance_id, status)
SELECT 4, 43, 'planned' FROM DUAL
WHERE (SELECT end_time FROM Performance WHERE performance_id = 43) > NOW();
INSERT INTO Planned_Performance (user_id, performance_id, status)
SELECT 4, 45, 'booked' FROM DUAL
WHERE (SELECT end_time FROM Performance WHERE performance_id = 45) > NOW();
INSERT INTO Planned_Performance (user_id, performance_id, status)
SELECT 5, 15, 'planned' FROM DUAL
WHERE (SELECT end_time FROM Performance WHERE performance_id = 15) > NOW();
INSERT INTO Planned_Performance (user_id, performance_id, status)
SELECT 5, 21, 'planned' FROM DUAL
WHERE (SELECT end_time FROM Performance WHERE performance_id = 21) > NOW();
INSERT INTO Planned_Performance (user_id, performance_id, status)
SELECT 5, 36, 'booked' FROM DUAL
WHERE (SELECT end_time FROM Performance WHERE performance_id = 36) > NOW();
INSERT INTO Planned_Performance (user_id, performance_id, status)
SELECT 6, 33, 'booked' FROM DUAL
WHERE (SELECT end_time FROM Performance WHERE performance_id = 33) > NOW();
INSERT INTO Planned_Performance (user_id, performance_id, status)
SELECT 6, 39, 'planned' FROM DUAL
WHERE (SELECT end_time FROM Performance WHERE performance_id = 39) > NOW();
INSERT INTO Planned_Performance (user_id, performance_id, status)
SELECT 6, 46, 'planned' FROM DUAL
WHERE (SELECT end_time FROM Performance WHERE performance_id = 46) > NOW();

-- 15. 周边餐厅：课程演示数据，每个剧院三档
INSERT INTO Nearby_Restaurant (restaurant_id, theater_id, restaurant_name, category, avg_price, distance_m, price_tier) VALUES
    (1, 1, '大剧院剧前轻食', '简餐', 58.00, 180, 'low'),
    (2, 1, '大剧院本帮小馆', '本帮菜', 138.00, 320, 'mid'),
    (3, 1, '大剧院剧院西餐厅', '西餐', 288.00, 520, 'high'),
    (4, 2, '文化广场剧前轻食', '简餐', 58.00, 180, 'low'),
    (5, 2, '文化广场本帮小馆', '本帮菜', 138.00, 320, 'mid'),
    (6, 2, '文化广场剧院西餐厅', '西餐', 288.00, 520, 'high'),
    (7, 3, '话剧艺术中心剧前轻食', '简餐', 58.00, 180, 'low'),
    (8, 3, '话剧艺术中心本帮小馆', '本帮菜', 138.00, 320, 'mid'),
    (9, 3, '话剧艺术中心剧院西餐厅', '西餐', 288.00, 520, 'high'),
    (10, 4, '话剧艺术中心剧前轻食', '简餐', 58.00, 180, 'low'),
    (11, 4, '话剧艺术中心本帮小馆', '本帮菜', 138.00, 320, 'mid'),
    (12, 4, '话剧艺术中心剧院西餐厅', '西餐', 288.00, 520, 'high'),
    (13, 5, '东方艺术中心剧前轻食', '简餐', 58.00, 180, 'low'),
    (14, 5, '东方艺术中心本帮小馆', '本帮菜', 138.00, 320, 'mid'),
    (15, 5, '东方艺术中心剧院西餐厅', '西餐', 288.00, 520, 'high'),
    (16, 6, '保利大剧院剧前轻食', '简餐', 58.00, 180, 'low'),
    (17, 6, '保利大剧院本帮小馆', '本帮菜', 138.00, 320, 'mid'),
    (18, 6, '保利大剧院剧院西餐厅', '西餐', 288.00, 520, 'high'),
    (19, 7, '国际舞蹈中心大剧场剧前轻食', '简餐', 58.00, 180, 'low'),
    (20, 7, '国际舞蹈中心大剧场本帮小馆', '本帮菜', 138.00, 320, 'mid'),
    (21, 7, '国际舞蹈中心大剧场剧院西餐厅', '西餐', 288.00, 520, 'high'),
    (22, 8, '美琪大戏院剧前轻食', '简餐', 58.00, 180, 'low'),
    (23, 8, '美琪大戏院本帮小馆', '本帮菜', 138.00, 320, 'mid'),
    (24, 8, '美琪大戏院剧院西餐厅', '西餐', 288.00, 520, 'high'),
    (25, 9, '上音歌剧院剧前轻食', '简餐', 58.00, 180, 'low'),
    (26, 9, '上音歌剧院本帮小馆', '本帮菜', 138.00, 320, 'mid'),
    (27, 9, '上音歌剧院剧院西餐厅', '西餐', 288.00, 520, 'high'),
    (28, 10, '中国大戏院剧前轻食', '简餐', 58.00, 180, 'low'),
    (29, 10, '中国大戏院本帮小馆', '本帮菜', 138.00, 320, 'mid'),
    (30, 10, '中国大戏院剧院西餐厅', '西餐', 288.00, 520, 'high');

-- 16. 交通方案：覆盖原 6 个用户居住区，并新增嘉定区方案
INSERT INTO Transport_Option (transport_id, theater_id, transport_type, estimated_time, estimated_cost, suitable_district) VALUES
    (1, 1, 'walk', 12, 0.00, '黄浦区'),
    (2, 1, 'subway', 30, 5.00, '徐汇区'),
    (3, 1, 'subway', 25, 5.00, '静安区'),
    (4, 1, 'subway', 42, 7.00, '长宁区'),
    (5, 1, 'subway', 42, 7.00, '浦东新区'),
    (6, 1, 'subway', 50, 7.00, '普陀区'),
    (7, 1, 'taxi', 75, 95.00, '嘉定区'),
    (8, 2, 'walk', 12, 0.00, '黄浦区'),
    (9, 2, 'subway', 30, 5.00, '徐汇区'),
    (10, 2, 'subway', 25, 5.00, '静安区'),
    (11, 2, 'subway', 42, 7.00, '长宁区'),
    (12, 2, 'subway', 42, 7.00, '浦东新区'),
    (13, 2, 'subway', 50, 7.00, '普陀区'),
    (14, 2, 'taxi', 75, 95.00, '嘉定区'),
    (15, 3, 'subway', 28, 5.00, '黄浦区'),
    (16, 3, 'walk', 12, 0.00, '徐汇区'),
    (17, 3, 'subway', 32, 5.00, '静安区'),
    (18, 3, 'subway', 30, 5.00, '长宁区'),
    (19, 3, 'subway', 48, 7.00, '浦东新区'),
    (20, 3, 'subway', 55, 9.00, '普陀区'),
    (21, 3, 'taxi', 78, 95.00, '嘉定区'),
    (22, 4, 'subway', 28, 5.00, '黄浦区'),
    (23, 4, 'walk', 12, 0.00, '徐汇区'),
    (24, 4, 'subway', 32, 5.00, '静安区'),
    (25, 4, 'subway', 30, 5.00, '长宁区'),
    (26, 4, 'subway', 48, 7.00, '浦东新区'),
    (27, 4, 'subway', 55, 9.00, '普陀区'),
    (28, 4, 'taxi', 78, 95.00, '嘉定区'),
    (29, 5, 'subway', 45, 7.00, '黄浦区'),
    (30, 5, 'subway', 48, 7.00, '徐汇区'),
    (31, 5, 'subway', 45, 7.00, '静安区'),
    (32, 5, 'subway', 48, 7.00, '长宁区'),
    (33, 5, 'walk', 12, 0.00, '浦东新区'),
    (34, 5, 'subway', 55, 9.00, '普陀区'),
    (35, 5, 'taxi', 82, 95.00, '嘉定区'),
    (36, 6, 'taxi', 75, 95.00, '黄浦区'),
    (37, 6, 'taxi', 78, 95.00, '徐汇区'),
    (38, 6, 'taxi', 70, 95.00, '静安区'),
    (39, 6, 'subway', 55, 9.00, '长宁区'),
    (40, 6, 'taxi', 82, 95.00, '浦东新区'),
    (41, 6, 'subway', 58, 9.00, '普陀区'),
    (42, 6, 'walk', 12, 0.00, '嘉定区'),
    (43, 7, 'subway', 42, 7.00, '黄浦区'),
    (44, 7, 'subway', 30, 5.00, '徐汇区'),
    (45, 7, 'subway', 30, 5.00, '静安区'),
    (46, 7, 'walk', 12, 0.00, '长宁区'),
    (47, 7, 'subway', 50, 7.00, '浦东新区'),
    (48, 7, 'subway', 38, 7.00, '普陀区'),
    (49, 7, 'subway', 55, 9.00, '嘉定区'),
    (50, 8, 'subway', 24, 5.00, '黄浦区'),
    (51, 8, 'subway', 32, 5.00, '徐汇区'),
    (52, 8, 'walk', 12, 0.00, '静安区'),
    (53, 8, 'subway', 30, 5.00, '长宁区'),
    (54, 8, 'subway', 45, 7.00, '浦东新区'),
    (55, 8, 'subway', 35, 5.00, '普陀区'),
    (56, 8, 'taxi', 70, 95.00, '嘉定区'),
    (57, 9, 'subway', 28, 5.00, '黄浦区'),
    (58, 9, 'walk', 12, 0.00, '徐汇区'),
    (59, 9, 'subway', 32, 5.00, '静安区'),
    (60, 9, 'subway', 30, 5.00, '长宁区'),
    (61, 9, 'subway', 48, 7.00, '浦东新区'),
    (62, 9, 'subway', 55, 9.00, '普陀区'),
    (63, 9, 'taxi', 78, 95.00, '嘉定区'),
    (64, 10, 'walk', 12, 0.00, '黄浦区'),
    (65, 10, 'subway', 30, 5.00, '徐汇区'),
    (66, 10, 'subway', 25, 5.00, '静安区'),
    (67, 10, 'subway', 42, 7.00, '长宁区'),
    (68, 10, 'subway', 42, 7.00, '浦东新区'),
    (69, 10, 'subway', 50, 7.00, '普陀区'),
    (70, 10, 'taxi', 75, 95.00, '嘉定区');

-- 17. 管理员日志
INSERT INTO Admin_Log (admin_user_id, action_type, target_table, target_id, description) VALUES
    (7, 'ALTER', 'User', NULL, '扩展区域枚举，加入嘉定区'),
    (7, 'ALTER', 'Transport_Option', NULL, '扩展交通适用区域，加入嘉定区'),
    (7, 'INSERT', 'Theater', 6, '新增嘉定区上海保利大剧院'),
    (7, 'INSERT', 'Production', 13, '新增音乐剧《大状王》并维护独立卡司'),
    (7, 'INSERT', 'Production', 12, '新增音乐剧《粉丝来信》并维护独立卡司'),
    (7, 'INSERT', 'Performance_Cast', NULL, '按场次维护A/B卡司，避免不同剧目卡司混用');

COMMIT;
SET FOREIGN_KEY_CHECKS = @OLD_FOREIGN_KEY_CHECKS;

-- 18. 生成画像推荐缓存：v_hybrid_recommendation 的 profile_based 路径依赖该缓存
CALL sp_recommend_by_profile(1);
CALL sp_recommend_by_profile(2);
CALL sp_recommend_by_profile(3);
CALL sp_recommend_by_profile(4);
CALL sp_recommend_by_profile(5);
CALL sp_recommend_by_profile(6);

-- 检查建议：
-- SELECT p.performance_id, pr.title, th.theater_name, th.district, p.start_time, p.special_tag FROM Performance p JOIN Production pr ON p.production_id=pr.production_id JOIN Theater th ON p.theater_id=th.theater_id ORDER BY p.start_time;
-- SELECT p.performance_id, pr.title, r.role_name, a.actor_name, pc.cast_group FROM Performance_Cast pc JOIN Performance p ON pc.performance_id=p.performance_id JOIN Production pr ON p.production_id=pr.production_id JOIN `Role` r ON pc.role_id=r.role_id JOIN Actor a ON pc.actor_id=a.actor_id ORDER BY p.performance_id, r.role_id;
-- SELECT * FROM v_planned_trip_assistance ORDER BY user_id, start_time;
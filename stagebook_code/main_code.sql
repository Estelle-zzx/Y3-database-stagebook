DROP DATABASE IF EXISTS StageBook;
CREATE DATABASE StageBook
DEFAULT CHARACTER SET utf8mb4
DEFAULT COLLATE utf8mb4_0900_ai_ci;

USE StageBook;

SET NAMES utf8mb4;

-- =========================
-- 1. 基础表
-- =========================

CREATE TABLE User (
    user_id            INT PRIMARY KEY AUTO_INCREMENT,
    username           VARCHAR(50) NOT NULL UNIQUE,
    nickname           VARCHAR(50) NOT NULL,
    city               VARCHAR(50) NOT NULL,
    register_time      DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    price_preference   ENUM('economy', 'mid', 'premium') DEFAULT 'mid',
    time_preference    ENUM('weekday_evening', 'weekend_evening', 'weekend_matinee') DEFAULT 'weekend_evening',
    home_district      ENUM('黄浦区', '徐汇区', '静安区', '长宁区', '浦东新区', '普陀区')
) ENGINE=InnoDB;

ALTER TABLE User
ADD COLUMN role ENUM('user', 'admin') NOT NULL DEFAULT 'user';

CREATE TABLE Production (
    production_id      INT PRIMARY KEY AUTO_INCREMENT,
    title              VARCHAR(100) NOT NULL,
    category           VARCHAR(50) NOT NULL,
    duration_min       INT NOT NULL,
    language           VARCHAR(50) NOT NULL,
    version            ENUM('original', 'revival', 'tour', 'limited') NOT NULL DEFAULT 'original',
    CONSTRAINT chk_production_duration CHECK (duration_min > 0)
) ENGINE=InnoDB;

CREATE TABLE Theater (
    theater_id         INT PRIMARY KEY AUTO_INCREMENT,
    theater_name       VARCHAR(100) NOT NULL,
    city               VARCHAR(50) NOT NULL,
    district           VARCHAR(50) NOT NULL,
    address            VARCHAR(255) NOT NULL
) ENGINE=InnoDB;

CREATE TABLE Performance (
    performance_id     INT PRIMARY KEY AUTO_INCREMENT,
    production_id      INT NOT NULL,
    theater_id         INT NOT NULL,
    start_time         DATETIME NOT NULL,
    end_time           DATETIME NOT NULL,
    price_min          DECIMAL(10,2) NOT NULL,
    price_max          DECIMAL(10,2) NOT NULL,
    special_tag        VARCHAR(50),
    CONSTRAINT fk_performance_production
        FOREIGN KEY (production_id) REFERENCES Production(production_id)
        ON DELETE CASCADE ON UPDATE CASCADE,
    CONSTRAINT fk_performance_theater
        FOREIGN KEY (theater_id) REFERENCES Theater(theater_id)
        ON DELETE RESTRICT ON UPDATE CASCADE,
    CONSTRAINT chk_performance_time CHECK (end_time > start_time),
    CONSTRAINT chk_performance_price CHECK (price_min >= 0 AND price_max >= price_min)
) ENGINE=InnoDB;

CREATE TABLE Actor (
    actor_id           INT PRIMARY KEY AUTO_INCREMENT,
    actor_name         VARCHAR(50) NOT NULL,
    gender             ENUM('male', 'female', 'other') DEFAULT 'other'
) ENGINE=InnoDB;

CREATE TABLE Role (
    role_id            INT PRIMARY KEY AUTO_INCREMENT,
    production_id      INT NOT NULL,
    role_name          VARCHAR(100) NOT NULL,
    CONSTRAINT fk_role_production
        FOREIGN KEY (production_id) REFERENCES Production(production_id)
        ON DELETE CASCADE ON UPDATE CASCADE,
    CONSTRAINT uk_role_production_name UNIQUE (production_id, role_name)
) ENGINE=InnoDB;

CREATE TABLE Performance_Cast (
    performance_id     INT NOT NULL,
    actor_id           INT NOT NULL,
    role_id            INT NOT NULL,
    cast_type          ENUM('leading', 'supporting', 'ensemble', 'guest') DEFAULT 'leading',
    cast_group         VARCHAR(20) DEFAULT 'A',
    PRIMARY KEY (performance_id, actor_id, role_id),
    CONSTRAINT fk_pc_performance
        FOREIGN KEY (performance_id) REFERENCES Performance(performance_id)
        ON DELETE CASCADE ON UPDATE CASCADE,
    CONSTRAINT fk_pc_actor
        FOREIGN KEY (actor_id) REFERENCES Actor(actor_id)
        ON DELETE CASCADE ON UPDATE CASCADE,
    CONSTRAINT fk_pc_role
        FOREIGN KEY (role_id) REFERENCES Role(role_id)
        ON DELETE CASCADE ON UPDATE CASCADE
) ENGINE=InnoDB;

CREATE TABLE Watch_Record (
    record_id          INT PRIMARY KEY AUTO_INCREMENT,
    user_id            INT NOT NULL,
    performance_id     INT NOT NULL,
    watch_date         DATE NOT NULL,
    score              DECIMAL(3,1),
    CONSTRAINT fk_watch_user
        FOREIGN KEY (user_id) REFERENCES User(user_id)
        ON DELETE CASCADE ON UPDATE CASCADE,
    CONSTRAINT fk_watch_performance
        FOREIGN KEY (performance_id) REFERENCES Performance(performance_id)
        ON DELETE CASCADE ON UPDATE CASCADE,
    CONSTRAINT chk_watch_score CHECK (score IS NULL OR (score >= 0 AND score <= 10))
) ENGINE=InnoDB;

CREATE TABLE Planned_Performance (
    user_id            INT NOT NULL,
    performance_id     INT NOT NULL,
    add_time           DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    status             ENUM('planned', 'booked', 'canceled') NOT NULL DEFAULT 'planned',
    PRIMARY KEY (user_id, performance_id),
    CONSTRAINT fk_plan_user
        FOREIGN KEY (user_id) REFERENCES User(user_id)
        ON DELETE CASCADE ON UPDATE CASCADE,
    CONSTRAINT fk_plan_performance
        FOREIGN KEY (performance_id) REFERENCES Performance(performance_id)
        ON DELETE CASCADE ON UPDATE CASCADE
) ENGINE=InnoDB;

CREATE TABLE Favorite_Actor (
    user_id            INT NOT NULL,
    actor_id           INT NOT NULL,
    mark_time          DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    PRIMARY KEY (user_id, actor_id),
    CONSTRAINT fk_fa_user
        FOREIGN KEY (user_id) REFERENCES User(user_id)
        ON DELETE CASCADE ON UPDATE CASCADE,
    CONSTRAINT fk_fa_actor
        FOREIGN KEY (actor_id) REFERENCES Actor(actor_id)
        ON DELETE CASCADE ON UPDATE CASCADE
) ENGINE=InnoDB;

CREATE TABLE Favorite_Category (
    user_id            INT NOT NULL,
    category           VARCHAR(50) NOT NULL,
    mark_time          DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    PRIMARY KEY (user_id, category),
    CONSTRAINT fk_fc_user
        FOREIGN KEY (user_id) REFERENCES User(user_id)
        ON DELETE CASCADE ON UPDATE CASCADE
) ENGINE=InnoDB;

CREATE TABLE Favorite_Language (
    user_id            INT NOT NULL,
    language           VARCHAR(50) NOT NULL,
    mark_time          DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    PRIMARY KEY (user_id, language),
    CONSTRAINT fk_fl_user
        FOREIGN KEY (user_id) REFERENCES User(user_id)
        ON DELETE CASCADE ON UPDATE CASCADE
) ENGINE=InnoDB;

CREATE TABLE Favorite_District (
    user_id            INT NOT NULL,
    city               VARCHAR(50) NOT NULL,
    district           VARCHAR(50) NOT NULL,
    mark_time          DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    PRIMARY KEY (user_id, city, district),
    CONSTRAINT fk_fd_user
        FOREIGN KEY (user_id) REFERENCES User(user_id)
        ON DELETE CASCADE ON UPDATE CASCADE
) ENGINE=InnoDB;

CREATE TABLE Nearby_Restaurant (
    restaurant_id      INT PRIMARY KEY AUTO_INCREMENT,
    theater_id         INT NOT NULL,
    restaurant_name    VARCHAR(100) NOT NULL,
    category           VARCHAR(50) NOT NULL,
    avg_price          DECIMAL(10,2) NOT NULL,
    distance_m         INT NOT NULL,
    price_tier         ENUM('low', 'mid', 'high') NOT NULL DEFAULT 'mid',
    CONSTRAINT fk_restaurant_theater
        FOREIGN KEY (theater_id) REFERENCES Theater(theater_id)
        ON DELETE CASCADE ON UPDATE CASCADE,
    CONSTRAINT chk_restaurant_price CHECK (avg_price >= 0),
    CONSTRAINT chk_restaurant_distance CHECK (distance_m >= 0)
) ENGINE=InnoDB;

CREATE TABLE Transport_Option (
    transport_id       INT PRIMARY KEY AUTO_INCREMENT,
    theater_id         INT NOT NULL,
    transport_type     ENUM('subway', 'bus', 'taxi', 'walk') NOT NULL,
    estimated_time     INT NOT NULL,
    estimated_cost     DECIMAL(10,2) NOT NULL,
    suitable_district  ENUM('黄浦区', '徐汇区', '静安区', '长宁区', '浦东新区', '普陀区') NOT NULL,
    CONSTRAINT fk_transport_theater
        FOREIGN KEY (theater_id) REFERENCES Theater(theater_id)
        ON DELETE CASCADE ON UPDATE CASCADE,
    CONSTRAINT chk_transport_time CHECK (estimated_time >= 0),
    CONSTRAINT chk_transport_cost CHECK (estimated_cost >= 0)
) ENGINE=InnoDB;

CREATE TABLE IF NOT EXISTS Profile_Recommendation_Result (
    user_id INT NOT NULL,
    performance_id INT NOT NULL,
    production_title VARCHAR(200) NOT NULL,
    version_name VARCHAR(50),
    category VARCHAR(50),
    language VARCHAR(50),
    start_time DATETIME,
    theater_name VARCHAR(100),
    district VARCHAR(50),
    price_min DECIMAL(10,2),
    price_max DECIMAL(10,2),
    special_tag VARCHAR(50),
    recommendation_source VARCHAR(30) NOT NULL,
    matched_profile_type VARCHAR(50),
    match_score INT NOT NULL,
    recommendation_reason VARCHAR(255),
    generated_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    PRIMARY KEY (user_id, performance_id),
    CONSTRAINT fk_profile_result_performance
        FOREIGN KEY (performance_id) REFERENCES Performance(performance_id),
    CONSTRAINT fk_profile_result_user
        FOREIGN KEY (user_id) REFERENCES User(user_id)
);

CREATE TABLE IF NOT EXISTS Admin_Log (
    log_id INT PRIMARY KEY AUTO_INCREMENT,
    admin_user_id INT NOT NULL,
    action_type VARCHAR(50) NOT NULL,
    target_table VARCHAR(50) NOT NULL,
    target_id INT,
    action_time DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    description VARCHAR(255),
    CONSTRAINT fk_admin_log_user
        FOREIGN KEY (admin_user_id) REFERENCES User(user_id)
);

-- =========================
-- 2. 索引
-- =========================

CREATE INDEX idx_performance_start_time ON Performance(start_time);
CREATE INDEX idx_performance_special_tag ON Performance(special_tag);
CREATE INDEX idx_performance_production ON Performance(production_id);
CREATE INDEX idx_performance_theater ON Performance(theater_id);

CREATE INDEX idx_watch_user ON Watch_Record(user_id);
CREATE INDEX idx_watch_performance ON Watch_Record(performance_id);

CREATE INDEX idx_plan_user_status ON Planned_Performance(user_id, status);

CREATE INDEX idx_pc_actor ON Performance_Cast(actor_id);
CREATE INDEX idx_pc_role ON Performance_Cast(role_id);

CREATE INDEX idx_prod_category ON Production(category);
CREATE INDEX idx_prod_language ON Production(language);

CREATE INDEX idx_theater_city_district ON Theater(city, district);

CREATE INDEX idx_restaurant_theater_price ON Nearby_Restaurant(theater_id, price_tier);
CREATE INDEX idx_transport_theater_district ON Transport_Option(theater_id, suitable_district);

-- =========================
-- 3. 触发器
-- =========================

DELIMITER $$

CREATE TRIGGER trg_after_insert_watch_record
AFTER INSERT ON Watch_Record
FOR EACH ROW
BEGIN
    DELETE FROM Planned_Performance
    WHERE user_id = NEW.user_id
      AND performance_id = NEW.performance_id;
END$$

CREATE TRIGGER trg_before_insert_performance_cast
BEFORE INSERT ON Performance_Cast
FOR EACH ROW
BEGIN
    DECLARE v_perf_production_id INT;
    DECLARE v_role_production_id INT;

    SELECT production_id
      INTO v_perf_production_id
      FROM Performance
     WHERE performance_id = NEW.performance_id;

    SELECT production_id
      INTO v_role_production_id
      FROM Role
     WHERE role_id = NEW.role_id;

    IF v_perf_production_id IS NULL OR v_role_production_id IS NULL THEN
        SIGNAL SQLSTATE '45000'
        SET MESSAGE_TEXT = 'Performance 或 Role 不存在';
    END IF;

    IF v_perf_production_id <> v_role_production_id THEN
        SIGNAL SQLSTATE '45000'
        SET MESSAGE_TEXT = '角色所属剧目与场次所属剧目不一致';
    END IF;
END$$

CREATE TRIGGER trg_before_insert_planned_performance
BEFORE INSERT ON Planned_Performance
FOR EACH ROW
BEGIN
    DECLARE v_end_time DATETIME;

    SELECT end_time
      INTO v_end_time
      FROM Performance
     WHERE performance_id = NEW.performance_id;

    IF v_end_time IS NULL THEN
        SIGNAL SQLSTATE '45000'
        SET MESSAGE_TEXT = '场次不存在';
    END IF;

    IF v_end_time < NOW() THEN
        SIGNAL SQLSTATE '45000'
        SET MESSAGE_TEXT = '已结束场次不能加入计划观看';
    END IF;
END$$

DELIMITER ;

-- =========================
-- 4. 函数
-- =========================

DROP FUNCTION IF EXISTS fn_audience_type;
DELIMITER $$

CREATE FUNCTION fn_audience_type(p_user_id INT)
RETURNS VARCHAR(50)
DETERMINISTIC
BEGIN
    DECLARE v_fav_actor_count INT DEFAULT 0;
    DECLARE v_overlap_actor_count INT DEFAULT 0;
    DECLARE v_category_count INT DEFAULT 0;
    DECLARE v_max_category_watch INT DEFAULT 0;
    DECLARE v_total_watch INT DEFAULT 0;
    DECLARE v_planned_count INT DEFAULT 0;
    DECLARE v_has_district_pref INT DEFAULT 0;
    DECLARE v_price_pref VARCHAR(20);
    DECLARE v_avg_price DECIMAL(10,2) DEFAULT NULL;

    -- 1. 主动喜欢演员数
    SELECT COUNT(*)
    INTO v_fav_actor_count
    FROM Favorite_Actor
    WHERE user_id = p_user_id;

    -- 2. 喜欢演员与实际观看演员的重合数
    SELECT COUNT(DISTINCT fa.actor_id)
    INTO v_overlap_actor_count
    FROM Favorite_Actor fa
    JOIN Performance_Cast pc ON fa.actor_id = pc.actor_id
    JOIN Watch_Record wr ON wr.performance_id = pc.performance_id
    WHERE fa.user_id = p_user_id
      AND wr.user_id = p_user_id;

    -- 3. 看过的剧种种类数
    SELECT COUNT(DISTINCT pr.category)
    INTO v_category_count
    FROM Watch_Record wr
    JOIN Performance pf ON wr.performance_id = pf.performance_id
    JOIN Production pr ON pf.production_id = pr.production_id
    WHERE wr.user_id = p_user_id;

    -- 4. 总观看场次
    SELECT COUNT(*)
    INTO v_total_watch
    FROM Watch_Record
    WHERE user_id = p_user_id;

    -- 5. 单一剧种的最大观看次数（用于判断是否“分布较均匀”）
    SELECT COALESCE(MAX(cat_cnt), 0)
    INTO v_max_category_watch
    FROM (
        SELECT COUNT(*) AS cat_cnt
        FROM Watch_Record wr
        JOIN Performance pf ON wr.performance_id = pf.performance_id
        JOIN Production pr ON pf.production_id = pr.production_id
        WHERE wr.user_id = p_user_id
        GROUP BY pr.category
    ) t;

    -- 6. 用户价格偏好
    SELECT price_preference
    INTO v_price_pref
    FROM User
    WHERE user_id = p_user_id;

    -- 7. 历史平均票价（用 price_min 和 price_max 的均值近似）
    SELECT AVG((pf.price_min + pf.price_max) / 2)
    INTO v_avg_price
    FROM Watch_Record wr
    JOIN Performance pf ON wr.performance_id = pf.performance_id
    WHERE wr.user_id = p_user_id;

    -- 8. planned/booked 数量
    SELECT COUNT(*)
    INTO v_planned_count
    FROM Planned_Performance
    WHERE user_id = p_user_id
      AND status IN ('planned', 'booked');

    -- 9. 是否有区域偏好
    SELECT COUNT(*)
    INTO v_has_district_pref
    FROM Favorite_District
    WHERE user_id = p_user_id;

    -- 判断顺序按文档主线来
    IF v_fav_actor_count >= 3 AND v_overlap_actor_count >= 2 THEN
        RETURN '演员驱动型';

    ELSEIF v_category_count >= 3
       AND v_total_watch >= 4
       AND v_max_category_watch <= CEIL(v_total_watch * 0.6) THEN
        RETURN '剧种探索型';

    ELSEIF v_price_pref = 'economy'
       OR (v_avg_price IS NOT NULL AND v_avg_price <= 220) THEN
        RETURN '高性价比型';

    ELSEIF v_planned_count >= 3 AND v_has_district_pref > 0 THEN
        RETURN '行程敏感型';

    ELSE
        RETURN '综合型观众';
    END IF;
END$$
DELIMITER ;

DROP FUNCTION IF EXISTS fn_most_similar_user;
DELIMITER $$

CREATE FUNCTION fn_most_similar_user(p_user_id INT)
RETURNS INT
DETERMINISTIC
BEGIN
    DECLARE v_similar_user_id INT DEFAULT NULL;

    SELECT candidate.user_id
    INTO v_similar_user_id
    FROM (
        SELECT
            u2.user_id,

            -- 1. 共同看过剧目的评分接近度（差值越小越好）
            COALESCE((
                SELECT SUM(GREATEST(0, 10 - ABS(wr1.score - wr2.score)))
                FROM Watch_Record wr1
                JOIN Watch_Record wr2
                  ON wr1.performance_id = wr2.performance_id
                WHERE wr1.user_id = p_user_id
                  AND wr2.user_id = u2.user_id
            ), 0) AS score_similarity,

            -- 2. 喜欢演员重合数
            COALESCE((
                SELECT COUNT(*)
                FROM Favorite_Actor fa1
                JOIN Favorite_Actor fa2
                  ON fa1.actor_id = fa2.actor_id
                WHERE fa1.user_id = p_user_id
                  AND fa2.user_id = u2.user_id
            ), 0) AS actor_overlap,

            -- 3. 喜欢剧种重合数
            COALESCE((
                SELECT COUNT(*)
                FROM Favorite_Category fc1
                JOIN Favorite_Category fc2
                  ON fc1.category = fc2.category
                WHERE fc1.user_id = p_user_id
                  AND fc2.user_id = u2.user_id
            ), 0) AS category_overlap,

            -- 4. 喜欢语言重合数
            COALESCE((
                SELECT COUNT(*)
                FROM Favorite_Language fl1
                JOIN Favorite_Language fl2
                  ON fl1.language = fl2.language
                WHERE fl1.user_id = p_user_id
                  AND fl2.user_id = u2.user_id
            ), 0) AS language_overlap,

            -- 5. 喜欢区域重合数
            COALESCE((
                SELECT COUNT(*)
                FROM Favorite_District fd1
                JOIN Favorite_District fd2
                  ON fd1.city = fd2.city
                 AND fd1.district = fd2.district
                WHERE fd1.user_id = p_user_id
                  AND fd2.user_id = u2.user_id
            ), 0) AS district_overlap

        FROM User u2
        WHERE u2.user_id <> p_user_id
    ) candidate
    ORDER BY
        (
            candidate.score_similarity * 0.40 +
            candidate.actor_overlap * 0.25 +
            candidate.category_overlap * 0.15 +
            candidate.language_overlap * 0.10 +
            candidate.district_overlap * 0.10
        ) DESC,
        candidate.score_similarity DESC,
        candidate.actor_overlap DESC,
        candidate.category_overlap DESC,
        candidate.user_id ASC
    LIMIT 1;

    RETURN v_similar_user_id;
END$$


CREATE FUNCTION fn_suggested_departure_time(p_user_id INT, p_performance_id INT)
RETURNS DATETIME
DETERMINISTIC
READS SQL DATA
BEGIN
    DECLARE v_start_time DATETIME;
    DECLARE v_transport_type VARCHAR(20);
    DECLARE v_estimated_time INT;
    DECLARE v_buffer INT DEFAULT 10;
    DECLARE v_departure DATETIME;

    SELECT pf.start_time, tpo.transport_type, tpo.estimated_time
      INTO v_start_time, v_transport_type, v_estimated_time
      FROM Performance pf
      JOIN Theater th ON pf.theater_id = th.theater_id
      JOIN User u ON u.user_id = p_user_id
      JOIN Transport_Option tpo
        ON tpo.theater_id = th.theater_id
       AND tpo.suitable_district = u.home_district
     WHERE pf.performance_id = p_performance_id
     ORDER BY tpo.estimated_time ASC
     LIMIT 1;

    IF v_transport_type = 'subway' THEN
        SET v_buffer = 15;
    ELSEIF v_transport_type = 'bus' THEN
        SET v_buffer = 20;
    ELSEIF v_transport_type = 'taxi' THEN
        SET v_buffer = 10;
    ELSEIF v_transport_type = 'walk' THEN
        SET v_buffer = 5;
    END IF;

    SET v_departure = DATE_SUB(v_start_time, INTERVAL (v_estimated_time + v_buffer) MINUTE);
    RETURN v_departure;
END$$

DELIMITER ;

-- =========================
-- 5. 存储过程
-- 说明：由于 MySQL 对返回结果集函数支持受限，原设计里“返回结果表”的推荐函数在 MySQL 中更适合写成存储过程，采用‘过程 + 结果表’方式实现 fn_recommend_by_profile 的功能”
-- =========================

-- =========================
-- 5.1 推荐结果缓存表
-- 用于承接画像推荐函数的结果表能力
-- =========================

CREATE TABLE IF NOT EXISTS Profile_Recommendation_Result (
    user_id INT NOT NULL,
    performance_id INT NOT NULL,
    production_title VARCHAR(200) NOT NULL,
    version_name VARCHAR(50),
    category VARCHAR(50),
    language VARCHAR(50),
    start_time DATETIME,
    theater_name VARCHAR(100),
    district VARCHAR(50),
    price_min DECIMAL(10,2),
    price_max DECIMAL(10,2),
    special_tag VARCHAR(50),
    recommendation_source VARCHAR(30) NOT NULL,
    matched_profile_type VARCHAR(50),
    match_score INT NOT NULL,
    recommendation_reason VARCHAR(255),
    generated_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    PRIMARY KEY (user_id, performance_id),
    CONSTRAINT fk_profile_result_performance
        FOREIGN KEY (performance_id) REFERENCES Performance(performance_id),
    CONSTRAINT fk_profile_result_user
        FOREIGN KEY (user_id) REFERENCES User(user_id)
);
DROP PROCEDURE IF EXISTS sp_recommend_by_profile;
DELIMITER $$

CREATE PROCEDURE sp_recommend_by_profile(IN p_user_id INT)
BEGIN
    DECLARE v_audience_type VARCHAR(50);

    SET v_audience_type = fn_audience_type(p_user_id);

    DELETE FROM Profile_Recommendation_Result
    WHERE user_id = p_user_id;

    INSERT INTO Profile_Recommendation_Result (
        user_id,
        performance_id,
        production_title,
        version_name,
        category,
        language,
        start_time,
        theater_name,
        district,
        price_min,
        price_max,
        special_tag,
        recommendation_source,
        matched_profile_type,
        match_score,
        recommendation_reason
    )
    WITH candidate AS (
        SELECT
            pf.performance_id,
            pr.title AS production_title,
            pr.version AS version_name,
            pr.category,
            pr.language,
            pf.start_time,
            th.theater_name,
            th.district,
            pf.price_min,
            pf.price_max,
            pf.special_tag,
            (
                CASE 
                    WHEN EXISTS (
                        SELECT 1
                        FROM Performance_Cast pc
                        JOIN Favorite_Actor fa ON pc.actor_id = fa.actor_id
                        WHERE pc.performance_id = pf.performance_id
                          AND fa.user_id = p_user_id
                    ) THEN 
                        CASE 
                            WHEN v_audience_type = '演员驱动型' THEN 40
                            ELSE 20
                        END
                    ELSE 0
                END
                +
                CASE
                    WHEN EXISTS (
                        SELECT 1
                        FROM Favorite_Category fc
                        WHERE fc.user_id = p_user_id
                          AND fc.category = pr.category
                    ) THEN
                        CASE
                            WHEN v_audience_type = '剧种探索型' THEN 35
                            ELSE 20
                        END
                    ELSE 0
                END
                +
                CASE
                    WHEN EXISTS (
                        SELECT 1
                        FROM Favorite_Language fl
                        WHERE fl.user_id = p_user_id
                          AND fl.language = pr.language
                    ) THEN 10
                    ELSE 0
                END
                +
                CASE
                    WHEN EXISTS (
                        SELECT 1
                        FROM Favorite_District fd
                        WHERE fd.user_id = p_user_id
                          AND fd.city = th.city
                          AND fd.district = th.district
                    ) THEN
                        CASE
                            WHEN v_audience_type = '行程敏感型' THEN 25
                            ELSE 10
                        END
                    ELSE 0
                END
                +
                CASE
                    WHEN (SELECT price_preference FROM User WHERE user_id = p_user_id) = 'economy'
                         AND pf.price_min <= 200 THEN 15
                    WHEN (SELECT price_preference FROM User WHERE user_id = p_user_id) = 'mid'
                         AND pf.price_min BETWEEN 200 AND 500 THEN 15
                    WHEN (SELECT price_preference FROM User WHERE user_id = p_user_id) = 'premium'
                         AND pf.price_max >= 500 THEN 15
                    ELSE 0
                END
                +
                CASE
                    WHEN (SELECT time_preference FROM User WHERE user_id = p_user_id) = 'weekday_evening'
                         AND DAYOFWEEK(pf.start_time) BETWEEN 2 AND 6
                         AND HOUR(pf.start_time) >= 18 THEN 10
                    WHEN (SELECT time_preference FROM User WHERE user_id = p_user_id) = 'weekend_evening'
                         AND DAYOFWEEK(pf.start_time) IN (1,7)
                         AND HOUR(pf.start_time) >= 18 THEN 10
                    WHEN (SELECT time_preference FROM User WHERE user_id = p_user_id) = 'weekend_matinee'
                         AND DAYOFWEEK(pf.start_time) IN (1,7)
                         AND HOUR(pf.start_time) < 18 THEN 10
                    ELSE 0
                END
                +
                CASE
                    WHEN pf.special_tag IS NOT NULL AND pf.special_tag <> '' THEN 8
                    ELSE 0
                END
            ) AS match_score
        FROM Performance pf
        JOIN Production pr ON pf.production_id = pr.production_id
        JOIN Theater th ON pf.theater_id = th.theater_id
        WHERE pf.start_time > NOW()
          AND NOT EXISTS (
                SELECT 1
                FROM Watch_Record wr
                WHERE wr.user_id = p_user_id
                  AND wr.performance_id = pf.performance_id
          )
          AND NOT EXISTS (
                SELECT 1
                FROM Planned_Performance pp
                WHERE pp.user_id = p_user_id
                  AND pp.performance_id = pf.performance_id
          )
    )
    SELECT
        p_user_id,
        performance_id,
        production_title,
        version_name,
        category,
        language,
        start_time,
        theater_name,
        district,
        price_min,
        price_max,
        special_tag,
        'profile_based',
        v_audience_type,
        match_score,
        CASE
            WHEN v_audience_type = '演员驱动型' THEN '优先匹配喜欢演员出演场次'
            WHEN v_audience_type = '剧种探索型' THEN '优先匹配剧种偏好并兼顾多样化'
            WHEN v_audience_type = '高性价比型' THEN '优先匹配预算友好的场次'
            WHEN v_audience_type = '行程敏感型' THEN '优先匹配区域与时间便利性'
            ELSE '综合画像推荐'
        END
    FROM candidate
    ORDER BY match_score DESC, start_time ASC
    LIMIT 20;

    SELECT *
    FROM Profile_Recommendation_Result
    WHERE user_id = p_user_id
    ORDER BY match_score DESC, start_time ASC;
END$$

DELIMITER ;

-- =========================
-- 6. 视图
-- =========================

DROP VIEW IF EXISTS v_public_performance_info;

CREATE OR REPLACE VIEW v_public_performance_info AS
SELECT
    pf.performance_id,
    pr.title,
    pr.version,
    pr.category,
    pr.language,
    th.theater_name,
    th.city,
    th.district,
    pf.start_time,
    pf.end_time,
    pf.price_min,
    pf.price_max,
    pf.special_tag
FROM Performance pf
JOIN Production pr ON pf.production_id = pr.production_id
JOIN Theater th ON pf.theater_id = th.theater_id;

CREATE OR REPLACE VIEW v_user_calendar AS
SELECT
    wr.user_id,
    pf.performance_id,
    pr.title,
    pr.version AS version_name,
    th.theater_name,
    pf.start_time,
    pf.end_time,
    'watched' AS calendar_status,
    wr.score
FROM Watch_Record wr
JOIN Performance pf ON wr.performance_id = pf.performance_id
JOIN Production pr ON pf.production_id = pr.production_id
JOIN Theater th ON pf.theater_id = th.theater_id

UNION ALL

SELECT
    pp.user_id,
    pf.performance_id,
    pr.title,
    pr.version AS version_name,
    th.theater_name,
    pf.start_time,
    pf.end_time,
    pp.status AS calendar_status,
    NULL AS score
FROM Planned_Performance pp
JOIN Performance pf ON pp.performance_id = pf.performance_id
JOIN Production pr ON pf.production_id = pr.production_id
JOIN Theater th ON pf.theater_id = th.theater_id;

CREATE OR REPLACE VIEW v_user_preference_profile AS
SELECT
    u.user_id,
    u.username,
    u.city,
    (
        SELECT GROUP_CONCAT(a.actor_name ORDER BY a.actor_name SEPARATOR '、')
        FROM Favorite_Actor fa
        JOIN Actor a ON fa.actor_id = a.actor_id
        WHERE fa.user_id = u.user_id
    ) AS favorite_actors,
    (
        SELECT GROUP_CONCAT(fc.category ORDER BY fc.category SEPARATOR '、')
        FROM Favorite_Category fc
        WHERE fc.user_id = u.user_id
    ) AS favorite_categories,
    (
        SELECT GROUP_CONCAT(fl.language ORDER BY fl.language SEPARATOR '、')
        FROM Favorite_Language fl
        WHERE fl.user_id = u.user_id
    ) AS favorite_languages,
    (
        SELECT GROUP_CONCAT(CONCAT(fd.city, '-', fd.district) ORDER BY fd.city, fd.district SEPARATOR '、')
        FROM Favorite_District fd
        WHERE fd.user_id = u.user_id
    ) AS favorite_districts,
    u.price_preference,
    u.time_preference,
    (
        SELECT pr.category
        FROM Watch_Record wr
        JOIN Performance pf ON wr.performance_id = pf.performance_id
        JOIN Production pr ON pf.production_id = pr.production_id
        WHERE wr.user_id = u.user_id
        GROUP BY pr.category
        ORDER BY COUNT(*) DESC, pr.category
        LIMIT 1
    ) AS most_watched_category,
    (
        SELECT a.actor_name
        FROM Watch_Record wr
        JOIN Performance_Cast pc ON wr.performance_id = pc.performance_id
        JOIN Actor a ON pc.actor_id = a.actor_id
        WHERE wr.user_id = u.user_id
        GROUP BY a.actor_id, a.actor_name
        ORDER BY COUNT(*) DESC, a.actor_name
        LIMIT 1
    ) AS most_watched_actor,
    (
        SELECT th.theater_name
        FROM Watch_Record wr
        JOIN Performance pf ON wr.performance_id = pf.performance_id
        JOIN Theater th ON pf.theater_id = th.theater_id
        WHERE wr.user_id = u.user_id
        GROUP BY th.theater_id, th.theater_name
        ORDER BY COUNT(*) DESC, th.theater_name
        LIMIT 1
    ) AS most_visited_theater,
    (
        SELECT ROUND(AVG(wr.score), 2)
        FROM Watch_Record wr
        WHERE wr.user_id = u.user_id
    ) AS avg_score,
    (
        SELECT COUNT(*)
        FROM Watch_Record wr
        WHERE wr.user_id = u.user_id
    ) AS total_watched,
    fn_audience_type(u.user_id) AS audience_type
FROM User u;

DROP VIEW IF EXISTS v_hybrid_recommendation;

CREATE OR REPLACE VIEW v_hybrid_recommendation AS
WITH future_perf AS (
    SELECT
        pf.performance_id,
        pf.production_id,
        pf.theater_id,
        pf.start_time,
        pf.end_time,
        pf.price_min,
        pf.price_max,
        pf.special_tag,
        pr.title AS production_title,
        pr.version AS version_name,
        pr.category,
        pr.language,
        th.theater_name,
        th.district,
        th.city
    FROM Performance pf
    JOIN Production pr ON pf.production_id = pr.production_id
    JOIN Theater th ON pf.theater_id = th.theater_id
    WHERE pf.start_time > NOW()
),

similar_user_rec AS (
    SELECT DISTINCT
        u.user_id,
        fp.performance_id AS recommended_performance_id,
        fp.production_title,
        fp.version_name,
        fp.category,
        fp.language,
        fp.start_time,
        fp.theater_name,
        fp.district,
        fp.price_min,
        fp.price_max,
        fp.special_tag AS tag_label,
        'similar_user' AS recommendation_source,
        fn_audience_type(u.user_id) AS matched_profile_type,
        '来自相似用户的高评分观看记录' AS recommendation_reason,
        2 AS source_priority
    FROM User u
    JOIN Watch_Record wr2
      ON wr2.user_id = fn_most_similar_user(u.user_id)
    JOIN future_perf fp
      ON wr2.performance_id = fp.performance_id
    WHERE wr2.score >= 8
),

profile_based_rec AS (
    SELECT DISTINCT
        prr.user_id,
        prr.performance_id AS recommended_performance_id,
        prr.production_title,
        prr.version_name,
        prr.category,
        prr.language,
        prr.start_time,
        prr.theater_name,
        prr.district,
        prr.price_min,
        prr.price_max,
        prr.special_tag AS tag_label,
        prr.recommendation_source,
        prr.matched_profile_type,
        prr.recommendation_reason,
        1 AS source_priority
    FROM Profile_Recommendation_Result prr
),

rule_based_rec AS (
    SELECT DISTINCT
        u.user_id,
        fp.performance_id AS recommended_performance_id,
        fp.production_title,
        fp.version_name,
        fp.category,
        fp.language,
        fp.start_time,
        fp.theater_name,
        fp.district,
        fp.price_min,
        fp.price_max,
        fp.special_tag AS tag_label,
        'rule_based' AS recommendation_source,
        fn_audience_type(u.user_id) AS matched_profile_type,
        CASE
            WHEN fp.special_tag IS NOT NULL AND fp.special_tag <> '' THEN '特殊标签场次补充推荐'
            WHEN u.time_preference = 'weekday_evening'
                 AND DAYOFWEEK(fp.start_time) BETWEEN 2 AND 6
                 AND HOUR(fp.start_time) >= 18 THEN '匹配工作日晚间时间偏好'
            WHEN u.time_preference = 'weekend_evening'
                 AND DAYOFWEEK(fp.start_time) IN (1, 7)
                 AND HOUR(fp.start_time) >= 18 THEN '匹配周末晚间时间偏好'
            WHEN u.time_preference = 'weekend_matinee'
                 AND DAYOFWEEK(fp.start_time) IN (1, 7)
                 AND HOUR(fp.start_time) < 18 THEN '匹配周末下午场时间偏好'
            ELSE '规则补充推荐'
        END AS recommendation_reason,
        3 AS source_priority
    FROM User u
    JOIN future_perf fp
    WHERE
        fp.special_tag IS NOT NULL
        OR (
            u.time_preference = 'weekday_evening'
            AND DAYOFWEEK(fp.start_time) BETWEEN 2 AND 6
            AND HOUR(fp.start_time) >= 18
        )
        OR (
            u.time_preference = 'weekend_evening'
            AND DAYOFWEEK(fp.start_time) IN (1, 7)
            AND HOUR(fp.start_time) >= 18
        )
        OR (
            u.time_preference = 'weekend_matinee'
            AND DAYOFWEEK(fp.start_time) IN (1, 7)
            AND HOUR(fp.start_time) < 18
        )
),

all_rec AS (
    SELECT * FROM similar_user_rec
    UNION ALL
    SELECT * FROM profile_based_rec
    UNION ALL
    SELECT * FROM rule_based_rec
),

filtered_rec AS (
    SELECT *
    FROM all_rec rec
    WHERE NOT EXISTS (
        SELECT 1
        FROM Watch_Record wr
        WHERE wr.user_id = rec.user_id
          AND wr.performance_id = rec.recommended_performance_id
    )
      AND NOT EXISTS (
        SELECT 1
        FROM Planned_Performance pp
        WHERE pp.user_id = rec.user_id
          AND pp.performance_id = rec.recommended_performance_id
    )
),

best_priority AS (
    SELECT
        user_id,
        recommended_performance_id,
        MIN(source_priority) AS best_priority
    FROM filtered_rec
    GROUP BY user_id, recommended_performance_id
)

SELECT
    fr.user_id,
    fr.recommended_performance_id,
    fr.production_title,
    fr.version_name,
    fr.category,
    fr.language,
    fr.start_time,
    fr.theater_name,
    fr.district,
    fr.price_min,
    fr.price_max,
    fr.tag_label,
    fr.recommendation_source,
    fr.matched_profile_type,
    fr.recommendation_reason
FROM filtered_rec fr
JOIN best_priority bp
  ON fr.user_id = bp.user_id
 AND fr.recommended_performance_id = bp.recommended_performance_id
 AND fr.source_priority = bp.best_priority;

DROP VIEW IF EXISTS v_planned_trip_assistance;

CREATE OR REPLACE VIEW v_planned_trip_assistance AS
WITH planned_base AS (
    SELECT
        pp.user_id,
        pp.performance_id,
        pp.status,
        pf.theater_id,
        pf.start_time,
        pf.end_time,
        th.theater_name,
        th.city,
        th.district,
        u.price_preference,
        u.home_district
    FROM Planned_Performance pp
    JOIN Performance pf ON pp.performance_id = pf.performance_id
    JOIN Theater th ON pf.theater_id = th.theater_id
    JOIN User u ON pp.user_id = u.user_id
    WHERE pp.status IN ('planned', 'booked')
),

restaurant_ranked AS (
    SELECT
        pb.user_id,
        pb.performance_id,
        nr.restaurant_id,
        nr.restaurant_name,
        nr.category,
        nr.price_tier,
        nr.avg_price,
        nr.distance_m,
        ROW_NUMBER() OVER (
            PARTITION BY pb.user_id, pb.performance_id
            ORDER BY nr.distance_m ASC, nr.avg_price ASC, nr.restaurant_id ASC
        ) AS rn
    FROM planned_base pb
    JOIN Nearby_Restaurant nr
      ON pb.theater_id = nr.theater_id
    WHERE
        (pb.price_preference = 'economy' AND nr.price_tier = 'low')
        OR (pb.price_preference = 'mid' AND nr.price_tier = 'mid')
        OR (pb.price_preference = 'premium' AND nr.price_tier = 'high')
),

transport_ranked AS (
    SELECT
        pb.user_id,
        pb.performance_id,
        tp.transport_id,
        tp.transport_type,
        tp.estimated_time,
        tp.estimated_cost,
        tp.suitable_district,
        ROW_NUMBER() OVER (
            PARTITION BY pb.user_id, pb.performance_id
            ORDER BY tp.estimated_time ASC, tp.estimated_cost ASC, tp.transport_id ASC
        ) AS rn
    FROM planned_base pb
    JOIN Transport_Option tp
      ON pb.theater_id = tp.theater_id
    WHERE tp.suitable_district = pb.home_district
)

SELECT
    pb.user_id,
    pb.performance_id,
    pb.theater_name,
    pb.start_time,
    pb.end_time,
    rr.restaurant_name,
    rr.category AS restaurant_category,
    rr.price_tier,
    rr.avg_price,
    rr.distance_m,
    tr.transport_type,
    tr.estimated_time,
    tr.estimated_cost,
    tr.suitable_district,
    fn_suggested_departure_time(pb.user_id, pb.performance_id) AS suggested_departure_time
FROM planned_base pb
LEFT JOIN restaurant_ranked rr
       ON pb.user_id = rr.user_id
      AND pb.performance_id = rr.performance_id
      AND rr.rn = 1
LEFT JOIN transport_ranked tr
       ON pb.user_id = tr.user_id
      AND pb.performance_id = tr.performance_id
      AND tr.rn = 1;
      
-- =========================
-- 7. 身份和权限管理
-- =========================

CREATE ROLE IF NOT EXISTS stagebook_user;
CREATE ROLE IF NOT EXISTS stagebook_admin;

GRANT SELECT ON stagebook.v_public_performance_info TO stagebook_user;
GRANT SELECT ON stagebook.v_user_calendar TO stagebook_user;
GRANT SELECT ON stagebook.v_user_preference_profile TO stagebook_user;
GRANT SELECT ON stagebook.v_hybrid_recommendation TO stagebook_user;
GRANT SELECT ON stagebook.v_planned_trip_assistance TO stagebook_user;

GRANT SELECT, INSERT, UPDATE, DELETE ON stagebook.Watch_Record TO stagebook_user;
GRANT SELECT, INSERT, UPDATE, DELETE ON stagebook.Planned_Performance TO stagebook_user;
GRANT SELECT, INSERT, UPDATE, DELETE ON stagebook.Favorite_Actor TO stagebook_user;
GRANT SELECT, INSERT, UPDATE, DELETE ON stagebook.Favorite_Category TO stagebook_user;
GRANT SELECT, INSERT, UPDATE, DELETE ON stagebook.Favorite_Language TO stagebook_user;
GRANT SELECT, INSERT, UPDATE, DELETE ON stagebook.Favorite_District TO stagebook_user;

GRANT SELECT, UPDATE ON stagebook.User TO stagebook_user;

GRANT ALL PRIVILEGES ON stagebook.Production TO stagebook_admin;
GRANT ALL PRIVILEGES ON stagebook.Performance TO stagebook_admin;
GRANT ALL PRIVILEGES ON stagebook.Theater TO stagebook_admin;
GRANT ALL PRIVILEGES ON stagebook.Actor TO stagebook_admin;
GRANT ALL PRIVILEGES ON stagebook.Role TO stagebook_admin;
GRANT ALL PRIVILEGES ON stagebook.Performance_Cast TO stagebook_admin;
GRANT ALL PRIVILEGES ON stagebook.Nearby_Restaurant TO stagebook_admin;
GRANT ALL PRIVILEGES ON stagebook.Transport_Option TO stagebook_admin;

GRANT SELECT ON stagebook.User TO stagebook_admin;
GRANT SELECT ON stagebook.Watch_Record TO stagebook_admin;
GRANT SELECT ON stagebook.Planned_Performance TO stagebook_admin;
GRANT SELECT ON stagebook.v_user_preference_profile TO stagebook_admin;
GRANT SELECT ON stagebook.v_hybrid_recommendation TO stagebook_admin;
GRANT SELECT ON stagebook.v_planned_trip_assistance TO stagebook_admin;
GRANT SELECT ON stagebook.v_public_performance_info TO stagebook_admin;

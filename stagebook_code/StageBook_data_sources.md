# StageBook 数据集来源说明

本数据集采用“真实场馆锚点 + 教学合成业务数据”的方式构造。

## 真实参考部分

- 上海大剧院：上海市黄浦区人民大道300号。
- 上音歌剧院：上海市徐汇区汾阳路6号。
- 大宁剧院：上海市静安区平型关路1222号。
- 上海虹桥艺术中心：上海市长宁区天山路888号。
- 上海东方艺术中心：上海市浦东新区丁香路425号。
- 万代南梦宫上海文化中心·梦想剧场：上海市普陀区宜昌路179号万代南梦宫艺术中心一层。

## 教学合成部分

以下数据为课程数据库展示用途的合成数据，不对应真实售票排期或真实用户行为：

- Production 剧目
- Performance 演出场次、票价、special_tag
- Actor / Role / Performance_Cast
- User / Watch_Record / Planned_Performance / Favorite_*
- Nearby_Restaurant / Transport_Option / Admin_Log

这样处理是为了避免真实演出排期快速过期，同时确保视图、函数、存储过程和触发器都能稳定展示。

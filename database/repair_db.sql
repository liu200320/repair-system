-- MySQL dump 10.13  Distrib 5.7.26, for Win64 (x86_64)
--
-- Host: localhost    Database: repair_db
-- ------------------------------------------------------
-- Server version	5.7.26
/*!40103 SET @OLD_TIME_ZONE=@@TIME_ZONE */;
/*!40103 SET TIME_ZONE='+00:00' */;
/*!40014 SET @OLD_UNIQUE_CHECKS=@@UNIQUE_CHECKS, UNIQUE_CHECKS=0 */;
/*!40014 SET @OLD_FOREIGN_KEY_CHECKS=@@FOREIGN_KEY_CHECKS, FOREIGN_KEY_CHECKS=0 */;
/*!40101 SET @OLD_SQL_MODE=@@SQL_MODE, SQL_MODE='NO_AUTO_VALUE_ON_ZERO' */;
/*!40111 SET @OLD_SQL_NOTES=@@SQL_NOTES, SQL_NOTES=0 */;

--
-- Current Database: `repair_db`
--

CREATE DATABASE /*!32312 IF NOT EXISTS*/ `repair_db` /*!40100 DEFAULT CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci */;

USE `repair_db`;

--
-- Table structure for table `monitor_points`
--

DROP TABLE IF EXISTS `monitor_points`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `monitor_points` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `name` varchar(200) NOT NULL COMMENT '点位名称',
  `address` varchar(300) DEFAULT NULL COMMENT '详细地址',
  `area` varchar(100) DEFAULT NULL COMMENT '所属区域',
  `created_at` datetime DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (`id`),
  UNIQUE KEY `name` (`name`)
) ENGINE=MyISAM AUTO_INCREMENT=223 DEFAULT CHARSET=utf8mb4 COMMENT='监控/维修点位表';
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `monitor_points`
--

LOCK TABLES `monitor_points` WRITE;
/*!40000 ALTER TABLE `monitor_points` DISABLE KEYS */;
INSERT INTO `monitor_points` VALUES (1,'足球场照大屏',NULL,NULL,'2026-07-20 00:17:41'),(2,'足球场1',NULL,NULL,'2026-07-20 00:17:41'),(3,'足球场2',NULL,NULL,'2026-07-20 00:17:41'),(4,'足球场3',NULL,NULL,'2026-07-20 00:17:41'),(5,'足球场观景台1',NULL,NULL,'2026-07-20 00:17:41'),(6,'足球场观景台2',NULL,NULL,'2026-07-20 00:17:41'),(7,'后门堤坝',NULL,NULL,'2026-07-20 00:17:41'),(8,'后门水面',NULL,NULL,'2026-07-20 00:17:41'),(9,'学校后门',NULL,NULL,'2026-07-20 00:17:41'),(10,'耕道院宿管旁',NULL,NULL,'2026-07-20 00:17:41'),(11,'耕道院至水塔小路',NULL,NULL,'2026-07-20 00:17:41'),(12,'耕道院篮球场1',NULL,NULL,'2026-07-20 00:17:41'),(13,'耕道院篮球场2',NULL,NULL,'2026-07-20 00:17:41'),(14,'耕道院篮球场3',NULL,NULL,'2026-07-20 00:17:41'),(15,'耕道院外墙1',NULL,NULL,'2026-07-20 00:17:41'),(16,'耕道院后墙1',NULL,NULL,'2026-07-20 00:17:41'),(17,'耕道院后墙2',NULL,NULL,'2026-07-20 00:17:41'),(18,'耕道院楼梯入口',NULL,NULL,'2026-07-20 00:17:41'),(19,'耕道院值班室',NULL,NULL,'2026-07-20 00:17:41'),(20,'嘉锐楼至商业街道路',NULL,NULL,'2026-07-20 00:17:41'),(21,'嘉锐楼至商业街过道2',NULL,NULL,'2026-07-20 00:17:41'),(22,'嘉锐楼大厅',NULL,NULL,'2026-07-20 00:17:41'),(23,'嘉锐楼至实训楼前',NULL,NULL,'2026-07-20 00:17:41'),(24,'嘉锐楼至健身器材处',NULL,NULL,'2026-07-20 00:17:41'),(25,'嘉锐楼楼顶',NULL,NULL,'2026-07-20 00:17:41'),(26,'嘉锐楼照实训楼',NULL,NULL,'2026-07-20 00:17:41'),(27,'嘉锐楼照复兴楼',NULL,NULL,'2026-07-20 00:17:41'),(28,'嘉锐楼至实训楼',NULL,NULL,'2026-07-20 00:17:41'),(29,'综合训练场',NULL,NULL,'2026-07-20 00:17:41'),(30,'综合训练场至商业街过道',NULL,NULL,'2026-07-20 00:17:41'),(31,'综合楼停车场1',NULL,NULL,'2026-07-20 00:17:41'),(32,'综合楼后停车场',NULL,NULL,'2026-07-20 00:17:41'),(33,'综合楼停车场2',NULL,NULL,'2026-07-20 00:17:41'),(34,'综合楼大厅',NULL,NULL,'2026-07-20 00:17:41'),(35,'综合楼过道1',NULL,NULL,'2026-07-20 00:17:41'),(36,'综合楼过道2',NULL,NULL,'2026-07-20 00:17:41'),(37,'综合楼楼顶',NULL,NULL,'2026-07-20 00:17:41'),(38,'综合楼304保密室1',NULL,NULL,'2026-07-20 00:17:41'),(39,'综合楼304保密室2',NULL,NULL,'2026-07-20 00:17:41'),(40,'鸿翼楼',NULL,NULL,'2026-07-20 00:17:41'),(41,'鸿翼楼楼顶',NULL,NULL,'2026-07-20 00:17:41'),(42,'鸿翼楼过道',NULL,NULL,'2026-07-20 00:17:41'),(43,'鸿翼楼至嘉锐楼道路',NULL,NULL,'2026-07-20 00:17:41'),(44,'实训楼大厅',NULL,NULL,'2026-07-20 00:17:41'),(45,'实训楼后球机',NULL,NULL,'2026-07-20 00:17:41'),(46,'实训楼楼顶',NULL,NULL,'2026-07-20 00:17:41'),(47,'复兴楼',NULL,NULL,'2026-07-20 00:17:41'),(48,'复兴楼2',NULL,NULL,'2026-07-20 00:17:41'),(49,'复兴楼楼梯出入口',NULL,NULL,'2026-07-20 00:17:41'),(50,'复兴楼至游泳池',NULL,NULL,'2026-07-20 00:17:41'),(51,'复兴新楼照嘉锐楼',NULL,NULL,'2026-07-20 00:17:41'),(52,'复兴楼照养德楼',NULL,NULL,'2026-07-20 00:17:41'),(53,'复兴楼楼顶出入口',NULL,NULL,'2026-07-20 00:17:41'),(54,'养德楼过道',NULL,NULL,'2026-07-20 00:17:41'),(55,'养德楼外墙1',NULL,NULL,'2026-07-20 00:17:41'),(56,'养德楼外墙2',NULL,NULL,'2026-07-20 00:17:41'),(57,'养德楼出入口',NULL,NULL,'2026-07-20 00:17:41'),(58,'养德楼照复兴楼',NULL,NULL,'2026-07-20 00:17:41'),(59,'养德楼楼顶出入口',NULL,NULL,'2026-07-20 00:17:41'),(60,'养德楼照维新院',NULL,NULL,'2026-07-20 00:17:41'),(61,'维新苑1',NULL,NULL,'2026-07-20 00:17:41'),(62,'维新苑2',NULL,NULL,'2026-07-20 00:17:41'),(63,'维新苑3',NULL,NULL,'2026-07-20 00:17:41'),(64,'维新苑4',NULL,NULL,'2026-07-20 00:17:41'),(65,'维新院楼顶',NULL,NULL,'2026-07-20 00:17:41'),(66,'维新院楼顶1',NULL,NULL,'2026-07-20 00:17:41'),(67,'维新苑楼顶2',NULL,NULL,'2026-07-20 00:17:41'),(68,'维新苑外墙',NULL,NULL,'2026-07-20 00:17:41'),(69,'维新苑出入口',NULL,NULL,'2026-07-20 00:17:41'),(70,'维新苑照鸿鹄楼',NULL,NULL,'2026-07-20 00:17:41'),(71,'维新苑楼顶照楼顶入口',NULL,NULL,'2026-07-20 00:17:41'),(72,'维新苑照豳风楼',NULL,NULL,'2026-07-20 00:17:41'),(73,'豳风楼楼顶1',NULL,NULL,'2026-07-20 00:17:41'),(74,'豳风楼楼顶2',NULL,NULL,'2026-07-20 00:17:41'),(75,'豳风楼3',NULL,NULL,'2026-07-20 00:17:41'),(76,'豳风楼出入口',NULL,NULL,'2026-07-20 00:17:41'),(77,'豳风楼过道',NULL,NULL,'2026-07-20 00:17:41'),(78,'豳风楼外墙',NULL,NULL,'2026-07-20 00:17:41'),(79,'豳风楼后墙',NULL,NULL,'2026-07-20 00:17:41'),(80,'豳风楼广场',NULL,NULL,'2026-07-20 00:17:41'),(81,'豳风楼后围栏过道',NULL,NULL,'2026-07-20 00:17:41'),(82,'鸿鹄楼出入口',NULL,NULL,'2026-07-20 00:17:41'),(83,'鸿鹄楼外墙',NULL,NULL,'2026-07-20 00:17:41'),(84,'鸿鹄楼一楼过道',NULL,NULL,'2026-07-20 00:17:41'),(85,'鸿鹄楼楼顶1',NULL,NULL,'2026-07-20 00:17:41'),(86,'鸿鹄楼楼顶防火门1',NULL,NULL,'2026-07-20 00:17:41'),(87,'鸿鹄楼楼顶防火门2',NULL,NULL,'2026-07-20 00:17:41'),(88,'秋实路',NULL,NULL,'2026-07-20 00:17:41'),(89,'五谷苑1',NULL,NULL,'2026-07-20 00:17:41'),(90,'五谷苑2',NULL,NULL,'2026-07-20 00:17:41'),(91,'五谷苑宿舍1',NULL,NULL,'2026-07-20 00:17:41'),(92,'五谷苑宿舍2',NULL,NULL,'2026-07-20 00:17:41'),(93,'五谷苑宿舍3',NULL,NULL,'2026-07-20 00:17:41'),(94,'牧歌院1号楼',NULL,NULL,'2026-07-20 00:17:41'),(95,'牧歌院1栋出入口',NULL,NULL,'2026-07-20 00:17:41'),(96,'牧歌院2栋出入口',NULL,NULL,'2026-07-20 00:17:41'),(97,'形体室至女生宿舍',NULL,NULL,'2026-07-20 00:17:41'),(98,'监控室',NULL,NULL,'2026-07-20 00:17:41'),(99,'监控中心门前',NULL,NULL,'2026-07-20 00:17:41'),(100,'图书馆大厅',NULL,NULL,'2026-07-20 00:17:41'),(101,'图书馆阅览室',NULL,NULL,'2026-07-20 00:17:41'),(102,'图书馆斜对面',NULL,NULL,'2026-07-20 00:17:41'),(103,'图书馆配电房旁',NULL,NULL,'2026-07-20 00:17:41'),(104,'图书馆门口',NULL,NULL,'2026-07-20 00:17:41'),(105,'学生服务中心大厅',NULL,NULL,'2026-07-20 00:17:41'),(106,'学生服务中心会议室',NULL,NULL,'2026-07-20 00:17:41'),(107,'学生服务中心外墙',NULL,NULL,'2026-07-20 00:17:41'),(108,'学生服务中心一楼过道',NULL,NULL,'2026-07-20 00:17:41'),(109,'绍年院',NULL,NULL,'2026-07-20 00:17:41'),(110,'绍年苑至田之院',NULL,NULL,'2026-07-20 00:17:41'),(111,'团委门口',NULL,NULL,'2026-07-20 00:17:41'),(112,'团委过道',NULL,NULL,'2026-07-20 00:17:41'),(113,'蚕桑礼堂内',NULL,NULL,'2026-07-20 00:17:41'),(114,'蚕桑礼堂后门',NULL,NULL,'2026-07-20 00:17:41'),(115,'礼堂侧门',NULL,NULL,'2026-07-20 00:17:41'),(116,'礼堂小广场',NULL,NULL,'2026-07-20 00:17:41'),(117,'礼堂小广场2',NULL,NULL,'2026-07-20 00:17:41'),(118,'礼堂斜对面',NULL,NULL,'2026-07-20 00:17:41'),(119,'礼堂斜对面照学生服务中心道路',NULL,NULL,'2026-07-20 00:17:41'),(120,'汽修院子',NULL,NULL,'2026-07-20 00:17:41'),(121,'汽修院子2',NULL,NULL,'2026-07-20 00:17:41'),(122,'大门出入口1.2',NULL,NULL,'2026-07-20 00:17:41'),(123,'大门出入口3',NULL,NULL,'2026-07-20 00:17:41'),(124,'大门口停车场',NULL,NULL,'2026-07-20 00:17:41'),(125,'大门内第三颗电杆',NULL,NULL,'2026-07-20 00:17:41'),(126,'后大门岗亭',NULL,NULL,'2026-07-20 00:17:41'),(127,'新大门对道闸入口',NULL,NULL,'2026-07-20 00:17:41'),(128,'新大门翼闸入口',NULL,NULL,'2026-07-20 00:17:41'),(129,'新大门道闸出口',NULL,NULL,'2026-07-20 00:17:41'),(130,'新大门对值班室',NULL,NULL,'2026-07-20 00:17:41'),(131,'老大门翼闸出口',NULL,NULL,'2026-07-20 00:17:41'),(132,'老大们对外路面',NULL,NULL,'2026-07-20 00:17:41'),(133,'老大门对停车场',NULL,NULL,'2026-07-20 00:17:41'),(134,'昆明学院门前',NULL,NULL,'2026-07-20 00:17:41'),(135,'文清楼门口',NULL,NULL,'2026-07-20 00:17:41'),(136,'文清楼至德三楼',NULL,NULL,'2026-07-20 00:17:41'),(137,'文清楼停车场1',NULL,NULL,'2026-07-20 00:17:41'),(138,'文清楼停车场2',NULL,NULL,'2026-07-20 00:17:41'),(139,'一号楼ATM机1',NULL,NULL,'2026-07-20 00:17:41'),(140,'一号楼ATM机2',NULL,NULL,'2026-07-20 00:17:41'),(141,'新商业区大路',NULL,NULL,'2026-07-20 00:17:41'),(142,'网球场旁',NULL,NULL,'2026-07-20 00:17:41'),(143,'网球场照秋实路',NULL,NULL,'2026-07-20 00:17:41'),(144,'众创空间',NULL,NULL,'2026-07-20 00:17:41'),(145,'众创空间饼屋旁',NULL,NULL,'2026-07-20 00:17:41'),(146,'众创空间照维新院',NULL,NULL,'2026-07-20 00:17:41'),(147,'春华路',NULL,NULL,'2026-07-20 00:17:41'),(148,'春华路至教师宿舍',NULL,NULL,'2026-07-20 00:17:41'),(149,'春华路至绍年苑',NULL,NULL,'2026-07-20 00:17:41'),(150,'双女教职工宿舍中间',NULL,NULL,'2026-07-20 00:17:41'),(151,'职工宿舍至女教工宿舍',NULL,NULL,'2026-07-20 00:17:41'),(152,'教工宿舍4栋后围墙',NULL,NULL,'2026-07-20 00:17:41'),(153,'教工下河堤坝',NULL,NULL,'2026-07-20 00:17:41'),(154,'男教师宿舍楼',NULL,NULL,'2026-07-20 00:17:41'),(155,'水塘人行桥上方',NULL,NULL,'2026-07-20 00:17:41'),(156,'德三楼照文清楼',NULL,NULL,'2026-07-20 00:17:41'),(157,'德三楼文清楼之间',NULL,NULL,'2026-07-20 00:17:41'),(158,'德三楼至教工宿舍',NULL,NULL,'2026-07-20 00:17:41'),(159,'后勤服务中心门前',NULL,NULL,'2026-07-20 00:17:41'),(160,'后勤停车场1',NULL,NULL,'2026-07-20 00:17:41'),(161,'后勤停车场2',NULL,NULL,'2026-07-20 00:17:41'),(162,'后勤服务中心洗手池旁',NULL,NULL,'2026-07-20 00:17:41'),(163,'求索园',NULL,NULL,'2026-07-20 00:17:41'),(164,'求索园后围墙',NULL,NULL,'2026-07-20 00:17:41'),(165,'水塔水池',NULL,NULL,'2026-07-20 00:17:41'),(166,'水塔后围墙',NULL,NULL,'2026-07-20 00:17:41'),(167,'基础体育办公室',NULL,NULL,'2026-07-20 00:17:41'),(168,'投掷场',NULL,NULL,'2026-07-20 00:17:41'),(169,'实训中心至鱼塘水面',NULL,NULL,'2026-07-20 00:17:41'),(170,'实训中心鱼塘水面球机',NULL,NULL,'2026-07-20 00:17:41'),(171,'鱼塘实训中心后大门',NULL,NULL,'2026-07-20 00:17:41'),(172,'鱼塘实训中心过道1',NULL,NULL,'2026-07-20 00:17:41'),(173,'鱼塘实训中心过道2',NULL,NULL,'2026-07-20 00:17:41'),(174,'水产养殖实训中心',NULL,NULL,'2026-07-20 00:17:41'),(175,'水产养殖旁水面',NULL,NULL,'2026-07-20 00:17:41'),(176,'专家一号楼',NULL,NULL,'2026-07-20 00:17:41'),(177,'专家楼小广场',NULL,NULL,'2026-07-20 00:17:41'),(178,'专家楼旁道路',NULL,NULL,'2026-07-20 00:17:41'),(179,'河东岸观景台',NULL,NULL,'2026-07-20 00:17:41'),(180,'夏耕亭',NULL,NULL,'2026-07-20 00:17:41'),(181,'夏耕亭球机',NULL,NULL,'2026-07-20 00:17:41'),(182,'春雨亭',NULL,NULL,'2026-07-20 00:17:41'),(183,'雅思亭',NULL,NULL,'2026-07-20 00:17:41'),(184,'镜台',NULL,NULL,'2026-07-20 00:17:41'),(185,'雅思亭前',NULL,NULL,'2026-07-20 00:17:41'),(186,'人合台',NULL,NULL,'2026-07-20 00:17:41'),(187,'人合台岔路口',NULL,NULL,'2026-07-20 00:17:41'),(188,'网球篮球场旁',NULL,NULL,'2026-07-20 00:17:41'),(189,'篮球场1',NULL,NULL,'2026-07-20 00:17:41'),(190,'篮球场2',NULL,NULL,'2026-07-20 00:17:41'),(191,'篮球场3',NULL,NULL,'2026-07-20 00:17:41'),(192,'稻田大棚前',NULL,NULL,'2026-07-20 00:17:41'),(193,'农场新修道路至花庄河',NULL,NULL,'2026-07-20 00:17:41'),(194,'农牧场新修道路第一湾',NULL,NULL,'2026-07-20 00:17:41'),(195,'农牧场新修道路第二湾',NULL,NULL,'2026-07-20 00:17:41'),(196,'农牧场新修道路第三湾',NULL,NULL,'2026-07-20 00:17:41'),(197,'花庄河道路楼梯口',NULL,NULL,'2026-07-20 00:17:41'),(198,'花庄河新修道路1',NULL,NULL,'2026-07-20 00:17:41'),(199,'花庄河新修道路2',NULL,NULL,'2026-07-20 00:17:41'),(200,'花庄河新修道路3',NULL,NULL,'2026-07-20 00:17:41'),(201,'清真食堂后门',NULL,NULL,'2026-07-20 00:17:41'),(202,'检测中心门口',NULL,NULL,'2026-07-20 00:17:41'),(203,'检测中心药房1',NULL,NULL,'2026-07-20 00:17:41'),(204,'检测中心药房2',NULL,NULL,'2026-07-20 00:17:41'),(205,'新源小区大门外',NULL,NULL,'2026-07-20 00:17:41'),(206,'新源小区主道1',NULL,NULL,'2026-07-20 00:17:41'),(207,'新源小区主道2',NULL,NULL,'2026-07-20 00:17:41'),(208,'新源小区值班室',NULL,NULL,'2026-07-20 00:17:41'),(209,'新源小区停车场1',NULL,NULL,'2026-07-20 00:17:41'),(210,'新源小区停车场2',NULL,NULL,'2026-07-20 00:17:41'),(211,'新办公楼旁',NULL,NULL,'2026-07-20 00:17:41'),(212,'招待所楼顶',NULL,NULL,'2026-07-20 00:17:41'),(213,'原老办公楼旁1',NULL,NULL,'2026-07-20 00:17:41'),(214,'原老办公楼旁2',NULL,NULL,'2026-07-20 00:17:41'),(215,'招待所后路口',NULL,NULL,'2026-07-20 00:17:41'),(216,'原老办公楼旁通道',NULL,NULL,'2026-07-20 00:17:41'),(217,'菜市场门口左侧',NULL,NULL,'2026-07-20 00:17:41'),(218,'菜市场右侧房屋',NULL,NULL,'2026-07-20 00:17:41'),(219,'卫生所照青年商店',NULL,NULL,'2026-07-20 00:17:41'),(220,'菜市场门口',NULL,NULL,'2026-07-20 00:17:41'),(221,'种蓄场大门口',NULL,NULL,'2026-07-20 00:17:41'),(222,'老办公楼门口',NULL,NULL,'2026-07-20 00:17:41');
/*!40000 ALTER TABLE `monitor_points` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `repair_locations`
--

DROP TABLE IF EXISTS `repair_locations`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `repair_locations` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `name` varchar(200) COLLATE utf8mb4_unicode_ci NOT NULL COMMENT '点位名称',
  `address` varchar(300) COLLATE utf8mb4_unicode_ci DEFAULT NULL COMMENT '详细地址',
  `notes` text COLLATE utf8mb4_unicode_ci COMMENT '备注',
  `created_at` datetime DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (`id`),
  UNIQUE KEY `ix_repair_locations_name` (`name`)
) ENGINE=MyISAM DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `repair_locations`
--

LOCK TABLES `repair_locations` WRITE;
/*!40000 ALTER TABLE `repair_locations` DISABLE KEYS */;
/*!40000 ALTER TABLE `repair_locations` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `repair_photos`
--

DROP TABLE IF EXISTS `repair_photos`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `repair_photos` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `repair_id` int(11) NOT NULL,
  `phase` enum('before','during','after') COLLATE utf8mb4_unicode_ci NOT NULL COMMENT '维修阶段：before/during/after',
  `filename` varchar(255) COLLATE utf8mb4_unicode_ci NOT NULL COMMENT '存储文件名',
  `original_name` varchar(255) COLLATE utf8mb4_unicode_ci DEFAULT NULL COMMENT '原始文件名',
  `filepath` varchar(500) COLLATE utf8mb4_unicode_ci NOT NULL COMMENT '文件相对路径',
  `created_at` datetime DEFAULT CURRENT_TIMESTAMP,
  `thumb_filename` varchar(255) COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  PRIMARY KEY (`id`),
  KEY `repair_id` (`repair_id`),
  KEY `ix_repair_photos_id` (`id`)
) ENGINE=MyISAM AUTO_INCREMENT=8 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `repair_photos`
--

LOCK TABLES `repair_photos` WRITE;
/*!40000 ALTER TABLE `repair_photos` DISABLE KEYS */;
INSERT INTO `repair_photos` VALUES (2,2,'before','db899aab9d59494bbbfb326c799f106e.jpg','image.jpg','uploads\\db899aab9d59494bbbfb326c799f106e.jpg','2026-07-19 23:58:20','db899aab9d59494bbbfb326c799f106e_thumb.jpg'),(3,2,'before','cab9ebd4c4dc4779a0467b95c60c14da.jpg','image.jpg','uploads\\cab9ebd4c4dc4779a0467b95c60c14da.jpg','2026-07-19 23:58:27','cab9ebd4c4dc4779a0467b95c60c14da_thumb.jpg'),(4,2,'during','8a401c272dc549dcb5eb33a47e94d1a9.jpg','image.jpg','uploads\\8a401c272dc549dcb5eb33a47e94d1a9.jpg','2026-07-19 23:58:32','8a401c272dc549dcb5eb33a47e94d1a9_thumb.jpg'),(5,2,'during','56c0af59add044b8b0151888401ee208.jpg','image.jpg','uploads\\56c0af59add044b8b0151888401ee208.jpg','2026-07-19 23:58:37','56c0af59add044b8b0151888401ee208_thumb.jpg'),(6,2,'after','50838633048041779843fe0c41ca877e.jpg','image.jpg','uploads\\50838633048041779843fe0c41ca877e.jpg','2026-07-19 23:58:42','50838633048041779843fe0c41ca877e_thumb.jpg'),(7,2,'after','8fecac665261493d9655f8f8f8f68eb1.jpg','image.jpg','uploads\\8fecac665261493d9655f8f8f8f68eb1.jpg','2026-07-19 23:58:47','8fecac665261493d9655f8f8f8f68eb1_thumb.jpg');
/*!40000 ALTER TABLE `repair_photos` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `repair_records`
--

DROP TABLE IF EXISTS `repair_records`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `repair_records` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `record_no` varchar(50) COLLATE utf8mb4_unicode_ci NOT NULL COMMENT '工单编号，如 R20260719001',
  `repair_date` varchar(20) COLLATE utf8mb4_unicode_ci NOT NULL COMMENT '维修日期 YYYY-MM-DD',
  `location` varchar(200) COLLATE utf8mb4_unicode_ci NOT NULL COMMENT '维修点位',
  `description` text COLLATE utf8mb4_unicode_ci COMMENT '故障描述',
  `repair_content` text COLLATE utf8mb4_unicode_ci COMMENT '维修内容',
  `repairer` varchar(50) COLLATE utf8mb4_unicode_ci DEFAULT NULL COMMENT '维修人员',
  `status` enum('pending','in_progress','completed') COLLATE utf8mb4_unicode_ci DEFAULT NULL COMMENT '状态',
  `created_at` datetime DEFAULT CURRENT_TIMESTAMP,
  `updated_at` datetime DEFAULT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `record_no` (`record_no`),
  KEY `ix_repair_records_id` (`id`)
) ENGINE=MyISAM AUTO_INCREMENT=3 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `repair_records`
--

LOCK TABLES `repair_records` WRITE;
/*!40000 ALTER TABLE `repair_records` DISABLE KEYS */;
INSERT INTO `repair_records` VALUES (2,'R202607190001','2026-07-19','1','','','q','pending','2026-07-19 23:58:07',NULL);
/*!40000 ALTER TABLE `repair_records` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `users`
--

DROP TABLE IF EXISTS `users`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `users` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `username` varchar(50) COLLATE utf8mb4_unicode_ci NOT NULL COMMENT '用户名',
  `hashed_pw` varchar(200) COLLATE utf8mb4_unicode_ci NOT NULL COMMENT 'bcrypt 哈希密码',
  `full_name` varchar(50) COLLATE utf8mb4_unicode_ci DEFAULT NULL COMMENT '姓名',
  `role` varchar(20) COLLATE utf8mb4_unicode_ci DEFAULT NULL COMMENT 'admin=管理员 viewer=只读',
  `is_active` tinyint(1) DEFAULT NULL COMMENT '账号是否启用',
  `created_at` datetime DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (`id`),
  UNIQUE KEY `ix_users_username` (`username`),
  KEY `ix_users_id` (`id`)
) ENGINE=MyISAM AUTO_INCREMENT=2 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `users`
--

LOCK TABLES `users` WRITE;
/*!40000 ALTER TABLE `users` DISABLE KEYS */;
INSERT INTO `users` VALUES (1,'kuoci','$2b$12$7JBP8307LQoHkTl4anbtmuFi9fnCnNNwGGkSQrdVH7o8r8pQeQoTC','管理员','admin',1,'2026-07-19 23:38:27');
/*!40000 ALTER TABLE `users` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Dumping routines for database 'repair_db'
--
/*!40103 SET TIME_ZONE=@OLD_TIME_ZONE */;

/*!40101 SET SQL_MODE=@OLD_SQL_MODE */;
/*!40014 SET FOREIGN_KEY_CHECKS=@OLD_FOREIGN_KEY_CHECKS */;
/*!40014 SET UNIQUE_CHECKS=@OLD_UNIQUE_CHECKS */;
/*!40111 SET SQL_NOTES=@OLD_SQL_NOTES */;

-- Dump completed on 2026-07-20  0:37:00

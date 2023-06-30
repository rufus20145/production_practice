-- --------------------------------------------------------
-- Хост:                         127.0.0.1
-- Версия сервера:               8.0.33 - MySQL Community Server - GPL
-- Операционная система:         Win64
-- HeidiSQL Версия:              12.5.0.6677
-- --------------------------------------------------------

/*!40101 SET @OLD_CHARACTER_SET_CLIENT=@@CHARACTER_SET_CLIENT */;
/*!40101 SET NAMES utf8 */;
/*!50503 SET NAMES utf8mb4 */;
/*!40103 SET @OLD_TIME_ZONE=@@TIME_ZONE */;
/*!40103 SET TIME_ZONE='+00:00' */;
/*!40014 SET @OLD_FOREIGN_KEY_CHECKS=@@FOREIGN_KEY_CHECKS, FOREIGN_KEY_CHECKS=0 */;
/*!40101 SET @OLD_SQL_MODE=@@SQL_MODE, SQL_MODE='NO_AUTO_VALUE_ON_ZERO' */;
/*!40111 SET @OLD_SQL_NOTES=@@SQL_NOTES, SQL_NOTES=0 */;


-- Дамп структуры базы данных test_schema
CREATE DATABASE IF NOT EXISTS `test_schema` /*!40100 DEFAULT CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci */ /*!80016 DEFAULT ENCRYPTION='N' */;
USE `test_schema`;

-- Дамп структуры для таблица test_schema.test_table
CREATE TABLE IF NOT EXISTS `test_table` (
  `id` int unsigned NOT NULL,
  `record_id` int unsigned NOT NULL AUTO_INCREMENT,
  `foo` varchar(50) NOT NULL,
  `bar` varchar(50) NOT NULL,
  PRIMARY KEY (`record_id`)
) ENGINE=InnoDB AUTO_INCREMENT=4 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;

-- Дамп данных таблицы test_schema.test_table: ~3 rows (приблизительно)
INSERT INTO `test_table` (`id`, `record_id`, `foo`, `bar`) VALUES
	(1, 1, 'foo', 'bar'),
	(2, 2, 'fizz', 'buzz'),
	(2, 3, 'changed', 'buzz');

/*!40103 SET TIME_ZONE=IFNULL(@OLD_TIME_ZONE, 'system') */;
/*!40101 SET SQL_MODE=IFNULL(@OLD_SQL_MODE, '') */;
/*!40014 SET FOREIGN_KEY_CHECKS=IFNULL(@OLD_FOREIGN_KEY_CHECKS, 1) */;
/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40111 SET SQL_NOTES=IFNULL(@OLD_SQL_NOTES, 1) */;

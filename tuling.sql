/*
Navicat MySQL Data Transfer

Source Server         : localhost
Source Server Version : 50549
Source Host           : localhost:3306
Source Database       : python

Target Server Type    : MYSQL
Target Server Version : 50549
File Encoding         : 65001

Date: 2018-10-10 09:25:04
*/

SET FOREIGN_KEY_CHECKS=0;

-- ----------------------------
-- Table structure for `tuling`
-- ----------------------------
DROP TABLE IF EXISTS `tuling`;
CREATE TABLE `tuling` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `receive` text,
  `reply` text,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=10 DEFAULT CHARSET=utf8;

-- ----------------------------
-- Records of tuling
-- ----------------------------
INSERT INTO `tuling` VALUES ('1', '1', '4');
INSERT INTO `tuling` VALUES ('2', '2', '2');

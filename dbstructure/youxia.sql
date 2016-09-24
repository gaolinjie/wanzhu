/*
 Navicat Premium Data Transfer

 Source Server         : localhost
 Source Server Type    : MySQL
 Source Server Version : 50527
 Source Host           : localhost
 Source Database       : wanzhu

 Target Server Type    : MySQL
 Target Server Version : 50527
 File Encoding         : utf-8

 Date: 01/02/2014 18:26:36 PM
*/

SET NAMES utf8;
SET FOREIGN_KEY_CHECKS = 0;

-- ----------------------------
--  Table structure for `user`
-- ----------------------------
DROP TABLE IF EXISTS `user`;
CREATE TABLE `user` (
  `uid` int(11) NOT NULL AUTO_INCREMENT,
  `username` text,
  `password` text,
  `nickname` text,
  `name` text,
  `gender` text,
  `email` text,
  `mobile` text,
  `sign` text,
  `avatar` text,
  `intro` text,
  `followees` int(11) DEFAULT 0,
  `followers` int(11) DEFAULT 0,
  `questions` int(11) DEFAULT 0,
  `answers` int(11) DEFAULT 0,
  `posts` int(11) DEFAULT 0,
  `comments` int(11) DEFAULT 0,
  `up_num` int(11) DEFAULT 0,
  `down_num` int(11) DEFAULT 0,
  `thank_num` int(11) DEFAULT 0,
  `report_num` int(11) DEFAULT 0,
  `reputation` int(11) DEFAULT 0,
  `income` int(11) DEFAULT 2000,
  `expend` int(11) DEFAULT 0,
  `permission` int(11) DEFAULT 0,
  `created` datetime DEFAULT NULL,
  `updated` datetime DEFAULT NULL,
  `last_login` datetime DEFAULT NULL,
  `view_follow` datetime DEFAULT NULL,
  `admin` text,
  PRIMARY KEY (`uid`)
) ENGINE=MyISAM AUTO_INCREMENT=1 DEFAULT CHARSET=utf8;

-- ----------------------------
--  Table structure for `post`
-- ----------------------------
DROP TABLE IF EXISTS `post`;
CREATE TABLE `post` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `title` text,
  `content` text,
  `cover` text,
  `up_num` int(11) DEFAULT 0,
  `reply_num` int(11) DEFAULT 0,
  `view_num` int(11) DEFAULT 1,
  `follow_num` int(11) DEFAULT 0,
  `author_id` int(11) DEFAULT NULL,
  `is_video` int(11) DEFAULT 0,
  `video_time` int(11) DEFAULT NULL,
  `updated` datetime DEFAULT NULL,
  `created` datetime DEFAULT NULL,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=1 DEFAULT CHARSET=utf8;

-- ----------------------------
--  Table structure for `nowfeed`
-- ----------------------------
DROP TABLE IF EXISTS `nowfeed`;
CREATE TABLE `nowfeed` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `avatar` text,
  `name` text,
  `subname` text,
  `content` text,
  `image` text,
  `source` text,
  `link` text,
  `nowfeed_type` text,
  `video_time` text,
  `created` datetime DEFAULT NULL,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=1 DEFAULT CHARSET=utf8;

-- ----------------------------
--  Table structure for `newsfeed`
-- ----------------------------
DROP TABLE IF EXISTS `newsfeed`;
CREATE TABLE `newsfeed` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `title` text,
  `brief` text,
  `channel_name` text,
  `channel_img` text,
  `channel_link` text,
  `user_name` text,
  `user_img` text,
  `user_link` text,
  `post1_id` int(11) DEFAULT NULL,
  `post2_id` int(11) DEFAULT NULL,
  `post3_id` int(11) DEFAULT NULL,
  `layout_type` text,
  `created` datetime DEFAULT NULL,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=1 DEFAULT CHARSET=utf8;

-- ----------------------------
--  Table structure for `reply`
-- ----------------------------
DROP TABLE IF EXISTS `reply`;
CREATE TABLE `reply` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `reply_type` text,
  `obj_id` int(11) DEFAULT NULL,
  `content` text,
  `up_num` int(11) DEFAULT 0,
  `down_num` int(11) DEFAULT 0,
  `author_id` int(11) DEFAULT NULL,
  `reply_to` int(11) DEFAULT NULL,
  `created` datetime DEFAULT NULL,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=1 DEFAULT CHARSET=utf8;

-- ----------------------------
--  Table structure for `tag`
-- ----------------------------
DROP TABLE IF EXISTS `tag`;
CREATE TABLE `tag` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `name` text,
  `thumb` text,
  `cover` text,
  `intro` text,
  `tag_type` text,
  `post_num` int(11) DEFAULT 0,
  `follow_num` int(11) DEFAULT 0,
  `created` datetime DEFAULT NULL,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=1 DEFAULT CHARSET=utf8;

-- ----------------------------
--  Table structure for `post_tag`
-- ----------------------------
DROP TABLE IF EXISTS `post_tag`;
CREATE TABLE `post_tag` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `post_id` int(11) DEFAULT NULL,
  `tag_id` int(11) DEFAULT NULL,
  `created` datetime DEFAULT NULL,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=1 DEFAULT CHARSET=utf8;

-- ----------------------------
--  Table structure for `car_data`
-- ----------------------------
DROP TABLE IF EXISTS `car_data`;
CREATE TABLE `car_data` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `data_type` text,
  `car_size` text,
  `car_sort` text,
  `name` text,
  `pinyin` text,
  `english` text,
  `thumb` text,
  `cover` text,
  `tag_id` int(11) DEFAULT NULL,
  `order_num` text,
  `brand_id` int(11) DEFAULT NULL,
  `brand_name` text,
  `vender_id` int(11) DEFAULT NULL,
  `vender_name` text,
  `fgcolor` text,
  `bgcolor` text,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=1 DEFAULT CHARSET=utf8;
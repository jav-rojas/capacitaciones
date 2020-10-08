-- Selección de db a utilizar
USE capacitaciones;

-- Borramos tablas 
DROP TABLE UsernameTraining;
DROP TABLE Username;
DROP TABLE TrainingQuestion;
DROP TABLE TrainingVideo;
DROP TABLE Training;

-- Creación de tables utilizadas en Web de Capacitaciones

-- ************************************** `Username`

CREATE TABLE `Username`
(
 `id`         integer NOT NULL AUTO_INCREMENT ,
 `username`   varchar(45) NOT NULL ,
 `password`   varchar(16) NOT NULL ,
 `first_name` varchar(100) NULL ,
 `last_name`  varchar(100) NULL ,
 `email`      varchar(255) NULL ,
 `created_at` datetime NOT NULL ,
 `updated_at` datetime NOT NULL ,

PRIMARY KEY (`id`)
) ENGINE=INNODB;



-- ************************************** `Training`

-- ************************************** `Training`

CREATE TABLE `Training`
(
 `id`         integer NOT NULL AUTO_INCREMENT ,
 `key_name`   varchar(45) NOT NULL ,
 `name`       varchar(100) NOT NULL ,
 `title`      text NOT NULL ,
 `text1`      text NULL ,
 `text2`      text NULL ,
 `text3`      text NULL ,
 `created_at` datetime NOT NULL ,
 `updated_at` datetime NOT NULL ,

PRIMARY KEY (`id`)
) ENGINE=INNODB;

-- ************************************** `UsernameTraining`

CREATE TABLE `UsernameTraining`
(
 `username_id` integer NOT NULL ,
 `training_id` integer NOT NULL ,

PRIMARY KEY (`username_id`, `training_id`),
KEY `fkIdx_79` (`username_id`),
CONSTRAINT `FK_79` FOREIGN KEY `fkIdx_79` (`username_id`) REFERENCES `Username` (`id`) ON DELETE CASCADE ON UPDATE CASCADE,
KEY `fkIdx_85` (`training_id`),
CONSTRAINT `FK_85` FOREIGN KEY `fkIdx_85` (`training_id`) REFERENCES `Training` (`id`) ON DELETE CASCADE ON UPDATE CASCADE
) ENGINE=INNODB;

-- ************************************** `TrainingVideo`

CREATE TABLE `TrainingVideo`
(
 `id`          integer NOT NULL AUTO_INCREMENT ,
 `training_id` integer NOT NULL ,
 `title`       text NOT NULL ,
 `link`        text NOT NULL ,
 `orden`       int NOT NULL ,
 `text1`       text NULL ,
 `text2`       text NULL ,
 `created_at`  datetime NOT NULL ,
 `updated_at`  datetime NOT NULL ,

PRIMARY KEY (`id`, `training_id`),
KEY `fkIdx_93` (`training_id`),
CONSTRAINT `FK_93` FOREIGN KEY `fkIdx_93` (`training_id`) REFERENCES `Training` (`id`) ON DELETE CASCADE ON UPDATE CASCADE
) ENGINE=INNODB;

-- ************************************** `TrainingQuestion`

CREATE TABLE `TrainingQuestion`
(
 `id`               integer NOT NULL AUTO_INCREMENT ,
 `training_id`      integer NOT NULL ,
 `trainingvideo_id` integer NOT NULL ,
 `type`             text NOT NULL ,
 `title`            text NOT NULL ,
 `choice1`          text NULL ,
 `choice2`          text NULL ,
 `choice3`          text NULL ,
 `choice4`          text NULL ,
 `created_at`       datetime NOT NULL ,
 `updated_at`       datetime NOT NULL ,

PRIMARY KEY (`id`, `training_id`, `trainingvideo_id`),
KEY `fkIdx_68` (`trainingvideo_id`, `training_id`),
CONSTRAINT `FK_68` FOREIGN KEY `fkIdx_68` (`trainingvideo_id`, `training_id`) REFERENCES `TrainingVideo` (`id`, `training_id`) ON DELETE CASCADE ON UPDATE CASCADE
) ENGINE=INNODB;


-- Ingresamos valores iniciales

INSERT INTO Username (username,password,first_name,last_name,email,created_at,updated_at) VALUES ("admin","Microdatos2020","Javier","Rojas","jrojasc@fen.uchile.cl",now()- INTERVAL 3 HOUR,now()- INTERVAL 3 HOUR);
INSERT INTO Training (name,title,created_at,updated_at) VALUES ("default","-- Seleccione un proyecto --",now()- INTERVAL 3 HOUR,now()- INTERVAL 3 HOUR);

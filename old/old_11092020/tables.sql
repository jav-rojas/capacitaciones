USE capacitaciones;

DROP TABLE users_info;
DROP TABLE users_login;

CREATE TABLE users_login (
    username varchar(16) NOT NULL PRIMARY KEY,
    password varchar(16) NOT NULL
) ENGINE = InnoDB;

CREATE TABLE users_info (
	username varchar(16) NOT NULL,
    nombre varchar(35),
    apellido varchar(35),
    email varchar(255),
    creation_date datetime,
    last_access_date datetime,
    FOREIGN KEY (username) REFERENCES users_login(username) ON DELETE CASCADE ON UPDATE CASCADE
) ENGINE = InnoDB;

INSERT INTO users_login VALUES ("admin","Microdatos2020");
INSERT INTO users_info VALUES ("admin","Javier","Rojas","jrojasc@fen.uchile.cl",now()- INTERVAL 3 HOUR,now()- INTERVAL 3 HOUR);

CREATE TABLE capacitaciones (
  id_cap varchar(10) NOT NULL PRIMARY KEY,
  cap_name varchar(10),
  title varchar(50),
  text_1 text,
  text_2 text,
  text_3 text
) ENGINE = InnoDB;

CREATE TABLE capacitaciones_videos (
  id_cap varchar(10) NOT NULL,
  id_video tinyint(127) NOT NULL,
  link text,
  PRIMARY KEY(id_cap, id_video),
  FOREIGN KEY (id_cap) REFERENCES capacitaciones(id_cap) ON DELETE CASCADE ON UPDATE CASCADE,
) ENGINE = InnoDB;

CREATE TABLE capacitaciones_cuestionario (
  id_cap varchar(10) NOT NULL,
  id_video tinyint(127) NOT NULL,
  id_pregunta tinyint(127) NOT NULL,
  tipo_pregunta text,
  titulo_pregunta text,
  opcion_1 text,
  opcion_2 text,
  opcion_3 text,
  PRIMARY KEY(id_cap, id_video, id_pregunta),
  FOREIGN KEY (id_cap, id_video) REFERENCES capacitaciones_videos(id_cap, id_video) ON DELETE CASCADE ON UPDATE CASCADE
) ENGINE = InnoDB;

INSERT INTO capacitaciones (id_cap, cap_name) VALUES ("default","-- Seleccione un proyecto --")

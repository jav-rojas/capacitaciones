USE capacitaciones;

CREATE TABLE users_table (
    username varchar(16) NOT NULL PRIMARY KEY,
    password varchar(16) NOT NULL
);

CREATE TABLE users_info (
	username varchar(16) NOT NULL,
    nombre varchar(35),
    apellido varchar(35),
    email varchar(255),
    creation_date datetime,
    last_access_date datetime,
    FOREIGN KEY (username) REFERENCES users_table(username) ON DELETE CASCADE ON UPDATE CASCADE
);

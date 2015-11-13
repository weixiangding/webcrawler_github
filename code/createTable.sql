DROP TABLE IF EXISTS `Movie`;

CREATE TABLE Movie( 
   movie_id INT(11) NOT NULL AUTO_INCREMENT,
   actor_id INT(11),
   link VARCHAR(30) NOT NULL,
   PRIMARY KEY (movie_id)
);

DROP TABLE IF EXISTS `Actor`;

CREATE TABLE Actor( 
   actor_id INT(11) NOT NULL AUTO_INCREMENT,
   link VARCHAR(100) NOT NULL,
   location VARCHAR(25),
   birthday VARCHAR(15),
   birthyear VARCHAR(10),
   PRIMARY KEY (actor_id)
);

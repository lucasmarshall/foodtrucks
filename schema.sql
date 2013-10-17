DROP TABLE IF EXISTS foodtrucks;
CREATE TABLE foodtrucks (
  id integer primary key autoincrement,
  title text not null,
  text text not null
);
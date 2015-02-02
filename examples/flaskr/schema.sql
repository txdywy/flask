drop table if exists entries;
create table entries (
  id integer primary key autoincrement,
  title text not null,
  'text' text not null
);

create table users (
  id integer primary key autoincrement,
  email text not null,
  password text not null,
  name text,
  icon text
);

create table projects (
  id integer primary key autoincrement,
  name text not null,
  image text,
  url text
);
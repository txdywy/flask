drop table if exists user;
create table user (
  user_id integer primary key autoincrement,
  username text not null,
  email text not null,
  pw_hash text not null,
  school text,
  city text,
  country text,
  zipcode text,
  phone text
);

drop table if exists follower;
create table follower (
  who_id integer,
  whom_id integer
);

drop table if exists message;
create table message (
  message_id integer primary key autoincrement,
  author_id integer not null,
  text text not null,
  pub_date integer
);

drop table if exists project;
create table project (
  title text not null,
  description text,
  client text not null,
  image_url text,
  create_time text not null
);


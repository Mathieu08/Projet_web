create table article (
  id integer primary key,
  titre varchar(100),
  identifiant varchar(50),
  auteur varchar(100),
  date_publication text,
  paragraphe varchar(500)
);

create table users (
  id integer primary key,
  utilisateur varchar(25),
  email varchar(100),
  salt varchar(32),
  hash varchar(128)
);

create table sessions (
  id integer primary key,
  id_session varchar(32),
  utilisateur varchar(25)
);

create table tokens (
  id integer primary key,
  email varchar(100),
  id_token varchar(32)
);

insert into users(utilisateur, salt, hash) values ('correcteur', 'a543e48bea4c4cc3baca51964fcb9755', '47b328286df4c0d81e5e1c46685070cc86f89c3c14c5c710bc33a58c204e5670ee1f491e3282f5efdc4acef7b23172585aa9452882730c9d493960ecf0291938');
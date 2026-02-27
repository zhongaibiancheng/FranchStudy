-- 数据库创建脚本
CREATE USER franchuser WITH PASSWORD 'franchpass';
drop database franchdb;
CREATE DATABASE franchdb OWNER franchuser;
GRANT ALL PRIVILEGES ON DATABASE franchdb TO franchuser;

-- 表: users

CREATE TABLE "users" (
	id SERIAL NOT NULL, 
	username VARCHAR(80) NOT NULL, 
	email VARCHAR(120) NOT NULL, 
	password_hash VARCHAR(1024) NOT NULL, 
	is_admin BOOLEAN, 
	created_at TIMESTAMP WITH TIME ZONE, 
	PRIMARY KEY (id), 
	UNIQUE (username), 
	UNIQUE (email)
);

-- 授予表权限
GRANT SELECT, INSERT, UPDATE, DELETE ON users TO franchuser;

-- 授予序列权限（如果使用 SERIAL 或 IDENTITY）
GRANT USAGE, SELECT ON SEQUENCE users_id_seq TO franchuser;

-- 授予表所在 schema 的权限
GRANT USAGE ON SCHEMA public TO franchuser;

-- 如果还需要其他表的权限
GRANT SELECT, INSERT, UPDATE, DELETE ON ALL TABLES IN SCHEMA public TO franchuser;
GRANT USAGE, SELECT ON ALL SEQUENCES IN SCHEMA public TO franchuser;

--words
CREATE TABLE "words" (
	id SERIAL NOT NULL, 
	book integer not null,
	lesson integer not null,
	french VARCHAR(128) NOT NULL, 
	chinese VARCHAR(128) NOT NULL, 
	part_of_speech VARCHAR(128) NOT NULL, 
	part_of_speech_full_chinese VARCHAR(128) NOT NULL, 
	PRIMARY KEY (id)
);

-- 授予表权限
GRANT SELECT, INSERT, UPDATE, DELETE ON words TO franchuser;

-- 授予序列权限（如果使用 SERIAL 或 IDENTITY）
GRANT USAGE, SELECT ON SEQUENCE words_id_seq TO franchuser;

-- 授予表所在 schema 的权限
GRANT USAGE ON SCHEMA public TO franchuser;

-- 如果还需要其他表的权限
GRANT SELECT, INSERT, UPDATE, DELETE ON ALL TABLES IN SCHEMA public TO franchuser;
GRANT USAGE, SELECT ON ALL SEQUENCES IN SCHEMA public TO franchuser;

--exercise_words
drop table if exists exercise_words;
CREATE TABLE "exercise_words" (
	id SERIAL NOT NULL, 
	word_id integer not null,
	user_id integer not null,
	result integer not null default 0, -- 0:wrong 1:right
	finished boolean not null default false,
	created_at TIMESTAMP WITH TIME ZONE,
	PRIMARY KEY (id)
);

-- 授予表权限
GRANT SELECT, INSERT, UPDATE, DELETE ON exercise_words TO franchuser;

-- 授予序列权限（如果使用 SERIAL 或 IDENTITY）
GRANT USAGE, SELECT ON SEQUENCE exercise_words_id_seq TO franchuser;

-- 授予表所在 schema 的权限
GRANT USAGE ON SCHEMA public TO franchuser;

-- 如果还需要其他表的权限
GRANT SELECT, INSERT, UPDATE, DELETE ON ALL TABLES IN SCHEMA public TO franchuser;
GRANT USAGE, SELECT ON ALL SEQUENCES IN SCHEMA public TO franchuser;

--mistake_notebook
CREATE TABLE "mistake_notebook"(
	id SERIAL NOT NULL,
	word_id integer not null,
	user_id integer not null,
	wrong_count integer not null default 1,
	right_count integer not null default 0,
	created_at TIMESTAMP WITH TIME ZONE default now(),
	PRIMARY KEY (id)
);

-- 授予表权限
GRANT SELECT, INSERT, UPDATE, DELETE ON mistake_notebook TO franchuser;

-- 授予序列权限（如果使用 SERIAL 或 IDENTITY）
GRANT USAGE, SELECT ON SEQUENCE mistake_notebook_id_seq TO franchuser;

-- 授予表所在 schema 的权限
GRANT USAGE ON SCHEMA public TO franchuser;

-- 如果还需要其他表的权限
GRANT SELECT, INSERT, UPDATE, DELETE ON ALL TABLES IN SCHEMA public TO franchuser;
GRANT USAGE, SELECT ON ALL SEQUENCES IN SCHEMA public TO franchuser;

-- 数据库创建脚本
CREATE USER franchuser WITH PASSWORD 'franchpass';
CREATE DATABASE franchdb OWNER franchuser;
GRANT ALL PRIVILEGES ON DATABASE franchdb TO franchuser;

-- 表: user

CREATE TABLE "user" (
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
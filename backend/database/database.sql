-- 数据库创建脚本
CREATE USER franchuser WITH PASSWORD 'franchpass';
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
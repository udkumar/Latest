DROP DATABASE IF EXISTS MAIIC_DB1;
CREATE DATABASE MAIIC_DB1;


CREATE TABLE roles (
	role_id BIGSERIAL PRIMARY KEY,
	role_name TEXT UNIQUE NOT NULL
);
INSERT INTO roles (role_name) VALUES ('student'),('faculty'),('admin');

CREATE TABLE users (
	u_id BIGSERIAL PRIMARY KEY, 
	public_id TEXT UNIQUE NOT NULL,
	user_id TEXT UNIQUE NOT NULL,
	email TEXT UNIQUE NOT NULL,
	alternet_email TEXT,
	password TEXT NOT NULL,
	first_name TEXT NOT NULL,
	last_name TEXT NOT NULL,
	mobile_number TEXT NOT NULL,
	city TEXT NOT NULL,
	class_standard TEXT NOT NULL,
	subject TEXT NOT NULL,
	edu_board  TEXT NOT NULL,
	payment_status BOOLEAN DEFAULT FALSE,

	role_id BIGINT REFERENCES roles(role_id) NOT NULL,
	created_at timestamp with time zone DEFAULT CURRENT_TIMESTAMP(2), 
	updated_at timestamp with time zone DEFAULT CURRENT_TIMESTAMP(2) 
);

-- alter table users add column verification_code TEXT;
-- alter table users add column email_verified BOOLEAN DEFAULT FALSE;


CREATE TABLE videos (
	id BIGSERIAL PRIMARY KEY, 
	u_id BIGINT REFERENCES users(u_id) NOT NULL,
	file_path TEXT,
	file_type TEXT,
	class_standard TEXT NOT NULL,
	subject TEXT NOT NULL,
	chapter TEXT NOT NULL,
	video_status TEXT NOT NULL DEFAULT 'draft',
	video_url TEXT,

	created_at timestamp with time zone DEFAULT CURRENT_TIMESTAMP(2), 
	updated_at timestamp with time zone DEFAULT CURRENT_TIMESTAMP(2) 
);

-- 2008-08-15, jsled: add "group" column to Adjunct table
ALTER TABLE app_adjunct ADD "group" varchar(30) NOT NULL DEFAULT "";

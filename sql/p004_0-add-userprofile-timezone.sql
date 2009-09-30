-- 2009-09-27, jsled: add timezone to app_userprofile
ALTER TABLE app_userprofile ADD "timezone" varchar(100) NOT NULL DEFAULT "UTC";



-- 2012-05-25, jsled.  After picking brew-journal sources back up after a
-- long time, and updating python or south or something, I realized that
-- previous south migrations with '-'s in their names were not being
-- processed anymore.  They're probably being treated as python modules,
-- which of course can't have '-' in their names.  Normalize the already-used
-- names with the renamed git repository contents on existing (eg.,
-- brew-journal.com) DBs by using:

UPDATE south_migrationhistory SET migration = replace(migration, '-', '_');
UPDATE south_migrationhistory SET migration = replace(migration, ' ', '_');
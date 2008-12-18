-- 2008-12-17, jsled: resize some volume Decimal types.

-- Run this script, then syncdb to get the correct tables, then run p003_1-increase-volume-size-copy.sql

BEGIN TRANSACTION;

ALTER TABLE app_recipe RENAME TO app_recipe_save;
DROP INDEX app_recipe_author_id;
DROP INDEX app_recipe_derived_from_recipe_id;
DROP INDEX app_recipe_style_id;

ALTER TABLE app_step RENAME TO app_step_save;
DROP INDEX app_step_brew_id;

COMMIT;

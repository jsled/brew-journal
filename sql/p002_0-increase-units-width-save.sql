-- 2008-12-17, jsled: change the range of units from 2 chars to 4 to admit 'tsp' and 'tbsp'.
-- Run this script, then syncdb to get the correct tables, then run p002-increase-units-width-copy.sql.

BEGIN TRANSACTION;

ALTER TABLE app_recipe RENAME TO app_recipe_save;
DROP INDEX app_recipe_author_id;
DROP INDEX app_recipe_derived_from_recipe_id;
DROP INDEX app_recipe_style_id;

ALTER TABLE app_recipeadjunct RENAME TO app_recipeadjunct_save;
DROP INDEX "app_recipeadjunct_adjunct_id";
DROP INDEX "app_recipeadjunct_recipe_id";

ALTER TABLE app_step RENAME TO app_step_save;
DROP INDEX app_step_brew_id;

COMMIT;

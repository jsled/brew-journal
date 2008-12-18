-- 2008-12-17, jsled: copy data.

BEGIN TRANSACTION;

INSERT INTO app_recipe (id, author_id, name, insert_date, batch_size, batch_size_units, style_id, derived_from_recipe_id, type, source_url, notes)
SELECT id, author_id, name, insert_date, batch_size, batch_size_units, style_id, derived_from_recipe_id, type, source_url, notes
FROM app_recipe_save;

INSERT INTO app_recipeadjunct (id, recipe_id, adjunct_id, amount_value, amount_units, boil_time, notes)
SELECT id, recipe_id, adjunct_id, amount_value, amount_units, boil_time, notes
FROM app_recipeadjunct_save;

INSERT INTO app_step (id, brew_id, type, date, entry_date, volume, volume_units, temp, temp_units, gravity_read, gravity_read_temp, gravity_read_temp_units, notes)
SELECT id, brew_id, type, date, entry_date, volume, volume_units, temp, temp_units, gravity_read, gravity_read_temp, gravity_read_temp_units, notes
FROM app_step_save;

DROP TABLE app_recipe_save;
DROP TABLE app_recipeadjunct_save;
DROP TABLE app_step_save;

COMMIT;

-- 2008-07-12, jsled: fix tyop
UPDATE app_step SET type = 'vorlauf' WHERE type = 'vourlauf';
UPDATE app_brew SET last_state = 'vorlauf' WHERE last_state = 'vourlauf';

-- 1/ correct existing names in app_hops
-- 2/ load sourced/combined data
-- 3/ copy combined entires into app_hops
-- 4/ load sources substitutions -> app_hops
-- 5/ create combined substitutions in app_hops

-- 1/ correct existing names in app_hops
update app_hop set name = 'Admiral' where name = 'Admiral (UK)';
update app_hop set name = 'Bramling Cross' where name like 'Bramling Cross%';
update app_hop set name = 'Brewers\'s Gold (UK)' where name like 'Brewer\'s Gold (DE)';
update app_hop set name = 'Challenger' where name like 'Challenger%';
update app_hop set name = 'Columbus/Tomahawk/Zeus' where name like 'Columbus';
update app_hop set name = 'First Gold' where name like 'First Gold%';
update app_hop set name = 'Green Bullet' where name like 'Green Bullet%';
update app_hop set name = 'Hallertau (US)' where name = 'Hallertauer (US)';
update app_hop set name = 'Hallertau Gold' where name = 'Hallertauer Gold';
update app_hop set name = 'Hallertau Mittelfrüh (DE)' where name = 'Hallertauer Mittelfrüh';
update app_hop set name = 'Hallertau Tradition (DE)' where name = 'Hallertauer Tradition (DE)';
update app_hop set name = 'Hallertau Hersbrucker (DE)' where name = 'Hersbrucker (DE)';
update app_hop set name = 'East Kent Golding' where name like = 'Kent Golding%';
update app_hop set name = 'Magnum (US)' where name = 'Magnum';
update app_hop set name = 'Mount Hood' where name = 'Mt. Hood';
update app_hop set name = 'Nelson Sauvin' where name like 'Nelson Sauvin%';
update app_hop set name = 'Northdown' where name like 'Northdown%';
delete from app_hop where name = 'Northwest Golding';
update app_hop set name = 'Pacific Gem' where name like 'Pacific Gem%';
update app_hop set name = 'Phoenix' where name like 'Phoenix%';
update app_hop set name = 'Pioneer' where name like 'Pioneer%';
update app_hop set name = 'Lublin/Lubelski' where name = 'Polish Lublin';
update app_hop set name = 'Pride of Ringwood' where name like 'Pride of%';
update app_hop set name = 'Progress' where name like 'Progress%';
update app_hop set name = 'Saphir' where name like 'Saphir%';
update app_hop set name = 'Sorachi Ace' where name like 'Sorachi Ace%';
update app_hop set name = 'Spalt Select' where name like 'Spalt Select%';
update app_hop set name = 'Target' where name like 'Target%';
update app_hop set name = 'Tettnang (US)' where name = 'Tettnanger (US)';
update app_hop set name = 'Tettnang (DE)' where name = 'Tettnanger (DE)';

update app_recipehop
    set hop_id = (select id from app_hop where name = 'Columbus/Tomahawk/Zeus')
    where hop_id in (select id from app_hop where name in ('Tomahawk', 'Zeus'));
delete from app_hop where name in ('Tomahawk', 'Zeus');

update app_hop set name = 'Tradition' where name like 'Tradition%';
update app_hop set name = 'Whitbread Goldings Variety' where name like 'Whitbread%';


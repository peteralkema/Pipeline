-- 0002: speaking_rate + category_id on project (31 Jul fix-commit).
-- speaking_rate: channel.json's rate finally travels (teaser drift receipt).
-- category_id: upload category as project data (the 24-vs-27 sore, ended).
ALTER TABLE project ADD COLUMN speaking_rate REAL NOT NULL DEFAULT 1.0;
ALTER TABLE project ADD COLUMN category_id TEXT;

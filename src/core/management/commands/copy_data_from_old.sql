ATTACH DATABASE 'default_old.sqlite3' AS old;

INSERT INTO core_seiyuu
(
    id,
    name,
    screen_name,
    id_name,
    activated,
    interval,
    image_folder,
    hidden
)
SELECT
    id,
    name,
    screen_name,
    id_name,
    activated,
    interval,
    image_folder,
    hidden
FROM old.bot_seiyuu;

INSERT INTO core_media
(
    id,
    file_path,
    file_type,
    weight,
    seiyuu_id
)
SELECT
    id,
    file,
    file_type,
    weight,
    seiyuu_id
FROM old.bot_media;

UPDATE core_media
SET file_path = REPLACE(file_path, 'data/media/Library/', '')
WHERE file_path LIKE 'data/media/Library/%';

INSERT INTO core_tweet
(
    id,
    post_time,
    data_time,
    like,
    rt,
    reply,
    quote,
    media_id
)
SELECT
    id,
    post_time,
    data_time,
    like,
    rt,
    reply,
    quote,
    media_id
FROM old.bot_tweet;

INSERT INTO core_followers
(
    data_time,
    followers,
    seiyuu_id
)
SELECT
    data_time,
    followers,
    seiyuu_id
FROM old.bot_followers;
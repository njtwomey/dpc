-- comments for challenge 3676
PRAGMA foreign_keys=OFF;
BEGIN TRANSACTION;
INSERT INTO comments ("id", "image_id", "commenter_id", "raw_comment", "comment", "date", "edited", "made_during_challenge") VALUES
(7759674, 1284820, 141319, '<td valign="top">Stunning image, but I don''t get the time capsule.</td>', 'Stunning image, but I don''t get the time capsule.', '2023-11-05 14:09:04.000000', NULL, 1),
(7759720, 1284926, 42733, '<td valign="top">My favorite in this challenge.</td>', 'My favorite in this challenge.', '2023-11-07 08:24:19.000000', NULL, 1),
(7759721, 1284820, 42733, '<td valign="top">My pick for red in this challenge.</td>', 'My pick for red in this challenge.', '2023-11-07 08:24:30.000000', NULL, 1),
(7759722, 1284929, 42733, '<td valign="top">My pick for yellow in this challenge.</td>', 'My pick for yellow in this challenge.', '2023-11-07 08:24:58.000000', NULL, 1),
(7759854, 1284926, 97225, '<td valign="top">My pick for blue. Great shot.</td>', 'My pick for blue. Great shot.', '2023-11-09 23:09:45.000000', NULL, 1),
(7759864, 1284926, 141319, '<td valign="top">Brilliant, congratulations.</td>', 'Brilliant, congratulations.', '2023-11-10 11:52:33.000000', NULL, 0);
COMMIT;

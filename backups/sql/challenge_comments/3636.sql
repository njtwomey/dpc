-- comments for challenge 3636
PRAGMA foreign_keys=OFF;
BEGIN TRANSACTION;
INSERT INTO comments ("id", "image_id", "commenter_id", "raw_comment", "comment", "date", "edited", "made_during_challenge") VALUES
(7756530, 1283327, 50864, '<td valign="top">I love this. The blurriness of the person makes it look like he is falling forward from exhaustion. Great colors and composition.</td>', 'I love this. The blurriness of the person makes it look like he is falling forward from exhaustion. Great colors and composition.', '2023-08-16 21:33:15.000000', NULL, 1),
(7756752, 1283442, 42733, '<td valign="top">My favorite in this challenge.</td>', 'My favorite in this challenge.', '2023-08-22 14:45:41.000000', NULL, 1),
(7756753, 1283440, 42733, '<td valign="top">My pick for red in this challenge.</td>', 'My pick for red in this challenge.', '2023-08-22 14:45:53.000000', NULL, 1),
(7756770, 1283420, 68504, '<td valign="top">well, shoot, this is a hoot.</td>', 'well, shoot, this is a hoot.', '2023-08-23 00:17:55.000000', NULL, 1),
(7756771, 1283327, 68504, '<td valign="top">will he make it to one of those seats?</td>', 'will he make it to one of those seats?', '2023-08-23 00:18:54.000000', NULL, 1),
(7756772, 1283432, 68504, '<td valign="top">the unbearable weakness of being.</td>', 'the unbearable weakness of being.', '2023-08-23 00:20:13.000000', NULL, 1),
(7756775, 1283432, 50695, '<td valign="top">didn''t comment but i did give you a 10. best in the challenge.</td>', 'didn''t comment but i did give you a 10. best in the challenge.', '2023-08-23 12:06:48.000000', NULL, 0),
(7756776, 1283327, 50695, '<td valign="top">strategic blur, well done</td>', 'strategic blur, well done', '2023-08-23 12:07:17.000000', NULL, 0),
(7756789, 1283442, 103142, '<td valign="top">Congrats, kiddo! Well done!</td>', 'Congrats, kiddo! Well done!', '2023-08-23 23:19:51.000000', NULL, 0),
(7757017, 1283441, 28742, '<td valign="top">Congrats on the ribbon! Although she doesn''t look weak. ;-)</td>', 'Congrats on the ribbon! Although she doesn''t look weak. ;-)', '2023-08-30 02:14:50.000000', NULL, 0);
COMMIT;

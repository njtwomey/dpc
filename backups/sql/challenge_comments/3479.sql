-- comments for challenge 3479
PRAGMA foreign_keys=OFF;
BEGIN TRANSACTION;
INSERT INTO comments ("id", "image_id", "commenter_id", "raw_comment", "comment", "date", "edited", "made_during_challenge") VALUES
(7731045, 1273573, 42733, '<td valign="top">My favorite in this challenge.</td>', 'My favorite in this challenge.', '2022-10-12 11:08:27.000000', NULL, 1),
(7731046, 1273444, 42733, '<td valign="top">In my top three for this challenge.</td>', 'In my top three for this challenge.', '2022-10-12 11:08:38.000000', NULL, 1),
(7731047, 1273474, 42733, '<td valign="top">In my top three for this challenge.</td>', 'In my top three for this challenge.', '2022-10-12 11:08:52.000000', NULL, 1),
(7731080, 1273588, 113411, '<td valign="top">wow@ Very cool processing..really works!</td>', 'wow@ Very cool processing..really works!', '2022-10-12 22:09:03.000000', NULL, 1),
(7731081, 1273564, 113411, '<td valign="top">wonderful shot!</td>', 'wonderful shot!', '2022-10-12 22:09:55.000000', NULL, 1),
(7731121, 1273564, 68504, '<td valign="top">the sea!</td>', 'the sea!', '2022-10-14 01:50:03.000000', NULL, 0),
(7731131, 1273444, 122678, '<td valign="top">Congratulations <br/>your image is beautiful.</td>', 'Congratulations your image is beautiful.', '2022-10-14 12:32:42.000000', NULL, 0),
(7731132, 1273572, 122678, '<td valign="top">Congrats<br/>Very nice image, nice lighting.</td>', 'CongratsVery nice image, nice lighting.', '2022-10-14 12:35:21.000000', NULL, 0),
(7731159, 1273581, 67145, '<td valign="top">WOW .. what a glorious place you live .. well your photo makes it so .. its very ordered and neat .. <br/>i do like a bit of mayhem myself .. lol .. <br/>anyway .. congratulations on the ribbon .. <br/>btw .. i believe we are all almost home .. but dont know it .. xx</td>', 'WOW .. what a glorious place you live .. well your photo makes it so .. its very ordered and neat .. i do like a bit of mayhem myself .. lol .. anyway .. congratulations on the ribbon .. btw .. i believe we are all almost home .. but dont know it .. xx', '2022-10-15 01:13:44.000000', NULL, 0),
(7731337, 1273517, 122678, '<td valign="top">This is a truly beautiful image that meets the challenge and beyond, Congrats</td>', 'This is a truly beautiful image that meets the challenge and beyond, Congrats', '2022-10-19 20:26:44.000000', NULL, 0),
(7731338, 1273517, 122678, '<td valign="top">Best in show</td>', 'Best in show', '2022-10-19 20:27:31.000000', NULL, 0);
COMMIT;

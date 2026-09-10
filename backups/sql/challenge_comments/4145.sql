-- comments for challenge 4145
PRAGMA foreign_keys=OFF;
BEGIN TRANSACTION;
INSERT INTO comments ("id", "image_id", "commenter_id", "raw_comment", "comment", "date", "edited", "made_during_challenge") VALUES
(7819520, 1307058, 99263, '<td valign="top">
Lovely well composed vista</td>', 'Lovely well composed vista', '2026-06-01 06:24:36.000000', NULL, 1),
(7819521, 1306955, 99263, '<td valign="top">
Pleasant well composed scene</td>', 'Pleasant well composed scene', '2026-06-01 06:25:05.000000', NULL, 1),
(7819522, 1307112, 99263, '<td valign="top">
Pleasant backlit scene</td>', 'Pleasant backlit scene', '2026-06-01 06:25:54.000000', NULL, 1),
(7819523, 1307179, 99263, '<td valign="top">
Nice soft edit of a peaceful scene</td>', 'Nice soft edit of a peaceful scene', '2026-06-01 06:26:29.000000', NULL, 1),
(7819524, 1307174, 99263, '<td valign="top">
Interesting scene but your horizon slants down towards the right a bit</td>', 'Interesting scene but your horizon slants down towards the right a bit', '2026-06-01 06:27:41.000000', NULL, 1),
(7819526, 1307111, 99263, '<td valign="top">
Lovely vista with a nice feeling of depth</td>', 'Lovely vista with a nice feeling of depth', '2026-06-01 06:29:20.000000', NULL, 1),
(7819527, 1306978, 99263, '<td valign="top">
Pleasant park scene</td>', 'Pleasant park scene', '2026-06-01 06:30:13.000000', NULL, 1),
(7819528, 1307136, 99263, '<td valign="top">
Nice autumn colors and refections</td>', 'Nice autumn colors and refections', '2026-06-01 06:30:50.000000', NULL, 1),
(7819529, 1307149, 99263, '<td valign="top">
Lovely clouds</td>', 'Lovely clouds', '2026-06-01 06:31:16.000000', NULL, 1),
(7819530, 1307173, 99263, '<td valign="top">
Sweet sunrise scene</td>', 'Sweet sunrise scene', '2026-06-01 06:31:59.000000', NULL, 1),
(7819531, 1307168, 99263, '<td valign="top">
Looks cold and forlorn out there</td>', 'Looks cold and forlorn out there', '2026-06-01 06:32:41.000000', NULL, 1),
(7819532, 1307160, 99263, '<td valign="top">
Dramatic looking vista</td>', 'Dramatic looking vista', '2026-06-01 06:33:08.000000', NULL, 1),
(7819533, 1307117, 99263, '<td valign="top">
Lovely vista</td>', 'Lovely vista', '2026-06-01 06:33:43.000000', NULL, 1),
(7819537, 1307174, 113270, '<td valign="top">
Looks like a IKEA poster</td>', 'Looks like a IKEA poster', '2026-06-01 08:30:49.000000', NULL, 1),
(7819538, 1306978, 113270, '<td valign="top">
I would''ve preferred to see more of the trees to the right. As it is the top of them is out of frame</td>', 'I would''ve preferred to see more of the trees to the right. As it is the top of them is out of frame', '2026-06-01 08:37:03.000000', NULL, 1),
(7819586, 1307137, 86447, '<td valign="top">
I don''t see any land at all.  Hmmm...  I hope others think it fits the challenge.  5</td>', 'I don''t see any land at all.  Hmmm...  I hope others think it fits the challenge.  5', '2026-06-01 13:23:02.000000', NULL, 1),
(7819594, 1307114, 100831, '<td valign="top">
AWESOME.</td>', 'AWESOME.', '2026-06-01 16:34:56.000000', NULL, 1),
(7819595, 1307136, 100831, '<td valign="top">
To me the horizon is just a bit tilted, but the reflection is magnificent.</td>', 'To me the horizon is just a bit tilted, but the reflection is magnificent.', '2026-06-01 16:36:02.000000', NULL, 1),
(7819596, 1307174, 100831, '<td valign="top">
Nice picture, more water and sky than land but I love the mountains/hills in the distance, the monotone, and the leading line.</td>', 'Nice picture, more water and sky than land but I love the mountains/hills in the distance, the monotone, and the leading line.', '2026-06-01 16:37:11.000000', NULL, 1),
(7819598, 1307173, 100831, '<td valign="top">
Can''t fault this.. The layers of land/water, the color(s), reflections, happy birds AND the setting sun... perfection!</td>', 'Can''t fault this.. The layers of land/water, the color(s), reflections, happy birds AND the setting sun... perfection!', '2026-06-01 16:40:51.000000', NULL, 1),
(7819600, 1307008, 100831, '<td valign="top">
A splendid surprise of a photograph. SO original. I love it.</td>', 'A splendid surprise of a photograph. SO original. I love it.', '2026-06-01 16:41:54.000000', NULL, 1),
(7819601, 1307112, 100831, '<td valign="top">
Let the light shine down. <a href="https://www.google.com/search?q=let+the+light+shine+down+on+me+lumineers&amp;sca_esv=f309c00a8710a5de&amp;biw=1979&amp;bih=990&amp;sxsrf=ANbL-n5E04HA6Mr30SI6cvnuJEzncYI95A%3A1780346558825&amp;ei=vu4dat6NMrCgqtsPxJnBwA0&amp;oq=Let+the+light+shine+down&amp;gs_lp=Egxnd3Mtd2l6LXNlcnAiGExldCB0aGUgbGlnaHQgc2hpbmUgZG93bioCCAQyBRAuGIAEMgsQABj6BhjyBhiPBzILEAAYgAQYigUYkQIyBhAAGBYYHjIGEAAYFhgeMgYQABgWGB4yBhAAGBYYHjIIEAAYFhgeGAoyBhAAGBYYHjIGEAAYFhgeSIyVAVAAWP0ncAB4AZABAJgBlQGgAZkWqgEEMC4yNLgBAcgBAPgBAZgCG6AC6qICwgIREC4YgAQYsQMYgwEYxwEY0QPCAhcQLhiABBiKBRiNBhixAxjHARivARiOBcICChAAGIAEGIoFGEPCAggQABiABBixA8ICERAuGIAEGIoFGI0GGLEDGIMBwgIREAAYgAQYigUYjQYYsQMYgwHCAggQLhiABBixA8ICFBAuGIAEGIoFGLEDGIMBGMcBGNEDwgIgEC4YgAQYsQMYgwEYxwEY0QMYlwUY3AQY3gQY4ATYAQHCAhQQLhiABBiKBRiNBhixAxjHARivAcICDhAuGIAEGLEDGMcBGNEDwgIKEC4YgAQYigUYQ8ICEBAuGIAEGIoFGEMYxwEY0QPCAg0QLhiABBiKBRhDGLEDwgILEAAYgAQYsQMYgwHCAgUQABiABMICCBAuGLEDGIAEwgIKEC4YQxiABBiKBcICFBAuGIAEGJcFGNwEGN4EGOAE2AEBwgILEAAY-wYY8gYYjweYAwC6BgYIARABGBSSBwgwLjI0LjktM6AH7_ACsgcEMC4yNLgHhxfCBwYwLjIuMjXIB2GACAE&amp;sclient=gws-wiz-serp#fpstate=ive&amp;vld=cid:fe088b59,vid:t70QpClGspM,st:0" rel="nofollow" target="_blank">The Lumineers version</a></td>', 'Let the light shine down. The Lumineers version', '2026-06-01 16:45:31.000000', NULL, 1),
(7819602, 1306878, 100831, '<td valign="top">
A mix of emotions. And a fabulous photo.</td>', 'A mix of emotions. And a fabulous photo.', '2026-06-01 16:46:49.000000', NULL, 1),
(7819603, 1307085, 100831, '<td valign="top">
More waterscape, IMO. I may have tried this in b/w but it''s a beautiful scene. 6</td>', 'More waterscape, IMO. I may have tried this in b/w but it''s a beautiful scene. 6', '2026-06-01 16:47:30.000000', NULL, 1),
(7819617, 1307160, 67145, '<td valign="top">
one of my top picks .. like a crazy patchwork quilt .. 
<br/>i can just imagine some giant grabbing one of the corners and shaking it out .. :) .. 9 ..</td>', 'one of my top picks .. like a crazy patchwork quilt .. 
i can just imagine some giant grabbing one of the corners and shaking it out .. :) .. 9 ..', '2026-06-01 20:26:51.000000', NULL, 1),
(7819618, 1307168, 67145, '<td valign="top">
one of my top picks .. this is sombre and dramatic and very eye catching .. 
<br/>i feel like those clouds are going to fall on top of me . . 8 ..</td>', 'one of my top picks .. this is sombre and dramatic and very eye catching .. 
i feel like those clouds are going to fall on top of me . . 8 ..', '2026-06-01 20:28:12.000000', NULL, 1),
(7819619, 1307058, 67145, '<td valign="top">
love the sweep of the railroad tracks .. and all the pines with the mountains in the distance .. great shot .. 8 ..</td>', 'love the sweep of the railroad tracks .. and all the pines with the mountains in the distance .. great shot .. 8 ..', '2026-06-01 20:29:51.000000', NULL, 1),
(7819620, 1307117, 67145, '<td valign="top">
one of my top picks . this is the third btw . !! .. ;)
<br/>its just wonderful .. so impactful .. 8 ..</td>', 'one of my top picks . this is the third btw . !! .. ;)
its just wonderful .. so impactful .. 8 ..', '2026-06-01 20:30:41.000000', NULL, 1),
(7819621, 1306978, 67145, '<td valign="top">
very very nice .. and very serene .. 
<br/>i''d love to take tod there .. !! .. :)</td>', 'very very nice .. and very serene .. 
i''d love to take tod there .. !! .. :)', '2026-06-01 20:31:11.000000', NULL, 1),
(7819622, 1307111, 67145, '<td valign="top">
i have four top picks so far and this is one of them . 
<br/>but this might be the top of the top pics though .. 
<br/>i''m loving the patterns in the water .. the tones .. and the depth of this image .. it also seems a bit sombre which i''m rather liking too .. 
<br/>it speaks of journeys .. 9 ..</td>', 'i have four top picks so far and this is one of them . 
but this might be the top of the top pics though .. 
i''m loving the patterns in the water .. the tones .. and the depth of this image .. it also seems a bit sombre which i''m rather liking too .. 
it speaks of journeys .. 9 ..', '2026-06-01 20:34:18.000000', NULL, 1),
(7819623, 1307173, 67145, '<td valign="top">
just gorgeous .. and if i hadnt seen another image with similar colouring in a minimal edit challenge i''d be thinking those beautiful pink/orange tones were created somehow in your editing program .. 
<br/>either way its neither here nor there for me though ..
<br/>i love it either way .. 8 ..</td>', 'just gorgeous .. and if i hadnt seen another image with similar colouring in a minimal edit challenge i''d be thinking those beautiful pink/orange tones were created somehow in your editing program .. 
either way its neither here nor there for me though ..
i love it either way .. 8 ..', '2026-06-01 20:37:13.000000', NULL, 1),
(7819629, 1307173, 28742, '<td valign="top">
Composition: 7
<br/>Technical: 7
<br/>Creativity: 7
<br/>Appeal: 7
<br/>Challenge: 5
<br/>Overall Calculated Average Score: 7</td>', 'Composition: 7
Technical: 7
Creativity: 7
Appeal: 7
Challenge: 5
Overall Calculated Average Score: 7', '2026-06-01 22:04:21.000000', NULL, 1),
(7819630, 1306978, 28742, '<td valign="top">
Composition: 6
<br/>Technical: 6
<br/>Creativity: 6
<br/>Appeal: 6
<br/>Challenge: 6
<br/>Overall Calculated Average Score: 6</td>', 'Composition: 6
Technical: 6
Creativity: 6
Appeal: 6
Challenge: 6
Overall Calculated Average Score: 6', '2026-06-01 22:05:01.000000', NULL, 1),
(7819631, 1307082, 28742, '<td valign="top">
Composition: 5
<br/>Technical: 5
<br/>Creativity: 8
<br/>Appeal: 5 - A bit too much darkness/contrast for my taste
<br/>Challenge: 6
<br/>Overall Calculated Average Score: 6</td>', 'Composition: 5
Technical: 5
Creativity: 8
Appeal: 5 - A bit too much darkness/contrast for my taste
Challenge: 6
Overall Calculated Average Score: 6', '2026-06-01 22:05:57.000000', NULL, 1),
(7819632, 1307159, 28742, '<td valign="top">
Composition: 6
<br/>Technical: 5
<br/>Creativity: 6
<br/>Appeal: 5
<br/>Challenge: 5
<br/>Overall Calculated Average Score: 5</td>', 'Composition: 6
Technical: 5
Creativity: 6
Appeal: 5
Challenge: 5
Overall Calculated Average Score: 5', '2026-06-01 22:06:49.000000', NULL, 1),
(7819633, 1307149, 28742, '<td valign="top">
Composition: 5
<br/>Technical: 5
<br/>Creativity: 7
<br/>Appeal: 6
<br/>Challenge: 4 - More of a skyscape 😉
<br/>Overall Calculated Average Score: 5</td>', 'Composition: 5
Technical: 5
Creativity: 7
Appeal: 6
Challenge: 4 - More of a skyscape 😉
Overall Calculated Average Score: 5', '2026-06-01 22:09:43.000000', NULL, 1),
(7819634, 1306955, 28742, '<td valign="top">
Composition: 6
<br/>Technical: 5
<br/>Creativity: 7
<br/>Appeal: 7
<br/>Challenge: 6
<br/>Overall Calculated Average Score: 6</td>', 'Composition: 6
Technical: 5
Creativity: 7
Appeal: 7
Challenge: 6
Overall Calculated Average Score: 6', '2026-06-01 22:10:21.000000', NULL, 1),
(7819635, 1306951, 28742, '<td valign="top">
Composition: 6
<br/>Technical: 8
<br/>Creativity: 7
<br/>Appeal: 6
<br/>Challenge: 5
<br/>Overall Calculated Average Score: 6</td>', 'Composition: 6
Technical: 8
Creativity: 7
Appeal: 6
Challenge: 5
Overall Calculated Average Score: 6', '2026-06-01 22:10:58.000000', NULL, 1),
(7819636, 1307085, 28742, '<td valign="top">
Composition: 5
<br/>Technical: 6
<br/>Creativity: 6
<br/>Appeal: 6
<br/>Challenge: 4 - Call me a DNMC Nazi - Not much "land"
<br/>Overall Calculated Average Score: <strike>5</strike> Bump to 6</td>', 'Composition: 5
Technical: 6
Creativity: 6
Appeal: 6
Challenge: 4 - Call me a DNMC Nazi - Not much "land"
Overall Calculated Average Score: 5 Bump to 6', '2026-06-01 22:12:49.000000', NULL, 1),
(7819637, 1307160, 28742, '<td valign="top">
Composition: 7
<br/>Technical: 6
<br/>Creativity: 9
<br/>Appeal: 8
<br/>Challenge: 7
<br/>Overall Calculated Average Score: 7</td>', 'Composition: 7
Technical: 6
Creativity: 9
Appeal: 8
Challenge: 7
Overall Calculated Average Score: 7', '2026-06-01 22:13:19.000000', NULL, 1),
(7819638, 1307049, 28742, '<td valign="top">
Composition: 7
<br/>Technical: 8
<br/>Creativity: 7
<br/>Appeal: 8
<br/>Challenge: 5
<br/>Overall Calculated Average Score: 7</td>', 'Composition: 7
Technical: 8
Creativity: 7
Appeal: 8
Challenge: 5
Overall Calculated Average Score: 7', '2026-06-01 22:15:36.000000', NULL, 1),
(7819639, 1307144, 28742, '<td valign="top">
Composition: 6
<br/>Technical: 5
<br/>Creativity: 6
<br/>Appeal: 4
<br/>Challenge: 6
<br/>Overall Calculated Average Score: 5 - That green has blinded me! 🤪😎</td>', 'Composition: 6
Technical: 5
Creativity: 6
Appeal: 4
Challenge: 6
Overall Calculated Average Score: 5 - That green has blinded me! 🤪😎', '2026-06-01 22:17:12.000000', NULL, 1),
(7819640, 1307058, 28742, '<td valign="top">
Composition: 8
<br/>Technical: 9
<br/>Creativity: 9
<br/>Appeal: 9
<br/>Challenge: 9
<br/>Overall Calculated Average Score: 9 - A good mix of everything here! My fave so far.
<br/>
<br/>My pick for <img border="0" src="https://www.dpchallenge.com/images/rib1.gif" xalt="'' . substr(''https://www.dpchallenge.com/images/rib1.gif'', strrpos(''https://www.dpchallenge.com/images/rib1.gif'', ''/'') + 1) . ''"/></td>', 'Composition: 8
Technical: 9
Creativity: 9
Appeal: 9
Challenge: 9
Overall Calculated Average Score: 9 - A good mix of everything here! My fave so far.

My pick for', '2026-06-01 22:18:43.000000', NULL, 1),
(7819641, 1307137, 28742, '<td valign="top">
Composition: 5
<br/>Technical: 3
<br/>Creativity: 5
<br/>Appeal: 3
<br/>Challenge: 1
<br/>Overall Calculated Average Score: 3
<br/>It''s a potentially great scene in the right challenge with some heavy editing.
<br/><img border="0" src="https://images.dpchallenge.com/images_portfolio/25000-29999/28742/1200/Copyrighted_Image_Reuse_Prohibited_1224437.png" xalt="'' . substr(''https://images.dpchallenge.com/images_portfolio/25000-29999/28742/1200/Copyrighted_Image_Reuse_Prohibited_1224437.png'', strrpos(''https://images.dpchallenge.com/images_portfolio/25000-29999/28742/1200/Copyrighted_Image_Reuse_Prohibited_1224437.png'', ''/'') + 1) . ''"/></td>', 'Composition: 5
Technical: 3
Creativity: 5
Appeal: 3
Challenge: 1
Overall Calculated Average Score: 3
It''s a potentially great scene in the right challenge with some heavy editing.', '2026-06-01 22:21:26.000000', NULL, 1),
(7819642, 1307126, 28742, '<td valign="top">
Composition: 6
<br/>Technical: 6
<br/>Creativity: 6
<br/>Appeal: 5
<br/>Challenge: 5
<br/>Overall Calculated Average Score: 6</td>', 'Composition: 6
Technical: 6
Creativity: 6
Appeal: 5
Challenge: 5
Overall Calculated Average Score: 6', '2026-06-01 22:22:02.000000', NULL, 1),
(7819643, 1307174, 28742, '<td valign="top">
Composition: 7
<br/>Technical: 7
<br/>Creativity: 8
<br/>Appeal: 7
<br/>Challenge: 3
<br/>Overall Calculated Average Score: 6
<br/>I''ll let you off with a warning this time, <a href="https://www.dpchallenge.com/image.php?IMAGE_ID=1224437" rel="nofollow" target="_blank">but next time...</a> 😎</td>', 'Composition: 7
Technical: 7
Creativity: 8
Appeal: 7
Challenge: 3
Overall Calculated Average Score: 6
I''ll let you off with a warning this time, but next time... 😎', '2026-06-01 22:24:18.000000', NULL, 1),
(7819645, 1307176, 28742, '<td valign="top">
Composition: 9
<br/>Technical: 9
<br/>Creativity: 10
<br/>Appeal: 10
<br/>Challenge: 9
<br/>Overall Calculated Average Score: 9
<br/>
<br/>My pick for <img border="0" src="https://www.dpchallenge.com/images/rib2.gif" xalt="'' . substr(''https://www.dpchallenge.com/images/rib2.gif'', strrpos(''https://www.dpchallenge.com/images/rib2.gif'', ''/'') + 1) . ''"/></td>', 'Composition: 9
Technical: 9
Creativity: 10
Appeal: 10
Challenge: 9
Overall Calculated Average Score: 9

My pick for', '2026-06-01 22:26:09.000000', NULL, 1),
(7819646, 1307114, 28742, '<td valign="top">
Composition: 6
<br/>Technical: 6
<br/>Creativity: 7
<br/>Appeal: 6
<br/>Challenge: 4 - A bit too much else going on for me to call this a "Landscape"
<br/>Overall Calculated Average Score: 6 - A very cool and interesting scene!</td>', 'Composition: 6
Technical: 6
Creativity: 7
Appeal: 6
Challenge: 4 - A bit too much else going on for me to call this a "Landscape"
Overall Calculated Average Score: 6 - A very cool and interesting scene!', '2026-06-01 22:28:39.000000', NULL, 1),
(7819648, 1307112, 28742, '<td valign="top">
Composition: 5 - Several other entries with "too much" sky, somewhat opposite here, but not gonna ding it too bad.
<br/>Technical: 7
<br/>Creativity: 8 - Editing is on point!
<br/>Appeal: 7
<br/>Challenge: 8
<br/>Overall Calculated Average Score: 7</td>', 'Composition: 5 - Several other entries with "too much" sky, somewhat opposite here, but not gonna ding it too bad.
Technical: 7
Creativity: 8 - Editing is on point!
Appeal: 7
Challenge: 8
Overall Calculated Average Score: 7', '2026-06-01 22:31:07.000000', NULL, 1),
(7819650, 1307154, 28742, '<td valign="top">
Composition: 8
<br/>Technical: 8
<br/>Creativity: 7
<br/>Appeal: 8
<br/>Challenge: 7
<br/>Overall Calculated Average Score: 8</td>', 'Composition: 8
Technical: 8
Creativity: 7
Appeal: 8
Challenge: 7
Overall Calculated Average Score: 8', '2026-06-01 22:31:51.000000', NULL, 1),
(7819651, 1307179, 28742, '<td valign="top">
Composition: 7
<br/>Technical: 5
<br/>Creativity: 5
<br/>Appeal: 5
<br/>Challenge: 6
<br/>Overall Calculated Average Score: 6</td>', 'Composition: 7
Technical: 5
Creativity: 5
Appeal: 5
Challenge: 6
Overall Calculated Average Score: 6', '2026-06-01 22:32:28.000000', NULL, 1),
(7819653, 1307008, 28742, '<td valign="top">
Composition: 3
<br/>Technical: 5
<br/>Creativity: 5
<br/>Appeal: 3
<br/>Challenge: 4
<br/>Overall Calculated Average Score: <strike>4</strike>  bump to 5 
<br/>I wonder what it would look like if you shifted the focus to the distant background - you know, where the LANDSCAPE is. 😉</td>', 'Composition: 3
Technical: 5
Creativity: 5
Appeal: 3
Challenge: 4
Overall Calculated Average Score: 4  bump to 5 
I wonder what it would look like if you shifted the focus to the distant background - you know, where the LANDSCAPE is. 😉', '2026-06-01 22:35:50.000000', NULL, 1),
(7819654, 1307117, 28742, '<td valign="top">
Composition: 9
<br/>Technical: 5 - Colors and Lighting could be improved to make this a masterpiece
<br/>Creativity: 7
<br/>Appeal: 7
<br/>Challenge: 8
<br/>Overall Calculated Average Score: 7</td>', 'Composition: 9
Technical: 5 - Colors and Lighting could be improved to make this a masterpiece
Creativity: 7
Appeal: 7
Challenge: 8
Overall Calculated Average Score: 7', '2026-06-01 22:37:30.000000', NULL, 1),
(7819655, 1307111, 28742, '<td valign="top">
Composition: 9
<br/>Technical: 9
<br/>Creativity: 10
<br/>Appeal: 10
<br/>Challenge: 10
<br/>Overall Calculated Average Score: 10
<br/>Well I already picked my blue, but this would supersede it if I wasn''t too lazy. So THIS is my official <img border="0" src="https://www.dpchallenge.com/images/rib1.gif" xalt="'' . substr(''https://www.dpchallenge.com/images/rib1.gif'', strrpos(''https://www.dpchallenge.com/images/rib1.gif'', ''/'') + 1) . ''"/>. Outstanding!</td>', 'Composition: 9
Technical: 9
Creativity: 10
Appeal: 10
Challenge: 10
Overall Calculated Average Score: 10
Well I already picked my blue, but this would supersede it if I wasn''t too lazy. So THIS is my official . Outstanding!', '2026-06-01 22:43:28.000000', NULL, 1),
(7819656, 1307168, 28742, '<td valign="top">
Composition: 5
<br/>Technical: 5 - a bit dark
<br/>Creativity: 6
<br/>Appeal: 4
<br/>Challenge: 5
<br/>Overall Calculated Average Score: 5 - I bet this would be awesome if the clouds would not have photobombed ya! 😃</td>', 'Composition: 5
Technical: 5 - a bit dark
Creativity: 6
Appeal: 4
Challenge: 5
Overall Calculated Average Score: 5 - I bet this would be awesome if the clouds would not have photobombed ya! 😃', '2026-06-01 22:45:50.000000', NULL, 1),
(7819657, 1307161, 28742, '<td valign="top">
Composition: 5
<br/>Technical: 5
<br/>Creativity: 7
<br/>Appeal: 6
<br/>Challenge: 2
<br/>Overall Calculated Average Score: 5
<br/>
<br/>Very strange/cool image, <a href="https://www.dpchallenge.com/image.php?IMAGE_ID=1213077" rel="nofollow" target="_blank">but...</a> 😉</td>', 'Composition: 5
Technical: 5
Creativity: 7
Appeal: 6
Challenge: 2
Overall Calculated Average Score: 5

Very strange/cool image, but... 😉', '2026-06-01 22:47:59.000000', NULL, 1),
(7819658, 1307166, 28742, '<td valign="top">
Composition: 6
<br/>Technical: 6
<br/>Creativity: 7
<br/>Appeal: 7
<br/>Challenge: 7
<br/>Overall Calculated Average Score: 7</td>', 'Composition: 6
Technical: 6
Creativity: 7
Appeal: 7
Challenge: 7
Overall Calculated Average Score: 7', '2026-06-01 22:48:38.000000', NULL, 1),
(7819659, 1306878, 28742, '<td valign="top">
Oh man, I knew I shouldn''t have taken those mushrooms before voting. 😵</td>', 'Oh man, I knew I shouldn''t have taken those mushrooms before voting. 😵', '2026-06-01 22:50:00.000000', NULL, 1),
(7819661, 1307019, 28742, '<td valign="top">
Composition: 5
<br/>Technical: 5
<br/>Creativity: 6
<br/>Appeal: 5
<br/>Challenge: 6
<br/>Overall Calculated Average Score: 5
<br/>I would have gotten rid of those people. ...or at least cloned them out of the photo. 😜</td>', 'Composition: 5
Technical: 5
Creativity: 6
Appeal: 5
Challenge: 6
Overall Calculated Average Score: 5
I would have gotten rid of those people. ...or at least cloned them out of the photo. 😜', '2026-06-01 22:51:46.000000', NULL, 1),
(7819662, 1307136, 28742, '<td valign="top">
Composition: 5
<br/>Technical: 5
<br/>Creativity: 7
<br/>Appeal: 5
<br/>Challenge: 5
<br/>Overall Calculated Average Score: 5</td>', 'Composition: 5
Technical: 5
Creativity: 7
Appeal: 5
Challenge: 5
Overall Calculated Average Score: 5', '2026-06-01 22:52:33.000000', NULL, 1),
(7819719, 1306878, 61396, '<td valign="top">
a true surprise and a tenner</td>', 'a true surprise and a tenner', '2026-06-02 18:31:13.000000', NULL, 1),
(7819826, 1306878, 99263, '<td valign="top">
Don''t quite know what to make of this</td>', 'Don''t quite know what to make of this', '2026-06-03 16:13:14.000000', NULL, 1),
(7819827, 1307137, 99263, '<td valign="top">
Could have been a great shot except it''s very blurry and out of focus</td>', 'Could have been a great shot except it''s very blurry and out of focus', '2026-06-03 16:13:22.000000', NULL, 1),
(7819828, 1307049, 99263, '<td valign="top">
A nice scene but it somehow doesn''t pop. It seems dull/flat and also not very sharp.</td>', 'A nice scene but it somehow doesn''t pop. It seems dull/flat and also not very sharp.', '2026-06-03 16:13:28.000000', NULL, 1),
(7819834, 1307111, 12200, '<td valign="top">
I predict an easy ribbon finish for this one. So pristinely rendered it feels like it belongs on the cover of a textbook about landscape photography.</td>', 'I predict an easy ribbon finish for this one. So pristinely rendered it feels like it belongs on the cover of a textbook about landscape photography.', '2026-06-03 16:35:48.000000', NULL, 1),
(7819836, 1307112, 12200, '<td valign="top">
Heavenly.</td>', 'Heavenly.', '2026-06-03 16:40:50.000000', NULL, 1),
(7820162, 1307160, 100831, '<td valign="top">
Nice shot. Love the wide perspective.</td>', 'Nice shot. Love the wide perspective.', '2026-06-06 23:08:59.000000', NULL, 1),
(7820163, 1307111, 100831, '<td valign="top">
Gorgeous. What a scene.</td>', 'Gorgeous. What a scene.', '2026-06-06 23:10:32.000000', NULL, 1),
(7820179, 1306878, 56502, '<td valign="top">
Pretty weird - taken during a stunt flight?</td>', 'Pretty weird - taken during a stunt flight?', '2026-06-07 08:53:03.000000', NULL, 1),
(7820180, 1307137, 56502, '<td valign="top">
More like a "moonscape"</td>', 'More like a "moonscape"', '2026-06-07 08:53:41.000000', NULL, 1),
(7820181, 1307166, 56502, '<td valign="top">
Nice colors.</td>', 'Nice colors.', '2026-06-07 08:57:25.000000', NULL, 1),
(7820182, 1307144, 56502, '<td valign="top">
Hm - the texture in the green got lost in post processing, I guess.</td>', 'Hm - the texture in the green got lost in post processing, I guess.', '2026-06-07 09:03:21.000000', NULL, 1),
(7820183, 1307144, 66597, '<td valign="top">
I really like the scene but the greens look too pushed IMO</td>', 'I really like the scene but the greens look too pushed IMO', '2026-06-07 09:10:05.000000', NULL, 1),
(7820184, 1307166, 42733, '<td valign="top">
My favorite in this challenge.</td>', 'My favorite in this challenge.', '2026-06-07 09:58:00.000000', NULL, 1),
(7820185, 1307085, 42733, '<td valign="top">
My pick for red in this challenge.</td>', 'My pick for red in this challenge.', '2026-06-07 09:58:10.000000', NULL, 1),
(7820186, 1307168, 42733, '<td valign="top">
My pick for yellow in this challenge.</td>', 'My pick for yellow in this challenge.', '2026-06-07 09:58:22.000000', NULL, 1),
(7820234, 1307161, 96751, '<td valign="top">
an amazing phenomenon, but the image looks murky to me</td>', 'an amazing phenomenon, but the image looks murky to me', '2026-06-07 20:57:51.000000', NULL, 1),
(7820235, 1306951, 96751, '<td valign="top">
I like the leaf framing.</td>', 'I like the leaf framing.', '2026-06-07 20:58:14.000000', NULL, 1),
(7820236, 1307049, 96751, '<td valign="top">
picturesque but out of focus.</td>', 'picturesque but out of focus.', '2026-06-07 20:58:34.000000', NULL, 1),
(7820237, 1307168, 96751, '<td valign="top">
i like the crop on this - makes the weather quite oppressive!</td>', 'i like the crop on this - makes the weather quite oppressive!', '2026-06-07 20:58:57.000000', NULL, 1),
(7820238, 1307117, 96751, '<td valign="top">
the fisheye effect enhances the curve of the stream</td>', 'the fisheye effect enhances the curve of the stream', '2026-06-07 20:59:57.000000', NULL, 1),
(7820239, 1307058, 96751, '<td valign="top">
A spectacular view with wonderful leading lines. For me it''s the lighting that''s the issue - much earlier or later would have enhanced the image.</td>', 'A spectacular view with wonderful leading lines. For me it''s the lighting that''s the issue - much earlier or later would have enhanced the image.', '2026-06-07 21:00:46.000000', NULL, 1),
(7820240, 1307085, 96751, '<td valign="top">
Exceptional painterly look. Really like the processing.</td>', 'Exceptional painterly look. Really like the processing.', '2026-06-07 21:43:18.000000', NULL, 1),
(7820250, 1306878, 50641, '<td valign="top">
Wiggy</td>', 'Wiggy', '2026-06-07 23:15:31.000000', NULL, 1),
(7820264, 1306878, 100393, '<td valign="top">
More 1s than the Brown and as many 10s as the Blue. I’ll take that.</td>', 'More 1s than the Brown and as many 10s as the Blue. I’ll take that.', '2026-06-08 01:20:17.000000', NULL, 0),
(7820272, 1307174, 52628, '<td valign="top">
<table align="center" width="95%"><tr><td><div class="textsm"><b>Originally posted by ThingFish:</b></div><hr/><i> Interesting scene but your horizon slants down towards the right a bit </i></td></tr></table>
<br/>Yes, it''s the result of submitting late.  The horizon is a bit difficult and the floating dock and uneven sand does not help! :)</td>', 'Originally posted by ThingFish: Interesting scene but your horizon slants down towards the right a bit 
Yes, it''s the result of submitting late.  The horizon is a bit difficult and the floating dock and uneven sand does not help! :)', '2026-06-08 07:21:30.000000', NULL, 0),
(7820274, 1307174, 52628, '<td valign="top">
<table align="center" width="95%"><tr><td><div class="textsm"><b>Originally posted by Art Roflmao:</b></div><hr/><i> Composition: 7
<br/>Technical: 7
<br/>Creativity: 8
<br/>Appeal: 7
<br/>Challenge: 3
<br/>Overall Calculated Average Score: 6
<br/>I''ll let you off with a warning this time, <a href="https://www.dpchallenge.com/image.php?IMAGE_ID=1224437" rel="nofollow" target="_blank">but next time...</a> 😎 </i></td></tr></table>
<br/>
<br/>Thank you for making time to vote and telling us how you got to your score.  
<br/>
<br/>However I would like to object your challenge score of 3.  Just don''t get it.  I''ve been mostly shooting landscapes for leisure and professionally for the last 25 years.  Why do you think it''s not a landscape image, too much sky, too much water, too much dock?  Sorry for the nag, I just could not help it.
<br/>
<br/>Best, Hrannar</td>', 'Originally posted by Art Roflmao: Composition: 7
Technical: 7
Creativity: 8
Appeal: 7
Challenge: 3
Overall Calculated Average Score: 6
I''ll let you off with a warning this time, but next time... 😎 

Thank you for making time to vote and telling us how you got to your score.  

However I would like to object your challenge score of 3.  Just don''t get it.  I''ve been mostly shooting landscapes for leisure and professionally for the last 25 years.  Why do you think it''s not a landscape image, too much sky, too much water, too much dock?  Sorry for the nag, I just could not help it.

Best, Hrannar', '2026-06-08 08:06:41.000000', NULL, 0),
(7820275, 1307112, 67444, '<td valign="top">
Looks like when you wake up great from a good dream. Should have scored higher imo. Congrats!!</td>', 'Looks like when you wake up great from a good dream. Should have scored higher imo. Congrats!!', '2026-06-08 08:08:37.000000', NULL, 0),
(7820277, 1307166, 67444, '<td valign="top">
Stunning colors and reflection. I love how the small house gives the scene a quiet sense of scale, while the sky and pond make it feel vast and peaceful. Congrats!</td>', 'Stunning colors and reflection. I love how the small house gives the scene a quiet sense of scale, while the sky and pond make it feel vast and peaceful. Congrats!', '2026-06-08 08:19:36.000000', NULL, 0),
(7820278, 1307173, 67444, '<td valign="top">
Beautiful warm tones and reflection. I like how the birds, reeds, and small boat add life to the scene without taking away from the calm mood. COngratulations..</td>', 'Beautiful warm tones and reflection. I like how the birds, reeds, and small boat add life to the scene without taking away from the calm mood. COngratulations..', '2026-06-08 08:20:48.000000', NULL, 0),
(7820279, 1307160, 67444, '<td valign="top">
This feels epic. Dramatic clouds, and earthy colors make the landscape look almost otherworldly. love the title too. Congratulations, <img border="0" src="https://www.dpchallenge.com/images/user_icon/21.gif" xalt="'' . substr(''https://www.dpchallenge.com/images/user_icon/21.gif'', strrpos(''https://www.dpchallenge.com/images/user_icon/21.gif'', ''/'') + 1) . ''"/> <a href="https://www.dpchallenge.com/profile.php?USER_ID=108040" rel="nofollow" target="_blank">Gudjonotto</a>!</td>', 'This feels epic. Dramatic clouds, and earthy colors make the landscape look almost otherworldly. love the title too. Congratulations,  Gudjonotto!', '2026-06-08 08:24:28.000000', NULL, 0),
(7820280, 1307111, 67444, '<td valign="top">
I like how the winding river leads your eye into the mountains, and the dark clouds really match the title. The water looks soft, but the whole place still feels wild and powerful. Congratulations, <img border="0" src="https://www.dpchallenge.com/images/user_icon/21_F.gif" xalt="'' . substr(''https://www.dpchallenge.com/images/user_icon/21_F.gif'', strrpos(''https://www.dpchallenge.com/images/user_icon/21_F.gif'', ''/'') + 1) . ''"/> <a href="https://www.dpchallenge.com/profile.php?USER_ID=66597" rel="nofollow" target="_blank">noraneko</a>! Also for the high score!!</td>', 'I like how the winding river leads your eye into the mountains, and the dark clouds really match the title. The water looks soft, but the whole place still feels wild and powerful. Congratulations,  noraneko! Also for the high score!!', '2026-06-08 08:26:33.000000', NULL, 0),
(7820299, 1307112, 138630, '<td valign="top">
This was my 10 and I stand by it - as I was standing by you in awe as you experienced this moment.  I love it when light turns an ordinary scene magical.</td>', 'This was my 10 and I stand by it - as I was standing by you in awe as you experienced this moment.  I love it when light turns an ordinary scene magical.', '2026-06-08 10:02:27.000000', NULL, 0),
(7820301, 1307174, 138630, '<td valign="top">
<table align="center" width="95%"><tr><td><div class="textsm"><b>Originally posted by Hauxon:</b></div><hr/><i> . . .  Why do you think it''s not a landscape image, too much sky, too much water, too much dock? . . .  </i></td></tr></table>
<br/>
<br/>Art can (and undoubtedly will) speak for himself but I''ll say that while I love this image, I took it down a few points for all that dock; but now that you mention it, there is also a lot of sky and water LOL</td>', 'Originally posted by Hauxon: . . .  Why do you think it''s not a landscape image, too much sky, too much water, too much dock? . . .  

Art can (and undoubtedly will) speak for himself but I''ll say that while I love this image, I took it down a few points for all that dock; but now that you mention it, there is also a lot of sky and water LOL', '2026-06-08 10:06:53.000000', NULL, 0),
(7820317, 1307114, 68504, '<td valign="top">
cows following cows, a wonderful world.</td>', 'cows following cows, a wonderful world.', '2026-06-08 12:20:59.000000', NULL, 0),
(7820318, 1307019, 68504, '<td valign="top">
like Monet''s poppies!!</td>', 'like Monet''s poppies!!', '2026-06-08 12:24:50.000000', NULL, 0),
(7820319, 1307174, 52628, '<td valign="top">
<table align="center" width="95%"><tr><td><div class="textsm"><b>Originally posted by nam:</b></div><hr/><i> <table align="center" width="95%"><tr><td><div class="textsm"><b>Originally posted by Hauxon:</b></div><hr/><i> . . .  Why do you think it''s not a landscape image, too much sky, too much water, too much dock? . . .  </i></td></tr></table>
<br/>
<br/>Art can (and undoubtedly will) speak for himself but I''ll say that while I love this image, I took it down a few points for all that dock; but now that you mention it, there is also a lot of sky and water LOL </i></td></tr></table>
<br/>
<br/>For most people a landscape image is not just an image of "land", unless you''re autistic.  Think of landscape images from some famous location, say Lofoten Norway.  These images usually are mostly sea, sky and of course mountains.  Also houses that often take up a notable part of the image.  Nobody would state that the typical Lofoten shot wasn''t a landscape image ...unless on DPC.
<br/>
<br/>But to be fair I knew this image would suffer for not being a typical landscape and the pier is truly commanding.  I had shots from that location with more mountains but they were less crisp. :)
<br/>
<br/>Art has every right to vote as he wants and I appreciate his comments and voting method.  
<br/>
<br/>Peace out!</td>', 'Originally posted by nam: Originally posted by Hauxon: . . .  Why do you think it''s not a landscape image, too much sky, too much water, too much dock? . . .  

Art can (and undoubtedly will) speak for himself but I''ll say that while I love this image, I took it down a few points for all that dock; but now that you mention it, there is also a lot of sky and water LOL 

For most people a landscape image is not just an image of "land", unless you''re autistic.  Think of landscape images from some famous location, say Lofoten Norway.  These images usually are mostly sea, sky and of course mountains.  Also houses that often take up a notable part of the image.  Nobody would state that the typical Lofoten shot wasn''t a landscape image ...unless on DPC.

But to be fair I knew this image would suffer for not being a typical landscape and the pier is truly commanding.  I had shots from that location with more mountains but they were less crisp. :)

Art has every right to vote as he wants and I appreciate his comments and voting method.  

Peace out!', '2026-06-08 12:29:13.000000', NULL, 0),
(7820328, 1307111, 122678, '<td valign="top">
Congratulations, this is a beautiful landscape, crisp, and colorful, my favorite of the challenge.</td>', 'Congratulations, this is a beautiful landscape, crisp, and colorful, my favorite of the challenge.', '2026-06-08 13:49:31.000000', NULL, 0),
(7820329, 1307160, 122678, '<td valign="top">
Stunning photography, Congratulations!</td>', 'Stunning photography, Congratulations!', '2026-06-08 13:50:15.000000', NULL, 0),
(7820330, 1307173, 122678, '<td valign="top">
Beautiful sunset Congratulations!</td>', 'Beautiful sunset Congratulations!', '2026-06-08 13:50:51.000000', NULL, 0),
(7820331, 1307166, 122678, '<td valign="top">
Gorgeous photography, Congratulations!</td>', 'Gorgeous photography, Congratulations!', '2026-06-08 13:51:31.000000', NULL, 0),
(7820332, 1307112, 122678, '<td valign="top">
I love the Starburst in this cornfield.  Gorgeous, a top pick for me. Congratulations</td>', 'I love the Starburst in this cornfield.  Gorgeous, a top pick for me. Congratulations', '2026-06-08 13:53:44.000000', NULL, 0),
(7820333, 1307168, 122678, '<td valign="top">
Gorgeous low clouds on mountains</td>', 'Gorgeous low clouds on mountains', '2026-06-08 13:54:43.000000', NULL, 0),
(7820337, 1307166, 3306, '<td valign="top">
This was one of my top picks. A really beautiful scene and the colors are outstanding. So many tiny details to appreciate!
<br/>
<br/></td>', 'This was one of my top picks. A really beautiful scene and the colors are outstanding. So many tiny details to appreciate!', '2026-06-08 16:03:39.000000', NULL, 0),
(7820343, 1307111, 98565, '<td valign="top">
Congrats Catherine!
<br/>Love the composition with the different layers, so well done!</td>', 'Congrats Catherine!
Love the composition with the different layers, so well done!', '2026-06-08 16:21:09.000000', NULL, 0),
(7820356, 1307177, 91496, '<td valign="top">
No comments always sucks.
<br/>
<br/>I gave it a 6.  It has good composition with a leading line out to the distance.  Maybe crop off a bit of the top portion.  Did not have the wow factor of a sunset, mountain range, or Godzilla to push it over the top.</td>', 'No comments always sucks.

I gave it a 6.  It has good composition with a leading line out to the distance.  Maybe crop off a bit of the top portion.  Did not have the wow factor of a sunset, mountain range, or Godzilla to push it over the top.', '2026-06-08 19:10:22.000000', NULL, 0),
(7820357, 1307177, 28742, '<td valign="top">
<table align="center" width="95%"><tr><td><div class="textsm"><b>Originally posted by bobnospum:</b></div><hr/><i> Did not have the wow factor of a sunset, mountain range, or Godzilla to push it over the top. </i></td></tr></table>
<br/><a href="https://www.dpchallenge.com/image.php?IMAGE_ID=1307416" rel="nofollow" target="_blank"><img border="0" src="https://images.dpchallenge.com/images_portfolio/25000-29999/28742/120/Copyrighted_Image_Reuse_Prohibited_1307416.jpg" xalt="'' . substr(''https://images.dpchallenge.com/images_portfolio/25000-29999/28742/120/Copyrighted_Image_Reuse_Prohibited_1307416.jpg'', strrpos(''https://images.dpchallenge.com/images_portfolio/25000-29999/28742/120/Copyrighted_Image_Reuse_Prohibited_1307416.jpg'', ''/'') + 1) . ''"/></a>
<br/>I cloned him out - that was my mistake. 🤪</td>', 'Originally posted by bobnospum: Did not have the wow factor of a sunset, mountain range, or Godzilla to push it over the top. 

I cloned him out - that was my mistake. 🤪', '2026-06-08 19:39:05.000000', NULL, 0),
(7820386, 1307085, 66597, '<td valign="top">
I love your processing choices here, Anita. One of my favorites in the challenge</td>', 'I love your processing choices here, Anita. One of my favorites in the challenge', '2026-06-08 22:09:08.000000', NULL, 0),
(7820387, 1307085, 66597, '<td valign="top">
I love your processing choices here, Anita. One of my favorites in the challenge</td>', 'I love your processing choices here, Anita. One of my favorites in the challenge', '2026-06-08 22:09:17.000000', NULL, 0),
(7820396, 1307111, 138630, '<td valign="top">
Gorgeous.  Congratulations on the blue, Catherine.</td>', 'Gorgeous.  Congratulations on the blue, Catherine.', '2026-06-08 23:02:25.000000', NULL, 0),
(7820398, 1307111, 114285, '<td valign="top">
A very stunning scene,  lots of different layering for my eyes to look at, very pleasant. It was my top pick, well done,<br/><br/><i>Message edited by author 2026-06-09 01:04:15.</i></td>', 'A very stunning scene,  lots of different layering for my eyes to look at, very pleasant. It was my top pick, well done,', '2026-06-08 23:39:09.000000', '2026-06-09 01:04:15.000000', 0),
(7820438, 1307111, 98339, '<td valign="top">
Good for you!!!  Beautiful area!</td>', 'Good for you!!!  Beautiful area!', '2026-06-09 11:45:57.000000', NULL, 0),
(7820631, 1307168, 99687, '<td valign="top">
The clouds were the sole reason for me taking this photograph, so it was a very happy photobomb in my books. :)
<br/>
<br/><table align="center" width="95%"><tr><td><div class="textsm"><b>Originally posted by Art Roflmao:</b></div><hr/><i> Composition: 5
<br/>Technical: 5 - a bit dark
<br/>Creativity: 6
<br/>Appeal: 4
<br/>Challenge: 5
<br/>Overall Calculated Average Score: 5 - I bet this would be awesome if the clouds would not have photobombed ya! 😃 </i></td></tr></table></td>', 'The clouds were the sole reason for me taking this photograph, so it was a very happy photobomb in my books. :)

Originally posted by Art Roflmao: Composition: 5
Technical: 5 - a bit dark
Creativity: 6
Appeal: 4
Challenge: 5
Overall Calculated Average Score: 5 - I bet this would be awesome if the clouds would not have photobombed ya! 😃', '2026-06-10 17:04:18.000000', NULL, 0),
(7820694, 1306878, 67444, '<td valign="top">
<a href="https://www.dpchallenge.com/image.php?IMAGE_ID=1307519" rel="nofollow" target="_blank"><img border="0" src="https://images.dpchallenge.com/images_portfolio/65000-69999/67444/120/Copyrighted_Image_Reuse_Prohibited_1307519.png" xalt="'' . substr(''https://images.dpchallenge.com/images_portfolio/65000-69999/67444/120/Copyrighted_Image_Reuse_Prohibited_1307519.png'', strrpos(''https://images.dpchallenge.com/images_portfolio/65000-69999/67444/120/Copyrighted_Image_Reuse_Prohibited_1307519.png'', ''/'') + 1) . ''"/></a>
<br/>
<br/><b>The first Fleeting (In)Significance Award (TFIA) is Presented to <img border="0" src="https://www.dpchallenge.com/images/user_icon/user_id/100393.gif" xalt="'' . substr(''https://www.dpchallenge.com/images/user_icon/user_id/100393.gif'', strrpos(''https://www.dpchallenge.com/images/user_icon/user_id/100393.gif'', ''/'') + 1) . ''"/> <a href="https://www.dpchallenge.com/profile.php?USER_ID=100393" rel="nofollow" target="_blank">Paul</a> for “<a href="https://www.dpchallenge.com/image.php?IMAGE_ID=1306878" rel="nofollow" target="_blank">Homecoming</a>”
<br/>
<br/><a href="https://www.dpchallenge.com/image.php?IMAGE_ID=1306878" rel="nofollow" target="_blank"><img border="0" src="https://images.dpchallenge.com/images_challenge/4000-4999/4145/120/Copyrighted_Image_Reuse_Prohibited_1306878.jpg" xalt="'' . substr(''https://images.dpchallenge.com/images_challenge/4000-4999/4145/120/Copyrighted_Image_Reuse_Prohibited_1306878.jpg'', strrpos(''https://images.dpchallenge.com/images_challenge/4000-4999/4145/120/Copyrighted_Image_Reuse_Prohibited_1306878.jpg'', ''/'') + 1) . ''"/></a>
<br/>
<br/><i>"For creating a brave, unusual, and deeply visual image that challenges familiar ideas of beauty. This photograph (done in standard editing) presents an upside-down landscape, with a bonus hand, like the hand of justice or a second coming, saving us from our world of injustice and disparity. It asks the viewer to pause, look longer, and find meaning in the unfamiliar.
<br/>
<br/>Beautiful in its own world."</i>
<br/></b>
<br/>
<br/>~
<br/><a href="https://www.dpchallenge.com/forum.php?action=read&amp;FORUM_THREAD_ID=1461803" rel="nofollow" target="_blank">Forum link</a></td>', 'The first Fleeting (In)Significance Award (TFIA) is Presented to  Paul for “Homecoming”



"For creating a brave, unusual, and deeply visual image that challenges familiar ideas of beauty. This photograph (done in standard editing) presents an upside-down landscape, with a bonus hand, like the hand of justice or a second coming, saving us from our world of injustice and disparity. It asks the viewer to pause, look longer, and find meaning in the unfamiliar.

Beautiful in its own world."


~
Forum link', '2026-06-11 12:22:56.000000', NULL, 0);
COMMIT;

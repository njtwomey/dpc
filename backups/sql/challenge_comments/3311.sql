-- comments for challenge 3311
PRAGMA foreign_keys=OFF;
BEGIN TRANSACTION;
INSERT INTO comments ("id", "image_id", "commenter_id", "raw_comment", "comment", "date", "edited", "made_during_challenge") VALUES
(7706412, 1265648, 50641, '<td valign="top">Hi Mary!</td>', 'Hi Mary!', '2021-11-12 00:01:24.000000', NULL, 1),
(7706413, 1265844, 50641, '<td valign="top">hi t</td>', 'hi t', '2021-11-12 00:02:44.000000', NULL, 1),
(7706415, 1265423, 138630, '<td valign="top">Yo_Spiff</td>', 'Yo_Spiff', '2021-11-12 00:04:49.000000', NULL, 1),
(7706416, 1265774, 138630, '<td valign="top">Paul</td>', 'Paul', '2021-11-12 00:06:17.000000', NULL, 1),
(7706417, 1265803, 138630, '<td valign="top">vawendy</td>', 'vawendy', '2021-11-12 00:07:14.000000', NULL, 1),
(7706420, 1265423, 30861, '<td valign="top">Spiffy, I expect.</td>', 'Spiffy, I expect.', '2021-11-12 00:46:13.000000', NULL, 1),
(7706421, 1265831, 30861, '<td valign="top">JMRitz, for sure. How ya doing, John?</td>', 'JMRitz, for sure. How ya doing, John?', '2021-11-12 00:47:16.000000', NULL, 1),
(7706422, 1265838, 30861, '<td valign="top">Gotta be a Posthumous, based on the title alone :-)</td>', 'Gotta be a Posthumous, based on the title alone :-)', '2021-11-12 00:48:40.000000', NULL, 1),
(7706423, 1265827, 30861, '<td valign="top">Guaranteed to be a Mariuca :-)</td>', 'Guaranteed to be a Mariuca :-)', '2021-11-12 00:51:01.000000', NULL, 1),
(7706424, 1265843, 30861, '<td valign="top">Who else but Lydia?</td>', 'Who else but Lydia?', '2021-11-12 00:52:36.000000', NULL, 1),
(7706425, 1265704, 30861, '<td valign="top">Gotta be a Netherwood...</td>', 'Gotta be a Netherwood...', '2021-11-12 00:53:22.000000', NULL, 1),
(7706426, 1265841, 30861, '<td valign="top">Lei73 at her best :-)</td>', 'Lei73 at her best :-)', '2021-11-12 00:54:35.000000', NULL, 1),
(7706427, 1265590, 30861, '<td valign="top">If I don''t find a Tod, then this is Roz :-)</td>', 'If I don''t find a Tod, then this is Roz :-)', '2021-11-12 00:55:40.000000', NULL, 1),
(7706428, 1265824, 30861, '<td valign="top">This has GeneralE written all over it.</td>', 'This has GeneralE written all over it.', '2021-11-12 00:56:38.000000', NULL, 1),
(7706429, 1265777, 30861, '<td valign="top">Deliciously Hajeka.</td>', 'Deliciously Hajeka.', '2021-11-12 00:57:20.000000', NULL, 1),
(7706430, 1265819, 30861, '<td valign="top">Who but Alex Petrini drones around Italy''s backcountry so well?</td>', 'Who but Alex Petrini drones around Italy''s backcountry so well?', '2021-11-12 00:58:48.000000', NULL, 1),
(7706431, 1265648, 30861, '<td valign="top">Where''s there''s a wolfhound there''s <strike>MaryM</strike> MaryO I meant to type :-)<br/><br/><i>Message edited by author 2021-11-19 00:16:47.</i></td>', 'Where''s there''s a wolfhound there''s MaryM MaryO I meant to type :-)', '2021-11-12 00:59:24.000000', '2021-11-19 00:16:47.000000', 1),
(7706432, 1265803, 30861, '<td valign="top">Presumably Wendy, but a MINOLTA? Don''t you know they are allergic to peanut butter?</td>', 'Presumably Wendy, but a MINOLTA? Don''t you know they are allergic to peanut butter?', '2021-11-12 01:00:18.000000', NULL, 1),
(7706445, 1265648, 113411, '<td valign="top">Hello Mary O! Great looking Wolfhound, as usual!</td>', 'Hello Mary O! Great looking Wolfhound, as usual!', '2021-11-12 08:24:53.000000', NULL, 1),
(7706447, 1265821, 113411, '<td valign="top">Hello Wendy!!</td>', 'Hello Wendy!!', '2021-11-12 08:26:49.000000', NULL, 1),
(7706449, 1265590, 113411, '<td valign="top">Hello Roz! Great piece of sculpture!</td>', 'Hello Roz! Great piece of sculpture!', '2021-11-12 08:27:58.000000', NULL, 1),
(7706451, 1265843, 113411, '<td valign="top">Hello Lydia!!!</td>', 'Hello Lydia!!!', '2021-11-12 08:28:54.000000', NULL, 1),
(7706452, 1265618, 122678, '<td valign="top">Nice catch</td>', 'Nice catch', '2021-11-12 08:29:13.000000', NULL, 1),
(7706453, 1265586, 122678, '<td valign="top">This has to be Larry, GolferDDS. Wonderful image and just your style.</td>', 'This has to be Larry, GolferDDS. Wonderful image and just your style.', '2021-11-12 08:32:59.000000', NULL, 1),
(7706454, 1265803, 122678, '<td valign="top">Wow, I am guessing who this is, I will see if Im right. How do you train squirrels? SaraR</td>', 'Wow, I am guessing who this is, I will see if Im right. How do you train squirrels? SaraR', '2021-11-12 08:34:23.000000', NULL, 1),
(7706455, 1265839, 122678, '<td valign="top">MeMes2, beautiful cat. Nice image</td>', 'MeMes2, beautiful cat. Nice image', '2021-11-12 08:35:52.000000', NULL, 1),
(7706456, 1265843, 122678, '<td valign="top">Could this be Lydia???</td>', 'Could this be Lydia???', '2021-11-12 08:36:10.000000', NULL, 1),
(7706457, 1265590, 122678, '<td valign="top">I think I know who this is. Ron  LOL another nice image.</td>', 'I think I know who this is. Ron  LOL another nice image.', '2021-11-12 08:36:35.000000', NULL, 1),
(7706458, 1265821, 122678, '<td valign="top">Very nice, might be Grahamgator or a imposter learning.</td>', 'Very nice, might be Grahamgator or a imposter learning.', '2021-11-12 08:39:26.000000', NULL, 1),
(7706459, 1265612, 122678, '<td valign="top">LevT maybe???</td>', 'LevT maybe???', '2021-11-12 08:45:20.000000', NULL, 1),
(7706460, 1265841, 122678, '<td valign="top">MarioPierre???</td>', 'MarioPierre???', '2021-11-12 08:47:17.000000', NULL, 1),
(7706461, 1265423, 122678, '<td valign="top">Yo_Spiff</td>', 'Yo_Spiff', '2021-11-12 08:48:46.000000', NULL, 1),
(7706462, 1265774, 50695, '<td valign="top">This is like Neat plus Gyaban</td>', 'This is like Neat plus Gyaban', '2021-11-12 09:42:09.000000', NULL, 1),
(7706463, 1265819, 50695, '<td valign="top">looks like Alexkc</td>', 'looks like Alexkc', '2021-11-12 09:42:49.000000', NULL, 1),
(7706464, 1265777, 50695, '<td valign="top">looks like hajeka</td>', 'looks like hajeka', '2021-11-12 09:43:15.000000', NULL, 1),
(7706465, 1265844, 50695, '<td valign="top">seems like chaos, but then one realizes the palette is carefully chosen. lovely. Could be tnun.</td>', 'seems like chaos, but then one realizes the palette is carefully chosen. lovely. Could be tnun.', '2021-11-12 09:44:27.000000', NULL, 1),
(7706466, 1265843, 65234, '<td valign="top">OMG; the hat! And the little rake!! This is just too adorable.</td>', 'OMG; the hat! And the little rake!! This is just too adorable.', '2021-11-12 09:45:07.000000', NULL, 1),
(7706467, 1265590, 50695, '<td valign="top">looks like roz, I mean the photo, I mean the person taking the photo, I mean the kind of photo she takes, I mean.....</td>', 'looks like roz, I mean the photo, I mean the person taking the photo, I mean the kind of photo she takes, I mean.....', '2021-11-12 09:45:21.000000', NULL, 1),
(7706468, 1265612, 50695, '<td valign="top">this is tragic. what a catch. are you tvsometime?</td>', 'this is tragic. what a catch. are you tvsometime?', '2021-11-12 09:46:18.000000', NULL, 1),
(7706469, 1265847, 50695, '<td valign="top">glorious gorgeousness. looks like a skewsme spectacular</td>', 'glorious gorgeousness. looks like a skewsme spectacular', '2021-11-12 09:47:25.000000', NULL, 1),
(7706470, 1265786, 50695, '<td valign="top">looks like a NikonJeb. I like the color</td>', 'looks like a NikonJeb. I like the color', '2021-11-12 09:48:26.000000', NULL, 1),
(7706471, 1265505, 65234, '<td valign="top">I think I recognize that valley! But I do realize there are valleys other than "mine" LOL. I was just up on Skyline Drive last week, though, so of course that''s what I immediately think of.</td>', 'I think I recognize that valley! But I do realize there are valleys other than "mine" LOL. I was just up on Skyline Drive last week, though, so of course that''s what I immediately think of.', '2021-11-12 09:48:50.000000', NULL, 1),
(7706472, 1265827, 50695, '<td valign="top">might be a mariuca making connections</td>', 'might be a mariuca making connections', '2021-11-12 09:49:06.000000', NULL, 1),
(7706473, 1265505, 50695, '<td valign="top">I don''t know who this is but I like the hue shift or whatever is making this so cyan/turquoise/whatever</td>', 'I don''t know who this is but I like the hue shift or whatever is making this so cyan/turquoise/whatever', '2021-11-12 09:50:00.000000', NULL, 1),
(7706474, 1265833, 50695, '<td valign="top">Tiberius in a coy mood? I like the subtlety of this and how the subtlety makes it very abstract.</td>', 'Tiberius in a coy mood? I like the subtlety of this and how the subtlety makes it very abstract.', '2021-11-12 09:50:37.000000', NULL, 1),
(7706475, 1265590, 65234, '<td valign="top">This could be one of at least two photographers I can think of who are excellent at bug macros. I''m fascinated by that little face.</td>', 'This could be one of at least two photographers I can think of who are excellent at bug macros. I''m fascinated by that little face.', '2021-11-12 09:50:42.000000', NULL, 1),
(7706476, 1265843, 50695, '<td valign="top">A little grittier Lydia</td>', 'A little grittier Lydia', '2021-11-12 09:51:16.000000', NULL, 1),
(7706477, 1265639, 50695, '<td valign="top">I like this subtle observation of a lazy? line painter. I don''t know who it is. But now I wonder if the bridge is safe......</td>', 'I like this subtle observation of a lazy? line painter. I don''t know who it is. But now I wonder if the bridge is safe......', '2021-11-12 09:52:13.000000', NULL, 1),
(7706478, 1265831, 50695, '<td valign="top">I think this is jmritz making some comment about how style is self and self is style or perhaps saying that there is no such thing as a style or maybe he''s saying there is such a thing as style and it''s impossible not to have a style but you should try anyway... you should try just to show your self not your style... and that''s what is impossible.</td>', 'I think this is jmritz making some comment about how style is self and self is style or perhaps saying that there is no such thing as a style or maybe he''s saying there is such a thing as style and it''s impossible not to have a style but you should try anyway... you should try just to show your self not your style... and that''s what is impossible.', '2021-11-12 09:53:26.000000', NULL, 1),
(7706479, 1265803, 50695, '<td valign="top">I guess this is vawendy although it seems more like an homage to vawendy than a shot in vawendy''s style.</td>', 'I guess this is vawendy although it seems more like an homage to vawendy than a shot in vawendy''s style.', '2021-11-12 09:54:28.000000', NULL, 1),
(7706480, 1265704, 50695, '<td valign="top">Looks like MargaretNet''s software.</td>', 'Looks like MargaretNet''s software.', '2021-11-12 09:55:26.000000', NULL, 1),
(7706481, 1265803, 65234, '<td valign="top">I suspect <img alt="'' . substr(''https://www.dpchallenge.com/images/user_icon/21_F.gif'', strrpos(''https://www.dpchallenge.com/images/user_icon/21_F.gif'', ''/'') + 1) . ''" border="0" src="https://www.dpchallenge.com/images/user_icon/21_F.gif"/> <a href="https://www.dpchallenge.com/profile.php?USER_ID=103142" rel="nofollow" target="_blank">vawendy</a>, because, obviously, it''s a squirrel, and an uncommonly cooperative one at that. Really great image thanks to the model ... OK, and the photographer ;-)</td>', 'I suspect  vawendy, because, obviously, it''s a squirrel, and an uncommonly cooperative one at that. Really great image thanks to the model ... OK, and the photographer ;-)', '2021-11-12 09:57:22.000000', NULL, 1),
(7706482, 1265819, 65234, '<td valign="top">Gorgeous scene. Love the muted colors; very inviting.</td>', 'Gorgeous scene. Love the muted colors; very inviting.', '2021-11-12 09:58:31.000000', NULL, 1),
(7706485, 1265586, 123833, '<td valign="top">You are crazy, Larry! :)</td>', 'You are crazy, Larry! :)', '2021-11-12 10:25:50.000000', NULL, 1),
(7706486, 1265803, 123833, '<td valign="top">Not Wendy but very nice :)</td>', 'Not Wendy but very nice :)', '2021-11-12 10:27:22.000000', NULL, 1),
(7706495, 1265834, 50695, '<td valign="top">MargaretNet + Tiberius = ?</td>', 'MargaretNet + Tiberius = ?', '2021-11-12 11:34:28.000000', NULL, 1),
(7706497, 1265711, 50695, '<td valign="top">this is the style of that beautiful man with the weimeraner ... John ... has he really been gone so long I can''t think of his username? I hope he''s back. this is the best photo of a ghostorb portalbubble I''ve ever seen.</td>', 'this is the style of that beautiful man with the weimeraner ... John ... has he really been gone so long I can''t think of his username? I hope he''s back. this is the best photo of a ghostorb portalbubble I''ve ever seen.', '2021-11-12 11:37:11.000000', NULL, 1),
(7706498, 1265805, 50695, '<td valign="top">might be Neat. she''s unpredictable but always goes for beauty</td>', 'might be Neat. she''s unpredictable but always goes for beauty', '2021-11-12 11:55:11.000000', NULL, 1),
(7706499, 1265586, 50695, '<td valign="top">i don''t know who this is. might be GolferDDS though I would say it''s more his spirit than his style. the photo itself is great, dynamic with lots of energy</td>', 'i don''t know who this is. might be GolferDDS though I would say it''s more his spirit than his style. the photo itself is great, dynamic with lots of energy', '2021-11-12 11:56:07.000000', NULL, 1),
(7706503, 1265648, 138630, '<td valign="top">MaryO</td>', 'MaryO', '2021-11-12 12:45:00.000000', NULL, 1),
(7706511, 1265843, 30214, '<td valign="top">My first guess was Lydia, but she usually has more colorful toads... and less creative titles :). So, I''m not sure now...</td>', 'My first guess was Lydia, but she usually has more colorful toads... and less creative titles :). So, I''m not sure now...', '2021-11-12 14:38:26.000000', NULL, 1),
(7706512, 1265805, 30214, '<td valign="top">I think in this case strong noise add to the unsettling feel of this photo. Good job!</td>', 'I think in this case strong noise add to the unsettling feel of this photo. Good job!', '2021-11-12 14:39:46.000000', NULL, 1),
(7706513, 1265834, 30214, '<td valign="top">must be Georges. If not, take it as a compliment ))</td>', 'must be Georges. If not, take it as a compliment ))', '2021-11-12 14:40:54.000000', NULL, 1),
(7706514, 1265803, 30214, '<td valign="top">Wendy, is that your new assistant?</td>', 'Wendy, is that your new assistant?', '2021-11-12 14:42:11.000000', NULL, 1),
(7706515, 1265818, 67258, '<td valign="top">This model looks very familiar!  Could it be  an all grown up Rowan, I wonder?  The style is very Timfythetoo.  I love the way the  character comes out  in this portrait.  Possibly  slightly over whitened the eyes - dial that  back, and it  would be perfect.</td>', 'This model looks very familiar!  Could it be  an all grown up Rowan, I wonder?  The style is very Timfythetoo.  I love the way the  character comes out  in this portrait.  Possibly  slightly over whitened the eyes - dial that  back, and it  would be perfect.', '2021-11-12 14:42:23.000000', NULL, 1),
(7706516, 1265831, 30214, '<td valign="top">one and only jmritz?</td>', 'one and only jmritz?', '2021-11-12 14:43:04.000000', NULL, 1),
(7706517, 1265590, 30214, '<td valign="top">Roz, is that you? I''m a little doubtful though...</td>', 'Roz, is that you? I''m a little doubtful though...', '2021-11-12 14:45:18.000000', NULL, 1),
(7706518, 1265843, 67258, '<td valign="top">This has  to be a Lydia, surely?  That said, I associate Lydia with colour.  Super image with just the right depth of field.</td>', 'This has  to be a Lydia, surely?  That said, I associate Lydia with colour.  Super image with just the right depth of field.', '2021-11-12 14:46:18.000000', NULL, 1),
(7706519, 1265704, 67258, '<td valign="top">Margaret continuing your very successful exploration of new processing techniques?  A very  lovely, understated image.</td>', 'Margaret continuing your very successful exploration of new processing techniques?  A very  lovely, understated image.', '2021-11-12 14:47:30.000000', NULL, 1),
(7706520, 1265590, 67258, '<td valign="top">Well, it was always going to be a bejewelled insect , or Mr Tod :)  This is another Roz classic, and is definitely ribbon worthy.</td>', 'Well, it was always going to be a bejewelled insect , or Mr Tod :)  This is another Roz classic, and is definitely ribbon worthy.', '2021-11-12 14:48:41.000000', NULL, 1),
(7706521, 1265839, 30214, '<td valign="top">MeMex2, obviously ). She (the cat) does have gravitas in her gait!</td>', 'MeMex2, obviously ). She (the cat) does have gravitas in her gait!', '2021-11-12 14:50:36.000000', NULL, 1),
(7706522, 1265774, 67258, '<td valign="top">From the subject, I would guess at salmiaki, but the in  camera movement and processing are not styles I would have  expected.  This works really  well, bringing a sense of mystery to the Gormley sculptures.  And I still haven''t got  across the Penines to photograph them myself.</td>', 'From the subject, I would guess at salmiaki, but the in  camera movement and processing are not styles I would have  expected.  This works really  well, bringing a sense of mystery to the Gormley sculptures.  And I still haven''t got  across the Penines to photograph them myself.', '2021-11-12 14:51:03.000000', NULL, 1),
(7706524, 1265839, 67258, '<td valign="top">Memex2?  Your cat is very similar to mine :)  I love the addition of the two mysterious figures in the distance .</td>', 'Memex2?  Your cat is very similar to mine :)  I love the addition of the two mysterious figures in the distance .', '2021-11-12 15:10:01.000000', NULL, 1),
(7706544, 1265827, 28742, '<td valign="top">This has a <img alt="'' . substr(''https://www.dpchallenge.com/images/user_icon/21.gif'', strrpos(''https://www.dpchallenge.com/images/user_icon/21.gif'', ''/'') + 1) . ''" border="0" src="https://www.dpchallenge.com/images/user_icon/21.gif"/> <a href="https://www.dpchallenge.com/profile.php?USER_ID=30214" rel="nofollow" target="_blank">LevT</a> feel to it. Outstanding.</td>', 'This has a  LevT feel to it. Outstanding.', '2021-11-12 20:39:17.000000', NULL, 1),
(7706545, 1265590, 28742, '<td valign="top">Lord of the Flies. ;-)</td>', 'Lord of the Flies. ;-)', '2021-11-12 20:39:44.000000', NULL, 1),
(7706546, 1265648, 28742, '<td valign="top"><img alt="'' . substr(''https://www.dpchallenge.com/images/user_icon/21_F.gif'', strrpos(''https://www.dpchallenge.com/images/user_icon/21_F.gif'', ''/'') + 1) . ''" border="0" src="https://www.dpchallenge.com/images/user_icon/21_F.gif"/> <a href="https://www.dpchallenge.com/profile.php?USER_ID=65234" rel="nofollow" target="_blank">MaryO</a>?</td>', ' MaryO?', '2021-11-12 20:43:22.000000', NULL, 1),
(7706548, 1265843, 28742, '<td valign="top">I like how you titled it with the filename. Confirms who I think it is. ;-)</td>', 'I like how you titled it with the filename. Confirms who I think it is. ;-)', '2021-11-12 20:50:08.000000', NULL, 1),
(7706549, 1265423, 28742, '<td valign="top">Grog?</td>', 'Grog?', '2021-11-12 20:51:14.000000', NULL, 1),
(7706550, 1265618, 28742, '<td valign="top">I guarantee I''m not the only one who read that as "A little green Ahole"</td>', 'I guarantee I''m not the only one who read that as "A little green Ahole"', '2021-11-12 20:51:55.000000', NULL, 1),
(7706551, 1265803, 28742, '<td valign="top">The Squirrel Whisperer. ;-)</td>', 'The Squirrel Whisperer. ;-)', '2021-11-12 20:52:57.000000', NULL, 1),
(7706552, 1265423, 30982, '<td valign="top">This would be Steve, aka Yo_Spiff, aka Grog.</td>', 'This would be Steve, aka Yo_Spiff, aka Grog.', '2021-11-12 21:25:14.000000', NULL, 1),
(7706555, 1265648, 30982, '<td valign="top">Must be Mary!</td>', 'Must be Mary!', '2021-11-12 21:26:28.000000', NULL, 1),
(7706556, 1265612, 30982, '<td valign="top">LevT?</td>', 'LevT?', '2021-11-12 21:28:14.000000', NULL, 1),
(7706557, 1265843, 30982, '<td valign="top">Lydia, perhaps?</td>', 'Lydia, perhaps?', '2021-11-12 21:28:32.000000', NULL, 1),
(7706558, 1265827, 30982, '<td valign="top">Possibly Mariuca.</td>', 'Possibly Mariuca.', '2021-11-12 21:29:18.000000', NULL, 1),
(7706559, 1265777, 30982, '<td valign="top">Hajeka.</td>', 'Hajeka.', '2021-11-12 21:29:31.000000', NULL, 1),
(7706560, 1265590, 30982, '<td valign="top">Roz?</td>', 'Roz?', '2021-11-12 21:29:56.000000', NULL, 1),
(7706597, 1265843, 38162, '<td valign="top">sure this title has the number right?  looks like 4379 to me.  sorry, but lazy title hurts in close competition.</td>', 'sure this title has the number right?  looks like 4379 to me.  sorry, but lazy title hurts in close competition.', '2021-11-13 18:30:22.000000', NULL, 1),
(7706598, 1265841, 30214, '<td valign="top">Who are you, Botticelli? :) Wonderful portrait! 

<br/>Paul? lei_73?

<br/>(voted earlier)</td>', 'Who are you, Botticelli? :) Wonderful portrait! 

Paul? lei_73?

(voted earlier)', '2021-11-13 19:43:21.000000', NULL, 1),
(7706599, 1265618, 30214, '<td valign="top">Gorgeous colors and lighting... Roz, is that you? (voted earlier)</td>', 'Gorgeous colors and lighting... Roz, is that you? (voted earlier)', '2021-11-13 19:57:45.000000', NULL, 1),
(7706610, 1265775, 42733, '<td valign="top">In my top three.</td>', 'In my top three.', '2021-11-13 20:16:02.000000', NULL, 1),
(7706611, 1265590, 42733, '<td valign="top">My favorite in this challenge.</td>', 'My favorite in this challenge.', '2021-11-13 20:16:12.000000', NULL, 1),
(7706612, 1265803, 42733, '<td valign="top">Lovely! What a great model.</td>', 'Lovely! What a great model.', '2021-11-13 20:16:23.000000', NULL, 1),
(7706620, 1265818, 100831, '<td valign="top">Wow. What a treasure.</td>', 'Wow. What a treasure.', '2021-11-14 12:37:50.000000', NULL, 1),
(7706621, 1265711, 86447, '<td valign="top">Lev?   Is that you??  :D</td>', 'Lev?   Is that you??  :D', '2021-11-14 12:48:56.000000', NULL, 1),
(7706622, 1265839, 86447, '<td valign="top">And... she''s lovely as usual!</td>', 'And... she''s lovely as usual!', '2021-11-14 12:49:19.000000', NULL, 1),
(7706623, 1265590, 86447, '<td valign="top">Roz!   Gorgeous!</td>', 'Roz!   Gorgeous!', '2021-11-14 12:49:27.000000', NULL, 1),
(7706624, 1265834, 86447, '<td valign="top">This has Georges written all over it!</td>', 'This has Georges written all over it!', '2021-11-14 12:49:54.000000', NULL, 1),
(7706626, 1265833, 100831, '<td valign="top">see-through.</td>', 'see-through.', '2021-11-14 12:52:15.000000', NULL, 1),
(7706627, 1265844, 100831, '<td valign="top">Nature''s trick or treat! Lovely.</td>', 'Nature''s trick or treat! Lovely.', '2021-11-14 12:54:41.000000', NULL, 1),
(7706628, 1265831, 100831, '<td valign="top">... right back at ya.</td>', '... right back at ya.', '2021-11-14 12:55:04.000000', NULL, 1),
(7706635, 1265818, 170018, '<td valign="top">This should be grown-up Ada, if my "detective" work is correct! May be not...

<br/>As a mom of a 17-year-old daughter myself I appreciate that she still poses for you. Love the expression! 

<br/>Freckled kids keep ruling!</td>', 'This should be grown-up Ada, if my "detective" work is correct! May be not...

As a mom of a 17-year-old daughter myself I appreciate that she still poses for you. Love the expression! 

Freckled kids keep ruling!', '2021-11-14 20:18:10.000000', NULL, 1),
(7706636, 1265827, 170018, '<td valign="top">This could only be caught by the observant eye of Mariuca! How do you do it?  How much time do you spend in museums to be able to have such a collection of incredible finds?</td>', 'This could only be caught by the observant eye of Mariuca! How do you do it?  How much time do you spend in museums to be able to have such a collection of incredible finds?', '2021-11-14 20:29:09.000000', NULL, 1),
(7706637, 1265819, 170018, '<td valign="top">Is this Alessandro''s stunning work? It feels like dream-flying!</td>', 'Is this Alessandro''s stunning work? It feels like dream-flying!', '2021-11-14 21:12:10.000000', NULL, 1),
(7706638, 1265775, 170018, '<td valign="top">Feels like Cape Cod should be the next place for a gold rush!</td>', 'Feels like Cape Cod should be the next place for a gold rush!', '2021-11-14 21:22:33.000000', NULL, 1),
(7706639, 1265803, 170018, '<td valign="top">I think there''s only one photographer at DPC who can pull this shot off! And was not her goal once to bring back a squirrel to her profile page? :-)</td>', 'I think there''s only one photographer at DPC who can pull this shot off! And was not her goal once to bring back a squirrel to her profile page? :-)', '2021-11-14 21:43:58.000000', NULL, 1),
(7706640, 1265777, 170018, '<td valign="top">Delicious-looking food? Check! White background? Check! Henk-Jan?...</td>', 'Delicious-looking food? Check! White background? Check! Henk-Jan?...', '2021-11-14 21:47:17.000000', NULL, 1),
(7706641, 1265805, 170018, '<td valign="top">Is that Paul''s meditative, dream-like, unpredictable beauty?</td>', 'Is that Paul''s meditative, dream-like, unpredictable beauty?', '2021-11-14 22:04:05.000000', NULL, 1),
(7706642, 1265814, 170018, '<td valign="top">Not the colors one might expect from skewsme, but I feel this unmuted sky might be hers. If not, please, take this as a compliment!</td>', 'Not the colors one might expect from skewsme, but I feel this unmuted sky might be hers. If not, please, take this as a compliment!', '2021-11-14 22:14:25.000000', NULL, 1),
(7706643, 1265711, 170018, '<td valign="top">Great name for this strange place with "alien ship" structures and children with balloon heads...I put my bets on LevT as an author! If yes, did this remind you of Kin-dza-dza?</td>', 'Great name for this strange place with "alien ship" structures and children with balloon heads...I put my bets on LevT as an author! If yes, did this remind you of Kin-dza-dza?', '2021-11-14 22:22:35.000000', NULL, 1),
(7706644, 1265847, 170018, '<td valign="top">Is that dreamy field of glad2badad?</td>', 'Is that dreamy field of glad2badad?', '2021-11-14 22:27:51.000000', NULL, 1),
(7706645, 1265612, 170018, '<td valign="top">I''ve already decided about the other street shot captured by a keen eye as belonging to LevT, but now I am in doubt! This photo looks like it came from the pages of Parallels...</td>', 'I''ve already decided about the other street shot captured by a keen eye as belonging to LevT, but now I am in doubt! This photo looks like it came from the pages of Parallels...', '2021-11-14 22:35:29.000000', NULL, 1),
(7706646, 1265831, 170018, '<td valign="top">Poet in disguise?</td>', 'Poet in disguise?', '2021-11-14 22:37:45.000000', NULL, 1),
(7706647, 1265843, 170018, '<td valign="top">This could only be Lydia''s, though unusual in black-and-white!</td>', 'This could only be Lydia''s, though unusual in black-and-white!', '2021-11-14 22:40:16.000000', NULL, 1),
(7706648, 1265774, 170018, '<td valign="top">This is the most mysterious submission in the challenge... I hope she makes home to her planet safely!</td>', 'This is the most mysterious submission in the challenge... I hope she makes home to her planet safely!', '2021-11-14 22:45:14.000000', NULL, 1),
(7706649, 1265844, 170018, '<td valign="top">This can be a strange and poetic flora of tnun!</td>', 'This can be a strange and poetic flora of tnun!', '2021-11-14 22:50:41.000000', NULL, 1),
(7706650, 1265821, 170018, '<td valign="top">Colors and softness of the Master! 

<br/>This stalk of the fallen half-pear is heart-breaking...</td>', 'Colors and softness of the Master! 

This stalk of the fallen half-pear is heart-breaking...', '2021-11-14 22:55:27.000000', NULL, 1),
(7706659, 1265786, 50641, '<td valign="top">Bej</td>', 'Bej', '2021-11-14 23:50:05.000000', NULL, 1),
(7706686, 1265839, 8759, '<td valign="top">MeMex2 and Kramer. I not sure if is your style or HER style ;)</td>', 'MeMex2 and Kramer. I not sure if is your style or HER style ;)', '2021-11-15 05:12:32.000000', NULL, 1),
(7706687, 1265806, 8759, '<td valign="top">Ammie and the mysterious SA</td>', 'Ammie and the mysterious SA', '2021-11-15 05:14:34.000000', NULL, 1),
(7706690, 1265803, 8759, '<td valign="top">The card is full Wendy!</td>', 'The card is full Wendy!', '2021-11-15 05:25:03.000000', NULL, 1),
(7706691, 1265834, 8759, '<td valign="top">Did you get lost, George?</td>', 'Did you get lost, George?', '2021-11-15 05:25:42.000000', NULL, 1),
(7706692, 1265831, 8759, '<td valign="top">Hi John!</td>', 'Hi John!', '2021-11-15 05:28:01.000000', NULL, 1),
(7706693, 1265819, 8759, '<td valign="top">Your retreat, Alex?</td>', 'Your retreat, Alex?', '2021-11-15 05:29:34.000000', NULL, 1),
(7706695, 1265590, 8759, '<td valign="top">Roz, not the profile!</td>', 'Roz, not the profile!', '2021-11-15 05:31:53.000000', NULL, 1),
(7706703, 1265839, 23098, '<td valign="top">Like the perspective here. Looks like shes on a mission!</td>', 'Like the perspective here. Looks like shes on a mission!', '2021-11-15 08:50:43.000000', NULL, 1),
(7706704, 1265590, 23098, '<td valign="top">Outstanding. Must be Roz!</td>', 'Outstanding. Must be Roz!', '2021-11-15 08:52:50.000000', NULL, 1),
(7706705, 1265803, 23098, '<td valign="top">Nice setup and capture. Must be Wendy!</td>', 'Nice setup and capture. Must be Wendy!', '2021-11-15 08:57:34.000000', NULL, 1),
(7706737, 1265711, 100831, '<td valign="top">Great light! And a balloon!</td>', 'Great light! And a balloon!', '2021-11-15 13:34:19.000000', NULL, 1),
(7706748, 1265612, 100831, '<td valign="top">Love is in the air! Great catch!</td>', 'Love is in the air! Great catch!', '2021-11-15 14:24:36.000000', NULL, 1),
(7706750, 1265786, 100831, '<td valign="top">Love the close up view and saturated colors. Nice find.</td>', 'Love the close up view and saturated colors. Nice find.', '2021-11-15 14:25:16.000000', NULL, 1),
(7706752, 1265838, 100831, '<td valign="top">.. those who bloom. I like the wide view, creates movement.</td>', '.. those who bloom. I like the wide view, creates movement.', '2021-11-15 14:28:17.000000', NULL, 1),
(7706756, 1265827, 100831, '<td valign="top">the title pulls this together so nicely.</td>', 'the title pulls this together so nicely.', '2021-11-15 14:37:31.000000', NULL, 1),
(7706772, 1265612, 24454, '<td valign="top">Haha!  She seriously needs to go hang out with her girlfriends and leave that guy to his phone!  Great street photo and great title tho!  I love it!</td>', 'Haha!  She seriously needs to go hang out with her girlfriends and leave that guy to his phone!  Great street photo and great title tho!  I love it!', '2021-11-15 15:52:53.000000', NULL, 1),
(7706773, 1265843, 24454, '<td valign="top">So good!  I might think Lydia... but... hers are usually emerald green and lush-ey but definitely has her creative genius with the frog  :)</td>', 'So good!  I might think Lydia... but... hers are usually emerald green and lush-ey but definitely has her creative genius with the frog  :)', '2021-11-15 15:54:38.000000', NULL, 1),
(7706774, 1265841, 24454, '<td valign="top">What a beautiful portrait.  I just love this moody, vintage feel.</td>', 'What a beautiful portrait.  I just love this moody, vintage feel.', '2021-11-15 15:55:47.000000', NULL, 1),
(7706775, 1265774, 24454, '<td valign="top">I really love this.  I can definitely see this hanging on a wall enhancing a high-end contemporary decor.</td>', 'I really love this.  I can definitely see this hanging on a wall enhancing a high-end contemporary decor.', '2021-11-15 15:57:16.000000', NULL, 1),
(7706794, 1265818, 30982, '<td valign="top">This is a too!  I''m guessing Timfy.</td>', 'This is a too!  I''m guessing Timfy.', '2021-11-16 00:42:34.000000', NULL, 1),
(7706797, 1265786, 83313, '<td valign="top">Looks kinda Jebbish to me.</td>', 'Looks kinda Jebbish to me.', '2021-11-16 01:22:30.000000', NULL, 1),
(7706798, 1265831, 83313, '<td valign="top">JMRitz is my guess.</td>', 'JMRitz is my guess.', '2021-11-16 01:23:00.000000', NULL, 1),
(7706844, 1265777, 8759, '<td valign="top">Bon Appetit, Henk!</td>', 'Bon Appetit, Henk!', '2021-11-17 03:18:12.000000', NULL, 1),
(7706867, 1265590, 91360, '<td valign="top">Hi roz! congrta''s on your ribbon:)</td>', 'Hi roz! congrta''s on your ribbon:)', '2021-11-17 10:53:38.000000', NULL, 1),
(7706966, 1265777, 103142, '<td valign="top">Henk, is that you? Looks delicious! Makes me wonder what it would look like with the front one just a little to the right. It seems too lined up on the left hand side. I really like that you cropped the bottom half of the glass off. I would have left it in -- and that would have been so wrong! I love that you gave me an "aha!" moment</td>', 'Henk, is that you? Looks delicious! Makes me wonder what it would look like with the front one just a little to the right. It seems too lined up on the left hand side. I really like that you cropped the bottom half of the glass off. I would have left it in -- and that would have been so wrong! I love that you gave me an "aha!" moment', '2021-11-18 13:04:29.000000', NULL, 1),
(7706972, 1265612, 67258, '<td valign="top">I would say this is a  LevT  - the master of street photography and mono candids.  This doesn''t have the same fairly high contrast look that I usually associate with Lev, so I may be wrong.   The title works very well with the image, but beyond that, it doesn''t leave a lasting impression on me.</td>', 'I would say this is a  LevT  - the master of street photography and mono candids.  This doesn''t have the same fairly high contrast look that I usually associate with Lev, so I may be wrong.   The title works very well with the image, but beyond that, it doesn''t leave a lasting impression on me.', '2021-11-18 14:45:32.000000', NULL, 1),
(7706985, 1265648, 103142, '<td valign="top">Just be a MaryO. How are the doggies doing?</td>', 'Just be a MaryO. How are the doggies doing?', '2021-11-18 19:40:34.000000', NULL, 1),
(7706986, 1265590, 103142, '<td valign="top">Nice one, roz!</td>', 'Nice one, roz!', '2021-11-18 19:41:35.000000', NULL, 1),
(7706987, 1265827, 103142, '<td valign="top">Hmmmm not sure Im right is it a Mariuca?</td>', 'Hmmmm not sure Im right is it a Mariuca?', '2021-11-18 19:42:24.000000', NULL, 1),
(7706989, 1265423, 103142, '<td valign="top">A spiffy, perhaps?</td>', 'A spiffy, perhaps?', '2021-11-18 19:43:09.000000', NULL, 1),
(7706991, 1265843, 103142, '<td valign="top">Ummmm hard to guess. Lydia? ;)</td>', 'Ummmm hard to guess. Lydia? ;)', '2021-11-18 19:44:55.000000', NULL, 1),
(7706992, 1265704, 103142, '<td valign="top">This is really lovely! I love the treatment of it. I''d be really interesting in seeing the before and after and how you did it!</td>', 'This is really lovely! I love the treatment of it. I''d be really interesting in seeing the before and after and how you did it!', '2021-11-18 19:45:55.000000', NULL, 1),
(7706993, 1265827, 50641, '<td valign="top">Mariuca?  P.s. love that it looks like a csi serial killer corkboard!</td>', 'Mariuca?  P.s. love that it looks like a csi serial killer corkboard!', '2021-11-18 20:24:50.000000', NULL, 1),
(7706994, 1265777, 50641, '<td valign="top">Hajeka making me hungry again :)</td>', 'Hajeka making me hungry again :)', '2021-11-18 20:25:50.000000', NULL, 1),
(7706995, 1265775, 3306, '<td valign="top">Love the DOF. A beautiful scene.</td>', 'Love the DOF. A beautiful scene.', '2021-11-18 20:26:09.000000', NULL, 1),
(7706996, 1265804, 50641, '<td valign="top">Looks like my country too!</td>', 'Looks like my country too!', '2021-11-18 20:26:24.000000', NULL, 1),
(7706997, 1265590, 3306, '<td valign="top">Only you could do this Roz. Fantastic!</td>', 'Only you could do this Roz. Fantastic!', '2021-11-18 20:26:49.000000', NULL, 1),
(7706998, 1265648, 3306, '<td valign="top">So majestic. Well done portrait.</td>', 'So majestic. Well done portrait.', '2021-11-18 20:27:27.000000', NULL, 1),
(7706999, 1265843, 3306, '<td valign="top">You crack me up Lydia:)</td>', 'You crack me up Lydia:)', '2021-11-18 20:28:16.000000', NULL, 1),
(7707000, 1265814, 50641, '<td valign="top">I would almost peg Bear for title topic but image suggests the General.</td>', 'I would almost peg Bear for title topic but image suggests the General.', '2021-11-18 20:28:28.000000', NULL, 1),
(7707001, 1265704, 50641, '<td valign="top">Marnet?</td>', 'Marnet?', '2021-11-18 20:30:09.000000', NULL, 1),
(7707002, 1265803, 3306, '<td valign="top">Gotta love it!]</td>', 'Gotta love it!]', '2021-11-18 20:31:51.000000', NULL, 1),
(7707003, 1265586, 50641, '<td valign="top">lnede</td>', 'lnede', '2021-11-18 20:32:03.000000', NULL, 1),
(7707004, 1265844, 3306, '<td valign="top">Fanciful colors. Very attractive.</td>', 'Fanciful colors. Very attractive.', '2021-11-18 20:32:34.000000', NULL, 1),
(7707005, 1265831, 50641, '<td valign="top">hi

<br/>And thanks for keeping this place interesting.</td>', 'hi

And thanks for keeping this place interesting.', '2021-11-18 20:32:45.000000', NULL, 1),
(7707006, 1265774, 3306, '<td valign="top">Very surreal! I like it.</td>', 'Very surreal! I like it.', '2021-11-18 20:33:58.000000', NULL, 1),
(7707007, 1265774, 50641, '<td valign="top">Am reminded of gyaban but not sure he would blur this much.</td>', 'Am reminded of gyaban but not sure he would blur this much.', '2021-11-18 20:34:44.000000', NULL, 1),
(7707008, 1265590, 50641, '<td valign="top">One suspects Roz ;-)</td>', 'One suspects Roz ;-)', '2021-11-18 20:36:50.000000', NULL, 1),
(7707010, 1265841, 124815, '<td valign="top">A formidable photo. Sort of a B&amp;W Botticelli.

<br/>It''s an impulsive 9 before I look at all images and bump it to 10</td>', 'A formidable photo. Sort of a B&W Botticelli.

It''s an impulsive 9 before I look at all images and bump it to 10', '2021-11-18 21:14:10.000000', NULL, 1),
(7707020, 1265639, 68504, '<td valign="top">this is actually a very well considered composition, the canopy above painted with a delicate but steady hand, and the whole demonstrating an effective limited palette.</td>', 'this is actually a very well considered composition, the canopy above painted with a delicate but steady hand, and the whole demonstrating an effective limited palette.', '2021-11-18 22:48:18.000000', NULL, 1),
(7707021, 1265827, 68504, '<td valign="top">all about lines.</td>', 'all about lines.', '2021-11-18 22:49:16.000000', NULL, 1),
(7707022, 1265839, 68504, '<td valign="top">catwalk, even Hitchcockliche. youmex.</td>', 'catwalk, even Hitchcockliche. youmex.', '2021-11-18 22:51:03.000000', NULL, 1),
(7707023, 1265831, 68504, '<td valign="top">well, there you are, jm.</td>', 'well, there you are, jm.', '2021-11-18 22:51:44.000000', NULL, 1),
(7707025, 1265841, 68504, '<td valign="top">well, this is lovely.</td>', 'well, this is lovely.', '2021-11-18 22:52:47.000000', NULL, 1),
(7707027, 1265648, 68504, '<td valign="top">surprise surprise?</td>', 'surprise surprise?', '2021-11-18 22:53:23.000000', NULL, 1),
(7707028, 1265829, 68504, '<td valign="top">the power.</td>', 'the power.', '2021-11-18 22:53:48.000000', NULL, 1),
(7707031, 1265805, 68504, '<td valign="top">dreamy, good use of understatement.</td>', 'dreamy, good use of understatement.', '2021-11-18 22:55:54.000000', NULL, 1),
(7707032, 1265777, 68504, '<td valign="top">still waiting for an invite.</td>', 'still waiting for an invite.', '2021-11-18 22:57:06.000000', NULL, 1),
(7707034, 1265838, 68504, '<td valign="top">and it hurts the eyes, the light like tree needles.</td>', 'and it hurts the eyes, the light like tree needles.', '2021-11-18 22:58:02.000000', NULL, 1),
(7707035, 1265843, 68504, '<td valign="top">no, really. never seen Toad so grumpy. he told you he didn''t want to wear that hat.</td>', 'no, really. never seen Toad so grumpy. he told you he didn''t want to wear that hat.', '2021-11-18 22:59:12.000000', NULL, 1),
(7707036, 1265814, 68504, '<td valign="top">refreshing to see that bald bold connubial conjunction of red and blue. makes me feel young.</td>', 'refreshing to see that bald bold connubial conjunction of red and blue. makes me feel young.', '2021-11-18 23:00:39.000000', NULL, 1),
(7707037, 1265612, 68504, '<td valign="top">she gave you everything, you swine.</td>', 'she gave you everything, you swine.', '2021-11-18 23:01:20.000000', NULL, 1),
(7707038, 1265847, 68504, '<td valign="top">wow.</td>', 'wow.', '2021-11-18 23:01:40.000000', NULL, 1),
(7707039, 1265803, 68504, '<td valign="top">they should stop meeting like that.</td>', 'they should stop meeting like that.', '2021-11-18 23:02:10.000000', NULL, 1),
(7707040, 1265821, 68504, '<td valign="top">wow. this is the second conjunction of two primary colours in this challenge. excellent light...</td>', 'wow. this is the second conjunction of two primary colours in this challenge. excellent light...', '2021-11-18 23:03:28.000000', NULL, 1),
(7707041, 1265775, 68504, '<td valign="top">impressive, thingfish. the rocks look like beached and barnacled seals, otters, walruses and creatures we don''t even know about.</td>', 'impressive, thingfish. the rocks look like beached and barnacled seals, otters, walruses and creatures we don''t even know about.', '2021-11-18 23:04:47.000000', NULL, 1),
(7707042, 1265833, 68504, '<td valign="top">this looks like curtains, a gentle decor.</td>', 'this looks like curtains, a gentle decor.', '2021-11-18 23:05:53.000000', NULL, 1),
(7707043, 1265804, 68504, '<td valign="top">and this is a nice one. you have darkened your usual palette, effectively.</td>', 'and this is a nice one. you have darkened your usual palette, effectively.', '2021-11-18 23:06:58.000000', NULL, 1),
(7707044, 1265586, 68504, '<td valign="top">I don''t think anyone has ever filmed the traditional drowning of grownups who crash children''s parties before. Not sure he should look surprised,though.</td>', 'I don''t think anyone has ever filmed the traditional drowning of grownups who crash children''s parties before. Not sure he should look surprised,though.', '2021-11-18 23:09:09.000000', NULL, 1),
(7707045, 1265704, 68504, '<td valign="top">many light layers of fabric in a gentle breeze; drifting off to sleep.</td>', 'many light layers of fabric in a gentle breeze; drifting off to sleep.', '2021-11-18 23:10:21.000000', NULL, 1),
(7707046, 1265786, 68504, '<td valign="top">oh you! still trying to fix the unfixable.</td>', 'oh you! still trying to fix the unfixable.', '2021-11-18 23:10:51.000000', NULL, 1),
(7707047, 1265824, 68504, '<td valign="top">well shoot, I love me a good caption.</td>', 'well shoot, I love me a good caption.', '2021-11-18 23:11:19.000000', NULL, 1),
(7707048, 1265825, 68504, '<td valign="top">well shown, this transformation.</td>', 'well shown, this transformation.', '2021-11-18 23:15:21.000000', NULL, 1),
(7707049, 1265707, 68504, '<td valign="top">its that wedge of pure blue that makes that Mr. Green bearable.</td>', 'its that wedge of pure blue that makes that Mr. Green bearable.', '2021-11-18 23:17:31.000000', NULL, 1),
(7707050, 1265711, 68504, '<td valign="top">great grit. that balloon, that wheel totally weights this.</td>', 'great grit. that balloon, that wheel totally weights this.', '2021-11-18 23:20:48.000000', NULL, 1),
(7707057, 1265803, 67145, '<td valign="top">this was always going to be a winner .. 

<br/>i cant imagine how you were able to photograph this little creature so wonderfully .. 

<br/>this is up there are one of the most excellent pics i''ve seen here in dpc .. 

<br/>i mean .. i love animals .. and i love cameras .. so what''s not to like . !! .. 

<br/>
<br/>oh . and i have a feeling that little squirrel got a treat for his great ''performance'' .. 

<br/>this is AWESOME .. :)</td>', 'this was always going to be a winner .. 

i cant imagine how you were able to photograph this little creature so wonderfully .. 

this is up there are one of the most excellent pics i''ve seen here in dpc .. 

i mean .. i love animals .. and i love cameras .. so what''s not to like . !! .. 


oh . and i have a feeling that little squirrel got a treat for his great ''performance'' .. 

this is AWESOME .. :)', '2021-11-19 00:20:06.000000', NULL, 0),
(7707059, 1265586, 67145, '<td valign="top">i love this so much .. 

<br/>and i loved reading your notes .. 

<br/>i do feel that photography isnt always about great technicals but the emotion a photo creates in the viewer .. if you can nail both .. how great is that .. and you do .. 

<br/>you are a master of this art .. and i am in awe of your imagination and creativity .. 

<br/>this really did bring a smile to my face btw .. and i immediately thought of you when i first opened it .. 

<br/>many congratulations on another wonderful quirky and unforgettable image .. xx</td>', 'i love this so much .. 

and i loved reading your notes .. 

i do feel that photography isnt always about great technicals but the emotion a photo creates in the viewer .. if you can nail both .. how great is that .. and you do .. 

you are a master of this art .. and i am in awe of your imagination and creativity .. 

this really did bring a smile to my face btw .. and i immediately thought of you when i first opened it .. 

many congratulations on another wonderful quirky and unforgettable image .. xx', '2021-11-19 00:28:23.000000', NULL, 0),
(7707060, 1265612, 67145, '<td valign="top">absolutely BRILLIANT .. 

<br/>what an amazing catch .. and loving your title . 

<br/>should most definitely been in the top 5 .. at least .. 

<br/>but of course i''m in awe of an amazing street photog and i love black and white .. so i am slightly biased .. !! .. ;)

<br/>tick tick tick tick .. 

<br/>LOVE THIS . !! .. :)</td>', 'absolutely BRILLIANT .. 

what an amazing catch .. and loving your title . 

should most definitely been in the top 5 .. at least .. 

but of course i''m in awe of an amazing street photog and i love black and white .. so i am slightly biased .. !! .. ;)

tick tick tick tick .. 

LOVE THIS . !! .. :)', '2021-11-19 00:31:29.000000', NULL, 0),
(7707061, 1265847, 68504, '<td valign="top">top choice. thought it might be yours.</td>', 'top choice. thought it might be yours.', '2021-11-19 00:35:00.000000', NULL, 0),
(7707062, 1265711, 67145, '<td valign="top">i''m loving this A LOT . 

<br/>the black and white .. the contrast .. the light ..  and the stunning shadows .. 

<br/>congrats on something that i think is wonderful .. the voters dont know whether their pants are on fire some of the time .. ;)</td>', 'i''m loving this A LOT . 

the black and white .. the contrast .. the light ..  and the stunning shadows .. 

congrats on something that i think is wonderful .. the voters dont know whether their pants are on fire some of the time .. ;)', '2021-11-19 00:35:06.000000', NULL, 0),
(7707064, 1265844, 50641, '<td valign="top">Very true to you. And happy belated birdy too.</td>', 'Very true to you. And happy belated birdy too.', '2021-11-19 00:45:41.000000', NULL, 0),
(7707065, 1265844, 99263, '<td valign="top">This should have done way better...it''s like a beautiful finely woven tapestry</td>', 'This should have done way better...it''s like a beautiful finely woven tapestry', '2021-11-19 01:10:13.000000', NULL, 0);
INSERT INTO comments ("id", "image_id", "commenter_id", "raw_comment", "comment", "date", "edited", "made_during_challenge") VALUES
(7707066, 1265806, 99263, '<td valign="top">Signing off? I hope not</td>', 'Signing off? I hope not', '2021-11-19 01:12:21.000000', NULL, 0),
(7707068, 1265803, 123833, '<td valign="top">The white borders and the Minolta confused me :) Congrats on the Blue!</td>', 'The white borders and the Minolta confused me :) Congrats on the Blue!', '2021-11-19 02:13:03.000000', NULL, 0),
(7707072, 1265806, 101668, '<td valign="top"><table align="center" width="95%"><tr><td><div class="textsm"><b>Originally posted by ThingFish:</b></div><hr/><i> Signing off? I hope not </i></td></tr></table>
<br/>Sinspeel op die Challenge. Nee ek sal nie.</td>', 'Originally posted by ThingFish: Signing off? I hope not 
Sinspeel op die Challenge. Nee ek sal nie.', '2021-11-19 06:26:24.000000', NULL, 0),
(7707089, 1265803, 109227, '<td valign="top">No mystery as to who took this image, lol.  Great shot and I really like the set-up.  Congrats!</td>', 'No mystery as to who took this image, lol.  Great shot and I really like the set-up.  Congrats!', '2021-11-19 10:36:47.000000', NULL, 0),
(7707091, 1265590, 109227, '<td valign="top">It had to be youuuuuuu!  Nicely done Roz, your macros are so spot on.</td>', 'It had to be youuuuuuu!  Nicely done Roz, your macros are so spot on.', '2021-11-19 10:37:33.000000', NULL, 0),
(7707092, 1265704, 109227, '<td valign="top">I love this Margaret, so beautifully done.</td>', 'I love this Margaret, so beautifully done.', '2021-11-19 10:38:06.000000', NULL, 0),
(7707094, 1265590, 86447, '<td valign="top">POor you!  Poor Toddie!!

<br/>
<br/>Excellently done, as usual, Roz!  

<br/>
<br/>Congratulations on your RIBBON!

<br/></td>', 'POor you!  Poor Toddie!!


Excellently done, as usual, Roz!  


Congratulations on your RIBBON!

', '2021-11-19 11:21:29.000000', NULL, 0),
(7707095, 1265819, 86447, '<td valign="top">This is lovely.  As usual. :D

<br/>
<br/>Congratulations!</td>', 'This is lovely.  As usual. :D


Congratulations!', '2021-11-19 11:22:16.000000', NULL, 0),
(7707096, 1265841, 86447, '<td valign="top">Gorgeous!   I''m  not surprised.  :D

<br/>
<br/>Congrats on your HM!

<br/></td>', 'Gorgeous!   I''m  not surprised.  :D


Congrats on your HM!

', '2021-11-19 11:23:41.000000', NULL, 0),
(7707097, 1265704, 86447, '<td valign="top">This is SUCH a Margaret masterpiece!

<br/>
<br/>Congratulations on your HM!

<br/></td>', 'This is SUCH a Margaret masterpiece!


Congratulations on your HM!

', '2021-11-19 11:24:15.000000', NULL, 0),
(7707098, 1265618, 86447, '<td valign="top">Oh!   You got a Roz guess!   Congratulations on that great compliment and on your Top Ten!  :D

<br/></td>', 'Oh!   You got a Roz guess!   Congratulations on that great compliment and on your Top Ten!  :D

', '2021-11-19 11:25:09.000000', NULL, 0),
(7707099, 1265844, 30982, '<td valign="top">The shifted hues create such a gorgeous display - much like Fall herself does!</td>', 'The shifted hues create such a gorgeous display - much like Fall herself does!', '2021-11-19 11:26:29.000000', NULL, 0),
(7707100, 1265843, 30982, '<td valign="top">Wasn''t sure this was you because you always have titles!  But the bemused look on the poor toad''s face said it was...</td>', 'Wasn''t sure this was you because you always have titles!  But the bemused look on the poor toad''s face said it was...', '2021-11-19 11:27:22.000000', NULL, 0),
(7707101, 1265818, 30982, '<td valign="top">She is all grown up now!  I remember when they were just kids in their pjs.</td>', 'She is all grown up now!  I remember when they were just kids in their pjs.', '2021-11-19 11:28:01.000000', NULL, 0),
(7707103, 1265774, 86447, '<td valign="top">This is FABULOUS!

<br/>
<br/>AND you got TWO Gyaban references!

<br/>
<br/>Congratulations on both!

<br/></td>', 'This is FABULOUS!


AND you got TWO Gyaban references!


Congratulations on both!

', '2021-11-19 11:31:22.000000', NULL, 0),
(7707105, 1265586, 86447, '<td valign="top">I did laugh when I saw it, Larry!   I knew it was you, also.  I thought I commented on it during voting...

<br/>
<br/>Oh well, I''m doing it now.  :D

<br/>
<br/>Congratulations on your Top Ten!  And your signature style!  :D</td>', 'I did laugh when I saw it, Larry!   I knew it was you, also.  I thought I commented on it during voting...


Oh well, I''m doing it now.  :D


Congratulations on your Top Ten!  And your signature style!  :D', '2021-11-19 11:33:12.000000', NULL, 0),
(7707106, 1265648, 86447, '<td valign="top">I love your wolfhound shots, Mary!

<br/></td>', 'I love your wolfhound shots, Mary!

', '2021-11-19 11:33:57.000000', NULL, 0),
(7707107, 1265707, 86447, '<td valign="top">Pretty, as usual.

<br/>
<br/>Welcome home.

<br/>:D

<br/></td>', 'Pretty, as usual.


Welcome home.

:D

', '2021-11-19 11:35:10.000000', NULL, 0),
(7707108, 1265805, 100831, '<td valign="top">I did not peg this one to the author, but I love it. Great feeling here.</td>', 'I did not peg this one to the author, but I love it. Great feeling here.', '2021-11-19 11:49:27.000000', NULL, 0),
(7707109, 1265805, 62357, '<td valign="top">Ah now I guessed totally wrong on this, however it was my favourite by a country mile.  Gorgeous.</td>', 'Ah now I guessed totally wrong on this, however it was my favourite by a country mile.  Gorgeous.', '2021-11-19 11:53:40.000000', NULL, 0),
(7707110, 1265704, 62357, '<td valign="top">Lovely</td>', 'Lovely', '2021-11-19 11:55:21.000000', NULL, 0),
(7707111, 1265841, 38032, '<td valign="top">Im a buttmunch for not voting on this challenge . This has you all over it &amp;#128079;&amp;#128079;&amp;#128079;</td>', 'Im a buttmunch for not voting on this challenge . This has you all over it &#128079;&#128079;&#128079;', '2021-11-19 11:56:16.000000', NULL, 0),
(7707113, 1265618, 23098, '<td valign="top"><table align="center" width="95%"><tr><td><div class="textsm"><b>Originally posted by Lydia:</b></div><hr/><i> Oh!   You got a Roz guess!   Congratulations on that great compliment and on your Top Ten!  :D </i></td></tr></table>
<br/>
<br/>Thanks <img alt="'' . substr(''https://www.dpchallenge.com/images/user_icon/21_F.gif'', strrpos(''https://www.dpchallenge.com/images/user_icon/21_F.gif'', ''/'') + 1) . ''" border="0" src="https://www.dpchallenge.com/images/user_icon/21_F.gif"/> <a href="https://www.dpchallenge.com/profile.php?USER_ID=86447" rel="nofollow" target="_blank">Lydia</a>and <img alt="'' . substr(''https://www.dpchallenge.com/images/user_icon/21.gif'', strrpos(''https://www.dpchallenge.com/images/user_icon/21.gif'', ''/'') + 1) . ''" border="0" src="https://www.dpchallenge.com/images/user_icon/21.gif"/> <a href="https://www.dpchallenge.com/profile.php?USER_ID=30214" rel="nofollow" target="_blank">LevT</a>, Indeed, comparison to <img alt="'' . substr(''https://www.dpchallenge.com/images/user_icon/21_F.gif'', strrpos(''https://www.dpchallenge.com/images/user_icon/21_F.gif'', ''/'') + 1) . ''" border="0" src="https://www.dpchallenge.com/images/user_icon/21_F.gif"/> <a href="https://www.dpchallenge.com/profile.php?USER_ID=67145" rel="nofollow" target="_blank">Roz</a> is an appreciated and great compliment.</td>', 'Originally posted by Lydia: Oh!   You got a Roz guess!   Congratulations on that great compliment and on your Top Ten!  :D 

Thanks  Lydiaand  LevT, Indeed, comparison to  Roz is an appreciated and great compliment.', '2021-11-19 12:12:45.000000', NULL, 0),
(7707114, 1265841, 30214, '<td valign="top">Well, at least my second guess was correct (should''ve been the first guess, in the hindsight). Good job Elena, and good job Robert in unambiguously identifying her style!</td>', 'Well, at least my second guess was correct (should''ve been the first guess, in the hindsight). Good job Elena, and good job Robert in unambiguously identifying her style!', '2021-11-19 12:55:43.000000', NULL, 0),
(7707115, 1265711, 50695, '<td valign="top">hey I thought you were jagar in France so that should count for something. I was also your top score.</td>', 'hey I thought you were jagar in France so that should count for something. I was also your top score.', '2021-11-19 13:44:29.000000', NULL, 0),
(7707131, 1265841, 170018, '<td valign="top"><table align="center" width="95%"><tr><td><div class="textsm"><b>Originally posted by tate:</b></div><hr/><i> Im a buttmunch for not voting on this challenge . This has you all over it &amp;#128079;&amp;#128079;&amp;#128079; </i></td></tr></table> The signature crop, recommended by a master! :-)</td>', 'Originally posted by tate: Im a buttmunch for not voting on this challenge . This has you all over it &#128079;&#128079;&#128079;  The signature crop, recommended by a master! :-)', '2021-11-19 17:15:46.000000', NULL, 0),
(7707132, 1265612, 170018, '<td valign="top">You keep "catching" life in it''s funny, surreal, or quirky moments! 

<br/>That''s why I thought that you might have been the author of Melethia''s shot, and compared a structure in Disney to pepelatz! :-))</td>', 'You keep "catching" life in it''s funny, surreal, or quirky moments! 

That''s why I thought that you might have been the author of Melethia''s shot, and compared a structure in Disney to pepelatz! :-))', '2021-11-19 17:28:22.000000', NULL, 0),
(7707137, 1265704, 67145, '<td valign="top">stunning .. I absolutely love this .. 

<br/>much better than the one that came second .. this is pure art .. and beautiful as well .. you are such a creative .. xx</td>', 'stunning .. I absolutely love this .. 

much better than the one that came second .. this is pure art .. and beautiful as well .. you are such a creative .. xx', '2021-11-19 17:52:52.000000', NULL, 0),
(7707159, 1265803, 91360, '<td valign="top">fantastic image Wendy. congrats on the blue!<br/><br/><i>Message edited by author 2021-11-20 05:27:50.</i></td>', 'fantastic image Wendy. congrats on the blue!', '2021-11-20 05:27:32.000000', '2021-11-20 05:27:50.000000', 0),
(7707160, 1265803, 97225, '<td valign="top">Congrats on the blue, Wendy. Super-dooper!</td>', 'Congrats on the blue, Wendy. Super-dooper!', '2021-11-20 07:19:43.000000', NULL, 0),
(7707162, 1265814, 173844, '<td valign="top">Beautiful, and kind of a statement about beauty.  Love the colors, the transition between them, the abrupt curtaining of nightfall, the silhouetted, feathery treetops, the mood of peace and wonder.

<br/>Personal favorite of the challenge.</td>', 'Beautiful, and kind of a statement about beauty.  Love the colors, the transition between them, the abrupt curtaining of nightfall, the silhouetted, feathery treetops, the mood of peace and wonder.

Personal favorite of the challenge.', '2021-11-20 09:28:29.000000', NULL, 0),
(7707163, 1265841, 173844, '<td valign="top">Beautiful portrait, handsomely achieved.</td>', 'Beautiful portrait, handsomely achieved.', '2021-11-20 09:33:08.000000', NULL, 0),
(7707164, 1265704, 173844, '<td valign="top">Like a day in the woods as the wind whispers of eternity.  Lovely and evocative.</td>', 'Like a day in the woods as the wind whispers of eternity.  Lovely and evocative.', '2021-11-20 09:36:30.000000', NULL, 0),
(7707191, 1265774, 28742, '<td valign="top">This was one of my favorites - gave it a 9. It speaks to me for some reason.</td>', 'This was one of my favorites - gave it a 9. It speaks to me for some reason.', '2021-11-21 05:41:23.000000', NULL, 0),
(7707197, 1265803, 122678, '<td valign="top">Congratulations

<br/>Wow, a well designed image, perfectly presented, crisp, clear with beautiful colors. I love how you mastered this squirrel. On a scale of 1 to 10 this is a 15.

<br/>I voted 10 there was no 15. Hats off to you!</td>', 'Congratulations

Wow, a well designed image, perfectly presented, crisp, clear with beautiful colors. I love how you mastered this squirrel. On a scale of 1 to 10 this is a 15.

I voted 10 there was no 15. Hats off to you!', '2021-11-21 07:29:22.000000', NULL, 0),
(7707198, 1265590, 122678, '<td valign="top">Congratulations 

<br/>Yes.. Roz, of course, spell check on my computer UGH!!! But I knew it had to by yours.

<br/>Beautifully executed with your gorgeous colors in the bug and background.</td>', 'Congratulations 

Yes.. Roz, of course, spell check on my computer UGH!!! But I knew it had to by yours.

Beautifully executed with your gorgeous colors in the bug and background.', '2021-11-21 07:32:41.000000', NULL, 0),
(7707199, 1265819, 122678, '<td valign="top">Congratulations, on this masterpiece image.

<br/>I was not sure who the photographer was on this but I did see all its beauty.</td>', 'Congratulations, on this masterpiece image.

I was not sure who the photographer was on this but I did see all its beauty.', '2021-11-21 07:36:09.000000', NULL, 0),
(7707200, 1265841, 122678, '<td valign="top">Lovely image and I like cropping style you chose.

<br/>Beautiful work.</td>', 'Lovely image and I like cropping style you chose.

Beautiful work.', '2021-11-21 07:40:11.000000', NULL, 0),
(7707201, 1265704, 122678, '<td valign="top">Beautiful image and very much in your style of photographic painting. A simple, dreamy and gorgeous image.</td>', 'Beautiful image and very much in your style of photographic painting. A simple, dreamy and gorgeous image.', '2021-11-21 07:42:05.000000', NULL, 0),
(7707202, 1265618, 122678, '<td valign="top">Beautiful creature and well presented 8.</td>', 'Beautiful creature and well presented 8.', '2021-11-21 07:42:56.000000', NULL, 0),
(7707203, 1265774, 122678, '<td valign="top">Beautiful and very creative.</td>', 'Beautiful and very creative.', '2021-11-21 07:43:57.000000', NULL, 0),
(7707204, 1265586, 122678, '<td valign="top">Another really great image, 10 from me.

<br/>You have an unbelievable mind to go for the shots you go for and they are all well presented. You are a very talented photographer, nice work</td>', 'Another really great image, 10 from me.

You have an unbelievable mind to go for the shots you go for and they are all well presented. You are a very talented photographer, nice work', '2021-11-21 07:46:18.000000', NULL, 0),
(7707205, 1265648, 122678, '<td valign="top">Beautiful dog and yes I do remember him as the subject of a few of your images.</td>', 'Beautiful dog and yes I do remember him as the subject of a few of your images.', '2021-11-21 07:47:27.000000', NULL, 0),
(7707206, 1265707, 122678, '<td valign="top">Stunning image and very much your style. You are so lucky to live where you live to see such beauty and capture it.</td>', 'Stunning image and very much your style. You are so lucky to live where you live to see such beauty and capture it.', '2021-11-21 07:49:18.000000', NULL, 0),
(7707207, 1265775, 122678, '<td valign="top">Stunning image, a beautiful beach. I looked to see where this was taken.</td>', 'Stunning image, a beautiful beach. I looked to see where this was taken.', '2021-11-21 07:52:41.000000', NULL, 0),
(7707208, 1265612, 122678, '<td valign="top">I got this one correct. You have an eye for a good catch.</td>', 'I got this one correct. You have an eye for a good catch.', '2021-11-21 07:54:17.000000', NULL, 0),
(7707209, 1265821, 122678, '<td valign="top">Beautiful, the lighting was the giveaway for me. Your eye for color and lighting is amazing. I have always been intrigued by natural lighting and your images look like you are so at ease with it.</td>', 'Beautiful, the lighting was the giveaway for me. Your eye for color and lighting is amazing. I have always been intrigued by natural lighting and your images look like you are so at ease with it.', '2021-11-21 07:58:37.000000', NULL, 0),
(7707210, 1265839, 122678, '<td valign="top">Really nice image and your beautiful cat.</td>', 'Really nice image and your beautiful cat.', '2021-11-21 07:59:13.000000', NULL, 0),
(7707211, 1265777, 122678, '<td valign="top">Very nice image, will open my eyes wider to your work. I tried to figure this out but I must admit I didn''t recognize your work here.</td>', 'Very nice image, will open my eyes wider to your work. I tried to figure this out but I must admit I didn''t recognize your work here.', '2021-11-21 08:02:37.000000', NULL, 0),
(7707216, 1265843, 122678, '<td valign="top">I got this one right. I became a follower of your work back with the frogs. Those images were amazing and so well done. I know you have come a long way from then but I still love them and remember them. Your work is commendable.

<br/>I think more people were able to identify your work.</td>', 'I got this one right. I became a follower of your work back with the frogs. Those images were amazing and so well done. I know you have come a long way from then but I still love them and remember them. Your work is commendable.

I think more people were able to identify your work.', '2021-11-21 08:24:09.000000', NULL, 0),
(7707217, 1265711, 122678, '<td valign="top">I love this! Great title.</td>', 'I love this! Great title.', '2021-11-21 08:25:53.000000', NULL, 0),
(7707218, 1265834, 122678, '<td valign="top">Lovely image and certainly your amazing style.</td>', 'Lovely image and certainly your amazing style.', '2021-11-21 08:26:37.000000', NULL, 0),
(7707219, 1265816, 122678, '<td valign="top">I really like this image one of my favorites of the challenge. This clock is beautiful.</td>', 'I really like this image one of my favorites of the challenge. This clock is beautiful.', '2021-11-21 08:28:36.000000', NULL, 0),
(7707220, 1265806, 122678, '<td valign="top">This is a beautiful image, I gave it a high score, I love the sky, fog and the clouds. Way under rated.</td>', 'This is a beautiful image, I gave it a high score, I love the sky, fog and the clouds. Way under rated.', '2021-11-21 08:31:09.000000', NULL, 0),
(7707221, 1265423, 122678, '<td valign="top">Very nice image.</td>', 'Very nice image.', '2021-11-21 08:31:59.000000', NULL, 0);
COMMIT;

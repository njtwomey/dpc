-- schema for the dpc archive
PRAGMA foreign_keys=OFF;
BEGIN TRANSACTION;

-- table: alembic_version
CREATE TABLE alembic_version (
	version_num VARCHAR(32) NOT NULL, 
	CONSTRAINT alembic_version_pkc PRIMARY KEY (version_num)
);

-- table: award_grants
CREATE TABLE award_grants (
	id INTEGER NOT NULL, 
	award_id INTEGER NOT NULL, 
	recipient_id INTEGER NOT NULL, 
	comment_id INTEGER, 
	image_id INTEGER NOT NULL, 
	challenge_id INTEGER NOT NULL, 
	PRIMARY KEY (id), 
	CONSTRAINT uq_grant_award_image UNIQUE (award_id, image_id), 
	CONSTRAINT uq_grant_award_comment UNIQUE (award_id, comment_id), 
	FOREIGN KEY(award_id) REFERENCES awards (id) ON DELETE CASCADE, 
	FOREIGN KEY(recipient_id) REFERENCES members (id) ON DELETE CASCADE, 
	FOREIGN KEY(comment_id) REFERENCES comments (id) ON DELETE CASCADE, 
	FOREIGN KEY(image_id) REFERENCES images (id) ON DELETE CASCADE, 
	FOREIGN KEY(challenge_id) REFERENCES challenges (id) ON DELETE CASCADE
);

-- table: awards
CREATE TABLE awards (
	id INTEGER NOT NULL, 
	awarder_id INTEGER NOT NULL, 
	name VARCHAR(128) NOT NULL, 
	slug VARCHAR(128) NOT NULL, 
	description TEXT NOT NULL, 
	image_src VARCHAR(512) NOT NULL, 
	markers JSON NOT NULL, 
	PRIMARY KEY (id), 
	CONSTRAINT uq_award_awarder_name UNIQUE (awarder_id, name), 
	FOREIGN KEY(awarder_id) REFERENCES members (id) ON DELETE CASCADE
);

-- table: challenge_probes
CREATE TABLE challenge_probes (
	challenge_id INTEGER NOT NULL, 
	kind VARCHAR(16) NOT NULL, 
	checked_at DATETIME NOT NULL, 
	PRIMARY KEY (challenge_id)
);

-- table: challenges
CREATE TABLE challenges (
	id INTEGER NOT NULL, 
	name VARCHAR(256) NOT NULL, 
	description TEXT NOT NULL, 
	submission_start DATE NOT NULL, 
	submission_end DATE NOT NULL, 
	voting_start DATE NOT NULL, 
	voting_end DATE NOT NULL, 
	num_submissions INTEGER NOT NULL, 
	num_disqualifications INTEGER NOT NULL, 
	num_votes INTEGER NOT NULL, 
	num_comments INTEGER NOT NULL, 
	average_score FLOAT NOT NULL, 
	highest_score FLOAT NOT NULL, 
	median_score FLOAT NOT NULL, 
	lowest_score FLOAT NOT NULL, 
	PRIMARY KEY (id)
);

-- table: comments
CREATE TABLE comments (
	id INTEGER NOT NULL, 
	image_id INTEGER NOT NULL, 
	commenter_id INTEGER NOT NULL, 
	raw_comment TEXT NOT NULL, 
	comment TEXT NOT NULL, 
	date DATETIME NOT NULL, 
	edited DATETIME, 
	made_during_challenge BOOLEAN NOT NULL, 
	PRIMARY KEY (id), 
	FOREIGN KEY(image_id) REFERENCES images (id) ON DELETE CASCADE, 
	FOREIGN KEY(commenter_id) REFERENCES members (id) ON DELETE CASCADE
);

-- table: images
CREATE TABLE images (
	id INTEGER NOT NULL, 
	challenge_id INTEGER NOT NULL, 
	photographer_id INTEGER NOT NULL, 
	name VARCHAR(256) NOT NULL, 
	votes JSON NOT NULL, 
	disqualified BOOLEAN NOT NULL, 
	position INTEGER, 
	average_all FLOAT, 
	average_commenters FLOAT, 
	average_participants FLOAT, 
	average_non_participants FLOAT, 
	num_views INTEGER, 
	num_votes INTEGER, 
	PRIMARY KEY (id), 
	FOREIGN KEY(challenge_id) REFERENCES challenges (id) ON DELETE CASCADE, 
	FOREIGN KEY(photographer_id) REFERENCES members (id) ON DELETE CASCADE
);

-- table: members
CREATE TABLE members (
	id INTEGER NOT NULL, 
	name VARCHAR(128) NOT NULL, 
	join_date DATE, 
	cancelled BOOLEAN NOT NULL, 
	PRIMARY KEY (id)
);

-- index: ix_award_grants_award_id
CREATE INDEX ix_award_grants_award_id ON award_grants (award_id);

-- index: ix_award_grants_challenge_id
CREATE INDEX ix_award_grants_challenge_id ON award_grants (challenge_id);

-- index: ix_award_grants_comment_id
CREATE INDEX ix_award_grants_comment_id ON award_grants (comment_id);

-- index: ix_award_grants_image_id
CREATE INDEX ix_award_grants_image_id ON award_grants (image_id);

-- index: ix_award_grants_recipient_id
CREATE INDEX ix_award_grants_recipient_id ON award_grants (recipient_id);

-- index: ix_awards_awarder_id
CREATE INDEX ix_awards_awarder_id ON awards (awarder_id);

-- index: ix_awards_name
CREATE INDEX ix_awards_name ON awards (name);

-- index: ix_awards_slug
CREATE UNIQUE INDEX ix_awards_slug ON awards (slug);

-- index: ix_challenges_name
CREATE INDEX ix_challenges_name ON challenges (name);

-- index: ix_comments_commenter_id
CREATE INDEX ix_comments_commenter_id ON comments (commenter_id);

-- index: ix_comments_image_id
CREATE INDEX ix_comments_image_id ON comments (image_id);

-- index: ix_images_challenge_id
CREATE INDEX ix_images_challenge_id ON images (challenge_id);

-- index: ix_images_challenge_score
CREATE INDEX ix_images_challenge_score ON images (challenge_id, average_all);

-- index: ix_images_photographer_id
CREATE INDEX ix_images_photographer_id ON images (photographer_id);

-- index: ix_members_name
CREATE INDEX ix_members_name ON members (name);

COMMIT;

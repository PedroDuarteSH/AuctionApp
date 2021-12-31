CREATE TABLE bidding (
	id SERIAL,
	price	 FLOAT NOT NULL,
	bid_time	 TIMESTAMP NOT NULL,
	valid	 BOOL NOT NULL DEFAULT True,
	auction_id BIGINT,
	bidder_id	 INTEGER,
	PRIMARY KEY(id,auction_id,bidder_id)
);

CREATE TABLE users (
	id	 SERIAL,
	username	 VARCHAR(512) UNIQUE NOT NULL,
	email	 VARCHAR(512) UNIQUE NOT NULL,
	password	 VARCHAR(512) NOT NULL,
	is_admin	 BOOL NOT NULL DEFAULT False,
	is_banned BOOL NOT NULL DEFAULT False,
	ban_time	 TIMESTAMP,
	PRIMARY KEY(id)
);

CREATE TABLE auction (
	id		 SERIAL,
	EAN_ISBN   INTEGER NOT NULL,
	title	 VARCHAR(512) NOT NULL,
	item_name	 VARCHAR(512),
	description	 VARCHAR(512),
	end_time	 TIMESTAMP NOT NULL,
	current_price FLOAT,
	min_price	 FLOAT,
	start_date	 TIMESTAMP,
	seller_id	 INTEGER NOT NULL,
	finished	 BOOL NOT NULL DEFAULT False,
	canceled	 BOOL NOT NULL DEFAULT False,
	PRIMARY KEY(id)
);

CREATE TABLE history (
	id		 SERIAL,
	change_time	 TIMESTAMP,
	description	 VARCHAR(512) NOT NULL,
	title	 VARCHAR(512) NOT NULL,
	item_name	 VARCHAR(512) NOT NULL,
	change_price FLOAT,
	auction_id	 BIGINT NOT NULL,
	PRIMARY KEY(id,change_time)
);

CREATE TABLE notifications (
	id SERIAL,
	message	 VARCHAR(512) NOT NULL,
	mes_time TIMESTAMP NOT NULL,
	users_id INTEGER,
	PRIMARY KEY(id, users_id)
);

CREATE TABLE mural_message (
	id	 SERIAL,
	message	 VARCHAR(512),
	mes_time	 TIMESTAMP,
	auction_id BIGINT,
	users_id	 INTEGER,
	PRIMARY KEY(id,auction_id,users_id)
);


ALTER TABLE bidding ADD CONSTRAINT bidding_fk1 FOREIGN KEY (auction_id) REFERENCES auction(id);
ALTER TABLE bidding ADD CONSTRAINT bidding_fk2 FOREIGN KEY (bidder_id) REFERENCES users(id);
ALTER TABLE auction ADD CONSTRAINT auction_fk1 FOREIGN KEY (seller_id) REFERENCES users(id);
ALTER TABLE history ADD CONSTRAINT history_fk1 FOREIGN KEY (auction_id) REFERENCES auction(id);
ALTER TABLE notifications ADD CONSTRAINT notifications_fk1 FOREIGN KEY (users_id) REFERENCES users(id);
ALTER TABLE mural_message ADD CONSTRAINT mural_message_fk1 FOREIGN KEY (auction_id) REFERENCES auction(id);
ALTER TABLE mural_message ADD CONSTRAINT mural_message_fk2 FOREIGN KEY (users_id) REFERENCES users(id);
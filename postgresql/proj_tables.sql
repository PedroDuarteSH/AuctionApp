CREATE TABLE bidding (
	price	 BIGINT NOT NULL,
	bid_time	 TIMESTAMP NOT NULL,
	auction_id BIGINT,
	bidder	 INTEGER,
	PRIMARY KEY(bid_time, auction_id,bidder)
);

CREATE TABLE users (
	id	 SERIAL,
	username	 VARCHAR(512) UNIQUE NOT NULL,
	email	 VARCHAR(512) UNIQUE NOT NULL,
	password	 VARCHAR(512) NOT NULL,
	is_admin	 BOOL DEFAULT FALSE,
	is_banned BOOL DEFAULT FALSE,
	ban_time	 TIMESTAMP,
	PRIMARY KEY(id)
);

CREATE TABLE auction (
	id		 SERIAL,
	item_id	 INTEGER NOT NULL,
	title	 VARCHAR(512) NOT NULL,
	item_name	 VARCHAR(512) NOT NULL,
	description	 VARCHAR(512),
	end_time	 TIMESTAMP NOT NULL,
	start_time TIMESTAMP NOT NULL,
	current_price INTEGER,
	min_price	 FLOAT NOT NULL,
	seller_id	 INTEGER NOT NULL,
	PRIMARY KEY(id)
);

CREATE TABLE history (
	id		 SERIAL,
	change_time	 TIMESTAMP NOT NULL,
	description	 VARCHAR(512) NOT NULL,
	item_name	 VARCHAR(512) NOT NULL,
	changetime_price FLOAT(8),
	auction_id	 INTEGER NOT NULL,
	PRIMARY KEY(id)
);

CREATE TABLE notifications (
	mural_message_id INTEGER UNIQUE NOT NULL,
	users_id	 INTEGER,
	PRIMARY KEY(users_id)
);

CREATE TABLE mural_message (
	id	 SERIAL,
	message	 VARCHAR(512) NOT NULL,
	mes_time	 TIMESTAMP NOT NULL,
	auction_id BIGINT NOT NULL,
	users_id	 INTEGER NOT NULL,
	PRIMARY KEY(id)
);

ALTER TABLE bidding ADD CONSTRAINT bidding_fk1 FOREIGN KEY (auction_id) REFERENCES auction(id);
ALTER TABLE bidding ADD CONSTRAINT bidding_fk2 FOREIGN KEY (bidder) REFERENCES users(id);
ALTER TABLE auction ADD CONSTRAINT auction_fk1 FOREIGN KEY (seller_id) REFERENCES users(id);
ALTER TABLE history ADD CONSTRAINT history_fk1 FOREIGN KEY (auction_id) REFERENCES auction(id);
ALTER TABLE notifications ADD CONSTRAINT notifications_fk1 FOREIGN KEY (mural_message_id) REFERENCES mural_message(id);
ALTER TABLE notifications ADD CONSTRAINT notifications_fk2 FOREIGN KEY (users_id) REFERENCES users(id);
ALTER TABLE mural_message ADD CONSTRAINT mural_message_fk1 FOREIGN KEY (auction_id) REFERENCES auction(id);
ALTER TABLE mural_message ADD CONSTRAINT mural_message_fk2 FOREIGN KEY (users_id) REFERENCES users(id);
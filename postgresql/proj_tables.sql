CREATE TABLE bidding (
	price		 INTEGER NOT NULL,
	bid_time	 TIMESTAMP NOT NULL,
	auction_id INTEGER NOT NULL,
	bidder	 INTEGER NOT NULL
);

CREATE TABLE users (
	id	 SERIAL,
	username VARCHAR(512) UNIQUE NOT NULL,
	email	 VARCHAR(512) UNIQUE NOT NULL,
	password VARCHAR(512) NOT NULL,
	PRIMARY KEY(id)
);

CREATE TABLE auction_item (
	id		 SERIAL ,
	title		 VARCHAR(512) NOT NULL,
	description	 VARCHAR(512),
	end_time	 TIMESTAMP NOT NULL,
	current_price	 INTEGER,
	item_name	 VARCHAR(512) NOT NULL,
	item_min_price	 INTEGER NOT NULL,
	item_description VARCHAR(512),
	Seller_Id	 INTEGER NOT NULL,
	PRIMARY KEY(id)
);

CREATE TABLE private_message (
	user_Sended		 INTEGER NOT NULL,
	user_Recieved		 INTEGER NOT NULL,
	message_text VARCHAR(512) NOT NULL,
	message_time	 TIMESTAMP NOT NULL
);

CREATE TABLE mural_message (
	user_Sended		 INTEGER,
	auction_id	 INTEGER NOT NULL,
	message_text VARCHAR(512) NOT NULL,
	message_time	 TIMESTAMP NOT NULL
);

ALTER TABLE bidding ADD CONSTRAINT bidding_fk1 FOREIGN KEY (auction_id) REFERENCES auction_item(id);
ALTER TABLE bidding ADD CONSTRAINT bidding_fk2 FOREIGN KEY (bidder) REFERENCES users(id);
ALTER TABLE auction_item ADD CONSTRAINT auction_item_fk1 FOREIGN KEY (Seller_Id) REFERENCES users(id);
ALTER TABLE private_message ADD CONSTRAINT private_message_fk1 FOREIGN KEY (user_Sended) REFERENCES users(id);
ALTER TABLE private_message ADD CONSTRAINT private_message_fk2 FOREIGN KEY (user_Recieved) REFERENCES users(id);
ALTER TABLE mural_message ADD CONSTRAINT mural_message_fk1 FOREIGN KEY (user_Sended) REFERENCES users(id);
ALTER TABLE mural_message ADD CONSTRAINT mural_message_fk2 FOREIGN KEY (auction_id) REFERENCES auction_item(id);

--Insert Users:

INSERT INTO users (username, email, password)
VALUES ('Adriana1234', 'Adriana1234@gmail.pt', 'Adriana1234');

INSERT INTO users (username, email, password)
VALUES ('Tchabes1234', 'Tchabes1234@gmail.pt', 'Tchabes1234');

INSERT INTO users (username, email, password)
VALUES ('Duarte1234', 'Duarte1234@gmail.pt', 'Duarte1234');


--Criar leilão:

Insert into auction_item (title, description, end_time, item_name, item_min_price, item_description, seller_id)
Values ('Leilao de Relogio', 'Vendo relogio porque nao tenho pulsos', TIMESTAMP '2021-05-01 00:00:00', 'Relogio', 200, 'Relogio de Pulso', 1);

--Criar Bids: (Falta logica de verificar preços)

insert into bidding (price, bid_time, auction_id, bidder)
Values(300, current_timestamp, 1, 3);

insert into bidding (price, bid_time, auction_id, bidder)
Values(1100, current_timestamp, 1, 2);

insert into bidding (price, bid_time, auction_id, bidder)
Values(1000, current_timestamp, 1, 3);

--Inserir mensagens mural (Sistema):

insert into mural_message (auction_id, message_text, message_time)
values(1, 'New Bid', '2021-04-10 16:50:30.892133');

insert into mural_message (auction_id, message_text, message_time)
values(1, 'New Bid', '2021-04-10 17:03:27.538298');
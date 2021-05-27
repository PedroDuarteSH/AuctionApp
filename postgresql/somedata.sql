--Insert Users:

INSERT INTO users (username, email, password)
VALUES ('Adriana1234', 'Adriana1234@gmail.pt', 'Adriana1234');

INSERT INTO users (username, email, password)
VALUES ('Tchabes1234', 'Tchabes1234@gmail.pt', 'Tchabes1234');

INSERT INTO users (username, email, password)
VALUES ('Duarte1234', 'Duarte1234@gmail.pt', 'Duarte1234');


--Criar leilão:

Insert into auction (item_id, title, description, end_time, item_name, min_price, seller_id)
Values (1, 'Leilao de Relogio', 'Vendo relogio porque nao tenho pulsos', TIMESTAMP '2021-05-28 00:00:00', 'Relogio', 200, 1);

--Criar Bids: (Falta logica de verificar preços)

insert into bidding (price, bid_time, auction_id, bidder)
Values(300, current_timestamp, 1, 3);

insert into bidding (price, bid_time, auction_id, bidder)
Values(1100, current_timestamp, 1, 2);

insert into bidding (price, bid_time, auction_id, bidder)
Values(1000, current_timestamp, 1, 3);

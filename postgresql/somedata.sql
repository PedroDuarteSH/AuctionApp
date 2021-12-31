--Insert Users:

INSERT INTO users (username, email, password)
VALUES ('Adriana1234', 'Adriana1234@student.dei.uc.pt', 'Adriana1234');

INSERT INTO users (username, email, password)
VALUES ('Tchabes1234', 'Tchabes1234@student.dei.uc.pt', 'Tchabes1234');

INSERT INTO users (username, email, password)
VALUES ('Duarte1234', 'Duarte1234@student.dei.uc.pt', 'Duarte1234');

INSERT INTO users (username, email, password, is_admin)
VALUES ('Marco1234', 'Marco1234@dei.uc.pt', 'Marco1234', 'True');

--Criar leilão:

Insert into auction (EAN_ISBN, title, description, end_time, item_name, min_price, seller_id, start_date)
Values (12344321, 'Leilao de Relógio', 'Vendo relógio, porque não tenho pulsos :(', TIMESTAMP '2021-06-04 15:45:50', 'Relógio', 200, 1, current_timestamp(0));

Insert into auction (EAN_ISBN, title, description, end_time, item_name, min_price, seller_id, start_date)
Values (12345678, 'Leilao de Cabeças de leitão', 'Vendo cabeças de leitão, porque não gosto', TIMESTAMP '2021-06-04 15:30:00', 'Leitão', 50, 4, current_timestamp(0));

Insert into auction (EAN_ISBN, title, description, end_time, item_name, min_price, seller_id, start_date)
Values (87654321, 'Fiat 500 Cor de Rosa bom estado RARIDADE', 'Vendo Fiat 500 Cor de Rosa, 30000km, bom estado! -> 0.6L | cv: 18 Hp | Gasolina-> Automóvel incrivel para passear com a sua familia durante o fim de semana!', TIMESTAMP '2021-06-07 15:20:50', 'Automóvel', 10000, 3, current_timestamp(0));

Insert into auction (EAN_ISBN, title, description, end_time, item_name, min_price, seller_id, start_date)
Values (43211234, 'Barbie', 'Vendo uma barbie, porque não tenho o Ken :(', TIMESTAMP '2021-06-06 17:45:50', 'Barbie', 20, 2, current_timestamp(0));

Insert into auction (EAN_ISBN, title, description, end_time, item_name, min_price, seller_id, start_date)
Values (11223344, 'Leilao de Computador', 'Vendo computador em bom estado, mas não liga. Se for engenheiro informático de certeza que o põe a funcionar', TIMESTAMP '2021-06-06 16:30:50', 'Computador', 70, 4, current_timestamp(0));

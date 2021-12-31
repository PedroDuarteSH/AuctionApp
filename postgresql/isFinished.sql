CREATE OR REPLACE FUNCTION finish_notification()
RETURNS trigger AS
$$
DECLARE
    cur cursor for 
    SELECT DISTINCT bidder_id as "reciever" From bidding where auction_id = NEW.id
    UNION
    SELECT DISTINCT users_id as "reciever" from mural_message,auction where auction_id = NEW.id and
    auction.id = mural_message.auction_id and users_id <> seller_id;
    
    winner_id users.id%type;
    winner_username users.username%type;
    win_price bidding.price%type;
    mess VARCHAR;
BEGIN
    SELECT MAX(price) into win_price from bidding where auction_id = New.id;
    SELECT bidder_id into winner_id from bidding where price = win_price and auction_id = New.id;
    SELECT username into winner_username from bidding,users where price = win_price and users.id = bidding.bidder_id;

    mess := concat('Parabens! Vencedor/a do leilao ', NEW.ID, '-> ', NEW.title , ' com o valor de ' || win_price || '€.');
    insert into notifications (message, mes_time, users_id)
    values(mess, current_timestamp(0) , winner_id);
    

    for elem in cur
    loop
        if elem.reciever <> winner_id THEN
            mess := concat('Não foi o Vencedor! Leilão ', NEW.ID, '-> ', NEW.title , ' -> foi vencido pelo utilizador ' || winner_username || ' com o valor de ' || win_price || '€.');
            insert into notifications (message, mes_time, users_id)
            values(mess, current_timestamp(0) , elem.reciever);
        end if;
    end loop;
    RETURN NULL;
END;
$$
LANGUAGE plpgsql;

CREATE TRIGGER onFinished
AFTER UPDATE OF FINISHED ON auction
FOR EACH ROW Execute PROCEDURE finish_notification();
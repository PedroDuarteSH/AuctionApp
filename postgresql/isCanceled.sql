CREATE OR REPLACE FUNCTION cancel_notification()
RETURNS trigger AS
$$
DECLARE
    cur cursor for 
        SELECT DISTINCT bidder_id as "reciever" From bidding where auction_id = NEW.id
        UNION
        SELECT DISTINCT users_id as "reciever" from mural_message,auction where auction_id = NEW.id and
            auction.id = mural_message.auction_id and users_id <> seller_id;
    mess VARCHAR;
BEGIN
    mess := concat('O seu leilao ', NEW.id, '-> ', NEW.title , ' foi cancelado, pedimos desculpa pelo incomodo');
    insert into notifications (message, mes_time, users_id)
    values(mess, current_timestamp(0) , New.seller_id);
    

    for elem in cur
    loop
        if elem.reciever <> NEW.ID THEN
            mess := concat('O Leilão em participava ', NEW.id, '-> ', NEW.title , ' -> foi cancelado, pedimos desculpa pelo incomodo');
            insert into notifications (message, mes_time, users_id)
            values(mess, current_timestamp(0) , elem.reciever);
        end if;
    end loop;
    RETURN NULL;
END;
$$
LANGUAGE plpgsql;

CREATE TRIGGER onCancel
AFTER UPDATE OF canceled ON auction
FOR EACH ROW Execute PROCEDURE cancel_notification();
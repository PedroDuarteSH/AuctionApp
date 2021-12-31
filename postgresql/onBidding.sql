CREATE OR REPLACE FUNCTION bid_notification()
RETURNS trigger AS
$$
DECLARE
    cur cursor for 
    select DISTINCT bidder_id as "reciever" From bidding where
    auction_id = NEW.auction_id
    and bidder_id <> NEW.bidder_id;

    new_bidder users.username%type;
    new_value bidding.price%type;
    auction_title auction.title%type;
    auction_id auction.id%type;
    mess VARCHAR;
BEGIN
    SELECT username into new_bidder from users where id = NEW.bidder_id;
    SELECT price into new_value from bidding where id = NEW.id;
    SELECT title into auction_title from auction where id = NEW.auction_id;
    SELECT id into auction_id from auction where id = NEW.auction_id;
    for elem in cur
    loop
        mess := concat('Licitacao ultrapassada no leilão ', auction_id, '-> ', auction_title , ' -> pelo utilizador ' || new_bidder || ' no valor de ' || new_value || '€.');
        insert into notifications (message, mes_time, users_id)
        values(mess, current_timestamp(0) , elem.reciever);
    end loop;
    RETURN NULL;
END;
$$
LANGUAGE plpgsql;

CREATE TRIGGER onBidding
AFTER INSERT ON bidding
FOR EACH ROW Execute PROCEDURE bid_notification();
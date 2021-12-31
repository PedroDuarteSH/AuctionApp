CREATE OR REPLACE FUNCTION InvalidBid()
RETURNS trigger AS
$$
DECLARE
    auc_title auction.title%type;

BEGIN
    Select title into auc_title from auction where id = NEW.auction_id;
    
    Insert INto notifications(message, mes_time, users_id)
    Values ('Your bid on auction [' || NEW.ID || '-> ' || auc_title || ' was considered invalid! Sorry for the inconvenience' , current_timestamp(0), NEW.bidder_id);
    RETURN NULL;
END;
$$
LANGUAGE plpgsql;

CREATE TRIGGER onInvalidBid
AFTER UPDATE OF valid ON bidding
FOR EACH ROW Execute PROCEDURE InvalidBid();
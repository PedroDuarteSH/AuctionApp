CREATE OR REPLACE FUNCTION save_history()
RETURNS trigger AS
$$
BEGIN
    Insert INto history(change_time, description, title, item_name, change_price, auction_id)
    Values (current_timestamp(0), OLD.description, OLD.title, OLD.item_name, OLD.current_price, OLD.ID);
    RETURN NULL;
END;
$$
LANGUAGE plpgsql;

CREATE TRIGGER onAuctUpdate
AFTER UPDATE OF title, item_name, description ON auction
FOR EACH ROW Execute PROCEDURE save_history();
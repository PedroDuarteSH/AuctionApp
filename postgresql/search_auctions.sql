CREATE OR REPLACE FUNCTION search_auctions(keyword VARCHAR(512))
RETURNS TABLE(
    auct_id INTEGER,
    descrip VARCHAR(512)
)
AS $$
BEGIN
    IF keyword~E'^\\d+$' THEN
            return QUERY SELECT id, description FROM  auction 
                    where (description like ('% ' || keyword || ' %')  or  auction.EAN_ISBN = (keyword::INTEGER))
                    ORDER BY end_time DESC, id ASC;
    ELSE
        RETURN QUERY  SELECT id, description FROM  auction 
                where (UPPER(description) like ('% ' || UPPER(keyword) || ' %')
                or UPPER(description) like ('% ' || UPPER(keyword) || '%')
                or UPPER(description) like ('%' || UPPER(keyword) || ' %'))
                ORDER BY end_time DESC, id ASC;
    END IF;
END;
$$
LANGUAGE plpgsql;
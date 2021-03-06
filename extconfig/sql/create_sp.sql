CREATE PROCEDURE `update_or_insert_response`
(
	IN in_TLD varchar(255),
    IN in_REQUEST_URI varchar(1023),
    IN in_RESPONSE_HTTP_STATUS int,
    IN in_RESPONSE_HEADERS longtext,
    IN in_RESPONSE_BODY longtext
)
BEGIN
	SET @id = (SELECT RESPONSE_ID FROM `response` WHERE TLD=in_TLD LIMIT 1);
	IF @id IS NULL THEN
		INSERT INTO `response` (TLD, REQUEST_URI, RESPONSE_HTTP_STATUS, RESPONSE_HEADERS, RESPONSE_BODY)
        VALUES (in_TLD, in_REQUEST_URI, in_RESPONSE_HTTP_STATUS, in_RESPONSE_HEADERS, in_RESPONSE_BODY);
	ELSE
		UPDATE `response`
        SET TLD = in_TLD, REQUEST_URI = in_REQUEST_URI, RESPONSE_HTTP_STATUS = in_RESPONSE_HTTP_STATUS,
			RESPONSE_HEADERS = in_RESPONSE_HEADERS, RESPONSE_BODY = in_RESPONSE_BODY
        WHERE RESPONSE_ID = @id;
    END IF;
END;

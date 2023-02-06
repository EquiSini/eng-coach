-- Create the sequence to generate unique IDs for the eng_user
CREATE SEQUENCE eng_user_id_seq;

-- Create the eng_user table
CREATE TABLE eng_user (
    -- The id column is the primary key and will be generated using the sequence
    id INTEGER DEFAULT nextval('eng_user_id_seq') PRIMARY KEY,
    -- The name column is a required text field
    username TEXT NOT NULL,
    -- The surname column is a required text field
    email CHARACTER VARYING(255),
    auth_id TEXT NOT NULL, 
    picture TEXT NOT NULL, 
    session_token CHARACTER VARYING(36), 
    session_expire TIMESTAMP
);

-- Add a comment to the eng_user table
COMMENT ON TABLE eng_user IS 'Table to store information about eng_user';

-- Add comments to the columns in the eng_user table
COMMENT ON COLUMN eng_user.id IS 'Unique identifier for each eng_user';
COMMENT ON COLUMN eng_user.username IS 'The name of the eng_user';
COMMENT ON COLUMN eng_user.email IS 'The email of the eng_user';
COMMENT ON COLUMN eng_user.auth_id IS 'User id from OAUTH system';
COMMENT ON COLUMN eng_user.picture IS 'Link to user picture';
COMMENT ON COLUMN eng_user.session_token IS 'User session token (UUID4)';
COMMENT ON COLUMN eng_user.session_expire IS 'Date time until session works';
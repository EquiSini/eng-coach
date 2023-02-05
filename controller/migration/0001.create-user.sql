-- Create the sequence to generate unique IDs for the eng_user
CREATE SEQUENCE eng_user_id_seq;

-- Create the eng_user table
CREATE TABLE eng_user (
    -- The id column is the primary key and will be generated using the sequence
    id INTEGER DEFAULT nextval('eng_user_id_seq') PRIMARY KEY,
    -- The name column is a required text field
    username TEXT NOT NULL,
    -- The surname column is a required text field
    email TEXT NOT NULL
);

-- Add a comment to the eng_user table
COMMENT ON TABLE eng_user IS 'Table to store information about eng_user';

-- Add comments to the columns in the eng_user table
COMMENT ON COLUMN eng_user.id IS 'Unique identifier for each eng_user';
COMMENT ON COLUMN eng_user.name IS 'The name of the eng_user';
COMMENT ON COLUMN eng_user.surname IS 'The surname of the eng_user';
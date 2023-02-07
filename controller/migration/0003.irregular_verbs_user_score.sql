CREATE TABLE irregular_verbs_user_score  (
    user_id INTEGER REFERENCES eng_user (id),
    verb_id INTEGER REFERENCES irregular_verbs (id),
    score numeric,
    PRIMARY KEY (user_id, verb_id)
);

COMMENT ON TABLE irregular_verbs_user_score IS 'Table to store user scores of irregular verbs';

COMMENT ON COLUMN irregular_verbs_user_score.user_id IS 'User id';
COMMENT ON COLUMN irregular_verbs_user_score.verb_id IS 'Verb id';
COMMENT ON COLUMN irregular_verbs_user_score.score IS 'User score for verb. Value between 0 and 1';
CREATE TABLE options_func_usertracker (
    id BIGSERIAL PRIMARY KEY,
    user_id INTEGER NOT NULL,
    method VARCHAR(100) NOT NULL,
    stock1 VARCHAR(10) NOT NULL,
    stock2 VARCHAR(10) NOT NULL,
    start_date DATE NOT NULL,
    end_date DATE NOT NULL,
    n_std NUMERIC(5, 2) NOT NULL,
    window_size INTEGER NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT fk_user
        FOREIGN KEY(user_id) 
        REFERENCES auth_user(id)
        ON DELETE CASCADE
);
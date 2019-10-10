CREATE USER gitsu;
CREATE DATABASE gitsu;
GRANT ALL PRIVILEGES ON DATABASE gitsu TO gitsu;


CREATE TABLE IF NOT EXISTS public.data_lake (
	key VARCHAR(256) PRIMARY KEY
	, schema VARCHAR(256)
	, data JSONB NULL
	, dw_created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
	, dw_updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
	, dw_etl_at TIMESTAMP WITH TIME ZONE NULL
	, dw_etl_job_name VARCHAR(256) NULL
);

CREATE INDEX IF NOT EXISTS 
	idx__data_lake__schema_lower
	ON public.data_lake ((lower(schema)));


/* Repo */
CREATE TABLE IF NOT EXISTS public.github_repo (
	repo_id VARCHAR(128) PRIMARY KEY
	, repo_name VARCHAR(128)
	, repo_organization_name VARCHAR(128)
    , dw_row_created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
    , dw_row_updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

CREATE UNIQUE INDEX IF NOT EXISTS idx__github_repo__repo_name ON public.github_repo (repo_name);


/* Github User */
CREATE TABLE IF NOT EXISTS public.github_user (
	user_ext_id BIGINT PRIMARY KEY
	, user_name VARCHAR(64)
    , dw_row_created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
    , dw_row_updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP	
);


/* Issue */
CREATE TABLE IF NOT EXISTS public.github_issue (
	issue_ext_id BIGINT PRIMARY KEY
    , issue_state VARCHAR(16) NOT NULL
    , issue_comments INTEGER DEFAULT 0
    , issue_created_at TIMESTAMP WITH TIME ZONE NOT NULL
    , issue_closed_at TIMESTAMP WITH TIME ZONE NULL
    , issue_updated_at TIMESTAMP WITH TIME ZONE NULL
	, issue_user_ext_id INTEGER REFERENCES public.github_user(user_ext_id)
    , issue_is_pull_request BOOLEAN
    , issue_events_url TEXT
    , issue_events_last_loaded_at TIMESTAMP WITH TIME ZONE NULL
	, issue_repo_id VARCHAR(128) REFERENCES public.github_repo(repo_id)    
    , dw_row_created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
    , dw_row_updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);


CREATE INDEX IF NOT EXISTS 
	idx__github_issue__issue_events_last_loaded_at__nulls_first
	ON public.github_issue (
		issue_events_last_loaded_at NULLS FIRST
	);


CREATE TABLE IF NOT EXISTS public.github_issue_event (
	event_ext_id BIGINT PRIMARY KEY
	, event VARCHAR(32)	
	, event_issue_ext_id INTEGER REFERENCES public.github_issue(issue_ext_id)
	, event_user_ext_id INTEGER REFERENCES public.github_user(user_ext_id)
	, event_created_at TIMESTAMP WITH TIME ZONE
	, event_label VARCHAR(128) NULL
	, event_user_login VARCHAR(64)
    , dw_row_created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
    , dw_row_updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP	
);

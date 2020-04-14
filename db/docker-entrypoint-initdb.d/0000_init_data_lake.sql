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

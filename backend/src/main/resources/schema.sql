create table if not exists candidates (
  user_id text not null,
  scene text not null,
  item_id text not null,
  score double precision default 0,
  updated_at timestamptz default now(),
  primary key (user_id, scene, item_id)
);

create index if not exists idx_candidates_user_scene on candidates (user_id, scene);
create index if not exists idx_candidates_score on candidates (score desc);

create table if not exists feedback_events (
  id bigserial primary key,
  request_id text not null,
  user_id text not null, -- irreversible token: tok_<saltVersion>_<digest>
  item_id text not null,
  event_type text not null,
  scene text not null,
  model_version text,
  ts bigint not null,
  extra jsonb,
  storage_tier text not null default 'hot',
  created_at timestamptz default now()
);

create index if not exists idx_feedback_user on feedback_events (user_id, created_at desc);
create index if not exists idx_feedback_item on feedback_events (item_id, created_at desc);
create index if not exists idx_feedback_event on feedback_events (event_type, created_at desc);
create index if not exists idx_feedback_tier_created on feedback_events (storage_tier, created_at desc);

create table if not exists retention_job_audit (
  id bigserial primary key,
  job_name text not null,
  started_at timestamptz not null,
  finished_at timestamptz not null,
  status text not null,
  affected_rows bigint not null default 0,
  details text
);

create index if not exists idx_retention_job_started on retention_job_audit (job_name, started_at desc);

create table if not exists user_deletion_audit (
  id bigserial primary key,
  user_token text not null,
  reason text,
  deleted_rows bigint not null default 0,
  requested_at timestamptz not null default now()
);

create index if not exists idx_user_deletion_requested on user_deletion_audit (user_token, requested_at desc);

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
  user_id text not null,
  item_id text not null,
  event_type text not null,
  scene text not null,
  model_version text,
  ts bigint not null,
  extra jsonb,
  created_at timestamptz default now()
);

create index if not exists idx_feedback_user on feedback_events (user_id, created_at desc);
create index if not exists idx_feedback_item on feedback_events (item_id, created_at desc);
create index if not exists idx_feedback_event on feedback_events (event_type, created_at desc);

create table public.menu_feedback (
 id uuid primary key default gen_random_uuid(),
 restaurant_id uuid not null references public.restaurants(id) on delete cascade,
 rating integer not null check(rating between 1 and 5),
 comment text not null default '' check(length(comment)<=1500),
 created_at timestamptz not null default now()
);
alter table public.menu_feedback enable row level security;
revoke all on public.menu_feedback from public,anon,authenticated;
grant select,insert on public.menu_feedback to service_role;
create policy no_browser_feedback on public.menu_feedback for all to anon,authenticated using(false) with check(false);
create index menu_feedback_restaurant_created_idx on public.menu_feedback(restaurant_id,created_at desc);

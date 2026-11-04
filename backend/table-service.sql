-- Service-only mutations; HTTP handlers verify a real Supabase session first.
alter table public.restaurant_members drop constraint restaurant_members_role_check;
alter table public.restaurant_members add constraint restaurant_members_role_check check(role in ('owner','editor','viewer','waiter'));
create table public.waiter_profiles (
 restaurant_id uuid not null references public.restaurants(id) on delete cascade,
 user_id uuid primary key references auth.users(id) on delete cascade,
 username text not null check(username ~ '^[a-z0-9][a-z0-9_-]{2,31}$'),
 display_name text not null check(length(display_name) between 1 and 100),
 active boolean not null default true,
 tokens_after bigint not null default 0,
 unique(restaurant_id,username), unique(restaurant_id,user_id)
);
create table public.dining_tables (
 id uuid primary key default gen_random_uuid(), restaurant_id uuid not null references public.restaurants(id) on delete cascade,
 number integer not null check(number between 1 and 500), label text not null default '' check(length(label)<=80),
 active boolean not null default true, unique(restaurant_id,number), unique(restaurant_id,id)
);
create table public.table_sessions (
 id uuid primary key default gen_random_uuid(), restaurant_id uuid not null references public.restaurants(id) on delete cascade,
 table_id uuid not null, waiter_id uuid not null,
 guests integer not null check(guests between 1 and 100), opened_at timestamptz not null default now(), closed_at timestamptz,
 closed_by uuid references auth.users(id), revision bigint not null default 1 check(revision>0),
 basket jsonb not null default '[]' check(jsonb_typeof(basket)='array' and octet_length(basket::text)<=128000),
 foreign key(restaurant_id,table_id) references public.dining_tables(restaurant_id,id),
 foreign key(restaurant_id,waiter_id) references public.waiter_profiles(restaurant_id,user_id)
);
create unique index one_open_session_per_table on public.table_sessions(table_id) where closed_at is null;
create index table_sessions_restaurant_time_idx on public.table_sessions(restaurant_id,opened_at desc);
create index table_sessions_waiter_idx on public.table_sessions(waiter_id);
create index table_sessions_closed_by_idx on public.table_sessions(closed_by);
create table public.table_feedback (
 id uuid primary key default gen_random_uuid(), restaurant_id uuid not null references public.restaurants(id) on delete cascade,
 session_id uuid not null references public.table_sessions(id), rating integer not null check(rating between 1 and 5),
 comment text not null default '' check(length(comment)<=1500), created_at timestamptz not null default now()
);
create index table_feedback_restaurant_idx on public.table_feedback(restaurant_id,created_at desc);
create index table_feedback_session_idx on public.table_feedback(session_id);
create table public.service_rate_limits (key text primary key, expires_at timestamptz not null, hits integer not null);
create index service_rate_limits_expiry_idx on public.service_rate_limits(expires_at);
alter table public.waiter_profiles enable row level security;
alter table public.dining_tables enable row level security;
alter table public.table_sessions enable row level security;
alter table public.table_feedback enable row level security;
alter table public.service_rate_limits enable row level security;
revoke all on public.waiter_profiles,public.dining_tables,public.table_sessions,public.table_feedback,public.service_rate_limits from public,anon,authenticated;
grant all on public.waiter_profiles,public.dining_tables,public.table_sessions,public.table_feedback,public.service_rate_limits to service_role;

create function public.service_rate_gate(p_key text,p_limit integer,p_seconds integer) returns boolean language plpgsql security invoker set search_path=pg_catalog,public as $$
declare n integer;
begin
 if length(p_key)>200 or p_limit not between 1 and 5000 or p_seconds not between 1 and 86400 then raise exception 'invalid limit'; end if;
 insert into public.service_rate_limits(key,expires_at,hits) values(p_key,now()+make_interval(secs=>p_seconds),1)
 on conflict(key) do update set hits=case when service_rate_limits.expires_at<=now() then 1 else service_rate_limits.hits+1 end,
 expires_at=case when service_rate_limits.expires_at<=now() then now()+make_interval(secs=>p_seconds) else service_rate_limits.expires_at end returning hits into n;
 return n<=p_limit;
end $$;

create function public.table_service_action(p_restaurant uuid,p_actor uuid,p_action text,p_data jsonb) returns jsonb language plpgsql security invoker set search_path=pg_catalog,public as $$
declare member_role text; t public.dining_tables; s public.table_sessions; n integer; first_num integer; last_num integer; target_waiter uuid;
begin
 select role into member_role from public.restaurant_members where restaurant_id=p_restaurant and user_id=p_actor and active;
 if member_role is null or member_role not in ('owner','waiter') then raise exception 'forbidden' using errcode='42501'; end if;
 if member_role='waiter' and not exists(select 1 from public.waiter_profiles where restaurant_id=p_restaurant and user_id=p_actor and active) then raise exception 'inactive waiter' using errcode='42501'; end if;
 if p_action='create_tables' then
  if member_role<>'owner' then raise exception 'owner required' using errcode='42501'; end if;
  first_num:=(p_data->>'from')::integer; last_num:=(p_data->>'to')::integer;
  if first_num is null or last_num is null or first_num<1 or last_num>500 or last_num<first_num then raise exception 'invalid range' using errcode='22023'; end if;
  insert into public.dining_tables(restaurant_id,number) select p_restaurant,generate_series(first_num,last_num) on conflict(restaurant_id,number) do nothing;
  return jsonb_build_object('ok',true);
 elsif p_action='configure_table' then
  if member_role<>'owner' then raise exception 'owner required' using errcode='42501'; end if;
  select * into t from public.dining_tables where restaurant_id=p_restaurant and id=(p_data->>'tableId')::uuid for update;
  if not found then raise exception 'table not found' using errcode='P0002'; end if;
  if p_data->>'active'='false' and exists(select 1 from public.table_sessions where table_id=t.id and closed_at is null) then raise exception 'occupied table' using errcode='40001'; end if;
  update public.dining_tables set label=coalesce(p_data->>'label',label),active=coalesce((p_data->>'active')::boolean,active) where id=t.id;
  return jsonb_build_object('ok',true);
 elsif p_action='open' then
  select * into t from public.dining_tables where restaurant_id=p_restaurant and id=(p_data->>'tableId')::uuid and active for update;
  if not found then raise exception 'table not found' using errcode='P0002'; end if;
  target_waiter:=case when member_role='owner' then (p_data->>'waiterId')::uuid else p_actor end;
  if not exists(select 1 from public.waiter_profiles w join public.restaurant_members m on m.restaurant_id=w.restaurant_id and m.user_id=w.user_id where w.restaurant_id=p_restaurant and w.user_id=target_waiter and w.active and m.active and m.role='waiter') then raise exception 'invalid waiter' using errcode='42501'; end if;
  if exists(select 1 from public.table_sessions where table_id=t.id and closed_at is null) then raise exception 'table occupied' using errcode='40001'; end if;
  insert into public.table_sessions(restaurant_id,table_id,waiter_id,guests) values(p_restaurant,t.id,target_waiter,(p_data->>'guests')::integer) returning * into s;
  return to_jsonb(s);
 else
  select * into s from public.table_sessions where restaurant_id=p_restaurant and id=(p_data->>'sessionId')::uuid for update;
  if not found then raise exception 'session not found' using errcode='P0002'; end if;
  if member_role<>'owner' and s.waiter_id<>p_actor then raise exception 'not assigned' using errcode='42501'; end if;
  if s.closed_at is not null then
   if p_action='close' then return to_jsonb(s); end if;
   raise exception 'session closed' using errcode='40001';
  end if;
  if (p_data->>'expectedRevision') is null or (p_data->>'expectedRevision')::bigint<>s.revision then raise exception 'revision conflict' using errcode='40001'; end if;
  if p_action='save' then
   if p_data->'basket' is null or jsonb_typeof(p_data->'basket')<>'array' or jsonb_array_length(p_data->'basket')>100 then raise exception 'invalid basket' using errcode='22023'; end if;
   update public.table_sessions set basket=p_data->'basket',guests=coalesce((p_data->>'guests')::integer,guests),revision=revision+1 where id=s.id returning * into s;
  elsif p_action='close' then
   update public.table_sessions set closed_at=now(),closed_by=p_actor,revision=revision+1 where id=s.id returning * into s;
  elsif p_action='reassign' then
   if member_role<>'owner' then raise exception 'owner required' using errcode='42501'; end if;
   target_waiter:=(p_data->>'waiterId')::uuid;
   if not exists(select 1 from public.waiter_profiles w join public.restaurant_members m on m.restaurant_id=w.restaurant_id and m.user_id=w.user_id where w.restaurant_id=p_restaurant and w.user_id=target_waiter and w.active and m.active and m.role='waiter') then raise exception 'invalid waiter' using errcode='42501'; end if;
   update public.table_sessions set waiter_id=target_waiter,revision=revision+1 where id=s.id returning * into s;
  else raise exception 'invalid action' using errcode='22023'; end if;
  return to_jsonb(s);
 end if;
end $$;
revoke all on function public.table_service_action(uuid,uuid,text,jsonb),public.service_rate_gate(text,integer,integer) from public,anon,authenticated;
grant execute on function public.table_service_action(uuid,uuid,text,jsonb),public.service_rate_gate(text,integer,integer) to service_role;
create function public.service_waiter_profile(p_restaurant uuid,p_owner uuid,p_user uuid,p_username text,p_name text,p_active boolean,p_cutoff bigint default 0) returns void language plpgsql security invoker set search_path=pg_catalog,public as $$
begin
 if not exists(select 1 from public.restaurant_members where restaurant_id=p_restaurant and user_id=p_owner and role='owner' and active) then raise exception 'owner required' using errcode='42501'; end if;
 if exists(select 1 from public.restaurant_members where user_id=p_user and (restaurant_id<>p_restaurant or role<>'waiter')) then raise exception 'user already assigned' using errcode='42501'; end if;
 insert into public.waiter_profiles(restaurant_id,user_id,username,display_name,active,tokens_after) values(p_restaurant,p_user,p_username,p_name,p_active,p_cutoff)
 on conflict(user_id) do update set display_name=excluded.display_name,active=excluded.active,tokens_after=greatest(waiter_profiles.tokens_after,excluded.tokens_after)
 where waiter_profiles.restaurant_id=p_restaurant and waiter_profiles.username=p_username;
 if not found then raise exception 'waiter mismatch' using errcode='42501'; end if;
 insert into public.restaurant_members(restaurant_id,user_id,role,active) values(p_restaurant,p_user,'waiter',p_active)
 on conflict(restaurant_id,user_id) do update set active=excluded.active;
end $$;
revoke all on function public.service_waiter_profile(uuid,uuid,uuid,text,text,boolean,bigint) from public,anon,authenticated;
grant execute on function public.service_waiter_profile(uuid,uuid,uuid,text,text,boolean,bigint) to service_role;

-- Additional applied integrity/index/policy changes for fresh installations.
alter table public.table_feedback add constraint one_feedback_per_session unique(session_id);
create index table_sessions_table_fk_idx on public.table_sessions(restaurant_id,table_id);
create index table_sessions_waiter_fk_idx on public.table_sessions(restaurant_id,waiter_id);
create policy service_only_dining_tables on public.dining_tables for all to anon,authenticated using(false) with check(false);
create policy service_only_waiter_profiles on public.waiter_profiles for all to anon,authenticated using(false) with check(false);
create policy service_only_table_sessions on public.table_sessions for all to anon,authenticated using(false) with check(false);
create policy service_only_table_feedback on public.table_feedback for all to anon,authenticated using(false) with check(false);
create policy service_only_service_rate_limits on public.service_rate_limits for all to anon,authenticated using(false) with check(false);

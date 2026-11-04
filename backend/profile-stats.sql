create table if not exists public.menu_daily_views (
 restaurant_id uuid not null references public.restaurants(id) on delete cascade,
 day date not null, visits bigint not null default 0 check(visits>=0),
 primary key(restaurant_id,day)
);
alter table public.menu_daily_views enable row level security;
revoke all on public.menu_daily_views from public,anon,authenticated;
grant select,insert,update on public.menu_daily_views to service_role;
create policy menu_views_no_browser on public.menu_daily_views for all to anon,authenticated using(false) with check(false);
create or replace function public.service_record_menu_view(p_restaurant uuid)
returns void language sql security invoker set search_path=pg_catalog,public as $$
 insert into public.menu_daily_views(restaurant_id,day,visits)
 values(p_restaurant,(now() at time zone 'Asia/Damascus')::date,1)
 on conflict(restaurant_id,day) do update set visits=public.menu_daily_views.visits+1;
$$;
revoke all on function public.service_record_menu_view(uuid) from public,anon,authenticated;
grant execute on function public.service_record_menu_view(uuid) to service_role;
-- Internal aggregate endpoint: callable only by the verified Edge Function.
create or replace function public.service_profile_stats(p_restaurant uuid,p_actor uuid)
returns jsonb language plpgsql security invoker set search_path=pg_catalog,public as $$
declare r text; d date := (now() at time zone 'Asia/Damascus')::date; result jsonb;
begin
 select role into r from public.restaurant_members where restaurant_id=p_restaurant and user_id=p_actor and active;
 if r is null or r not in ('owner','waiter') then raise exception 'forbidden' using errcode='42501'; end if;
 if r='waiter' and not exists(select 1 from public.waiter_profiles where restaurant_id=p_restaurant and user_id=p_actor and active) then raise exception 'disabled' using errcode='42501'; end if;
 with eligible as (
 select * from public.table_sessions where restaurant_id=p_restaurant and (r='owner' or waiter_id=p_actor)
 ), daily as (
 select s.waiter_id,count(*) as closed,coalesce(sum((select coalesce(sum((l->>'unitUSD')::numeric*(l->>'qty')::numeric),0) from jsonb_array_elements(s.basket) l)),0) as amount
 from eligible s where s.closed_at >= (d::timestamp at time zone 'Asia/Damascus') and s.closed_at < ((d+1)::timestamp at time zone 'Asia/Damascus') group by s.waiter_id
 ), staff as (
 select w.user_id,w.display_name,w.username,w.active,coalesce(x.closed,0) as closed,coalesce(x.amount,0) as amount,
 (select count(*) from eligible s where s.waiter_id=w.user_id and s.closed_at is null) as open
 from public.waiter_profiles w left join daily x on w.user_id=x.waiter_id where w.restaurant_id=p_restaurant and (r='owner' or w.user_id=p_actor)
 ) select jsonb_build_object('day',d,'timezone','Asia/Damascus','closedTables',(select coalesce(sum(closed),0) from daily),'closedValueUSD',(select coalesce(sum(amount),0) from daily),'openTables',(select count(*) from eligible where closed_at is null),'staff',coalesce((select jsonb_agg(to_jsonb(staff) order by display_name) from staff),'[]'::jsonb)) into result;
 if r='owner' then
 result := result || jsonb_build_object('viewsToday',coalesce((select visits from public.menu_daily_views where restaurant_id=p_restaurant and day=d),0),'series',(
 select jsonb_agg(jsonb_build_object('day',g.bucket::date,'closed',coalesce(x.closed,0),'amount',coalesce(x.amount,0),'views',coalesce(v.visits,0)) order by g.bucket)
 from generate_series(d-6,d,interval '1 day') g(bucket)
 left join (select (closed_at at time zone 'Asia/Damascus')::date as bucket,count(*) as closed,
 sum((select coalesce(sum((l->>'unitUSD')::numeric*(l->>'qty')::numeric),0) from jsonb_array_elements(basket) l)) amount
 from public.table_sessions where restaurant_id=p_restaurant and closed_at>=(d-6)::timestamp at time zone 'Asia/Damascus' group by 1) x on x.bucket=g.bucket::date
 left join public.menu_daily_views v on v.restaurant_id=p_restaurant and v.day=g.bucket::date));
 end if;
 return result;
end $$;
revoke all on function public.service_profile_stats(uuid,uuid) from public,anon,authenticated;
grant execute on function public.service_profile_stats(uuid,uuid) to service_role;

create index if not exists table_sessions_restaurant_closed_stats_idx on public.table_sessions(restaurant_id,closed_at,waiter_id) where closed_at is not null;

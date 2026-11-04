-- Consolidated database operations; browser roles cannot execute these RPCs.
create or replace function public.service_submit_menu_feedback(p_restaurant uuid,p_client uuid,p_submission uuid,p_ip_hash text,p_rating integer,p_comment text)
returns jsonb language plpgsql security invoker set search_path=pg_catalog,public as $$
begin
 if p_restaurant is null or p_client is null or p_submission is null or p_rating is null or p_rating not between 1 and 5 or p_comment is null or length(p_comment)>1500 or p_ip_hash is null or p_ip_hash !~ '^[a-f0-9]{64}$' then raise exception 'invalid feedback' using errcode='22023'; end if;
 if exists(select 1 from public.menu_feedback where id=p_submission and restaurant_id=p_restaurant) then
  if not exists(select 1 from public.menu_feedback where id=p_submission and restaurant_id=p_restaurant and rating=p_rating and comment=btrim(p_comment)) then raise exception 'submission content changed' using errcode='22023'; end if;
  return jsonb_build_object('accepted',true);
 end if;
 if not public.service_rate_gate('menu-feedback-client:'||p_restaurant::text||':'||p_client::text,3,86400) then return jsonb_build_object('accepted',false); end if;
 if not public.service_rate_gate('menu-feedback-ip:'||p_ip_hash,60,3600) then return jsonb_build_object('accepted',false); end if;
 insert into public.menu_feedback(id,restaurant_id,rating,comment) values(p_submission,p_restaurant,p_rating,btrim(p_comment)) on conflict(id) do nothing;
 if not exists(select 1 from public.menu_feedback where id=p_submission and restaurant_id=p_restaurant) then raise exception 'invalid submission' using errcode='22023'; end if;
 return jsonb_build_object('accepted',true);
end $$;
revoke all on function public.service_submit_menu_feedback(uuid,uuid,uuid,text,integer,text) from public,anon,authenticated;
grant execute on function public.service_submit_menu_feedback(uuid,uuid,uuid,text,integer,text) to service_role;

create or replace function public.service_feedback_inbox(p_restaurant uuid,p_actor uuid)
returns jsonb language plpgsql security invoker set search_path=pg_catalog,public as $$
declare result jsonb;
begin
 if not exists(select 1 from public.restaurant_members where restaurant_id=p_restaurant and user_id=p_actor and role='owner' and active) then raise exception 'owner required' using errcode='42501'; end if;
 select coalesce(jsonb_agg(x.entry order by x.created_at desc),'[]'::jsonb) into result from (
 with recent_menu as (select * from public.menu_feedback where restaurant_id=p_restaurant order by created_at desc limit 100),
 recent_tables as (select * from public.table_feedback where restaurant_id=p_restaurant order by created_at desc limit 100)
 select q.* from (
 select m.created_at,jsonb_build_object('id',m.id,'source','menu','rating',m.rating,'comment',m.comment,'created_at',m.created_at) entry from recent_menu m
 union all
 select f.created_at,jsonb_build_object('id',f.id,'source','table','rating',f.rating,'comment',f.comment,'created_at',f.created_at,'table_sessions',jsonb_build_object('table_id',s.table_id,'waiter_id',s.waiter_id,'opened_at',s.opened_at)) entry from recent_tables f join public.table_sessions s on s.id=f.session_id and s.restaurant_id=f.restaurant_id
 ) q order by q.created_at desc limit 100) x;
 return result;
end $$;
revoke all on function public.service_feedback_inbox(uuid,uuid) from public,anon,authenticated;
grant execute on function public.service_feedback_inbox(uuid,uuid) to service_role;
create index if not exists table_feedback_restaurant_created_idx on public.table_feedback(restaurant_id,created_at desc);

create or replace function public.service_closed_history(p_restaurant uuid,p_actor uuid)
returns jsonb language plpgsql security invoker set search_path=pg_catalog,public as $$
declare result jsonb;
begin
 if not exists(select 1 from public.restaurant_members where restaurant_id=p_restaurant and user_id=p_actor and role='owner' and active) then raise exception 'owner required' using errcode='42501'; end if;
 select coalesce(jsonb_agg(jsonb_build_object('id',s.id,'table_id',s.table_id,'waiter_id',s.waiter_id,'guests',s.guests,'opened_at',s.opened_at,'closed_at',s.closed_at,'totalValueUSD',(select coalesce(sum((l->>'unitUSD')::numeric*(l->>'qty')::numeric),0) from jsonb_array_elements(s.basket) l)) order by s.closed_at desc),'[]'::jsonb) into result from (
 select id,table_id,waiter_id,guests,opened_at,closed_at,basket from public.table_sessions where restaurant_id=p_restaurant and closed_at is not null order by closed_at desc limit 100
 ) s;
 return result;
end $$;
revoke all on function public.service_closed_history(uuid,uuid) from public,anon,authenticated;
grant execute on function public.service_closed_history(uuid,uuid) to service_role;

-- Bound daily statistics to today/open sessions rather than copying all historical baskets.
create or replace function public.service_profile_stats(p_restaurant uuid,p_actor uuid)
returns jsonb language plpgsql security invoker set search_path=pg_catalog,public as $$
declare r text; d date := (now() at time zone 'Asia/Damascus')::date; result jsonb;
begin
 select role into r from public.restaurant_members where restaurant_id=p_restaurant and user_id=p_actor and active;
 if r is null or r not in ('owner','waiter') then raise exception 'forbidden' using errcode='42501'; end if;
 if r='waiter' and not exists(select 1 from public.waiter_profiles where restaurant_id=p_restaurant and user_id=p_actor and active) then raise exception 'disabled' using errcode='42501'; end if;
 with eligible as (
 select * from public.table_sessions where restaurant_id=p_restaurant and (r='owner' or waiter_id=p_actor) and (closed_at is null or (closed_at >= (d::timestamp at time zone 'Asia/Damascus') and closed_at < ((d+1)::timestamp at time zone 'Asia/Damascus')))
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
create index if not exists table_sessions_open_restaurant_idx on public.table_sessions(restaurant_id,waiter_id) where closed_at is null;

create or replace function public.service_submit_table_feedback(p_session uuid,p_ip_hash text,p_rating integer,p_comment text)
returns jsonb language plpgsql security invoker set search_path=pg_catalog,public as $$
declare tenant uuid; since timestamptz;
begin
 if p_session is null or p_rating is null or p_rating not between 1 and 5 or p_comment is null or length(p_comment)>1500 or p_ip_hash is null or p_ip_hash !~ '^[a-f0-9]{64}$' then raise exception 'invalid feedback' using errcode='22023'; end if;
 select restaurant_id,coalesce(closed_at,opened_at) into tenant,since from public.table_sessions where id=p_session;
 if tenant is null or now()-since>interval '24 hours' then return jsonb_build_object('accepted',false,'status',410); end if;
 if exists(select 1 from public.table_feedback where session_id=p_session) then
  if exists(select 1 from public.table_feedback where session_id=p_session and rating=p_rating and comment=btrim(p_comment)) then return jsonb_build_object('accepted',true); end if;
  return jsonb_build_object('accepted',false,'status',409);
 end if;
 if not public.service_rate_gate('feedback:'||p_session::text,5,86400) or not public.service_rate_gate('feedback-ip:'||p_ip_hash,60,3600) then return jsonb_build_object('accepted',false,'status',429); end if;
 insert into public.table_feedback(restaurant_id,session_id,rating,comment) values(tenant,p_session,p_rating,btrim(p_comment)) on conflict(session_id) do nothing;
 if not exists(select 1 from public.table_feedback where session_id=p_session and rating=p_rating and comment=btrim(p_comment)) then return jsonb_build_object('accepted',false,'status',409); end if;
 return jsonb_build_object('accepted',true);
end $$;
revoke all on function public.service_submit_table_feedback(uuid,text,integer,text) from public,anon,authenticated;
grant execute on function public.service_submit_table_feedback(uuid,text,integer,text) to service_role;

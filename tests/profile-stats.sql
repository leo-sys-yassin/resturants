begin;
do $$
declare r uuid:=gen_random_uuid(); o uuid:=gen_random_uuid(); w uuid:=gen_random_uuid(); w2 uuid:=gen_random_uuid(); tid uuid; p jsonb; daystart timestamptz:=((now() at time zone 'Asia/Damascus')::date)::timestamp at time zone 'Asia/Damascus';
begin
 insert into auth.users(id,email) values(o,o::text||'@example.invalid'),(w,w::text||'@example.invalid'),(w2,w2::text||'@example.invalid');
 insert into public.restaurants(id,slug,name) values(r,'stats-'||r::text,'Stats');
 insert into public.restaurant_members values(r,o,'owner',true);
 perform public.service_waiter_profile(r,o,w,'waiter_one','One',true);
 perform public.service_waiter_profile(r,o,w2,'waiter_two','Two',true);
 perform public.table_service_action(r,o,'create_tables','{"from":1,"to":2}');
 select id into tid from public.dining_tables where restaurant_id=r and number=1;
 insert into public.table_sessions(restaurant_id,table_id,waiter_id,guests,opened_at,closed_at,basket) values
 (r,tid,w,2,daystart,daystart+interval '1 hour','[{"unitUSD":5,"qty":2}]'),
 (r,tid,w2,2,daystart,daystart+interval '2 hour','[{"unitUSD":7,"qty":3}]'),
 (r,tid,w,1,daystart-interval '2 hour',daystart-interval '1 second','[{"unitUSD":1000,"qty":1}]'),
 (r,tid,w,1,now(),null,'[{"unitUSD":500,"qty":1}]');
 perform public.service_record_menu_view(r);perform public.service_record_menu_view(r);
 p:=public.service_profile_stats(r,o);
 if (p->>'closedTables')::int<>2 or (p->>'closedValueUSD')::numeric<>31 or (p->>'viewsToday')::int<>2 or jsonb_array_length(p->'series')<>7 then raise exception 'owner stats failed: %',p; end if;
 p:=public.service_profile_stats(r,w);
 if (p->>'closedTables')::int<>1 or (p->>'closedValueUSD')::numeric<>10 or jsonb_array_length(p->'staff')<>1 or p?'viewsToday' or p?'series' then raise exception 'waiter isolation failed: %',p; end if;
 if (p->>'openTables')::int<>1 then raise exception 'open table count failed'; end if;
 begin perform public.service_profile_stats(r,gen_random_uuid()); raise exception 'outsider allowed'; exception when insufficient_privilege then null; end;
 if has_function_privilege('anon','public.service_profile_stats(uuid,uuid)','execute') or has_table_privilege('authenticated','public.menu_daily_views','select') then raise exception 'public stats exposed'; end if;
end $$;
rollback;
select 'PASS: exact totals, local midnight, open-account exclusion, waiter isolation, visits, seven-day series, outsider denial' as verification;

-- Transaction-only fixtures: no test users or restaurant data persist.
begin;
do $$
declare a uuid:=gen_random_uuid(); v uuid:=gen_random_uuid(); r uuid:=gen_random_uuid(); other uuid:=gen_random_uuid();
begin
 insert into auth.users(id,email) values(a,a::text||'@example.invalid'),(v,v::text||'@example.invalid');
 insert into public.restaurants(id,slug,name) values(r,'test-'||r::text,'RLS test'),(other,'test-'||other::text,'Other tenant');
 insert into public.restaurant_members values(r,a,'owner',true),(r,v,'viewer',true);
 perform set_config('test.owner',a::text,true); perform set_config('test.viewer',v::text,true);
 perform set_config('test.restaurant',r::text,true); perform set_config('test.other',other::text,true);
end $$;
set local role authenticated;
select set_config('request.jwt.claim.sub',current_setting('test.owner'),true);
do $$
declare n integer; r uuid:=current_setting('test.restaurant')::uuid;
begin
 select count(*) into n from public.restaurants; if n<>1 then raise exception 'tenant isolation failed'; end if;
 select count(*) into n from public.save_menu_draft(r,0,'{"test":true}'); if n<>1 then raise exception 'initial save failed'; end if;
 select count(*) into n from public.save_menu_draft(r,1,'{"test":2}'); if n<>1 then raise exception 'revision save failed'; end if;
 select count(*) into n from public.save_menu_draft(r,1,'{"test":"stale"}'); if n<>0 then raise exception 'stale save accepted'; end if;
 begin
  perform public.save_menu_draft(current_setting('test.other')::uuid,0,'{}');
  raise exception 'cross tenant insert accepted';
 exception when insufficient_privilege then null; end;
 begin
  update public.restaurant_members set role='owner';
  raise exception 'membership update accepted';
 exception when insufficient_privilege then null; end;
end $$;
select set_config('request.jwt.claim.sub',current_setting('test.viewer'),true);
do $$
declare n integer;
begin
 select count(*) into n from public.menu_drafts; if n<>1 then raise exception 'viewer read failed'; end if;
 select count(*) into n from public.save_menu_draft(current_setting('test.restaurant')::uuid,2,'{}');
 if n<>0 then raise exception 'viewer update accepted'; end if;
end $$;
select set_config('request.jwt.claim.sub',gen_random_uuid()::text,true);
do $$ begin if exists(select 1 from public.restaurants) or exists(select 1 from public.menu_drafts) then raise exception 'outsider saw data'; end if; end $$;
reset role;
rollback;
select 'PASS: tenant isolation, owner save, stale revision, viewer read-only, membership protection, outsider isolation; fixtures rolled back' as verification;

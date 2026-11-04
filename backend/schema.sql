-- Apply only to the dedicated restaurant-platform project, never to REX.
-- Foundation applied to Restaurants Menu; see database verification notes.
begin;
create table public.restaurants (
 id uuid primary key default gen_random_uuid(),
 slug text not null unique check (slug ~ '^[a-z0-9][a-z0-9-]{2,59}$'),
 name text not null check(length(name) between 1 and 100),
 created_at timestamptz not null default now()
);
create table public.restaurant_members (
 restaurant_id uuid not null references public.restaurants(id) on delete cascade,
 user_id uuid not null references auth.users(id) on delete cascade,
 role text not null check(role in ('owner','editor','viewer')),
 active boolean not null default true,
 primary key(restaurant_id,user_id)
);
create index restaurant_members_user_idx on public.restaurant_members(user_id,restaurant_id) where active;
create table public.menu_drafts (
 restaurant_id uuid primary key references public.restaurants(id) on delete cascade,
 revision bigint not null default 1 check(revision>0),
 content jsonb not null check(jsonb_typeof(content)='object' and octet_length(content::text)<=12000000),
 updated_by uuid not null references auth.users(id),
 updated_at timestamptz not null default now()
);
create table public.menu_publications (
 id uuid primary key default gen_random_uuid(),
 restaurant_id uuid not null references public.restaurants(id) on delete cascade,
 revision bigint not null check(revision>0),
 object_key text not null,
 published_by uuid not null references auth.users(id),
 published_at timestamptz not null default now(),
 unique(restaurant_id,revision)
);
create index menu_drafts_updated_by_idx on public.menu_drafts(updated_by);
create index menu_publications_published_by_idx on public.menu_publications(published_by);
alter table public.restaurants enable row level security;
alter table public.restaurant_members enable row level security;
alter table public.menu_drafts enable row level security;
alter table public.menu_publications enable row level security;
revoke all on public.restaurants,public.restaurant_members,public.menu_drafts,public.menu_publications from anon,authenticated;
-- Membership provisioning remains an operator operation; users cannot grant themselves roles.
grant select on public.restaurants,public.restaurant_members to authenticated;
grant select,insert,update on public.menu_drafts to authenticated;
grant select,insert on public.menu_publications to authenticated;
create policy member_self_read on public.restaurant_members for select to authenticated
 using(user_id=(select auth.uid()));
create policy restaurant_member_read on public.restaurants for select to authenticated
 using(exists(select 1 from public.restaurant_members m where m.restaurant_id=restaurants.id and m.user_id=(select auth.uid()) and m.active));
create policy draft_member_read on public.menu_drafts for select to authenticated
 using(exists(select 1 from public.restaurant_members m where m.restaurant_id=menu_drafts.restaurant_id and m.user_id=(select auth.uid()) and m.active));
create policy draft_editor_insert on public.menu_drafts for insert to authenticated
 with check(updated_by=(select auth.uid()) and exists(select 1 from public.restaurant_members m where m.restaurant_id=menu_drafts.restaurant_id and m.user_id=(select auth.uid()) and m.active and m.role in ('owner','editor')));
create policy draft_editor_update on public.menu_drafts for update to authenticated
 using(exists(select 1 from public.restaurant_members m where m.restaurant_id=menu_drafts.restaurant_id and m.user_id=(select auth.uid()) and m.active and m.role in ('owner','editor')))
 with check(updated_by=(select auth.uid()) and exists(select 1 from public.restaurant_members m where m.restaurant_id=menu_drafts.restaurant_id and m.user_id=(select auth.uid()) and m.active and m.role in ('owner','editor')));
create policy publication_member_read on public.menu_publications for select to authenticated
 using(exists(select 1 from public.restaurant_members m where m.restaurant_id=menu_publications.restaurant_id and m.user_id=(select auth.uid()) and m.active));
create policy publication_editor_insert on public.menu_publications for insert to authenticated
 with check(published_by=(select auth.uid()) and exists(select 1 from public.restaurant_members m where m.restaurant_id=menu_publications.restaurant_id and m.user_id=(select auth.uid()) and m.active and m.role in ('owner','editor')));
-- Invoker security preserves RLS. The expected revision prevents overwriting another editor's changes.
create function public.save_menu_draft(p_restaurant uuid,p_expected bigint,p_content jsonb)
returns setof public.menu_drafts language plpgsql security invoker set search_path=pg_catalog,public as $$
begin
 if auth.uid() is null then raise exception 'authentication required' using errcode='42501'; end if;
 if p_expected<0 or p_content is null or jsonb_typeof(p_content)<>'object' then raise exception 'invalid input' using errcode='22023'; end if;
 if p_expected=0 then
  return query insert into public.menu_drafts(restaurant_id,content,updated_by) values(p_restaurant,p_content,auth.uid())
   on conflict(restaurant_id) do nothing returning *;
 else
  return query update public.menu_drafts set content=p_content,revision=revision+1,updated_by=auth.uid(),updated_at=now()
   where restaurant_id=p_restaurant and revision=p_expected returning *;
 end if;
end $$;
revoke all on function public.save_menu_draft(uuid,bigint,jsonb) from public,anon;
grant execute on function public.save_menu_draft(uuid,bigint,jsonb) to authenticated;
commit;

-- Run as project operator after inviting the owner through Supabase Auth.
-- Replace values interactively in the trusted SQL editor; do not expose admin keys to browsers.
-- Auth invitation/password setup is handled by Supabase Auth, never by storing passwords here.
begin;
with created as (
 insert into public.restaurants(slug,name) values('replace-restaurant-slug','اسم المطعم') returning id
)
insert into public.restaurant_members(restaurant_id,user_id,role)
select created.id,u.id,'owner' from created cross join auth.users u where lower(u.email)=lower('replace-owner-email@example.com');
-- Verify that exactly one owner membership was created before committing; roll back otherwise.
rollback;

alter table account add sz_locale varchar(20) not NULL; 
update account set sz_locale = 'en_US';
alter table account add sz_tz varchar(40) not null;
update account set sz_tz = 'CST';
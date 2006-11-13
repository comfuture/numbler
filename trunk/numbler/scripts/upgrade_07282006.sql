
/* create the new remote_txn table */

create table remote_txn (txnId integer unsigned not null primary key auto_increment, dt_expire DATETIME not null, sheetId integer unsigned not null, colid integer unsigned not null, rowid integer unsigned not null);

create unique index remote_txn_index on remote_txn (sheetId,colid,rowid);
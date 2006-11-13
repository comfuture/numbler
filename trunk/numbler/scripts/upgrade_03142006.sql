
/* might want to do these by hand */

create UNIQUE index dep_unique_idx on ssdb.dep (observed,observer); 
create UNIQUE index cell_unique_idx on ssdb.cell (sheetId,col,row);
create unique index col_unique_idx on ssdb.col (sheetId,colid);
create unique index row_unique_idx on row (sheetId,rowid);
create unique index alias_unique_idx on sheetalias (sheetid,alias(50));


alter table row modify rowid smallint not null;
alter table row add index (rowid);
alter table col add index (colid);

/* need to clear out bogus values for the row information */

delete from col where colid >= 127;
delete from row where rowid >= 127;



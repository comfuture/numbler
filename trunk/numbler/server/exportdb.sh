#!/bin/sh
mkdir -p tables
chmod a+w tables
for table in sheet sheetalias cell dep range col row;
do mysqldump -u ssdb --password=ssdb --no-create-info --tab=tables --lines-terminated-by="\n" ssdb $table;
done;

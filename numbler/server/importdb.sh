#!/bin/sh
for table in sheet sheetalias cell dep range col row;
do mysqlimport --local -u ssdb --password=ssdb --lines-terminated-by="\n" ssdb tables/$table.txt;
done;

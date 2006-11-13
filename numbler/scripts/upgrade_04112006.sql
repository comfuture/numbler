
use ssdb;
alter table sheet add (type smallint unsigned not NULL); /* defaults to 0, public */

CREATE TABLE `account` (
  `id_acc` int(10) unsigned NOT NULL auto_increment,
  `dt_crt` datetime NOT NULL default '0000-00-00 00:00:00',
  `dt_closed` datetime default NULL,
  `sz_user` varchar(255) NOT NULL default '',
  `sz_displayname` varchar(255) NOT NULL default '',
  `pass` varbinary(20) NOT NULL default '',
  `salt` binary(20) NOT NULL default '',
  `api_id` varchar(20) default NULL,
  `api_key` varbinary(20) default NULL,
  `acc_type` smallint(5) unsigned default NULL,
  `state` smallint(5) unsigned default NULL,
  `statetoken` varbinary(20) default NULL,
  `statetoken_dtcrt` datetime default NULL,
  `sz_pendinguser` varchar(255) default NULL,
  PRIMARY KEY  (`id_acc`),
  UNIQUE KEY `sz_user` (`sz_user`),
  KEY `account_sz_user` (`sz_user`),
  KEY `account_api_id` (`api_id`),
  KEY `account_api_key` (`api_key`),
  KEY `account_statetoken` (`statetoken`)
) ENGINE=MyISAM DEFAULT CHARSET=latin1;

CREATE TABLE `acc_sheet_map` (
  `id_acc` int(10) unsigned NOT NULL default '0',
  `sheetId` int(10) unsigned NOT NULL default '0',
  `owner` tinyint(1) default NULL,
  UNIQUE KEY `map_unique_idx` (`id_acc`,`sheetId`,`owner`),
  KEY `acc_sheet_map_id_acc` (`id_acc`),
  KEY `acc_sheet_map_sheetId` (`sheetId`)
) ENGINE=MyISAM DEFAULT CHARSET=latin1;

CREATE TABLE `acc_invite_pending` (
  `id_inviter` int(10) unsigned NOT NULL default '0',
  `sheetId` int(10) unsigned NOT NULL default '0',
  `sz_email` varchar(255) NOT NULL default '',
  UNIQUE KEY `invite_unique_idx` (`sheetId`,`sz_email`),
  KEY `acc_invite_pending_id_inviter` (`id_inviter`),
  KEY `acc_invite_pending_sz_email` (`sz_email`)
) ENGINE=MyISAM DEFAULT CHARSET=latin1;

/* modify the keys on sheetalias so sheetalias is unique to the ID */
drop index alias_unique_idx on sheetalias; 
/* add the primary key */
alter table sheetalias add PRIMARY key (sheetid);
/* add the unique key */
alter table sheetalias add UNIQUE KEY sheetId (sheetId);

insert into account (dt_crt,sz_user,sz_displayname,pass,acc_type,state) values (UTC_TIMESTAMP(),'__defuser','__defuser',SHA('1234SDF#@$@#42323!!(@@(*'),1,0);



insert into acc_sheet_map (id_acc,sheetId,owner) select 1,sheetId,1 from sheet;

analyze TABLE cell,col,dep,range,row,sheet,sheetalias;
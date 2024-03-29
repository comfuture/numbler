
# /usr/lib/python2.4/site-packages/numbler/server/locale/localtab_fr_FR.py
# This file is automatically generated. Do not edit.

_lr_method = 'SLR'

_lr_signature = '\xed \x18j<\xae\x17Ny\xf1_\x92L\x8671'

_lr_action_items = {'EXP':([11,14,17,26,],[35,39,40,-26,]),'TIMESEP':([72,62,17,8,],[41,-21,41,32,]),'SPACE':([64,28,63,2,75,73,43,40,17,20,78,35,9,58,67,61,24,5,14,11,65,26,3,23,59,29,12,27,1,21,72,62,16,10,19,39,15,8,30,34,4,13,22,],[-15,-44,48,-33,48,-14,-35,-30,47,-51,-52,-29,-11,-22,-53,-55,55,-24,-31,-27,-23,-26,-13,53,-54,57,36,48,-19,48,77,-21,-16,-20,-10,-32,-45,33,-50,-34,-25,38,52,]),'CLOCK':([38,47,77,33,],[61,65,65,59,]),'PERCENT':([47,52,11,22,4,2,14,17,39,26,43,35,40,5,34,],[66,69,-27,51,-25,-33,-31,44,-32,-26,-35,-29,-30,-24,-34,]),'SLASH':([15,63,64,27,21,75,17,28,],[-45,45,-15,45,45,45,45,-44,]),'PLUS':([0,36,53,12,23,],[12,12,12,12,12,]),'DASH':([12,17,15,64,36,21,23,28,0,27,75,63,53,],[23,46,-45,-15,23,46,23,-44,23,46,46,46,23,]),'CURRENCY':([40,5,11,43,4,22,34,52,35,17,14,39,26,2,],[-30,-24,-27,-35,-25,50,-34,68,-29,-28,-31,-32,-26,-33,]),'SHORTMONTH':([12,36,42,23,57,46,48,45,47,53,0,],[28,28,28,28,28,-47,-48,-46,-48,28,28,]),'FRACTION':([0,11,12,23,36,17,26,53,],[14,14,14,14,14,14,-26,14,]),'LONGMONTH':([57,46,42,23,45,47,53,0,12,48,36,],[15,-47,15,15,-46,-48,15,15,15,-48,15,]),'INTEGER':([55,76,57,0,47,23,32,41,42,36,56,45,46,49,48,53,12,],[72,78,75,17,-48,17,58,62,63,17,73,-46,-47,67,-48,17,17,]),'COMMAINT':([0,53,23,12,36,],[26,26,26,26,26,]),'$':([29,20,2,28,5,31,4,58,7,66,61,69,34,60,37,25,63,10,14,24,13,19,44,1,39,3,78,65,50,54,68,64,59,67,30,74,22,9,51,40,35,17,43,71,8,6,16,62,11,18,73,26,15,70,21,],[-3,-51,-33,-44,-24,0,-25,-22,-6,-38,-55,-39,-34,-43,-42,-1,-49,-20,-31,-4,-18,-10,-37,-19,-32,-13,-52,-23,-56,-40,-57,-15,-54,-53,-50,-9,-5,-11,-36,-30,-29,-28,-35,-8,-17,-2,-16,-21,-27,-7,-14,-26,-45,-41,-12,]),}

_lr_action = { }
for _k, _v in _lr_action_items.items():
   for _x,_y in zip(_v[0],_v[1]):
       _lr_action[(_x,_k)] = _y
del _lr_action_items

_lr_goto_items = {'medtimeclock':([12,53,55,0,23,36,],[1,1,1,1,1,1,]),'floatdec':([36,12,0,17,23,53,11,],[2,2,2,43,2,2,34,]),'monthyearint':([23,53,36,12,57,0,],[3,3,3,3,3,3,]),'float':([36,12,0,53,23,],[4,4,4,4,4,]),'normalint':([0,23,36,12,53,],[5,5,5,5,5,]),'timedate':([36,12,0,23,53,],[6,6,6,6,6,]),'currency':([23,36,53,0,12,],[7,7,7,7,7,]),'medtime':([55,36,0,12,53,23,],[8,8,8,8,8,8,]),'monthday':([36,12,23,57,0,53,],[9,9,9,9,9,9,]),'datetime':([23,0,53,36,12,],[25,25,25,25,25,]),'commaint':([36,0,53,12,23,],[11,11,11,11,11,]),'longtime':([53,23,0,55,36,12,],[13,13,13,13,13,13,]),'shorttime':([0,36,12,55,23,53,],[16,16,16,16,16,16,]),'percentage':([36,12,53,23,0,],[18,18,18,18,18,]),'formaldate':([12,53,23,57,0,36,],[19,19,19,19,19,19,]),'meddate':([36,0,53,57,23,12,],[20,20,20,20,20,20,]),'datesep':([75,27,21,17,63,],[42,56,49,42,76,]),'monthyear':([53,12,36,0,57,23,],[21,21,21,21,21,21,]),'number':([0,23,36,12,53,],[22,22,22,22,22,]),'date':([53,57,0,12,36,23,],[24,74,24,24,24,24,]),'month':([42,0,23,12,57,53,36,],[64,27,27,27,27,27,27,]),'expression':([0,12,36,53,23,],[31,37,60,70,54,]),'time':([23,0,12,55,36,53,],[29,29,29,71,29,29,]),'shortdate':([12,57,36,53,0,23,],[30,30,30,30,30,30,]),'longtimeclock':([0,53,55,36,12,23,],[10,10,10,10,10,10,]),}

_lr_goto = { }
for _k, _v in _lr_goto_items.items():
   for _x,_y in zip(_v[0],_v[1]):
       _lr_goto[(_x,_k)] = _y
del _lr_goto_items
_lr_productions = [
  ("S'",1,None,None,None),
  ('expression',1,'p_all_expressions','/usr/lib/python2.4/site-packages/numbler/server/locale/parser_fr_FR.py',55),
  ('expression',1,'p_all_expressions','/usr/lib/python2.4/site-packages/numbler/server/locale/parser_fr_FR.py',56),
  ('expression',1,'p_all_expressions','/usr/lib/python2.4/site-packages/numbler/server/locale/parser_fr_FR.py',57),
  ('expression',1,'p_all_expressions','/usr/lib/python2.4/site-packages/numbler/server/locale/parser_fr_FR.py',58),
  ('expression',1,'p_all_expressions','/usr/lib/python2.4/site-packages/numbler/server/locale/parser_fr_FR.py',59),
  ('expression',1,'p_all_expressions','/usr/lib/python2.4/site-packages/numbler/server/locale/parser_fr_FR.py',60),
  ('expression',1,'p_all_expressions','/usr/lib/python2.4/site-packages/numbler/server/locale/parser_fr_FR.py',61),
  ('datetime',3,'p_datetime','/usr/lib/python2.4/site-packages/numbler/server/locale/parser_fr_FR.py',66),
  ('timedate',3,'p_timedate','/usr/lib/python2.4/site-packages/numbler/server/locale/parser_fr_FR.py',71),
  ('date',1,'p_date','/usr/lib/python2.4/site-packages/numbler/server/locale/parser_fr_FR.py',76),
  ('date',1,'p_date','/usr/lib/python2.4/site-packages/numbler/server/locale/parser_fr_FR.py',77),
  ('date',1,'p_date','/usr/lib/python2.4/site-packages/numbler/server/locale/parser_fr_FR.py',78),
  ('date',1,'p_date','/usr/lib/python2.4/site-packages/numbler/server/locale/parser_fr_FR.py',79),
  ('monthday',3,'p_monthday','/usr/lib/python2.4/site-packages/numbler/server/locale/parser_fr_FR.py',91),
  ('monthyear',3,'p_monthyear','/usr/lib/python2.4/site-packages/numbler/server/locale/parser_fr_FR.py',106),
  ('time',1,'p_time','/usr/lib/python2.4/site-packages/numbler/server/locale/parser_fr_FR.py',120),
  ('time',1,'p_time','/usr/lib/python2.4/site-packages/numbler/server/locale/parser_fr_FR.py',121),
  ('time',1,'p_time','/usr/lib/python2.4/site-packages/numbler/server/locale/parser_fr_FR.py',122),
  ('time',1,'p_time','/usr/lib/python2.4/site-packages/numbler/server/locale/parser_fr_FR.py',123),
  ('time',1,'p_time','/usr/lib/python2.4/site-packages/numbler/server/locale/parser_fr_FR.py',124),
  ('medtime',3,'p_medtime','/usr/lib/python2.4/site-packages/numbler/server/locale/parser_fr_FR.py',130),
  ('longtime',3,'p_longtime','/usr/lib/python2.4/site-packages/numbler/server/locale/parser_fr_FR.py',136),
  ('shorttime',3,'p_short_time','/usr/lib/python2.4/site-packages/numbler/server/locale/parser_fr_FR.py',143),
  ('number',1,'p_number','/usr/lib/python2.4/site-packages/numbler/server/locale/parser_fr_FR.py',150),
  ('number',1,'p_number','/usr/lib/python2.4/site-packages/numbler/server/locale/parser_fr_FR.py',151),
  ('commaint',1,'p_commaint','/usr/lib/python2.4/site-packages/numbler/server/locale/parser_fr_FR.py',159),
  ('normalint',1,'p_normalint','/usr/lib/python2.4/site-packages/numbler/server/locale/parser_fr_FR.py',163),
  ('normalint',1,'p_normalint','/usr/lib/python2.4/site-packages/numbler/server/locale/parser_fr_FR.py',164),
  ('normalint',2,'p_normalint','/usr/lib/python2.4/site-packages/numbler/server/locale/parser_fr_FR.py',165),
  ('normalint',2,'p_normalint','/usr/lib/python2.4/site-packages/numbler/server/locale/parser_fr_FR.py',166),
  ('floatdec',1,'p_floatdec','/usr/lib/python2.4/site-packages/numbler/server/locale/parser_fr_FR.py',175),
  ('floatdec',2,'p_floatdec','/usr/lib/python2.4/site-packages/numbler/server/locale/parser_fr_FR.py',176),
  ('float',1,'p_float','/usr/lib/python2.4/site-packages/numbler/server/locale/parser_fr_FR.py',185),
  ('float',2,'p_float','/usr/lib/python2.4/site-packages/numbler/server/locale/parser_fr_FR.py',186),
  ('float',2,'p_float','/usr/lib/python2.4/site-packages/numbler/server/locale/parser_fr_FR.py',187),
  ('percentage',2,'p_percentage','/usr/lib/python2.4/site-packages/numbler/server/locale/parser_fr_FR.py',204),
  ('percentage',2,'p_percentage','/usr/lib/python2.4/site-packages/numbler/server/locale/parser_fr_FR.py',205),
  ('percentage',3,'p_percentage','/usr/lib/python2.4/site-packages/numbler/server/locale/parser_fr_FR.py',206),
  ('percentage',3,'p_percentage','/usr/lib/python2.4/site-packages/numbler/server/locale/parser_fr_FR.py',207),
  ('expression',2,'p_expr_negation','/usr/lib/python2.4/site-packages/numbler/server/locale/parser_fr_FR.py',213),
  ('expression',3,'p_expr_negation','/usr/lib/python2.4/site-packages/numbler/server/locale/parser_fr_FR.py',214),
  ('expression',2,'p_expr_positive','/usr/lib/python2.4/site-packages/numbler/server/locale/parser_fr_FR.py',222),
  ('expression',3,'p_expr_positive','/usr/lib/python2.4/site-packages/numbler/server/locale/parser_fr_FR.py',223),
  ('month',1,'p_month','/usr/lib/python2.4/site-packages/numbler/server/locale/parser_fr_FR.py',231),
  ('month',1,'p_month','/usr/lib/python2.4/site-packages/numbler/server/locale/parser_fr_FR.py',232),
  ('datesep',1,'p_datesep','/usr/lib/python2.4/site-packages/numbler/server/locale/parser_fr_FR.py',261),
  ('datesep',1,'p_datesep','/usr/lib/python2.4/site-packages/numbler/server/locale/parser_fr_FR.py',262),
  ('datesep',1,'p_datesep','/usr/lib/python2.4/site-packages/numbler/server/locale/parser_fr_FR.py',263),
  ('monthyearint',3,'p_monthyearint','/usr/lib/python2.4/site-packages/numbler/server/locale/parser_fr_FR.py',270),
  ('formaldate',1,'p_formaldate','/usr/lib/python2.4/site-packages/numbler/server/locale/parser_fr_FR.py',293),
  ('formaldate',1,'p_formaldate','/usr/lib/python2.4/site-packages/numbler/server/locale/parser_fr_FR.py',294),
  ('shortdate',5,'p_shortdate','/usr/lib/python2.4/site-packages/numbler/server/locale/parser_fr_FR.py',300),
  ('meddate',3,'p_meddate','/usr/lib/python2.4/site-packages/numbler/server/locale/parser_fr_FR.py',316),
  ('medtimeclock',3,'p_medtimeclock','/usr/lib/python2.4/site-packages/numbler/server/locale/parser_fr_FR.py',324),
  ('longtimeclock',3,'p_longtimeclock','/usr/lib/python2.4/site-packages/numbler/server/locale/parser_fr_FR.py',332),
  ('currency',2,'p_currency','/usr/lib/python2.4/site-packages/numbler/server/locale/parser_fr_FR.py',339),
  ('currency',3,'p_currency','/usr/lib/python2.4/site-packages/numbler/server/locale/parser_fr_FR.py',340),
]

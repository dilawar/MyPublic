# This file is part of pyDC software
# Copyright 2002 Anakim Border <aborder@users.sourceforge.net>
#
# pyDC is released under the terms of GPL licence.

import sys

sys.path.append('./he3_ed/')

from he3_ed.he3 import *

from DCFileList import *

class DCLocalListWriter:
  def __init__(self):
      pass 

  def write(self, filename, lists):
    s = ''
    for l in lists:
      for i in l._list:
        s += self.writeItem(i)

    f = open(filename, "wb")
    p = He3Encoder()
    f.write(p.encode(s))
    f.close()
    
  ###################
  # Private members #
  ###################

  def writeItem(self, item, level = 0):
    s = ''
    for i in range(0, level): s += '\t'

    if item.__class__ == UserDir:
      s += item.name + '\r\n'
      for i in item.children:
        s += self.writeItem(i, level+1)
    else:
      s += item.name + '|' + str(item.size) + '\r\n'
      
    return s

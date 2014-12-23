from __future__ import print_function
import sys

def msg(m): 
    print(m)
def dashes(): msg('-' * 40)
def msgn(m): msg('\n'); msg(m); dashes()
def msgt(m): dashes(); msg(m); dashes()
def msgx(m): msgt(m); msg('exiting..'); sys.exit(0)

import os

outlines = []
for line in open('input/15tstcar-2014-11-13.csv', 'r').readlines():
    if not line in outlines:
        outlines.append(line)

fname = 'input/carlist.csv'
open(fname, 'w').write('\n'.join(outlines))
print 'written: ', fname
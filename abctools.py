#!/usr/bin/python

import sys

chords = {
    'C': ('c','e','g'),
    'Dm': ('d','f','a'),
    'Em': ('e','g','b'),
    'F': ('f','a','c'),
    'G': ('g','b','d'),
    'Am': ('a','c','e')
}

def load_abc_file(fname):
    abc = {}
    with open(fname, 'r') as f:
        lines = f.readlines()
    i = 0
    for line in lines:
        line = line.strip()
        parts = line.split(':')
        header = parts[0].strip().upper()
        if len(header) != 1 or header not in ('X','T','R','M','L','K'):
            break
        abc[header] = ':'.join( parts[1:] ).strip()
        i += 1

    abc['tune'] = ' '.join( map( lambda x: x.strip(), lines[i:] ) ).strip()

    if 'X:' in abc['tune']:
        print 'Woops, more than one tune found in this file!'
        sys.exit(0)

    return abc

def extract_bars(tune):
    bars = tune.replace(':','').replace(' ','').split('|')
    for bar in bars:
        if len(bar)==0:
            bars.remove(bar)
    return bars

def main(argv):
    abc = load_abc_file( argv[1] )
    print '\t', abc['T'], '(%s)' % abc['K']
    if abc['K'] != "C" and abc['K'] != "Cmaj":
        print 'Woops, key is not C major!'
        sys.exit(0)
    i = 1
    for bar in extract_bars( abc['tune'] ):
        print i, bar
        i += 1
    
    #import pdb; pdb.set_trace()
    return 0

if __name__ == '__main__':
    sys.exit( main(sys.argv) )

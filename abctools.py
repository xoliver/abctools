#!/usr/bin/python

from operator import itemgetter
import re
import sys

# TODO
#   -Tolerate other headers (no big deal)
#   -Support accidentals (^,^^,=,_,__)
#
#
#
#
#

note_finder = re.compile('[a-g](?:\d+|/\d+|/*)')

chords = {
    'C': ('c','e','g'),
    'Dm': ('d','f','a'),
    'Em': ('e','g','b'),
    'F': ('f','a','c'),
    'G': ('g','b','d'),
    'Am': ('a','c','e')
}

scale = ['c','d','e','f','g','a','b']

def get_note_duration(note):
    """
    Return the duration of a note given as a string based on the note_finder
    regular expression: N , N/+ , N\d+ , N/\d+
    """

    if len(note) == 1:
        return 1.0
    else:
        duration = note[1:]
        if len( duration.replace('/','') ) == 0:
            return 1.0 / pow(2,len(duration))
        else:
            return float(duration)

def find_chords(bar):
    # Ignore octave and accidentals
    # TODO don't ignore accidentals
    bar = bar.translate(None,",'^=_").lower()
    notes = note_finder.findall(bar)
    count = 0.0
    note_count = {}

    #Get count of the given bar, just to try things
    for note in notes:
        duration = get_note_duration(note)
        if note[0] in note_count:
            note_count[note[0]] += duration
        else:
            note_count[note[0]] = duration

    found = {}
    for note in note_count.keys():
        for chord in chords.keys():
            if note in chords[chord]:
                if chord in found:
                    found[chord] += note_count[note]
                else:
                    found[chord] = note_count[note]

    return found

def load_abc_file(fname):
    """
    Read ABC file and return a dictionary containing the different headers plus
    the tune in the key 'tune'
    """

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
    """
    Separate a tune into bars ignoring bar playing order indicators and spaces
    and return an array with them
    """

    bars = tune.translate(None,': ').split('|')
    for bar in bars:
        if len(bar)==0:
            bars.remove(bar)
    return bars

def get_top_chords( found_chords ):
    highest = max( found_chords.values() )
    top = []
    for chord in found_chords:
        if found_chords[chord] == highest:
            top.append( chord )
    return top

def main(argv):
    abc = load_abc_file( argv[1] )
    print '\t', abc['T'], '(%s)' % abc['K']
    if abc['K'] != "C" and abc['K'] != "Cmaj":
        print 'Woops, key is not C major!'
        sys.exit(0)
    i = 1
    for bar in extract_bars( abc['tune'] ):
        found_chords = find_chords(bar)
        orderered_chords = sorted(found_chords.items(), key=itemgetter(1), reverse=True)
        print i, bar, get_top_chords( found_chords )
        #print i, bar, orderered_chords
        i += 1
    
    #import pdb; pdb.set_trace()
    return 0

if __name__ == '__main__':
    sys.exit( main(sys.argv) )

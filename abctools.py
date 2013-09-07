#!/usr/bin/python

from operator import itemgetter
import re
import sys

# TODO
#   -Tolerate other headers (no big deal)
#

note_finder = re.compile('(=?|\^|\^\^|_|__)([a-g])(\d+|/\d+|/*)')

scale = ('c','d','e','f','g','a','b')
major_scale_chord_suffixes = ('','m','m','','','m','dim')
minor_scale_chord_suffixes = ('m','dim','','m','m','','')

def abort(message):
    print message
    sys.exit(0)

def generate_chord_dict( root, major=True, skip_dim=True ):
    root = root.lower()
    if root not in scale:
        abort('Oops, root does not seem to be valid')

    if major:
        suffixes = major_scale_chord_suffixes
    else:
        suffixes = minor_scale_chord_suffixes

    chords = {}
    current = root
    total = 6 if skip_dim else 7
    while len(chords) < total:
        pos = scale.index(current)
        name = current.upper() + suffixes[ len(chords) ]
        current = scale[(pos+1)%7]

        if skip_dim and name[1:] == 'dim':
            continue
        chords[name]=(scale[pos], scale[(pos+2)%7],scale[(pos+4)%7])

    return chords

def calculate_note_duration(duration):
    """
    Return the duration of a note given as a string based on the note_finder
    regular expression: N , N/+ , N\d+ , N/\d+
    """

    if len(duration) == 0:
        return 1.0
    else:
        if len( duration.replace('/','') ) == 0:
            return 1.0 / pow(2,len(duration))
        else:
            return float(duration)

def find_chords(bar,chords):
    """
    Find potential chords for a given bar and return a dictionary with their
    scores
    """

    # Ignore octave
    bar = bar.translate(None,",'").lower()
    notes = note_finder.findall(bar)
    count = 0.0
    note_count = {}

    #Get count of the given bar, just to try things
    for (accidentals,note,duration) in notes:
        if accidentals:
            abort('Oops, found accidental and this is not supported yet!')
        duration = 1 if len(duration)==0 else calculate_note_duration(duration)
        if note[0] in note_count:
            note_count[note] += duration
        else:
            note_count[note] = duration

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
    Read ABC file and return a dictionary containing the different headers
    plus the tune in the key 'tune'
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
        aborT('Oops, more than one tune found in this file!')

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
    """
    Find the highest scoring chord(s)
    """

    highest = max( found_chords.values() )
    top = []
    for chord in found_chords:
        if found_chords[chord] == highest:
            top.append( chord )
    return top

def main(argv):
    skip_dim = True
    abc = load_abc_file( argv[1] )
    print '\t', abc['T'], '(%s)' % abc['K']

    key = abc['K']

    if len(key) == 1:
        is_major_key = True
    else:
        if key[1] in '#b':
            abort('Oops, flat and sharp roots are not supported yet')
        if key[1:].lower() == 'maj':
            is_major_key = True
        else:
            if key[1:].lower() in ('m','min'):
                is_major_key = False
            else:
                abort('Oops, unsupported key')

    is_major_key = len(key)==1 or key[1:].lower() == 'maj'
    scale_chords = generate_chord_dict(
                        key[0],
                        major=is_major_key,
                        skip_dim=skip_dim )
    print 'Using chords in %s %s %s:' % (
            key[0],
            'major' if is_major_key else 'minor',
            '(skipping diminished)' if skip_dim else '' )
    print scale_chords

    i = 1
    for bar in extract_bars( abc['tune'] ):
        found_chords = find_chords(bar,scale_chords)
        orderered_chords = sorted( 
                            found_chords.items(),
                            key=itemgetter(1),
                            reverse=True)

        print i, bar, get_top_chords( found_chords )
        #print i, bar, orderered_chords
        i += 1
    
    return 0

if __name__ == '__main__':
    sys.exit( main(sys.argv) )

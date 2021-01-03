# No Imports Allowed!


def backwards(sound):
    r_sound = sound.copy()
    r_sound["left"] = []
    r_sound["right"] = []

    r_sound["left"] = [l for l in reversed(sound["left"])]
    r_sound["right"] = [r for r in reversed(sound["right"])]

    return r_sound


def mix(sound1, sound2, p):
    if sound1["rate"] != sound2["rate"]:
        return None

    mixed = {"rate": sound1["rate"]}

    mixed["left"] = [p * l1 + (1 - p) * l2 for l1, l2 in zip(sound1["left"], sound2["left"])]
    mixed["right"] = [p * r1 + (1 - p) * r2 for r1, r2 in zip(sound1["right"], sound2["right"])]

    return mixed


def echo_samples(samples, sample_delay, scale ):


    new_samples = samples.copy()

    st_idx = len(samples)

    for i in range(sample_delay):
        scale_idx = st_idx - sample_delay
        if scale_idx < 0:
            new_samples.append( 0 )
        else:
            new_samples.append( scale * samples[ scale_idx ]  )
        st_idx += 1
    return new_samples


def echo(sound, num_echos, delay, scale):

    sample_delay = round(delay * sound["rate"])

    echoed = {"rate": sound["rate"] }

    left = sound["left"]
    right = sound["right"]
    for num in range( num_echos ):
        left = echo_samples(left, sample_delay, scale )
        right = echo_samples(right, sample_delay, scale )
    
    echoed["left"] = left
    echoed["right"] = right

    return echoed
    
def pan(sound):
    
    panned = {"rate": sound["rate"]}
    left_scale = lambda x,i: x * ( 1 - (i / ( len(sound["left"]) - 1 )) )
    right_scale = lambda x,i: x * ( i / (len(sound["right"]) - 1 ))

    panned["left"] = [ left_scale(l, i) for i, l in enumerate(sound["left"]) ]
    panned["right"] = [ right_scale(r, i) for i, r in enumerate(sound["right"])]
    
    return panned



def remove_vocals(sound):
    wo_vocal = {"rate": sound["rate"]}

    wo_vocal["left"] = [l - r for l, r in zip(sound["left"], sound["right"])]
    wo_vocal["right"] = wo_vocal["left"].copy()

    return wo_vocal

# below are helper functions for converting back-and-forth between WAV files
# and our internal dictionary representation for sounds

import io
import wave
import struct

def load_wav(filename):
    """
    Given the filename of a WAV file, load the data from that file and return a
    Python dictionary representing that sound
    """
    f = wave.open(filename, 'r')
    chan, bd, sr, count, _, _ = f.getparams()

    assert bd == 2, "only 16-bit WAV files are supported"

    left = []
    right = []
    for i in range(count):
        frame = f.readframes(1)
        if chan == 2:
            left.append(struct.unpack('<h', frame[:2])[0])
            right.append(struct.unpack('<h', frame[2:])[0])
        else:
            datum = struct.unpack('<h', frame)[0]
            left.append(datum)
            right.append(datum)

    left = [i/(2**15) for i in left]
    right = [i/(2**15) for i in right]

    return {'rate': sr, 'left': left, 'right': right}


def write_wav(sound, filename):
    """
    Given a dictionary representing a sound, and a filename, convert the given
    sound into WAV format and save it as a file with the given filename (which
    can then be opened by most audio players)
    """
    outfile = wave.open(filename, 'w')
    outfile.setparams((2, 2, sound['rate'], 0, 'NONE', 'not compressed'))

    out = []
    for l, r in zip(sound['left'], sound['right']):
        l = int(max(-1, min(1, l)) * (2**15-1))
        r = int(max(-1, min(1, r)) * (2**15-1))
        out.append(l)
        out.append(r)

    outfile.writeframes(b''.join(struct.pack('<h', frame) for frame in out))
    outfile.close()


if __name__ == '__main__':
    # code in this block will only be run when you explicitly run your script,
    # and not when the tests are being run.  this is a good place to put your
    # code for generating and saving sounds, or any other code you write for
    # testing, etc.

    # here is an example of loading a file (note that this is specified as
    # sounds/hello.wav, rather than just as hello.wav, to account for the
    # sound files being in a different directory than this file)
    car = load_wav('sounds/car.wav')

    write_wav(pan(car), 'sounds/car_pan.wav')

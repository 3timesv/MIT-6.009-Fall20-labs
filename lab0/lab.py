# No Imports Allowed!


import io
import struct
import wave


def backwards(sound):
    """
    Reverse given sound.

    Args:
        sound (dict): given sound of interest.

    Returns:
        (dict)
    """

    backward_sound = sound.copy()

    backward_sound["left"] = list(reversed(sound["left"]))
    backward_sound["right"] = list(reversed(sound["right"]))

    return backward_sound


def mix(sound1, sound2, p):
    """
    Mix two sounds together.

    Args:
        sound1 (dict): first sound
        sound2 (dict): second sound
        p (float): proportion of first sound to add; must lie between 0 and 1;
            second sound will be in (1-p) proportion.

    Returns:
        (dict)
    """

    if sound1["rate"] != sound2["rate"]:
        return None

    mixed = {"rate": sound1["rate"]}

    left = zip(sound1["left"], sound2["left"])
    right = zip(sound1["right"], sound2["right"])
    mixed["left"] = [p * l1 + (1 - p) * l2 for l1, l2 in left]
    mixed["right"] = [p * r1 + (1 - p) * r2 for r1, r2 in right]

    return mixed


def echo_filter(samples, sample_delay, scale):
    """
    Apply Echo filter to given list of samples.

    Args:
        samples (list): list of samples to apply filter on.
        sample_delay (int): amount by which each sample should be offset.
        scale (float): amount by which each sample should be scaled.

    Returns:
        (list)
    """

    new_samples = samples.copy()

    # index at which first echoed sample will append.
    start_idx = len(samples)

    for _ in range(sample_delay):
        # index whose element will scaled and inserted at start_idx
        scale_idx = start_idx - sample_delay

        if scale_idx < 0:
            new_samples.append(0)
        else:
            new_samples.append(scale * samples[scale_idx])
        start_idx += 1

    return new_samples


def echo(sound, num_echos, delay, scale):
    """
    Apply Echo filter to given (stereo) sound.

    Args:
        sound (dict): representation of original sound.
        num_echos (int): # additional coipies of sound to add.
        delay (float): amount (seconds) by which each "echo" should be delayed.
        scale (float): amount by which each echo's sample is scaled.

    Returns:
        (dict)
    """

    sample_delay = round(delay * sound["rate"])

    echoed = {"rate": sound["rate"]}

    left, right = sound["left"], sound["right"]

    for _ in range(num_echos):
        left = echo_filter(left, sample_delay, scale)
        right = echo_filter(right, sample_delay, scale)

    echoed["left"], echoed["right"] = left, right

    return echoed


def pan(sound):
    """
    Pan the given sound.

    Args:
        sound (dict): requires sound to be stereo.

    Returns:
        (dict)
    """

    panned = {"rate": sound["rate"]}

    def left_scale(sample, idx):
        # start at full volume and end at zero volume

        return sample * (1 - (idx / (len(sound["left"]) - 1)))

    def right_scale(sample, idx):
        # start at zero volume and end at full volume

        return sample * (idx / (len(sound["right"]) - 1))

    panned["left"] = [left_scale(s, i) for i, s in enumerate(sound["left"])]
    panned["right"] = [right_scale(s, i) for i, s in enumerate(sound["right"])]

    return panned


def remove_vocals(sound):
    """
    Remove vocals from sound.

    Args:
        sound (dict): given sound with vocals

    Returns:
        (dict)
    """

    wo_vocal = {"rate": sound["rate"]}

    left_right = zip(sound["left"], sound["right"])

    wo_vocal["left"] = [ls - rs for ls, rs in left_right]
    wo_vocal["right"] = wo_vocal["left"].copy()

    return wo_vocal

# below are helper functions for converting back-and-forth between WAV files
# and our internal dictionary representation for sounds


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

    # car = load_wav('sounds/car.wav')

    # write_wav(pan(car), 'sounds/car_pan.wav')

    pass

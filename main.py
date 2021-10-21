import sounddevice as sd
import soundfile as sf
import numpy as np
import math
from matplotlib import pyplot as plt

SAMPLE_RATE = 44100


def safe_wrap(f):
    def new_f(x):
        try:
            y = f(x)
            return y if y not in (np.inf, np.NINF) else np.nan
        except:
            return np.nan

    return new_f


def semitones_offset(base, offset):
    return base * np.power(2, offset / 12)


def render_function(f, domain, note_range, seconds, range_limit=None):
    num_samples = int(seconds * SAMPLE_RATE)

    # Run the function on N inputs evenly spread over the desired domain
    f_inputs = np.linspace(domain[0], domain[1], num_samples)
    f_values = (np.vectorize(safe_wrap(f)))(f_inputs)

    # Cut off any values outside of the acceptable range, this is useful
    # for functions with vertical asymptotes
    if range_limit != None:
        f_values[(f_values < range_limit[0]) | (
            f_values > range_limit[1])] = np.nan

    # Estimate the range of the function, ignoring NaN values
    f_range = (np.nanmin(f_values), np.nanmax(f_values))

    # Set the volume to zero whenever the function is undefined
    amplitude = np.where(np.isnan(f_values), 0.0, 1.0)

    # Map each function value onto an amount of semitones relative to A4
    semitone_values = np.interp(f_values, f_range, note_range)

    # Convert the notes from semitones to Hz
    freq_values = semitones_offset(440, semitone_values)
    # Zero out the NaN values so they don't interfere with other calculations
    freq_values[np.isnan(freq_values)] = 0

    # Integrate the frequency values
    freq_integral = np.cumsum(freq_values)

    samples = amplitude * np.sin(2 * np.pi * freq_integral / SAMPLE_RATE)
    return samples


# f = lambda x: 1/8 * (x + 2) * (x - 1) * (x - 3)
#
# seconds = 2
# domain = (-2.5, 5)
# note_range = (-12, 12)

# f = lambda x: math.sqrt(-x+4)
#
# seconds = 5
# domain = (0, 6)
# note_range = (-24, 24)

f = math.tan

seconds = 10
domain = (-math.pi/2, math.pi*7/2)
note_range = (-24, 12)
range_limit = (-6, 6)

samples = render_function(f, domain, note_range, seconds, range_limit)

sd.play(samples, SAMPLE_RATE)
sd.wait()
sf.write("graph.wav", samples, SAMPLE_RATE)

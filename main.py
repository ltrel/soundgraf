import sounddevice as sd
import soundfile as sf
import numpy as np

SAMPLE_RATE = 44100


def estimate_range(f, min_x, max_x, num_samples):
    # Who needs calculus
    inputs = np.linspace(min_x, max_x, num_samples)[1:]
    min = max = f(min_x)
    for x in inputs:
        y = f(x)
        if y < min:
            min = y
        elif y > max:
            max = y
    return (min, max)


def semitones_offset(base, offset):
    return base * np.power(2, offset / 12)


def render_function(f, domain, note_range, seconds):
    note_min, note_max = note_range

    # Estimate the range of the function across the desired domain
    # down to a resolution of one millisecond
    f_range = estimate_range(f, domain[0], domain[1], int(seconds * 1000))

    num_samples = int(seconds * SAMPLE_RATE)

    # Run the function on N inputs evenly spread over the desired domain
    f_inputs = np.linspace(domain[0], domain[1], num_samples)
    f_values = (np.vectorize(f))(f_inputs)

    # Map each function value onto an amount of semitones relative to A4
    semitone_values = np.interp(f_values, f_range, note_range)
    # Convert the notes from semitones to Hz
    freq_values = semitones_offset(440, semitone_values)

    # Integrate the frequency values
    freq_integral = np.cumsum(freq_values)

    samples = np.sin(2 * np.pi * freq_integral / SAMPLE_RATE)
    return samples


def f(x): return 1/8 * (x + 2) * (x - 1) * (x - 3)

seconds = 2
domain = (-2.5, 5)
note_range = (-12, 12)

samples = render_function(f, domain, note_range, seconds)

sd.play(samples, SAMPLE_RATE)
sd.wait()
sf.write("graph.wav", samples, SAMPLE_RATE)

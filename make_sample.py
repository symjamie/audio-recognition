# Filename: make_sample.py
# Description: clip an audio file and add noise, output to the same directory.
# Author: Yiming Sun
# Created: Dec 10, 2019

import sys
import librosa
import numpy as np

def main(argv):
	infile = argv[1]
	start = float(argv[2])
	dur = float(argv[3])
	noise_ratio = float(argv[4])

	x, sr = librosa.load(infile)

	# Scale to -1.0 - 1.0.
	x = x.astype(np.float32) / 32767.0 
	# Make max be 1.0.
	x = (1.0 / max(x)) * x
	print

	# Clip.
	start_idx = int(start * sr)
	end_idx = int((start + dur) * sr)
	clip = x[start_idx : end_idx]
	
	# Add noise.
	if noise_ratio != 0:
		noise = np.random.normal(0, noise_ratio, len(clip))
		clip = clip + noise

	# Write to file.
	outfile = "{}_{:0.0f}-{:0.0f}_{}.wav".format(infile[:-4], start, start+dur, noise_ratio)

	librosa.output.write_wav(outfile, clip, sr)


if __name__ == '__main__':
	if len(sys.argv) != 5:
		print("Usage: $ python3 make_sample.py <filename> <start time (sec)> <duration (sec)> <noise ratio (0-1)>")
		exit(1)
	main(sys.argv)
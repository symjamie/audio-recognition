# Filename: main.py
# Description: main program.
# Author: Yiming Sun
# Created: Dec 10, 2019

import os
import time
import librosa
import sqlite3
import numpy as np
from scipy.signal import stft
from config import get_config, print_usage

# ----------------------------------------
# Purpose:
#	Fingerprinting an audio signal.
# Parameters:
#	x: input signal (1-d list of floats)
#	params: parameters (dictionary)
# Return:
# 	fps: fingerprints (list of tuples as below)
#		(archor time in frame, (anchor's frequency, target point's frequency, time difference in frames))
def fingerprint(x, params):
	# Find peak frequency in each frame with Short-time Fourier transform.
	f, t, Zxx = stft(x, params["sr"], nperseg=params["win_size"])
	max_f_idx = np.argmax(np.abs(Zxx).T, axis=1)

	# Divide frequencies into 1024 bins (10 Hz each, maximum 10230 Hz).
	peaks = []
	for i in max_f_idx:
		p = int(f[i]//10)
		if p > 1023:
			p = 1023
		peaks += [p]

	fps = []
	# Iterate by time (index of frame) of anchor.
	for i in range(len(peaks)-params["anchor_dist"]-params["fan_out"]):
		anchor_f = peaks[i]
		for j in range(i+params["anchor_dist"], i+params["anchor_dist"]+params["anchor_dist"]):
			target_f = peaks[j]
			det_t = j - i
			# Hash each fingerprint into a 30-bit integer.
			fp = (anchor_f<<20) + (target_f<<10) + det_t
			fps += [(i, fp)]

	return fps


# ----------------------------------------
# Purpose:
#	Initialize the parameters and tables in the database.
# Parameters:
#	config: config instance
#	conn: Sqlite3 Connection instance
def initialize(config, conn):
	conn = sqlite3.connect(config.db)

	conn.execute("""CREATE TABLE IF NOT EXISTS Parameters (
					sr INT,
					win_size INT,
					anchor_dist INT,
					fan_out INT
					)""")

	conn.execute("""INSERT INTO Parameters VALUES (?, ?, ?, ?)""", 
					(config.sr, config.win_size, config.anchor_dist, config.fan_out))


	conn.execute("""CREATE TABLE IF NOT EXISTS Songs (
					id TINYINT,
					name VARCHAR,
					PRIMARY KEY (id)
					)""")

	conn.execute("""CREATE TABLE IF NOT EXISTS Fingerprints (
					id TINYINT,
					anchor_t SMALLINT,
					fp INT
					)""")

	conn.execute("""CREATE INDEX IF NOT EXISTS fp_idx ON Fingerprints (fp)""")

	conn.commit()


# ----------------------------------------
# Purpose:
#	Fetch parameters in the database.
# Parameters:
#	conn: Sqlite3 Connection instance
# Return:
# 	param: parameters (dictionary)
def parameters(conn):
	params = {}

	p = conn.execute("""SELECT * FROM Parameters""").fetchall()[0]
	params["sr"] = p[0]
	params["win_size"] = p[1]
	params["anchor_dist"] = p[2]
	params["fan_out"] = p[3]

	return params


# ----------------------------------------
# Purpose:
#	Build the database with the dataset.
# Parameters:
#	config: config instance
def build(config):
	conn = sqlite3.connect(config.db)
	initialize(config, conn)

	params = parameters(conn)
	path = config.dataset
	audios = os.listdir(path)

	start = time.time() # Runtime counter.

	idx = 0 # ID of each song.
	for audio in audios:
		if audio[-4:] not in [".wav", ".mp3"]:
			continue

		# Insert into Songs table.
		print(idx, audio)
		conn.execute("""INSERT INTO Songs VALUES (?, ?)""", (idx, audio[:-4]))

		# Fingerprint songs.
		if path[-1] != "/":
		    path = path + "/"
		x, sr = librosa.load(path+audio)
		# Resample if the sample rate is inconsistent.
		if sr != config.sr:
			x = librosa.core.resample(x, sr, config.sr)

		fps = fingerprint(x, params)

		# Insert into Fingerprints table.
		for fp in fps:
			conn.execute("""INSERT INTO Fingerprints VALUES (?, ?, ?)""", (idx, fp[0], fp[1]))
	        
		idx += 1
    
	print("Time spent on loading and fingerprinting {} song(s): {:.2f} s\n".format(idx, time.time()-start))

	conn.commit()
	conn.close()


# ----------------------------------------
# Purpose:
#	Query the sample in the fingerprint database.
# Parameters:
#	config: config instance
def query(config):
	conn = sqlite3.connect(config.db)
	params = parameters(conn)

	# Load sample audio.
	y, sr = librosa.load(config.sample)
	# Resample if the sample rate is inconsistent.
	if sr != config.sr:
		y = librosa.core.resample(x, sr, config.sr)

	start = time.time() # Runtime counter.

	fps_sample = fingerprint(y, params)

	offsets = {} # {id: [offsets (integer)]}
	for anchor_t_sample, fp in fps_sample:
		# [(id, anchor_t, fp)]
		fps_db = conn.execute("""SELECT * FROM Fingerprints WHERE fp = (?)""", (fp,)).fetchall()
		for id, anchor_t, _ in fps_db:
			if id not in offsets:
				offsets[id] = []
			offsets[id] += [anchor_t - anchor_t_sample]

	score = {} # {id: score (integer)}
	for id, ofs in offsets.items():
		# Score is the highest number of occurances in offsets.
		score[id] = max(np.histogram(ofs)[0])

	# Sort IDs descending by score.
	ids_sorted = sorted(score, key=(lambda key:score[key]), reverse=True)
	
	res = [] # [(name, score)]
	for i in range(len(ids_sorted)):
		name = conn.execute("""SELECT name FROM Songs WHERE id = (?)""", (ids_sorted[i],)).fetchall()[0][0]
		s = score[ids_sorted[i]]
		res += [(name, s)]

	# Print results.
	print(config.sample)

	if res == []:
		print("No match.")
	else:
		print("Top 10 results:")
		top_score = res[0][1]
		total_score = sum(x[1] for x in res)
		for i in range(len(res)):
			if i == 10:
				break
			name = res[i][0]
			score = res[i][1]
			# The top result is set to 100%.
			match = score / top_score * 100
			# Measure of confidence.
			score_pct = score / total_score * 100
			print("{:2d}. {}: {:.2f}%, score = {} ({:.2f}%)".format(i+1, name, match, score, score_pct))
	
	print("Time spent on fingerprinting and query: {:.2f} s\n".format(time.time()-start))

	conn.close()


def main(config):
	if config.db == None:
		print("Filename of database not parsed.")
		return

	if config.mode == "build":
		if config.dataset == None:
			print("Path of dataset not parsed.")
			return
		build(config)

	else:
		if config.sample == None:
			print("Filename of sample audio not parsed.")
			return
		if not os.path.exists(config.db):
			print("Database file does not exist.")
			return
		query(config)


if __name__ == '__main__':
	# Parse configuration.
	config, unparsed = get_config()

	if len(unparsed) > 0:
		print_usage()
		exit(1)

	main(config)
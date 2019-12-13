# Audio Recognition
Simple implementation of Shazam's audio fingerprinting algorithm as a course project for CSC 575 Music Information Retrieval at University of Victoria, Canada.

## Usage
To build a fingerprint database:

    python3 main.py --mode build
                    --db <filename of database to create>
                    --dataset <directory of audio dataset (only supports .mp3 and .wav)>
                    --sr <universal resample rate> (optional)
                    --win_size <window size> (optional)
                    --anchor_dist <anchor distance>
                    --fan_out <fan-out factor>
                    
To query for a song with an audio sample:

    python3 main.py --mode query (optional)
                    --db <filename of database>
                    --sample <filename of sample>

For details of the arguments:

    Python3 main.py --help

Script for clipping audio and adding artificial noise, outputs sample file in the same directory:

    Python3 make_sample.py <infile> <start time (sec)> <duration (sec)> <noise ration (0-1)>

## List of Files
main.py: main program.

config.py: configurations for main.py.

make_sample.py: script for sample making.

demo.ipynb: slow naive implementation for visual demostrations.

classical.db: pre-built database for 99 songs from Youtube Audio Library in classical genre.

build_log.txt: list of song names and runtime for building.

samples/: example samples for query.

    November.mp3: original file.
    November_original.wav: 10-second clip.
    November_mixed.mp3: 10-second recording, mixed with a disco music in the background.
    November_restaurant.mp3: 10-second recording in a noisy environment, failed to query.
    
results/: some experimental results.

## References
[1] Avery Li-Chun Wang, “An Industrial-Strength Audio Search Algorithm”. [online]. Available http://www.ee.columbia.edu/~dpwe/papers/Wang03-shazam.pdf. [Accessed on Dec.2, 2019]

[2] Youtube Audio Library. [online]. Available https://www.youtube.com/audiolibrary/music. [Accessed on Dec.9, 2019]

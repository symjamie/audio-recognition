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

## 
## References

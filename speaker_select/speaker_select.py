import os
from os import listdir
from os.path import isfile, join
import argparse
import zipfile
import shutil
from shutil import copyfile

import pandas as pd

# command line arguments
parser = argparse.ArgumentParser(description='Select data for training and validation.')
parser.add_argument('--docfile', dest='docfile', type=str, help='Speaker documentation file')
parser.add_argument('--gender', dest='gender', type=str, help='Speaker gender')
parser.add_argument('--acc', dest='acc', type=str, help='Speaker accent')
parser.add_argument('--scriptdir', dest='scriptdir', type=str, help='Script file directory')
parser.add_argument('--wavdir', dest='wavdir', type=str, help='Wav file directory')
parser.add_argument('--numspeakers', dest='numspeakers', type=int, help='Number of speakers to include in training')
parser.add_argument('--outdir', dest='outdir', type=str, help='Output directory for the pre-processed corpus')
args = parser.parse_args()

# Get speaker documentation
print("Getting speaker docs")
speakers = pd.read_excel(args.docfile, index_col=None)

# Filter speakers
print("Filtering speakers")
speakers = speakers[speakers['SEX'] == args.gender]
speakers = speakers[speakers['ACC'] == args.acc]
speaker_ids = [str(x) for x in speakers['SCD/PART2'].unique().tolist()]
speaker_ids = speaker_ids[0:args.numspeakers]

# Filter transcripts
print("Filtering transcripts")
scripts = [f for f in listdir(args.scriptdir) if isfile(join(args.scriptdir, f))]
filtered_scripts = []
for s in scripts:
    if s[1:5] in speaker_ids:
        filtered_scripts.append(s)

# Pre-process scripts into single list
out_wavs = []
for s in filtered_scripts:
    with open(join(args.scriptdir, s), "r") as f:
        prev_line = ""
        wav_file = ""
        punc = ""
        for line in f:
            line = line.strip()
            if line[0].isdigit():
                wav_file = line[0:9]
                transcription = line[9:].strip()
                prev_line = line
                if line[-1] == '.' or line[-1] == '?':
                    punc = line[-1]
                else:
                    punc = ""
            else:
                if "**" not in line and "/>" not in line and wav_file != "":
                    out_wavs.append(wav_file + '|' + transcription + '|' + line + punc)

print("Creating metadata")
with open(join(args.outdir, "metadata.csv"), "w") as meta_file:
    for line in out_wavs:
        meta_file.write(line+"\n")

print("Symlinking audio")
for idx in speaker_ids:
    os.symlink(join(args.wavdir, 'SPEAKER' + idx + '.zip'), join(args.outdir, 'SPEAKER' + idx + '.zip'))

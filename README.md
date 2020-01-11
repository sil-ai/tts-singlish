![](pipeline.png)

# Singlish speech synthesis using Tacotron2

This data pipeline and the included notebooks demonstrate the fine tuning of a TSS model for a local language/accent ([Singlish](https://en.wikipedia.org/wiki/Singlish)). The data pipeline utilizes audio/transcript data from the [IMDA National Speech Corpus](https://www.imda.gov.sg/NationalSpeechCorpus) and using [Mozilla's implementation of Tacotron2](https://github.com/mozilla/TTS).

After ensuring that you have the [pre-requisites](#pre-requisites), complete the following steps to deploy the Singlish pipeline:

1. [Prepare the input repository](#prepare_input_repository)
2. [Select a speaker and pre-process the corresponding data]()

## Pre-requisites

To run this pipeline you should first:

- Request access to the [IMDA National Speech Corpus](https://www.imda.gov.sg/NationalSpeechCorpus)
- Deploy a GPU enabled [Pachyderm](https://pachyderm.io/) cluster or create a cluster in the hosted [Pachyderm:Hub](https://hub.pachyderm.com/clusters) (The pipeline has been tested with V100 and K80 GPUs on Google Cloud)
- [Install `pachctl` locally](https://docs.pachyderm.com/latest/getting_started/local_installation/#install-pachctl) and connect it to your Pachyderm cluster

## 1. Prepare input repository

Pachyderm data pipelines utilize a versioned data storage layer backed by an object store. Data is organized into "data repositories" (repos) in this storage layer. To utilize the IMDA corpus in our data pipeline, we need to create an input repo, `corpus`, for this data and upload the data into the repo. For this example deploy, we will just be using `PART2` of the IMDA National Speech Corpus. Once created, your input repository should look like the following:

```sh
$ pachctl list file corpus@master:/
NAME           TYPE SIZE
/SCRIPT        dir  79.4MiB
/WAVE          dir  86.83GiB
/speakers.XLSX file 59.98KiB

$ pachctl list file corpus@master:/WAVE | head
NAME                  TYPE SIZE
/WAVE/SPEAKER2001.zip file 87.08MiB
/WAVE/SPEAKER2002.zip file 93.38MiB
/WAVE/SPEAKER2003.zip file 76.99MiB
/WAVE/SPEAKER2005.zip file 36.53MiB
/WAVE/SPEAKER2006.zip file 61.53MiB
/WAVE/SPEAKER2007.zip file 92.24MiB
/WAVE/SPEAKER2008.zip file 81.92MiB
/WAVE/SPEAKER2009.zip file 65.67MiB
/WAVE/SPEAKER2010.zip file 76.23MiB

$ pachctl list file corpus@master:/SCRIPT | head
NAME               TYPE SIZE
/SCRIPT/020010.TXT file 43.46KiB
/SCRIPT/020011.TXT file 43.91KiB
/SCRIPT/020020.TXT file 41.75KiB
/SCRIPT/020021.TXT file 40.09KiB
/SCRIPT/020030.TXT file 44.02KiB
/SCRIPT/020031.TXT file 40.5KiB
/SCRIPT/020050.TXT file 42.06KiB
/SCRIPT/020060.TXT file 34.96KiB
/SCRIPT/020061.TXT file 36.68KiB
```  

## 2. Select a speaker and pre-process the corresponding data

We will be fine-tuning an existing TTS model from Mozilla and thus we won't need as much data as we would if we were training from scratch. As such, we will just be selecting the audio and transcript files out of the IMDA corpus that correspond to a particular speaker. The IMDA corpus includes many male and female speakers with Chinese, Indian, and Malay accents. For our example we will utilize a female speaker with an Indian accent. 

The [`speaker_select.py` Python script](speaker_select/speaker_select.py) performs the necessary filtering of the corpus. It also reformat's IMDA's metadata and transcript information into [LJSpeech](https://keithito.com/LJ-Speech-Dataset/) format. We utilize the LJSpeech format because we will be using an base model trained on LJSpeech and because Mozilla's TTS implementation already has a pre-processor for LJSpeech formatted data.   

To filter the corpus for a female speaker with Indian accent, for example, you would run:

```sh
$ python speaker_select.py \
    --docfile <path to IMDA's speaker file> \
    --gender F --acc INDIAN \
    --scriptdir <path to the IMDA SCRIPT directory> \
    --wavdir <path to the IMDA WAVE directory> 
    --numspeakers 1 --outdir <output directory>
```

To run this in our Pachyderm cluster on the `corpus` repo we Dockerize the script with [this Dockerfile](speaker_select/Dockerfile). The resulting image is available publicly on Docker Hub as `dwhitena/tts-speaker-select`.

Using that Docker image, we create the `speaker_select` pipeline in our Pachyderm cluster using `pachctl`:

```sh
$ pachctl create pipeline -f speaker_select.json
```

This will automatically trigger a "job" to process the corpus data and output the filtered data to the `speaker_select` repo:

```sh
$ pachctl list job --no-pager --pipeline speaker_select
ID                               PIPELINE       STARTED      DURATION   RESTART PROGRESS  DL       UL       STATE
bcea6c90cb5a43e5b6f1cf6a206e50fa speaker_select 21 hours ago 15 seconds 0       1 + 0 / 1 79.46MiB 83.47KiB success
$ pachctl list file speaker_select@master:/
NAME             TYPE SIZE
/SPEAKER3162.zip file 94.07MiB
/metadata.csv    file 83.47KiB
```  

## References

- [Mozilla TTS (Tacotron2) Implementation](https://github.com/mozilla/TTS)
- [Pachyderm](https://pachyderm.io/) 
- [Tacotron2 Paper](https://arxiv.org/abs/1712.05884) 
- [WaveNet Blog Post](https://deepmind.com/blog/article/wavenet-generative-model-raw-audio) 
- [SIL](https://www.sil.org/) 
- [Wordly](https://wordly.sg/) 
- [IMDA Singlish Corpus](https://www.imda.gov.sg/NationalSpeechCorpus) 


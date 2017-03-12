from __future__ import unicode_literals

import tempfile
import shutil
import os
from itertools import zip_longest
from subprocess import call

import itertools

import youtube_dl
from PIL import Image


TEMPLATE_AVS = os.path.join('avs', 'template.avs')
TEMPLATE_REFERENCE_AVS = os.path.join('avs', 'template_reference.avs')
MASK_DIR = os.path.join('avs', 'mask')
OUTPUT_AVS = 'vhs.avs'
REFERENCE_AVS = 'reference.avs'
NOISE_CLIP = os.path.abspath(os.path.join('avs', 'noise-preprocess.avi'))
IMAGE_DIRNAME = 'images'
REFEREMCE_IMAGE_DIRNAME = 'ref_images'
N_FRAMES = 7
VIDEO_RANGE = (0,100000)
MAX_SAMPLES = 1000000
URL_BASE = 'https://www.youtube.com/watch?v='
OUTDIR = "D:\\datasets\\frames"

ydl_opts = {'outtmpl': 'download.mp4', 'format': '135'}

def get_formats(url):
    with youtube_dl.YoutubeDL({}) as ydl:
        return {f['format'].split()[0] for f in ydl.extract_info(url, download=False)['formats']}

def main():
    video_first, video_last = VIDEO_RANGE
    with open("ids.txt") as f:
        videos = [v for v in itertools.islice(f, video_first, video_last)]
    seqNo = 1

    itervideos = iter(videos)
    while(seqNo < MAX_SAMPLES):
#        try:
        v = next(itervideos)
        url = URL_BASE + v.strip()
        with youtube_dl.YoutubeDL(ydl_opts) as ydl:
            if ('135' in get_formats(url)):
                ydl.download([url])
                seqNo += process(os.path.abspath('download.mp4'), OUTDIR, seqNo)
                print("-"*80)
                print("%d samples generated" % seqNo)
                print("-"*80)
                os.remove('download.mp4')
#        except:
#            print("Processing video %s failed" % v)


def prepare_dir(dir, input_clip):
    shutil.copytree(MASK_DIR, os.path.join(dir, 'mask'))
    generate_avs(dir, input_clip)
    os.makedirs(os.path.join(dir, 'vhs'))
    os.makedirs(os.path.join(dir, 'ref'))


def sed(src, dst, replace_dir):
    with open(dst, 'wt') as d, open(src) as s:
        for line in s:
            for a, b in replace_dir.items():
                line = line.replace(a, b)
            d.write(line)


def generate_avs(dir, input_clip):
    avs = os.path.join(dir, OUTPUT_AVS)
    ref_avs = os.path.join(dir, REFERENCE_AVS)
    sed(TEMPLATE_AVS, avs, {'%INPUT%': input_clip, '%NOISE%': NOISE_CLIP, '%N%': str(N_FRAMES)})
    sed(TEMPLATE_REFERENCE_AVS, ref_avs, {'%INPUT%': input_clip, '%N%': str(N_FRAMES)})


def generate_images(avs, outdir):
    if not os.path.exists(outdir):
        os.makedirs(outdir)
    call(['ffmpeg', '-i', avs, "-q:v", '1', os.path.join(outdir, '%06d.png')])


def move_images(src, dst, start_index):
    files = [f for f in sorted(os.listdir(src))]
    for i, f in enumerate(files):
        shutil.copyfile(os.path.join(src, f), os.path.join(dst, '%08d.png' % (start_index + i)))
    return len(files)


def process(filename, outdir, seqNo = 1):
    vhs_output = os.path.join(outdir, 'vhs')
    if not os.path.exists(vhs_output):
        os.makedirs(vhs_output)

    ref_output = os.path.join(outdir, 'ref')
    if not os.path.exists(ref_output):
        os.makedirs(ref_output)

    dir = tempfile.mkdtemp()

    prepare_dir(dir, filename)

    generate_images(os.path.join(dir, OUTPUT_AVS), os.path.join(dir, 'vhs'))
    generate_images(os.path.join(dir, REFERENCE_AVS), os.path.join(dir, 'ref'))

    processed = move_images(os.path.join(dir, 'vhs'), vhs_output, seqNo)
    move_images(os.path.join(dir, 'ref'), ref_output, seqNo)

    shutil.rmtree(dir)

    return processed


if __name__ == '__main__':
    main()
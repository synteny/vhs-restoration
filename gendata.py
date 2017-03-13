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
NOISE_CLIP = os.path.abspath(os.path.join('avs', 'noise.mp4'))
IMAGE_DIRNAME = 'images'
REFEREMCE_IMAGE_DIRNAME = 'ref_images'
N_FRAMES = 7
TILE_HEIGHT = 20
TILE_WIDTH = 20
VIDEO_RANGE = (0,100000)
MAX_SAMPLES = 1000000
URL_BASE = 'https://www.youtube.com/watch?v='
OUTDIR = "D:\\dataset"


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
        try:
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
        except:
            print("Processing video %s failed" % v)


def prepare_dir(dir, input_clip):
    shutil.copytree(MASK_DIR, os.path.join(dir, 'mask'))
    generate_avs(dir, input_clip)


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


def generate_images(dir):
    imagedir = os.path.join(dir, IMAGE_DIRNAME)
    ref_imagedir = os.path.join(dir, REFEREMCE_IMAGE_DIRNAME)
    os.mkdir(imagedir)
    os.mkdir(ref_imagedir)
    call(['ffmpeg', '-i', os.path.join(dir, 'vhs.avs'), os.path.join(dir, 'images\%06d.bmp')])
    call(['ffmpeg', '-i', os.path.join(dir, 'reference.avs'), os.path.join(dir, 'ref_images\%06d.bmp')])


def batch_crop(infile, height, width):
    im = Image.open(infile)
    imgwidth, imgheight = im.size
    for i in range(imgheight//height):
        for j in range(imgwidth//width):
            box = (j*width, i*height, (j+1)*width, (i+1)*height)
            yield im.crop(box)


def split_image(infile, height, width, seqNo, batchNo, outdir):
    for k, piece in enumerate(batch_crop(infile, height, width), 0):
        dirpath = os.path.join(outdir, "%06d" % (seqNo + k))
        if not os.path.exists(dirpath):
            os.makedirs(dirpath)
        img = Image.new('RGB', (height, width), 255)
        img.paste(piece)
        path = os.path.join(dirpath, "%s.png" % batchNo)
        img.save(path)
    return k + 1


def grouper(iterable, n, fillvalue=None):
    "Collect data into fixed-length chunks or blocks"
    # grouper('ABCDEFG', 3, 'x') --> ABC DEF Gxx"
    args = [iter(iterable)] * n
    return zip_longest(*args, fillvalue=fillvalue)


def split_images(indir, outdir, seqNo, mask=set(range(1, N_FRAMES + 1))):
    processed = 0
    for filename_batch in grouper(sorted(os.listdir(indir)), N_FRAMES):
        for batchNo, filename in enumerate(filename_batch, 1):
            if batchNo in mask:
                tiles = split_image(os.path.join(indir, filename), TILE_HEIGHT, TILE_WIDTH, seqNo + processed, batchNo, outdir)
        processed += tiles
    return processed


def process(filename, outdir, seqNo = 1):
    vhs_output = os.path.join(outdir, 'vhs')
    if not os.path.exists(vhs_output):
        os.makedirs(vhs_output)

    ref_output = os.path.join(outdir, 'ref')
    if not os.path.exists(ref_output):
        os.makedirs(ref_output)

    dir = tempfile.mkdtemp()

    prepare_dir(dir, filename)

    generate_images(dir)

    processed = split_images(os.path.join(dir, 'images'), vhs_output, seqNo)
    split_images(os.path.join(dir, 'ref_images'), ref_output, seqNo, mask={4})

    shutil.rmtree(dir)

    return processed


if __name__ == '__main__':
    main()
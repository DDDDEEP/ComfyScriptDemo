import signal
import sys
import random
import os
import time
from playsound import playsound
from PIL import Image
from datetime import datetime

from utils.image import *
from utils.settings import *
from txt2img_artist_gallery.settings import *

sys.path.insert(0, 'src')
from comfy_script.runtime import *
load(args=ComfyUIArgs('--preview-method', 'auto'))
from comfy_script.runtime.nodes import *
from comfy_script.runtime.node import *
from PIL import Image
sys.path.insert(0, '../../')

from utils.task import *


# the common prefix of output file name
FILE_COMMON_PREFIX = f"txt2img_artist_gallery-{TASK_CONFIG[CKPT][:7]}-{TASK_CONFIG[SEED]}"


artist_images, artist_names = map(list, zip(*read_images_from_folder(
    folder_path=f"{ARTIST_DIRPATH}\\", start_index=READ_IMAGE_START_INDEX, max_count=READ_IMAGE_MAX_COUNT)))


def output_file_prefix_for(artist_name: str) -> str:
    return f"{FILE_COMMON_PREFIX}-{artist_name}"


if __name__ == "__main__":
    signal.signal(signal.SIGINT, cleanup)
    signal.signal(signal.SIGTERM, cleanup)

    with Workflow(wait=True) as wf:
        for artist_name in artist_names:
            output_filename_prefix = output_file_prefix_for(artist_name=artist_name)
            # if output img exist, don't submit duplicate task
            if check_file_exists(folder_path=OUTPUT_DIRPATH, match_prefix=output_filename_prefix):
                continue
            newConfig = TASK_CONFIG.copy()
            newConfig[PROMPT_ARTIST] = f"artist:{artist_name}"
            create_save_image_task(config=newConfig, filename_prefix=output_filename_prefix)

    # ===============  concat output images ===============
    output_images = [
        img for artist_name in artist_names
        for img, _ in read_images_from_folder(
            folder_path=OUTPUT_DIRPATH,
            match_prefix=output_file_prefix_for(artist_name=artist_name),
            max_count=1
        )
    ]

    WIDTH = int(TASK_CONFIG[WIDTH_S])
    HEIGHT = int(TASK_CONFIG[HEIGHT_S])

    artist_images = resize_images(
        images=artist_images, width=WIDTH, height=HEIGHT)
    for i in range(0, len(artist_names), PER_TOTAL_COUNT):
        singleImage = None
        batch_artist_names = artist_names[i:i + PER_TOTAL_COUNT]
        for j in range(0, len(batch_artist_names), PER_ROW_COUNT):
            row_artist_names = batch_artist_names[j:j + PER_ROW_COUNT]
            row_output_images = output_images[i:i + PER_TOTAL_COUNT][j:j + PER_ROW_COUNT]
            row_artist_images = artist_images[i:i + PER_TOTAL_COUNT][j:j + PER_ROW_COUNT]
            row_image = create_images_row(
                row_output_images, row_artist_images,
                titles=row_artist_names, title_height=100,
                width=WIDTH, height=HEIGHT
            )
            if singleImage is None:
                singleImage = row_image
            else:
                singleImage = concat_images([singleImage, row_image], Orientation.VERTICAL)
        save_path = f"{OUTPUT_DIRPATH}\\result-{FILE_COMMON_PREFIX}-{sanitize_path_for(path=ARTIST_DIRPATH)}-{i // PER_TOTAL_COUNT}.jpg"
        singleImage.save(save_path, format="JPEG")

    playsound(SOUND_FILEPATH)

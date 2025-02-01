import signal
import sys
import random
import os
import time
from playsound import playsound
from PIL import Image
from datetime import datetime
from itertools import product

from utils.settings import *
from utils.image import *
from txt2img_zyx.settings import *

sys.path.insert(0, 'src')
from comfy_script.runtime import *
load(args=ComfyUIArgs('--preview-method', 'auto'))
from comfy_script.runtime.nodes import *
from comfy_script.runtime.node import *
sys.path.insert(0, '../../')

from utils.task import *


FILE_COMMON_PREFIX = "txt2img_zyx"


def output_file_prefix_for(z: str, y: str = "", x: str = "") -> str:
    prefix_parts = [FILE_COMMON_PREFIX, TASK_CONFIG[SEED], z]
    if y:
        prefix_parts.append(y)
    if x:
        prefix_parts.append(x)

    return "-".join(prefix_parts)


def output_result_file_prefix(z: str = "") -> str:
    prefix_parts = ["result", FILE_COMMON_PREFIX, TASK_CONFIG[SEED], z]
    if z:
        prefix_parts.append(z)
    prefix_parts.append(".jpg")
    return "-".join(prefix_parts)


if __name__ == "__main__":
    signal.signal(signal.SIGINT, cleanup)
    signal.signal(signal.SIGTERM, cleanup)

    with Workflow(wait=True) as wf:
        for z, y, x in product(TASK_CONFIG_Z, TASK_CONFIG_Y, TASK_CONFIG_X):
            new_config = TASK_CONFIG.copy()

            for config_dict in [z[CONFIG], y[CONFIG], x[CONFIG]]:
                for key, func in config_dict.items():
                    if key in new_config and callable(func):
                        new_config[key] = func(new_config[key])

            output_filename_prefix = output_file_prefix_for(z=z[TITLE], y=y[TITLE], x=x[TITLE])
            create_save_image_task(config=new_config, filename_prefix=output_filename_prefix)

    # ===============  concat output images ===============
    for z in TASK_CONFIG_Z:
        output_images = []
        for y, x in product(TASK_CONFIG_Y, TASK_CONFIG_X):
            output_filename_prefix = output_file_prefix_for(z=z[TITLE], y=y[TITLE], x=x[TITLE])
            imageTuple = read_images_from_folder(
                folder_path=OUTPUT_DIRPATH,
                match_prefix=output_filename_prefix,
                max_count=1
            )[0]
            output_images.append(imageTuple[0])

        grid_images = None
        for xxx in range(0, len(output_images), len(TASK_CONFIG_X)):
            row_output_images = output_images[xxx: xxx + len(TASK_CONFIG_X)]
            row_image = create_images_row(
                row_output_images,
                # FIXME: not support dynamic WIDTH & HEIGHT
                width=int(TASK_CONFIG[WIDTH_S]), height=int(TASK_CONFIG[HEIGHT_S]),
            )
            if grid_images is None:
                grid_images = row_image
            else:
                grid_images = concat_images([grid_images, row_image], Orientation.VERTICAL)

        x_titles = [item[TITLE] for item in TASK_CONFIG_X]
        y_titles = [item[TITLE] for item in TASK_CONFIG_Y]
        grid_images = add_titles_for_image(image=grid_images, x_titles=x_titles, y_titles=y_titles)
        grid_images = add_titles_for_image(image=grid_images, x_titles=[z[TITLE]], font_size=40)

        save_path = f"{OUTPUT_DIRPATH}\\{output_result_file_prefix(z=z[TITLE])}"
        grid_images.save(save_path, format="JPEG")

    # ===============  concat output result z images ===============
    output_images = []
    for z in TASK_CONFIG_Z:
        output_filename_prefix = output_result_file_prefix(z=z[TITLE])
        imageTuple = read_images_from_folder(
            folder_path=OUTPUT_DIRPATH,
            match_prefix=output_filename_prefix,
            max_count=1
        )[0]
        output_images.append(imageTuple[0])

    save_path = f"{OUTPUT_DIRPATH}\\{output_result_file_prefix()}"
    res_image = concat_images(output_images, Orientation.VERTICAL)
    res_image.save(save_path, format="JPEG")

    playsound(SOUND_FILEPATH)

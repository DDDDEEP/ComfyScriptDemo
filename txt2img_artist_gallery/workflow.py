import signal
import sys
import random
import os
import time
from playsound import playsound
from PIL import Image
from datetime import datetime

from settings import *
from utils.utils import *
from txt2img_artist_gallery.settings import *

sys.path.insert(0, 'src')
from comfy_script.runtime import *
load(args=ComfyUIArgs('--preview-method', 'auto'))
from comfy_script.runtime.nodes import *
from comfy_script.runtime.node import *
from PIL import Image
sys.path.insert(0, '../../')


artist_images, artist_names = map(list, zip(*read_images_from_folder(
    folder_path=f"{ARTIST_DIRPATH}\\", start_index=READ_IMAGE_START_INDEX, max_count=READ_IMAGE_MAX_COUNT)))


def create_save_image_task(artist_name: str):
    postivie_prompt = StringConstant(
        POSITIVE_PROMPT_TEMPLATE.format(artist_name=danbooru_tag_to_sd(artist_name))
    )

    negative_prompt = StringConstant(
        NEGATIVE_PROMPT_TEMPLATE
    )

    model, conditioning, conditioning2, latent, vae, _, dependencies = EfficientLoader(
        CKPT_NAME, 'Baked VAE', -
        2, 'None', 1.0, 1.0, postivie_prompt, negative_prompt, 'none', 'comfy', WIDTH, HEIGHT, 1, None, None
    )

    model = DynamicThresholdingFull(
        model, 7.0, 1.0, 'Constant', 4.0, 'Half Cosine Up', 4.0, 4.0, 'enable', 'MEAN', 'AD', 1.0
    )

    # x_or_y = XYInputManualXYEntry('Positive Prompt S/R', artist_names_str)
    # script = XYPlot(0, 'False', 'Horizontal', 'True',
    #                 'Images', dependencies, None, x_or_y)
    _, _, _, latent, vae, image = KSamplerAdvEfficient(
        model, 'enable', NOICE_SEED, 28, 20.0, 'euler_ancestral',
        'karras', conditioning, conditioning2, latent, 0, 10000, 'disable', 'auto', 'true', vae
    )

    # PreviewImage(VAEDecode(latent, vae))

    _, saved_path = ImageSave(image, filename_prefix=output_file_prefix_for(artist_name=artist_name),
                              extension='jpg', dpi=370)


def cleanup(signum, frame):
    queue.cancel_all()
    sys.exit(0)


if __name__ == "__main__":
    signal.signal(signal.SIGINT, cleanup)
    signal.signal(signal.SIGTERM, cleanup)

    with Workflow(wait=True) as wf:
        for artist_name in artist_names:
            output_filename_prefix = output_file_prefix_for(artist_name=artist_name)
            # if output img exist, don't submit duplicate task
            if check_file_exists(folder_path=OUTPUT_DIRPATH, match_prefix=output_filename_prefix):
                continue
            create_save_image_task(artist_name=artist_name)

    # ===============  concat output images ===============
    output_images = [
        img for artist_name in artist_names
        for img, _ in read_images_from_folder(
            folder_path=OUTPUT_DIRPATH,
            match_prefix=output_file_prefix_for(artist_name=artist_name),
            max_count=1
        )
    ]
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
                width=WIDTH, height=HEIGHT,
            )
            if singleImage is None:
                singleImage = row_image
            else:
                singleImage = concat_images([singleImage, row_image], Orientation.VERTICAL)
        save_path = f"{OUTPUT_DIRPATH}\\result-{FILE_COMMON_PREFIX}-{sanitize_path_for(path=ARTIST_DIRPATH)}-{i // PER_TOTAL_COUNT}.jpg"
        singleImage.save(save_path, format="JPEG")

    playsound(SOUND_FILEPATH)

# process_images_and_texts(
#     texts=artist_names, images_group1=output_images, images_group2=artist_images, output_folder=OUTPUT_DIRPATH, output_prefix=f"result-{FILE_COMMON_PREFIX}", per_row_count=PER_ROW_COUNT, per_col_count=PER_COL_COUNT, width=WIDTH, height=HEIGHT)

# save_path = f"{OUTPUT_DIRPATH}\\result-{image_file_common_prefix}.jpg"
# res_output_image = concat_images(
#     images=output_images, orientation=Orientation.HORIZONTAL)

# res_artist_image = concat_images(
#     images=artist_images, orientation=Orientation.HORIZONTAL)
# res_artist_image.save(save_path, format="JPEG")

# res_title_image = create_title_images(
#     titles=artist_names, orientation=Orientation.HORIZONTAL, width=WIDTH, height=50)
# res_title_image.save(save_path, format="JPEG")

# time.sleep(3)

# is_process_done = False


# def empty_callback(wf):
#     global is_process_done
#     playsound(SOUND_FILEPATH)
#     is_process_done = True

# folder_path = ARTIST_DIRPATH
# image_list = read_images_from_folder(folder_path)

# for img, filename in image_list:
#     print(f"图片文件名: {danbooru_tag_to_sd(filename)}, 图片尺寸: {img.size}")


# queue.when_empty(empty_callback)

# while True:
#     time.sleep(1)  # 每分检查一次
#     if is_process_done:
#         break


# def add_preview_callback(self, callback: Callable[[Task, str, Image.Image], None]):
# queue.add_preview_callback()

# =============== 参考写法 ===============
# width, height, _, _ = CRImageSize(1216, 832, 1)
# image, _ = CRColorPanel(width, height, 'black', '#000000')
# string = StringConstantMultiline(
#     r'C:\Softlink\Gallery\artist\comfyui\normal_1', False)
# value = INTConstant(1)
# image2, file_path, _ = LoadImageListFromDirInspire(string, value, 0, False)
# image2, _, _ = ImageResize(image2, width, height,
#                            'nearest', 'pad', 'always', 0)
# image2 = ImageListToImageBatch(image2)
# image3 = ImageCombine(image, image2)
# string2 = StringConstant('abcdefg')
# string3 = StringConstantMultiline(r'\', False)
# string4 = JoinStrings(string, string3, '')
# string5, _ = CRTextReplace(file_path, string4, '', '.jpg', '', '.png', '')
# string6, _ = CRTextReplace(string5, '_', ' ', '(', r'\(', ')', r'\)')
# string6 = StringListToString(';', string6)
# string7 = JoinStrings(string2, string6, ';')
# string8 = StringConstantMultiline(';', False)
# string9 = JoinStrings(string7, string8, '')
# string9 = ShowTextPysssss(string9)
# grid_annotation = GridAnnotation(string9, 'Comfyui:;Reference:', 50)
# image3 = ImagesGridByRows(image3, 5, 2, grid_annotation)
# PreviewImage(image3)

# _ = PlaySoundPysssss(any=imageSaved, volume=1.0, file='notification.mp3')

# watch_for_new_images(
#     saved_path, r"D:\sd-webui\ComfyUI-aki-v1.5\notification.mp3")

# string3 = StringConstant('abcdefg')

# string4 = StringConstantMultiline(
#     r'C:\Softlink\Gallery\artist\comfyui\normal_1', False
# )

# imageCount = 1

# image, _, file_path = LoadImageListFromDirInspire(
#     string4, imageCount, 0, False)

# string5 = StringConstantMultiline(r'\\', False)

# string6 = JoinStrings(string4, string5, '')

# string7, _ = CRTextReplace(file_path, string6, '', '.jpg', '', '.png', '')

# string8, _ = CRTextReplace(string7, '_', ' ', '(', r'\(', ')', r'\)')

# string8 = StringListToString(';', string8)

# string9 = JoinStrings(string3, string8, ';')

# string10 = StringConstantMultiline(';', False)

# string11 = JoinStrings(string9, string10, '')

# string11 = ShowTextPysssss(string11)

# x_or_y = XYInputManualXYEntry('Positive Prompt S/R', string11)

# script = XYPlot(0, 'False', 'Horizontal', 'True',
#                 'Images', dependencies, None, x_or_y)


# model, clip, vae = CheckpointLoaderSimple(Checkpoints.waiNSFWIllustrious_v90)
# conditioning = CLIPTextEncode(
#     "beautiful scenery nature glass bottle landscape, , purple galaxy bottle,", clip
# )
# conditioning2 = CLIPTextEncode("text, watermark", clip)
# latent = EmptyLatentImage(512, 512, 1)
# latent = KSampler(
#     model,
#     156680208700286,
#     20,
#     8,
#     "euler",
#     "normal",
#     conditioning,
#     conditioning2,
#     latent,
#     1,
# )
# image = VAEDecode(latent, vae)
# SaveImage(image, "ComfyUI")

# To retrieve `image` instead of saving it, replace `SaveImage` with:
# images = util.get_images(image)
# `images` is of type `list[PIL.Image.Image]`

# def read_image_and_save():
#     return
#     width, height, _, _ = CRImageSize(1216, 832, 1)
#     image, _ = CRColorPanel(width, height, 'black', '#000000')

#     folder_path = ARTIST_DIRPATH
#     image_count = 3
#     image2, file_path, _ = LoadImageListFromDirInspire(
#         folder_path, image_count, 0, False)
#     image2, _, _ = ImageResize(image2, width, height,
#                                'nearest', 'pad', 'always', 0)
#     image3 = ImageListToImageBatch(image2)

#     grid_annotation = GridAnnotation(filenames_str, 'Comfyui:;Reference:', 50)
#     image3 = ImagesGridByRows(image3, 5, 2, grid_annotation)
#     _, saved_path = ImageSave(image3, filename_prefix='grid',
#                               extension='jpg', dpi=370)
# PreviewImage(image3)

import sys

from comfy_script.runtime import *
from comfy_script.runtime.nodes import *
from comfy_script.runtime.node import *
from utils.constant import *
from utils.image import *


def cleanup(signum, frame):
    queue.cancel_all()
    sys.exit(0)


def create_save_image_task(config: dict, filename_prefix: str):
    pos_str = danbooru_tag_to_sd(POSITIVE_PROMPT_TEMPLATE.format(**config))
    postivie_prompt = StringConstant(pos_str)

    neg_str = danbooru_tag_to_sd(NEGATIVE_PROMPT_TEMPLATE.format(**config))
    negative_prompt = StringConstant(neg_str)

    model, conditioning, conditioning2, latent, vae, _, dependencies = EfficientLoader(
        config[CKPT], 'Baked VAE', -
        2, 'None', 1.0, 1.0, postivie_prompt, negative_prompt, 'none', 'comfy', config[WIDTH_S], config[HEIGHT_S], 1, None, None
    )

    model = DynamicThresholdingFull(
        model, 7.0, 1.0, 'Constant', 4.0, 'Half Cosine Up', 4.0, 4.0, 'enable', 'MEAN', 'AD', 1.0
    )

    _, _, _, latent, vae, image = KSamplerAdvEfficient(
        model, 'enable', int(config[SEED]), 28, 20.0, 'euler_ancestral',
        'karras', conditioning, conditioning2, latent, 0, 10000, 'disable', 'auto', 'true', vae
    )

    _, saved_path = ImageSave(image, filename_prefix=filename_prefix,
                              extension='jpg', dpi=370)

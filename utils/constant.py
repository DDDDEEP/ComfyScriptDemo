# Constants
WIDTH_S = "width"
HEIGHT_S = "height"
SEED = "seed"
CKPT = "ckpt"

# Prompts
PROMPT_GIRLS = "prompt_girls"
PROMPT_ARTIST = "prompt_artist"
PROMPT_CLOTHES = "prompt_clothes"
PROMPT_BOYS = "prompt_boys"
PROMPT_SCENE = "prompt_scene"
PROMPT_MOTION = "prompt_motion"
PROMPT_DESC = "prompt_desc"
PROMPT_OTHERS = "prompt_others"
PROMPT_CKPT = "prompt_ckpt"
PROMPT_NEGATIVE = "prompt_negative"


POSITIVE_PROMPT_TEMPLATE = '''
{prompt_girls}
BREAK
{prompt_clothes}
BREAK
{prompt_artist}
BREAK
{prompt_boys}
BREAK
{prompt_scene}
BREAK
{prompt_motion}
BREAK
{prompt_desc}
BREAK
{prompt_others}
BREAK
{prompt_ckpt}
'''

NEGATIVE_PROMPT_TEMPLATE = '''
{prompt_negative}
'''

# XYZ
TITLE = "title"
CONFIG = "config"

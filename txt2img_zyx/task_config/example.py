# base task config
from utils.constant import *

PROMPTS = {
    PROMPT_GIRLS: '1girl,iino miko,brown eyes,brown hair,long hair,low twintails,'
                  'blunt bangs,medium breasts,collarbone',
    PROMPT_ARTIST: 'artist:alp',
    PROMPT_CLOTHES: 'shuuchiin academy school uniform, shuuchiin academy school uniform,'
                    'black dress,black pantyhose',
    PROMPT_BOYS: '',
    PROMPT_SCENE: 'classroom,window',
    PROMPT_MOTION: 'full body,waving,standing',
    PROMPT_DESC: '',
    PROMPT_OTHERS: 'sfw',
    PROMPT_CKPT: 'depth of field,masterpiece,best quality,amazing quality,very aesthetic,'
                 'high resolution,ultra-detailed,absurdres,newest,scenery,volumetric lighting',
    PROMPT_NEGATIVE: 'modern,recent,old,oldest,cartoon,graphic,text,painting,crayon,graphite,abstract,'
                     'glitch,deformed,mutated,ugly,disfigured,long body,lowres,bad anatomy,bad hands,'
                     'missing fingers,extra digit,fewer digits,cropped,very displeasing,(worst quality, '
                     'bad quality:1.2),bad anatomy,sketch,jpeg artifacts,signature,watermark,username,'
                     'signature,simple background,conjoined,bad ai-generated,text,door',
}

TASK_CONFIG = {
    WIDTH_S: "832",
    HEIGHT_S: "1216",
    SEED: "689914488429495",
    CKPT: "waiNSFWIllustrious_v90.safetensors",
    **PROMPTS
}


# zyx config
TASK_CONFIG_Z = [
    {
        TITLE: "waiNSFW",
        CONFIG: {
            CKPT: lambda s: "waiNSFWIllustrious_v90.safetensors"
        }
    },
    {
        TITLE: "novaAnimeXL",
        CONFIG: {
            CKPT: lambda s: "novaAnimeXL_ilV30HappyNewYear.safetensors"
        }
    }
]
TASK_CONFIG_Y = [
    {
        TITLE: "hews",
        CONFIG: {
            PROMPT_ARTIST: lambda s: "artist:hews"
        }
    },
    {
        TITLE: "alp",
        CONFIG: {
            PROMPT_ARTIST: lambda s: "artist:alp"
        }
    }
]

TASK_CONFIG_X = [
    {
        TITLE: "classroom",
        CONFIG: {
            PROMPT_CLOTHES: lambda s: "shuuchiin academy school uniform, shuuchiin academy school uniform,black dress,black pantyhose,",
            PROMPT_SCENE: lambda s: "classroom,window,",
            PROMPT_MOTION: lambda s: "full body,standing,holding book,hugging blue book,"
        }
    },
    {
        TITLE: "maid",
        CONFIG: {
            PROMPT_CLOTHES: lambda s: "apron, red bow, red bowtie, black dress, maid apron, puffy short sleeves, puffy sleeves, short sleeves, waist apron, white apron,white thighhighs",
            PROMPT_SCENE: lambda s: "Coffee shop",
            PROMPT_MOTION: lambda s: "full body,standing,mouth, enmaided, fingernails, holding own arm, looking at viewer, maid, split mouth,  wristban,shame,blush"
        }
    },
    {
        TITLE: "bedroom",
        CONFIG: {
            PROMPT_CLOTHES: lambda s: "black thighhighs, brown sweater, jewelry, long sleeves, no shoes, light yellow sweater,pink medium skirt",
            PROMPT_SCENE: lambda s: "bedroom",
            PROMPT_MOTION: lambda s: "pout, sideways glance, full body, standing, hand up, looking at viewer, open mouth, sleeves past wrists, solo"
        }
    },
    {
        TITLE: "restaurant",
        CONFIG: {
            PROMPT_CLOTHES: lambda s: "black dress, braid, collarbone, dress,  off-shoulder shirt, shirt, short sleeves, ",
            PROMPT_SCENE: lambda s: "high-end restaurant, elegant interior, romantic lighting, candlelight,warm, inviting, luxurious atmosphere, soft focus,",
            PROMPT_MOTION: lambda s: "full body,standing,blush, smile, looking at viewer,arm extended, welcoming gesture,"
        }
    }
]

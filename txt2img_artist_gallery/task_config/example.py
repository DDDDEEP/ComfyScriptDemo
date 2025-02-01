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

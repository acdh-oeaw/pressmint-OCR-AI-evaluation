from transformers import AutoModel, AutoTokenizer
import torch
import os


os.environ["CUDA_VISIBLE_DEVICES"] = '0'


model_name = 'deepseek-ai/DeepSeek-OCR'


tokenizer = AutoTokenizer.from_pretrained(model_name, trust_remote_code=True)
model = AutoModel.from_pretrained(model_name, _attn_implementation='flash_attention_2', trust_remote_code=True, use_safetensors=True)
model = model.eval().cuda().to(torch.bfloat16)



PROMPT = (
    "<image>\n<|grounding|>Transcribe the text of the following historic document. It is a german "
    "newspaper from the early 20th century, printed in 'Fraktur'. Keep the human reading order, "
    "meaning, that the natural flow of the text blocks must be respected. The output should only "
    "be plain text, without any categories or special structure."
)
IN_FOLDER = "/pressmint-ground-truth/data/texts/images/"
OUT_FOLDER = "/pressmint-ground-truth/data/texts/deepseek_ocr_3_english_extensive_2_all_output/"


# infer(self, tokenizer, PROMPT='', image_file='', output_path = ' ', base_size = 1024, image_size = 640, crop_mode = True, test_compress = False, save_results = False):

# Tiny: base_size = 512, image_size = 512, crop_mode = False
# Small: base_size = 640, image_size = 640, crop_mode = False
# Base: base_size = 1024, image_size = 1024, crop_mode = False
# Large: base_size = 1280, image_size = 1280, crop_mode = False

# Gundam: base_size = 1024, image_size = 640, crop_mode = True

for image_file_name in os.listdir(IN_FOLDER):
    image_file = IN_FOLDER + image_file_name
    image_id = image_file_name.replace(".jpg", "")
    output_path = OUT_FOLDER + image_id
    print(f"{image_file=}")
    print(f"{output_path=}")
    os.makedirs(output_path, exist_ok=True)
    res = model.infer(tokenizer, prompt=PROMPT, image_file=image_file, output_path = output_path, base_size = 1024, image_size = 640, crop_mode=True, save_results = True, test_compress = True)


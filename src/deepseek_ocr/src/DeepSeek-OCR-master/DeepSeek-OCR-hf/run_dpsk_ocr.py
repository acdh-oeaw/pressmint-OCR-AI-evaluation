from transformers import AutoModel, AutoTokenizer
import torch
import os

os.environ["CUDA_VISIBLE_DEVICES"] = '0'

model_name = 'deepseek-ai/DeepSeek-OCR'

tokenizer = AutoTokenizer.from_pretrained(model_name, trust_remote_code=True)
model = AutoModel.from_pretrained(
    model_name, 
    _attn_implementation='flash_attention_2', 
    trust_remote_code=True, 
    use_safetensors=True
)
model = model.eval().cuda().to(torch.bfloat16)

# Define your two example pairs (few-shot examples)
EXAMPLE_1_IMAGE = "1914-06-29_1.jpg"
with open("/pressmint-ground-truth/data/texts/transkribus_corrected/1914-06-29_1.txt", "r") as f:
    EXAMPLE_1_TEXT = f.read()

EXAMPLE_2_IMAGE = "1914-06-29_2.jpg"
with open("/pressmint-ground-truth/data/texts/transkribus_corrected/1914-06-29_2.txt", "r") as f:
    EXAMPLE_2_TEXT = f.read()

# Two-shot prompt with examples
PROMPT_TEMPLATE = """Here are two examples of how to transcribe German Fraktur newspaper text:

Example 1:
<image>
Transcription:
{example_1_text}

Example 2:
<image>
Transcription:
{example_2_text}

Now transcribe this image following the same approach:
<image>
<|grounding|>Transcribe the text of the following historic document. It is a german newspaper from the early 20th century, printed in 'Fraktur'. Keep the human reading order, meaning, that the natural flow of the text blocks must be respected. The output should only be plain text, without any categories or special structure."""

IN_FOLDER = "/pressmint-ground-truth/data/texts/images/"
OUT_FOLDER = "/pressmint-ground-truth/data/texts/deepseek_ocr_4_one_shot_all_output/"

# for image_file_name in os.listdir(IN_FOLDER):
for image_file_name in ["1914-06-29_3.jpg"]:
    # image_file = IN_FOLDER + image_file_name
    image_path_list = [IN_FOLDER + i for i in [EXAMPLE_1_IMAGE, EXAMPLE_2_IMAGE, image_file_name]]
    image_id = image_file_name.replace(".jpg", "")
    output_path = OUT_FOLDER + image_id
    
    print(f"{image_path_list=}")
    print(f"{output_path=}")
    
    os.makedirs(output_path, exist_ok=True)
    
    # Format prompt with examples
    prompt = PROMPT_TEMPLATE.format(
        example_1_text=EXAMPLE_1_TEXT,
        example_2_text=EXAMPLE_2_TEXT
    )
    
    # Check if model supports multiple images in one call
    # If yes, pass all three images: [EXAMPLE_1_IMAGE, EXAMPLE_2_IMAGE, image_file]
    # If no, use the text-based prompt approach shown above
    
    res = model.infer(
        tokenizer, 
        prompt=prompt, 
        image_file=image_path_list,  # May need to adjust based on model's multi-image support
        output_path=output_path, 
        base_size=1024, 
        image_size=640, 
        crop_mode=True, 
        save_results=True, 
        test_compress=True
    )

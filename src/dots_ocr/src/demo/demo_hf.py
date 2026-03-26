import os
if "LOCAL_RANK" not in os.environ:
    os.environ["LOCAL_RANK"] = "0"
from glob import glob
import pickle
from dots_ocr.utils import dict_promptmode_to_prompt
import torch
from transformers import AutoModelForCausalLM, AutoProcessor, AutoTokenizer
from qwen_vl_utils import process_vision_info


INFERENCE_ENABLED = True
MAX_NEW_TOKENS = 8000

PROMPT = """
This is a scan of a historic german newspaper from the early 20th century. Please do OCR on it,
extract all the text and keep the reading order. Also keep in mind that the writing is in german
'Fraktur'. The output should only be text."
"""


def inference(image_path, prompt, model, processor, image_id):
    print("-- inference")
    messages = [
        {
            "role": "user",
            "content": [
                {
                    "type": "image",
                    "image": image_path
                },
                {"type": "text", "text": prompt}
            ]
        }
    ]

    if INFERENCE_ENABLED:
        # Preparation for inference
        text = processor.apply_chat_template(
            messages, 
            tokenize=False, 
            add_generation_prompt=True
        )
        image_inputs, video_inputs = process_vision_info(messages)
        inputs = processor(
            text=[text],
            images=image_inputs,
            videos=video_inputs,
            padding=True,
            return_tensors="pt",
        )
        inputs = inputs.to("cuda")

        # Inference: Generation of the output
        generated_ids = model.generate(**inputs, max_new_tokens=MAX_NEW_TOKENS)
        generated_ids_trimmed = [
            out_ids[len(in_ids) :] for in_ids, out_ids in zip(inputs.input_ids, generated_ids)
        ]
        output_text = processor.batch_decode(
            generated_ids_trimmed, skip_special_tokens=True, clean_up_tokenization_spaces=False
        )
    else:
        output_text = "test"
    print(output_text)
    output_path = f"/pressmint-ground-truth/data/texts/dots_ocr_4/{image_id}.pkl"
    print(f"{output_path=}")
    with open(output_path, "wb") as f:
        pickle.dump(output_text, f)


if __name__ == "__main__":
    # We recommend enabling flash_attention_2 for better acceleration and memory saving, especially in multi-image and video scenarios.
    print("--- main")
    if INFERENCE_ENABLED:
        model_path = "./weights/DotsOCR"
        model = AutoModelForCausalLM.from_pretrained(
            model_path,
            attn_implementation="flash_attention_2",
            torch_dtype=torch.bfloat16,
            device_map="auto",
            trust_remote_code=True
        )
        processor = AutoProcessor.from_pretrained(model_path,  trust_remote_code=True)
    else:
        model = None
        processor = None
    print("--- model and processor loaded")

    folder = "/pressmint-ground-truth/data/texts/images/"
    for image_file_name in os.listdir(folder):
        image_path = folder + image_file_name
        print("--- new image")
        print(f"{image_path=}")
        image_id = image_file_name.replace(".jpg", "")
        inference(image_path, PROMPT, model, processor, image_id)
    

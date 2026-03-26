import os
if "LOCAL_RANK" not in os.environ:
    os.environ["LOCAL_RANK"] = "0"
import pickle
import random
from dots_ocr.utils import dict_promptmode_to_prompt
import torch
from transformers import AutoModelForCausalLM, AutoProcessor, AutoTokenizer
from qwen_vl_utils import process_vision_info


INFERENCE_ENABLED = True
MAX_NEW_TOKENS = 8000

FULL_RUN = True
NUM_GROUND_TRUTH = 3
PROMPT = (
    "You are an expert in historical German documents. Transcribe the text from "
    "German newspapers from the early 20th century written in Fraktur script. "
    "Follow these guidelines:\n"
    "- Follow the natural reading direction (left to right, top to bottom)\n"
    "- Recognize column layouts and logical text flow\n"
    "- Output only plain text without metadata or structural markup\n"
    "- Preserve paragraphs but add no additional formatting"
)
IN_IMAGE_FOLDER= "/pressmint-ground-truth/data/texts/images/"
IN_GROUND_TRUTH_FOLDER = "/pressmint-ground-truth/data/texts/transkribus_corrected/"
OUT_FOLDER = "/pressmint-ground-truth/data/texts/dots_ocr_11_three_shot_english_extensive_pkl"

def inference(model, processor, ground_truth_pair_list, image_file_infer):
    print("-- inference")
    messages = [
        {"role": "system", "content": PROMPT},
    ]
    for image_file_ground_truth, text_file_ground_truth in ground_truth_pair_list:
        image_path_ground_truth = os.path.join(IN_IMAGE_FOLDER, image_file_ground_truth)
        print(f"{image_path_ground_truth=}")
        messages.append({
            "role": "user",
            "content": [
                {"type": "text", "text": "transcribe this document:"},
                {"type": "image", "image": image_path_ground_truth},
            ]
        })
        text_path_ground_truth = os.path.join(IN_GROUND_TRUTH_FOLDER, text_file_ground_truth)
        print(f"{text_path_ground_truth=}")
        with open(text_path_ground_truth, "r") as f:
            text_ground_truth = f.read()
        messages.append(
            {"role": "assistant", "content": text_ground_truth}
        )
    image_path_infer = os.path.join(IN_IMAGE_FOLDER, image_file_infer)
    print(f"{image_path_infer=}")
    messages.append({
        "role": "user",
        "content": [
            {"type": "text", "text": "transcribe this document:"},
            {"type": "image", "image": image_path_infer},
        ],
    })

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
    out_path = os.path.join(OUT_FOLDER, image_file_infer.replace(".jpg", ".pkl"))
    print(f"{out_path=}")
    os.makedirs(OUT_FOLDER, exist_ok=True)
    with open(out_path, "wb") as f:
        pickle.dump(output_text, f)


def create_infer_and_ground_truth_groups():
    print("--- create_infer_and_ground_truth_groups")
    infer_and_ground_truth_groups = []
    image_file_list = os.listdir(IN_IMAGE_FOLDER)
    for image_file_infer in image_file_list:
        print(f"{image_file_infer=}")
        sample_pool = [i for i in image_file_list if i != image_file_infer]
        ground_truth_pair_list = []
        for image_file_ground_truth in random.sample(sample_pool, NUM_GROUND_TRUTH):
            text_file_ground_truth = image_file_ground_truth.replace(".jpg", ".txt")
            print(f"{text_file_ground_truth=}")
            print(f"{image_file_ground_truth=}")
            ground_truth_pair_list.append((image_file_ground_truth, text_file_ground_truth))
        infer_and_ground_truth_groups.append((ground_truth_pair_list, image_file_infer))
    return infer_and_ground_truth_groups


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

    infer_and_ground_truth_groups = create_infer_and_ground_truth_groups()
    if not FULL_RUN:
        limit = 3
        current = 0
    for ground_truth_pair_list, image_file_infer in infer_and_ground_truth_groups:
        if not FULL_RUN:
            if current == limit:
                break
            current += 1
        print(f"{image_file_infer=}")
        inference(model, processor, ground_truth_pair_list, image_file_infer)
    

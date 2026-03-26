#!/usr/bin/env python3
"""Run the fine-tuned Churro VLM on a single image using only Transformers and Pytorch.

This script is a lightweight fallback for environments that cannot install the
full Churro package. It loads the `stanford-oval/churro-3B` model from the
Hugging Face Hub and transcribes a document page to XML.
"""

from __future__ import annotations

import argparse
import os
import random
from pathlib import Path
from typing import Any

from PIL import Image
import torch
from transformers import AutoModelForImageTextToText, AutoProcessor
from transformers.image_utils import load_image


DEFAULT_MODEL_ID = "stanford-oval/churro-3B"
DEFAULT_SYSTEM_MESSAGE = "Transcribe these documents."
OUT_FOLDER = "/pressmint-ground-truth/data/texts/churro_7_two_shot_prompts_adapted/"
IN_IMAGE_FOLDER = "/pressmint-ground-truth/data/texts/images/"
IN_GROUND_TRUTH_FOLDER = "/pressmint-ground-truth/data/texts/transkribus_corrected/"

MAX_IMAGE_DIM = 2500
MIN_PIXELS = 512 * 28 * 28
MAX_PIXELS = 5120 * 28 * 28


def _parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Standalone Churro OCR inference")
    parser.add_argument("image", nargs='?', default=None, type=Path, help="Path to the page image (PNG, JPG, or WebP)")
    parser.add_argument(
        "--model-id",
        default=DEFAULT_MODEL_ID,
        help="Hugging Face model ID to load (defaults to stanford-oval/churro-3B)",
    )
    parser.add_argument(
        "--system-message",
        default=DEFAULT_SYSTEM_MESSAGE,
        help="System prompt to prepend before presenting the image",
    )
    parser.add_argument(
        "--max-new-tokens",
        type=int,
        default=20_000,
        help="Maximum number of tokens to generate",
    )
    parser.add_argument(
        "--temperature",
        type=float,
        default=0.6,
        help="Sampling temperature",
    )
    parser.add_argument(
        "--device",
        default="auto",
        choices=["auto", "cpu", "cuda"],
        help="Computation device. 'auto' picks CUDA when available",
    )
    return parser.parse_args()


def _resize_image_to_fit(image: Image.Image, max_width: int, max_height: int) -> Image.Image:
    """Match Churro's LLM preprocessing guard (<=2500px on the longest side)."""
    width, height = image.size
    if width <= max_width and height <= max_height:
        return image

    scale = min(max_width / width, max_height / height)
    new_size = (max(1, int(width * scale)), max(1, int(height * scale)))
    if hasattr(Image, "Resampling"):
        resample_filter = Image.Resampling.LANCZOS
    else:  # pragma: no cover - Pillow < 10 fallback
        resample_filter = Image.LANCZOS  # type: ignore[attr-defined]
    return image.resize(new_size, resample=resample_filter)


def _load_processor(model_id: str) -> AutoProcessor:
    """Instantiate the processor with the same pixel bounds used during fine-tuning."""
    processor_kwargs: dict[str, Any] = {"trust_remote_code": True}
    return AutoProcessor.from_pretrained(
        model_id,
        min_pixels=MIN_PIXELS,
        max_pixels=MAX_PIXELS,
        **processor_kwargs,
    )


def _select_device(preference: str) -> torch.device:
    if preference == "cpu":
        return torch.device("cpu")
    if preference == "cuda":
        if not torch.cuda.is_available():
            raise RuntimeError("CUDA requested but no GPU is available")
        return torch.device("cuda")
    return torch.device("cuda" if torch.cuda.is_available() else "cpu")


def _load_and_prepare_image(image_path: str | Path) -> Image.Image:
    """Load an image and prepare it for processing."""
    image = load_image(str(image_path))
    if not isinstance(image, Image.Image):  # pragma: no cover - defensive
        raise TypeError(f"Unexpected image type: {type(image)!r}")
    image = image.convert("RGB")
    image = _resize_image_to_fit(image, MAX_IMAGE_DIM, MAX_IMAGE_DIM)
    return image


def _prepare_inputs_n_shot(
    processor: AutoProcessor,
    ground_truth_pair_list: list[str, str],
    image_file_infer: str,
    system_message: str,
    device: torch.device,
) -> dict[str, Any]:
    print("--- _prepare_inputs_n_shot")
    images = []
    conversation = [
        {"role": "system", "content": [{"type": "text", "text": system_message}]},
    ]
    for image_file_ground_truth, text_file_ground_truth in ground_truth_pair_list:
        image_path_ground_truth = os.path.join(IN_IMAGE_FOLDER, image_file_ground_truth)
        print(f"{image_path_ground_truth=}")
        image_ground_truth = _load_and_prepare_image(image_path_ground_truth)
        images.append(image_ground_truth)
        conversation.append({
            "role": "user",
            "content": [
                {"type": "text", "text": "transcribe this document:"},
                {"type": "image", "image": image_ground_truth},
            ]
        })
        text_path_ground_truth = os.path.join(IN_GROUND_TRUTH_FOLDER, text_file_ground_truth)
        print(f"{text_path_ground_truth=}")
        with open(text_path_ground_truth, "r") as f:
            text_ground_truth = f.read()
        conversation.append(
            {"role": "assistant", "content": [{"type": "text", "text": text_ground_truth}]}
        )
    image_path_infer = os.path.join(IN_IMAGE_FOLDER, image_file_infer)
    print(f"{image_path_infer=}")
    image_infer = _load_and_prepare_image(image_path_infer)
    images.append(image_infer)
    conversation.append({
        "role": "user",
        "content": [
            {"type": "text", "text": "transcribe this document:"},
            {"type": "image", "image": image_infer},
        ],
    })
    
    prompt = processor.apply_chat_template(
        conversation,
        tokenize=False,
        add_generation_prompt=True,
    )
    
    encoded = processor(
        text=[prompt],
        images=images,
        return_tensors="pt",
    )
    encoded = {
        key: value.to(device) for key, value in encoded.items() if isinstance(value, torch.Tensor)
    }
    encoded["prompt_text"] = prompt
    encoded["conversation"] = conversation
    return encoded


def _prepare_inputs(
    processor: AutoProcessor,
    image_path: Path,
    system_message: str,
    device: torch.device,
) -> dict[str, Any]:
    image = _load_and_prepare_image(image_path)
    conversation = [
        {"role": "system", "content": [{"type": "text", "text": system_message}]},
        {"role": "user", "content": [{"type": "image", "image": image}]},
    ]
    prompt = processor.apply_chat_template(
        conversation,
        tokenize=False,
        add_generation_prompt=True,
    )
    encoded = processor(
        text=[prompt],
        images=[image],
        return_tensors="pt",
    )
    encoded = {
        key: value.to(device) for key, value in encoded.items() if isinstance(value, torch.Tensor)
    }
    encoded["prompt_text"] = prompt
    encoded["conversation"] = conversation
    return encoded


def _run_generation(
    model: AutoModelForImageTextToText,
    processor: AutoProcessor,
    inputs: dict[str, Any],
    max_new_tokens: int,
    temperature: float,
) -> str:
    input_ids = inputs["input_ids"]
    input_length = input_ids.shape[1]
    generation_kwargs: dict[str, Any] = {
        "max_new_tokens": max_new_tokens,
        "do_sample": temperature > 0,
    }
    if temperature > 0:
        generation_kwargs["temperature"] = temperature
    if processor.tokenizer.pad_token_id is not None:
        generation_kwargs.setdefault("pad_token_id", processor.tokenizer.pad_token_id)
    if processor.tokenizer.eos_token_id is not None:
        generation_kwargs.setdefault("eos_token_id", processor.tokenizer.eos_token_id)

    with torch.inference_mode():
        generated = model.generate(
            **{k: v for k, v in inputs.items() if isinstance(v, torch.Tensor)}, **generation_kwargs
        )

    new_tokens = generated[0, input_length:]
    transcription = processor.tokenizer.decode(new_tokens, skip_special_tokens=True)
    return transcription.strip()


def _create_infer_and_ground_truth_groups(num_ground_truth: int) ->  list[tuple[list[tuple[str, str]], str]]:
    print("--- _create_infer_and_ground_truth_groups")
    infer_and_ground_truth_groups = []
    image_file_list = os.listdir(IN_IMAGE_FOLDER)
    for image_file_infer in image_file_list:
        print(f"{image_file_infer=}")
        sample_pool = [i for i in image_file_list if i != image_file_infer]
        ground_truth_pair_list = []
        for image_file_ground_truth in random.sample(sample_pool, num_ground_truth):
            text_file_ground_truth = image_file_ground_truth.replace(".jpg", ".txt")
            print(f"{text_file_ground_truth=}")
            print(f"{image_file_ground_truth=}")
            ground_truth_pair_list.append((image_file_ground_truth, text_file_ground_truth))
        infer_and_ground_truth_groups.append((ground_truth_pair_list, image_file_infer))
    return infer_and_ground_truth_groups


def main() -> None:
    print("--- main")
    args = _parse_args()

    device = _select_device(args.device)
    dtype = torch.bfloat16 if device.type == "cuda" else torch.float32
    
    processor = _load_processor(args.model_id)
    model = AutoModelForImageTextToText.from_pretrained(
        args.model_id,
        dtype=dtype,
        trust_remote_code=True,
        low_cpu_mem_usage=True,
    )
    model.to(device)
    model.eval()

    if args.image is None:
        infer_and_ground_truth_groups = _create_infer_and_ground_truth_groups(2)
        # limit = 3
        # current = 0
        for ground_truth_pair_list, image_file_infer in infer_and_ground_truth_groups:
            # if current == limit:
            #     break
            # current += 1
            inputs = _prepare_inputs_n_shot(
                processor,
                ground_truth_pair_list,
                image_file_infer,
                args.system_message,
                device,
            )
            print(inputs["prompt_text"])
            print(f"Prompt length: {len(inputs['input_ids'][0])} tokens")
            transcription = _run_generation(
                model,
                processor,
                inputs,
                max_new_tokens=args.max_new_tokens,
                temperature=args.temperature,
            )
            print(f"{transcription=}")
            out_path = os.path.join(OUT_FOLDER, image_file_infer.replace(".jpg", ".txt"))
            print(f"{out_path=}")
            os.makedirs(OUT_FOLDER, exist_ok=True)
            with open(out_path, "w", encoding="utf-8") as f:
                f.write(transcription)
    else:
        # Single image processing (zero-shot)
        inputs = _prepare_inputs(processor, args.image, args.system_message, device)
        transcription = _run_generation(
            model,
            processor,
            inputs,
            max_new_tokens=args.max_new_tokens,
            temperature=args.temperature,
        )
        print(transcription)


if __name__ == "__main__":
    main()

# evaluation of various OCR inferences in the context of the pressmint project

## contents

- [comparison results plot](#comparison-results-plot)
- [individual OCR workflows](#individual-ocr-workflows)
- [comparison results details](#comparison-results-details)
- [variance details](#variance-details)
- [results per image](#results-per-image)
- [all image results ranked](#all-image-results-ranked)

This repo contains the builds, inferences and evaluations of all used OCR models.

The notebookt at [./src/pressmint_ocr.ipynb](./src/pressmint_ocr.ipynb) contains all the evaluation
logic and those OCR workflows directly that were delegatable to LLM APIs (namely those of OpenAI,
Anthropic, and Google). Other OCR workflows involving open source models that were executed
ourselves on [https://www.clip.science/](https://www.clip.science/) are found under [./src](./src)
and their results are only evaluated in the central notebook (namely
[churro](https://github.com/stanford-oval/Churro),
[dots.ocr](https://github.com/rednote-hilab/dots.ocr),
[deepseek-ocr](https://github.com/deepseek-ai/DeepSeek-OCR)). Models provided by
[https://pero-ocr.fit.vutbr.cz/](https://pero-ocr.fit.vutbr.cz/), and
[https://www.transkribus.org/](https://www.transkribus.org/) were tested separately through their
UI with theirs results persisted and evaulated here like the others.

## how to reproduce

\#TODO-origin-images

### notebook

To run the OCR worfklows via LLM APIs of Anthropic, Google, and OpenAI, use the respective functions
in the jupyter notebook. For this, have docker installed (and docker compose, usually integrated
into newer versions of docker) and do:
```
docker compose up
```
Then open the jupyterlab notebook at http://localhost:8888/lab/tree/src/pressmint_ocr.ipynb

Keys and tokens are necessary for their respective providers. This notebook assumes the keys to be
persisted into the [./data/keys/](./data/keys/) folder, where templates can be found. The json files
must be named `google_key.json` for the google API and `tokens.json` for OpenAI and Anthropic.

The notebook also does all the evaluations of all models.

### local open source models

They were run on [https://www.clip.science/](https://www.clip.science/) on a single A100 GPU with
[apptainer](https://apptainer.org/) and [slurm](https://slurm.schedmd.com/overview.html).

To reproduce those, an equally strong GPU is required. If available, then the respective slurm
scripts under [./src](./src) can be inspected which call the apptainer commands. These commands can
be extracted and called individually, e.g. like

```
apptainer exec --fakeroot --containall --writable-tmpfs --nv \
  --bind ../../data/:/pressmint-ground-truth/data/ \
  --bind ./src/churro_transformers_infer.py:/pressmint-ground-truth/src/churro/src/churro_transformers_infer.py \
  --bind ./churro.sh:/pressmint-ground-truth/src/churro/churro.sh \
  churro.sif bash /pressmint-ground-truth/src/churro/churro.sh
``` 

To reproduce individual OCR workflows, checkout their git commits and scripts as described below.

### others

[https://pero-ocr.fit.vutbr.cz/](https://pero-ocr.fit.vutbr.cz/), and
[https://www.transkribus.org/](https://www.transkribus.org/) offer their own UIs. To reproduce, use
these.

## comparison results plot

- workflow: described in following section
- WER: word error rate, lower = better
- CER: character error rate, lower = better
- difflib: python's native difflib, implementing "Gestalt pattern matching", higher = better

(Note that in this plot the axis for WER and CER are inverted so that better results are displayed 
consistently higher up.)

![results_per_workflow](data/analysis/plot_metrics_per_workflow.png)

This plot shows the variance per metric and per ocr workflow:

![plot_metrics_variances](data/analysis/plot_metrics_variances.png)

This plot shows the results per image averaged across workflows

![results_per_image](data/analysis/plot_metrics_per_image.png)

## notes on OCR models

- deepseek-ocr does not support few-shot learning; only one image per prompt.
- Llama vision is disallowed within the EU: https://huggingface.co/meta-llama/Llama-3.2-11B-Vision

## individual OCR workflows

The following is a list of all configurations and parameters of the evaluated models.

Their inference outputs are found at [./data/texts/](./data/texts/) respective their workflow name.

### anno

This is the only "OCR workflow" that was not executed by us, but provided by
[https://anno.onb.ac.at/](https://anno.onb.ac.at/) and used as a comparision to evaluated against.

### anthropic_1_simple

executed directly by [./src/pressmint_ocr.ipynb](./src/pressmint_ocr.ipynb) at section `# OCR
inferences`.

This prompt is shared directly between openai_1_simple, google_gemini_1_simple, anthropic_1_simple.

Very basic approach. Just throw a single prompt and image at AI.

```
prompt_simple = "Extrahiere den gesamten Text aus diesem Bild."
```

### anthropic_2_extensive

**note: this prompt crashed and returned no results**

executed directly by [./src/pressmint_ocr.ipynb](./src/pressmint_ocr.ipynb) at section `# OCR
inferences`.

This prompt is shared directly between openai_2_extensive, google_gemini_2_extensive,
anthropic_2_extensive.

Identical to simple workflows above, but with the prompt being a bit more extensive. Note 
that `anthropic_2_extensive` didn't work due to time-outs.
```
prompt_extensive = (
    "Das ist ein Scan einer deutschen historischen Zeitung aus dem frühen 20. Jahrhundert."
    "Bitte führe OCR darauf aus. "
    "Beachte dabei, dass die Schrift in Fraktur gehalten ist. "
    "Versuche keine Interpretationen zu machen bezüglich der Wörter, sondern transkripiere jeden Buchstaben wie du ihn siehst. "
    "Ohne irgendwelche Metabeschreibungen, nur den Text alleine."
)
```


### churro_1_simple

Code, configuration, and log at time of inference: 
[https://github.com/acdh-oeaw/pressmint-OCR-AI-evaluation/blob/e0de4ae339228a10c26b07538018d0a3f3b1a273/src/churro/](https://github.com/acdh-oeaw/pressmint-OCR-AI-evaluation/blob/e0de4ae339228a10c26b07538018d0a3f3b1a273/src/churro/)

Default prompt:

```
"Transcribe the entiretly of this historical documents to txt format."
```

### churro_2_german_extensive_2

Code, configuration, and log at time of inference: 
[https://github.com/acdh-oeaw/pressmint-OCR-AI-evaluation/blob/f6f4bcda1b75de39ac9d3f4564e3ff136855f8b5/src/churro/](https://github.com/acdh-oeaw/pressmint-OCR-AI-evaluation/blob/f6f4bcda1b75de39ac9d3f4564e3ff136855f8b5/src/churro/)

```
DEFAULT_SYSTEM_MESSAGE = (
    "Transkribiere den Text aus dem folgenden historischen Dokument. Hierbei handelt es sich um "
    "eine deutsche Zeitung aus dem frühen 20. Jahrhundert in Frakturschrift. Behalte die "
    "menschliche Leserichtung bei, also erkenne den Fluss in den Textblöcken. Der Output soll "
    "reiner Text sein, ohne spezielle Kategorisierung oder Strukturierung."
)
```

### churro_3_english_extensive_3

Code, configuration, and log at time of inference: 
[https://github.com/acdh-oeaw/pressmint-OCR-AI-evaluation/blob/f9f40ca545c242d32a37ece0f2116f3bb4cb9c27/src/churro/](https://github.com/acdh-oeaw/pressmint-OCR-AI-evaluation/blob/f9f40ca545c242d32a37ece0f2116f3bb4cb9c27/src/churro/)

```
DEFAULT_SYSTEM_MESSAGE = (
    "Transcribe the text of the following historic document. It is a german newspaper from the "
    "early 20th century, printed in 'Fraktur'. Keep the human reading order, meaning, that the "
    "natural flow of the text blocks must be respected. The output should only be plain text, "
    "without any categories or special structure."
)
```

### churro_4_one_shot

Code, configuration, and log at time of inference: 
[https://github.com/acdh-oeaw/pressmint-OCR-AI-evaluation/blob/de2543f3734cf11aac09515ac6ac22fc93585d6c/src/churro/](https://github.com/acdh-oeaw/pressmint-OCR-AI-evaluation/blob/de2543f3734cf11aac09515ac6ac22fc93585d6c/src/churro/)

- one shot with ground truth images

prompt and conversation:
```
DEFAULT_SYSTEM_MESSAGE = (
    "Transcribe the document following the example shown. Keep the human reading order and "
    "natural flow of text blocks. Output only plain text without any special structure."
)
# ...
for image_file_ground_truth, text_file_ground_truth in ground_truth_pair_list:
    # ...
    conversation.append(
        {"role": "user", "content": [{"type": "image", "image": image_ground_truth}]}
    )
# ...
conversation.append(
    {"role": "user", "content": [{"type": "image", "image": image_infer}]},
)

```

### churro_5_one_shot_s_replaced

Same data as churro_4_one_shot, but since it had transcribed 'ſ' instead of 's', in this dataset, 
they were replaced from 'ſ' to 's' with sed (note that this includes 's' which are supposed to be 
'ß').

### churro_6_two_shot

Code, configuration, and log at time of inference: 
[https://github.com/acdh-oeaw/pressmint-OCR-AI-evaluation/blob/14b546ef6ad9324af668c39b18714492a8116968/src/churro/](https://github.com/acdh-oeaw/pressmint-OCR-AI-evaluation/blob/14b546ef6ad9324af668c39b18714492a8116968/src/churro/)

Same prompt and code setup as `churro_4_one_shot`, but with two pairs of ground truth supplied.

### churro_7_two_shot_prompts_adapted

Code, configuration, and log at time of inference: 
[https://github.com/acdh-oeaw/pressmint-OCR-AI-evaluation/blob/fbcda001e9a630d869e57693d282143e9cf9dae7/src/churro/](https://github.com/acdh-oeaw/pressmint-OCR-AI-evaluation/blob/fbcda001e9a630d869e57693d282143e9cf9dae7/src/churro/)

same as `churro_6_two_shot` but with prompts and chat adapted:

```
DEFAULT_SYSTEM_MESSAGE = "Transcribe these documents."
# ...
for image_file_ground_truth, text_file_ground_truth in ground_truth_pair_list:
    # ...
    conversation.append({
        "role": "user",
        "content": [
            {"type": "text", "text": "transcribe this document:"},
            {"type": "image", "image": image_ground_truth},
        ]
    })
# ...
conversation.append({
    "role": "user",
    "content": [
        {"type": "text", "text": "transcribe this document:"},
        {"type": "image", "image": image_infer},
    ],
})
```

### churro_8_two_shot_zero_temperature

Code, configuration, and log at time of inference: 
[https://github.com/acdh-oeaw/pressmint-OCR-AI-evaluation/blob/b2e91e36a1fdbe0bcb40027acd3868bafa582e54/src/churro/](https://github.com/acdh-oeaw/pressmint-OCR-AI-evaluation/blob/b2e91e36a1fdbe0bcb40027acd3868bafa582e54/src/churro/)

Same as `churro_7_two_shot_prompts_adapted` but with temperature set to 0.

### churro_9_two_shot_zero_temperature

Code, configuration, and log at time of inference: 
[https://github.com/acdh-oeaw/pressmint-OCR-AI-evaluation/blob/18dd2a3e1c2ff366b9da8c9db7bca53e6abe20dd/src/churro/](https://github.com/acdh-oeaw/pressmint-OCR-AI-evaluation/blob/18dd2a3e1c2ff366b9da8c9db7bca53e6abe20dd/src/churro/)

Identical to `churro_8_two_shot_zero_temperature`, to check if results are the same.

### deepseek_ocr_1_default

Code, configuration, and log at time of inference: 
[https://github.com/acdh-oeaw/pressmint-OCR-AI-evaluation/blob/787dbbfac14d314e75233d4b243dc2dbbd4fba53/src/deepseek_ocr/](https://github.com/acdh-oeaw/pressmint-OCR-AI-evaluation/blob/787dbbfac14d314e75233d4b243dc2dbbd4fba53/src/deepseek_ocr/)

Default prompt:

```
"<image>\n<|grounding|>Convert the document to markdown. "
```

### deepseek_ocr_2_german_extensive_2

Code, configuration, and log at time of inference: 
[https://github.com/acdh-oeaw/pressmint-OCR-AI-evaluation/blob/ae4ae6a9ef9b45f61829193cd243f5908a72954e/src/deepseek_ocr/](https://github.com/acdh-oeaw/pressmint-OCR-AI-evaluation/blob/ae4ae6a9ef9b45f61829193cd243f5908a72954e/src/deepseek_ocr/)

```
PROMPT = (
    "<image>\n<|grounding|>Transkribiere den Text aus dem folgenden historischen Dokument. Hierbei "
    "handelt es sich um eine deutsche Zeitung aus dem frühen 20. Jahrhundert in Frakturschrift. "
    "Behalte die menschliche Leserichtung bei, also erkenne den Fluss in den Textblöcken. Der "
    "Output soll reiner Text sein, ohne spezielle Kategorisierung oder Strukturierung."
)
```

### deepseek_ocr_3_english_extensive_2

Code, configuration, and log at time of inference: 
[https://github.com/acdh-oeaw/pressmint-OCR-AI-evaluation/blob/a2ab3101d2cbaa922935808d0af41c4719f86796/src/deepseek_ocr/](https://github.com/acdh-oeaw/pressmint-OCR-AI-evaluation/blob/a2ab3101d2cbaa922935808d0af41c4719f86796/src/deepseek_ocr/)

```
PROMPT = (
    "<image>\n<|grounding|>Transcribe the text of the following historic document. It is a german "
    "newspaper from the early 20th century, printed in 'Fraktur'. Keep the human reading order, "
    "meaning, that the natural flow of the text blocks must be respected. The output should only "
    "be plain text, without any categories or special structure."
)
```

### dots_ocr_1_default

Code, configuration, and log at time of inference: 
[https://github.com/acdh-oeaw/pressmint-OCR-AI-evaluation/blob/616a2b8596b6fb9a7081ddcf48e99e47798111b0/src/dots_ocr/](https://github.com/acdh-oeaw/pressmint-OCR-AI-evaluation/blob/616a2b8596b6fb9a7081ddcf48e99e47798111b0/src/dots_ocr/)

Default setup of dots.ocr with the first of the four default prompts:
```
Please output the layout information from the PDF image, including each layout element's bbox, its category, and the corresponding text content within the bbox.

1. Bbox format: [x1, y1, x2, y2]

2. Layout Categories: The possible categories are ['Caption', 'Footnote', 'Formula', 'List-item', 'Page-footer', 'Page-header', 'Picture', 'Section-header', 'Table', 'Text', 'Title'].

3. Text Extraction & Formatting Rules:
    - Picture: For the 'Picture' category, the text field should be omitted.
    - Formula: Format its text as LaTeX.
    - Table: Format its text as HTML.
    - All Others (Text, Title, etc.): Format their text as Markdown.

4. Constraints:
    - The output text must be the original text from the image, with no translation.
    - All layout elements must be sorted according to human reading order.

5. Final Output: The entire output must be a single JSON object.
```

### dots_ocr_2_default

Code, configuration, and log at time of inference: 
[https://github.com/acdh-oeaw/pressmint-OCR-AI-evaluation/blob/616a2b8596b6fb9a7081ddcf48e99e47798111b0/src/dots_ocr/](https://github.com/acdh-oeaw/pressmint-OCR-AI-evaluation/blob/616a2b8596b6fb9a7081ddcf48e99e47798111b0/src/dots_ocr/)

**Discarded.**

The results concerned only the bounding boxes, but without texts.

```
"""
Please output the layout information from this PDF image, including each layout's bbox and its category. 
The bbox should be in the format [x1, y1, x2, y2]. The layout categories for the PDF document include 
['Caption', 'Footnote', 'Formula', 'List-item', 'Page-footer', 'Page-header', 'Picture', 'Section-header', 'Table', 'Text', 'Title']. 
Do not output the corresponding text. The layout result should be in JSON format.
"""
```

### dots_ocr_3_default

Code, configuration, and log at time of inference: 
[https://github.com/acdh-oeaw/pressmint-OCR-AI-evaluation/blob/616a2b8596b6fb9a7081ddcf48e99e47798111b0/src/dots_ocr/](https://github.com/acdh-oeaw/pressmint-OCR-AI-evaluation/blob/616a2b8596b6fb9a7081ddcf48e99e47798111b0/src/dots_ocr/)

Default setup of dots.ocr with the third of the four default prompts:

```
Extract the text content from this image.
```


### dots_ocr_4_default

Code, configuration, and log at time of inference: 
[https://github.com/acdh-oeaw/pressmint-OCR-AI-evaluation/blob/616a2b8596b6fb9a7081ddcf48e99e47798111b0/src/dots_ocr/](https://github.com/acdh-oeaw/pressmint-OCR-AI-evaluation/blob/616a2b8596b6fb9a7081ddcf48e99e47798111b0/src/dots_ocr/)

Default setup of dots.ocr with the fourth of the four default prompts:

```
Extract text from the given bounding box on the image (format: [x1, y1, x2, y2]).\nBounding Box:\n
```

### dots_ocr_5_german_extensive

Code, configuration, and log at time of inference: 
[https://github.com/acdh-oeaw/pressmint-OCR-AI-evaluation/blob/caa71941735123e18f45e0c385d6d109d4699319/src/dots_ocr/](https://github.com/acdh-oeaw/pressmint-OCR-AI-evaluation/blob/caa71941735123e18f45e0c385d6d109d4699319/src/dots_ocr/)

**Discarded.**

Model ran through all images and infered, but the outputs were all empty.

```
"""
Das ist ein Scan einer deutschen historischen Zeitung aus dem frühen 20. Jahrhundert. 
Bitte führe OCR darauf aus, also extrahiere den Text und behalte dabei die Leserichtung bei.
Beachte auch, dass die Schrift in Fraktur gehalten ist. Der Output soll nur der Text alleine sein.
"""
```

### dots_ocr_6_english_extensive

Code, configuration, and log at time of inference: 
[https://github.com/acdh-oeaw/pressmint-OCR-AI-evaluation/blob/0cccb80204cf9f08642259ef15691a5aba0c91ae/src/dots_ocr/](https://github.com/acdh-oeaw/pressmint-OCR-AI-evaluation/blob/0cccb80204cf9f08642259ef15691a5aba0c91ae/src/dots_ocr/)

```
"""
This is a scan of a historic german newspaper from the early 20th century. Please do OCR on it, 
extract all the text and keep the reading order. Also keep in mind that the writing is in german 
'Fraktur'. The output should only be text."
"""
```

### dots_ocr_7_german_extensive_2

Code, configuration, and log at time of inference: 
[https://github.com/acdh-oeaw/pressmint-OCR-AI-evaluation/blob/f8f574102d1ae9fa01de9776c028908acf8ae562/src/dots_ocr/](https://github.com/acdh-oeaw/pressmint-OCR-AI-evaluation/blob/f8f574102d1ae9fa01de9776c028908acf8ae562/src/dots_ocr/)

```
PROMPT = (
    "Transkribiere den Text aus dem folgenden historischen Dokument. Hierbei handelt es sich um "
    "eine deutsche Zeitung aus dem frühen 20. Jahrhundert in Frakturschrift. Behalte die "
    "menschliche Leserichtung bei, also erkenne den Fluss in den Textblöcken. Der Output soll "
    "reiner Text sein, ohne spezielle Kategorisierung oder Strukturierung."
)
```

### dots_ocr_8_one_shot

Code, configuration, and log at time of inference: 
[https://github.com/acdh-oeaw/pressmint-OCR-AI-evaluation/blob/8649c0458779c18ab2a18f48355e430801cde5ce/src/dots_ocr/](https://github.com/acdh-oeaw/pressmint-OCR-AI-evaluation/blob/8649c0458779c18ab2a18f48355e430801cde5ce/src/dots_ocr/)

same system prompt as `dots_ocr_7_german_extensive_2`. One shot learning adapted in code like this:

```
messages = [
    {"role": "system", "content": PROMPT},
]
for image_file_ground_truth, text_file_ground_truth in ground_truth_pair_list:
    # ...
    messages.append({
        "role": "user",
        "content": [
            {"type": "text", "text": "transcribe this document:"},
            {"type": "image", "image": image_path_ground_truth},
        ]
    })
    messages.append(
        {"role": "assistant", "content": text_ground_truth}
    )
# ...
messages.append({
    "role": "user",
    "content": [
        {"type": "text", "text": "transcribe this document:"},
        {"type": "image", "image": image_path_infer},
    ],
})
```

### dots_ocr_9_three_shot

Code, configuration, and log at time of inference: 
[https://github.com/acdh-oeaw/pressmint-OCR-AI-evaluation/blob/de06b9454fd12a2506da4562777824504bf9c5c0/src/dots_ocr/](https://github.com/acdh-oeaw/pressmint-OCR-AI-evaluation/blob/de06b9454fd12a2506da4562777824504bf9c5c0/src/dots_ocr/)

Same setup as `dots_ocr_8_one_shot`, but with three pairs of ground truth data.

### dots_ocr_10_one_shot_english_extensive

Code, configuration, and log at time of inference: 
[https://github.com/acdh-oeaw/pressmint-OCR-AI-evaluation/blob/eb85fa698036e5408eb8ad4b7520bda95cfe9984/src/dots_ocr/](https://github.com/acdh-oeaw/pressmint-OCR-AI-evaluation/blob/eb85fa698036e5408eb8ad4b7520bda95cfe9984/src/dots_ocr/)

Same few-shot code as above, with slight configuration improvements, and system prompt in english:

```
PROMPT = (
    "You are an expert in historical German documents. Transcribe the text from "
    "German newspapers from the early 20th century written in Fraktur script. "
    "Follow these guidelines:\n"
    "- Follow the natural reading direction (left to right, top to bottom)\n"
    "- Recognize column layouts and logical text flow\n"
    "- Output only plain text without metadata or structural markup\n"
    "- Preserve paragraphs but add no additional formatting"
)
```

### dots_ocr_11_three_shot_english_extensive

Code, configuration, and log at time of inference: 
[https://github.com/acdh-oeaw/pressmint-OCR-AI-evaluation/blob/9e84b4470c2449cb17bab07343e7959c1b0cea9e/src/dots_ocr/](https://github.com/acdh-oeaw/pressmint-OCR-AI-evaluation/blob/9e84b4470c2449cb17bab07343e7959c1b0cea9e/src/dots_ocr/)

Same as `dots_ocr_10_one_shot_english_extensive` but with three ground truth samples.

### google_gemini_1_simple

executed directly by [./src/pressmint_ocr.ipynb](./src/pressmint_ocr.ipynb) at section `# OCR
inferences`.

This prompt is shared directly between openai_1_simple, google_gemini_1_simple, anthropic_1_simple.

Very basic approach. Just throw a single prompt and image at AI.

```
prompt_simple = "Extrahiere den gesamten Text aus diesem Bild."
```

### google_gemini_2_extensive

executed directly by [./src/pressmint_ocr.ipynb](./src/pressmint_ocr.ipynb) at section `# OCR
inferences`.

This prompt is shared directly between openai_2_extensive, google_gemini_2_extensive,
anthropic_2_extensive.

Identical to simple workflows above, but with the prompt being a bit more extensive. Note 
that `anthropic_2_extensive` didn't work due to time-outs.
```
prompt_extensive = (
    "Das ist ein Scan einer deutschen historischen Zeitung aus dem frühen 20. Jahrhundert."
    "Bitte führe OCR darauf aus. "
    "Beachte dabei, dass die Schrift in Fraktur gehalten ist. "
    "Versuche keine Interpretationen zu machen bezüglich der Wörter, sondern transkripiere jeden Buchstaben wie du ihn siehst. "
    "Ohne irgendwelche Metabeschreibungen, nur den Text alleine."
)
```

### google_gemini_3_one_shot_simple

**note: this prompt crashed and returned no results**

executed directly by [./src/pressmint_ocr.ipynb](./src/pressmint_ocr.ipynb) at section `# OCR
inferences`.

One Shot learning experiment, where an image with its gold data transcription is shown to the AI
beforehand, with these prompts:

```
prompt_one_shot_ground_truth = "Hier ist ein Beispielbild einer historischen Frakturschrift-Zeitung mit seiner korrekten Transkription:"
prompt_one_shot_explanation = "Bitte beschreibe das folgende ähnliche Bild, so gut wie möglich."
prompt_one_shot_ocr_inference = "Anhand von dem vorher gezeigten Beispielbild, extrahiere den Text aus dem folgenden Bild."
```

### google_vision

executed directly by [./src/pressmint_ocr.ipynb](./src/pressmint_ocr.ipynb) at section `# OCR
inferences`.

Google Cloud Vision API is not a LLM or Gemini, but an image analyser, which can be used for OCR
too.

### openai_1_simple

executed directly by [./src/pressmint_ocr.ipynb](./src/pressmint_ocr.ipynb) at section `# OCR
inferences`.

This prompt is shared directly between openai_1_simple, google_gemini_1_simple, anthropic_1_simple.

Very basic approach. Just throw a single prompt and image at AI.

```
prompt_simple = "Extrahiere den gesamten Text aus diesem Bild."
```

### openai_2_extensive

executed directly by [./src/pressmint_ocr.ipynb](./src/pressmint_ocr.ipynb) at section `# OCR
inferences`.

This prompt is shared directly between openai_2_extensive, google_gemini_2_extensive,
anthropic_2_extensive.

Identical to simple workflows above, but with the prompt being a bit more extensive. Note 
that `anthropic_2_extensive` didn't work due to time-outs.
```
prompt_extensive = (
    "Das ist ein Scan einer deutschen historischen Zeitung aus dem frühen 20. Jahrhundert."
    "Bitte führe OCR darauf aus. "
    "Beachte dabei, dass die Schrift in Fraktur gehalten ist. "
    "Versuche keine Interpretationen zu machen bezüglich der Wörter, sondern transkripiere jeden Buchstaben wie du ihn siehst. "
    "Ohne irgendwelche Metabeschreibungen, nur den Text alleine."
)
```

### openai_3_one_shot_simple

executed directly by [./src/pressmint_ocr.ipynb](./src/pressmint_ocr.ipynb) at section `# OCR
inferences`.

One Shot learning experiment, where an image with its gold data transcription is shown to the AI
beforehand, with these prompts:

```
prompt_one_shot_ground_truth = "Hier ist ein Beispielbild einer historischen Frakturschrift-Zeitung mit seiner korrekten Transkription:"
prompt_one_shot_explanation = "Bitte beschreibe das folgende ähnliche Bild, so gut wie möglich."
prompt_one_shot_ocr_inference = "Anhand von dem vorher gezeigten Beispielbild, extrahiere den Text aus dem folgenden Bild."
```

### pero_ocr

\#TODO-pero

Inferred by running manually on https://pero-ocr.fit.vutbr.cz/.

### pero_scribblesense

\#TODO-pero

Inferred by running manually on https://scribblesense.cz/.

### transrkibus

\#TODO-transkribus

## comparison results details

|     | workflow                                 | image_id     |         WER |          CER |    difflib |
|----:|:-----------------------------------------|:-------------|------------:|-------------:|-----------:|
|   0 | anno                                     | 1914-06-29_1 |  0.300746   |  0.0891249   | 0.927337   |
|   1 | anno                                     | 1914-06-29_2 |  0.219292   |  0.0429944   | 0.965998   |
|   2 | anno                                     | 1914-06-29_3 |  0.130086   |  0.0248886   | 0.979545   |
|   3 | anno                                     | 1914-06-29_4 |  0.12885    |  0.0227116   | 0.980347   |
|   4 | anno                                     | 1914-06-29_5 |  0.179021   |  0.0326541   | 0.973684   |
|   5 | anno                                     | 1914-06-29_7 |  0.1771     |  0.0406416   | 0.970251   |
|   6 | anno                                     | 1915-12-28_1 |  0.218905   |  0.0836584   | 0.926895   |
|   7 | anno                                     | 1915-12-28_2 |  0.769446   |  0.627305    | 0.631292   |
|   8 | anno                                     | 1915-12-28_3 |  0.258993   |  0.0598589   | 0.95202    |
|   9 | anno                                     | 1915-12-28_4 |  0.444732   |  0.154068    | 0.865014   |
|  10 | anno                                     | 1917-12-28_1 |  0.196296   |  0.0735375   | 0.935992   |
|  11 | anno                                     | 1917-12-28_2 |  0.845309   |  0.709918    | 0.481758   |
|  12 | anno                                     | 1917-12-28_3 |  0.259978   |  0.0557485   | 0.955512   |
|  13 | anno                                     | 1917-12-28_4 |  0.586375   |  0.29414     | 0.769756   |
|  14 | anno                                     | 1918-12-27_1 |  0.312379   |  0.0818414   | 0.923912   |
|  15 | anno                                     | 1918-12-27_2 |  0.243472   |  0.0604731   | 0.948825   |
|  16 | anno                                     | 1918-12-27_3 |  0.254967   |  0.0709265   | 0.939721   |
|  17 | anno                                     | 1918-12-27_4 |  0.187313   |  0.0447538   | 0.964545   |
|  18 | anno                                     | 1918-12-27_5 |  0.783499   |  0.512721    | 0.611949   |
|  19 | anno                                     | 1918-12-27_6 |  0.576923   |  0.225356    | 0.808505   |
|  20 | anno                                     | average      |  0.353684   |  0.165366    | 0.875643   |
|  21 | anthropic_1_simple                       | 1914-06-29_1 |  0.961889   |  0.866667    | 0.160021   |
|  22 | anthropic_1_simple                       | 1914-06-29_2 |  0.961567   |  0.88931     | 0.106752   |
|  23 | anthropic_1_simple                       | 1914-06-29_3 |  0.962392   |  0.835766    | 0.102127   |
|  24 | anthropic_1_simple                       | 1914-06-29_4 |  0.941546   |  0.754163    | 0.113854   |
|  25 | anthropic_1_simple                       | 1914-06-29_5 |  0.960839   |  0.873732    | 0.147232   |
|  26 | anthropic_1_simple                       | 1914-06-29_7 |  0.969522   |  0.898017    | 0.110125   |
|  27 | anthropic_1_simple                       | 1915-12-28_1 |  0.966833   |  0.866968    | 0.202405   |
|  28 | anthropic_1_simple                       | 1915-12-28_2 |  0.983181   |  0.922131    | 0.0680517  |
|  29 | anthropic_1_simple                       | 1915-12-28_3 |  0.984303   |  0.935877    | 0.0566802  |
|  30 | anthropic_1_simple                       | 1915-12-28_4 |  0.974093   |  0.906981    | 0.12326    |
|  31 | anthropic_1_simple                       | 1917-12-28_1 |  0.981481   |  0.91452     | 0.068806   |
|  32 | anthropic_1_simple                       | 1917-12-28_2 |  0.978867   |  0.903861    | 0.0787831  |
|  33 | anthropic_1_simple                       | 1917-12-28_3 |  0.986516   |  0.946566    | 0.0418542  |
|  34 | anthropic_1_simple                       | 1917-12-28_4 |  0.982157   |  0.926586    | 0.0701754  |
|  35 | anthropic_1_simple                       | 1918-12-27_1 |  0.970019   |  0.901483    | 0.11473    |
|  36 | anthropic_1_simple                       | 1918-12-27_2 |  0.948483   |  0.847029    | 0.178386   |
|  37 | anthropic_1_simple                       | 1918-12-27_3 |  0.980132   |  0.927396    | 0.0744296  |
|  38 | anthropic_1_simple                       | 1918-12-27_4 |  0.956716   |  0.883358    | 0.142206   |
|  39 | anthropic_1_simple                       | 1918-12-27_5 |  0.972705   |  0.889655    | 0.128019   |
|  40 | anthropic_1_simple                       | 1918-12-27_6 |  0.97669    |  0.898755    | 0.0962315  |
|  41 | anthropic_1_simple                       | average      |  0.969997   |  0.889441    | 0.109206   |
|  42 | churro_1_simple                          | 1914-06-29_1 |  0.533554   |  0.176227    | 0.868022   |
|  43 | churro_1_simple                          | 1914-06-29_2 |  0.478523   |  0.0785702   | 0.935781   |
|  44 | churro_1_simple                          | 1914-06-29_3 |  0.31381    |  0.0470886   | 0.966722   |
|  45 | churro_1_simple                          | 1914-06-29_4 |  0.323696   |  0.0602317   | 0.959934   |
|  46 | churro_1_simple                          | 1914-06-29_5 |  0.311888   |  0.0689743   | 0.944607   |
|  47 | churro_1_simple                          | 1914-06-29_7 |  0.219934   |  0.057982    | 0.954184   |
|  48 | churro_1_simple                          | 1915-12-28_1 |  5.8068     |  5.51468     | 0.145533   |
|  49 | churro_1_simple                          | 1915-12-28_2 | 11.0126     |  7.94766     | 0.0351503  |
|  50 | churro_1_simple                          | 1915-12-28_3 |  0.265533   |  3.46073     | 0.353653   |
|  51 | churro_1_simple                          | 1915-12-28_4 |  0.326425   |  0.0808859   | 0.936187   |
|  52 | churro_1_simple                          | 1917-12-28_1 |  0.480556   |  0.148291    | 0.893481   |
|  53 | churro_1_simple                          | 1917-12-28_2 |  1.09045    |  1.13583     | 0.498904   |
|  54 | churro_1_simple                          | 1917-12-28_3 |  1.8069     | 12.2775      | 0.132611   |
|  55 | churro_1_simple                          | 1917-12-28_4 |  0.626115   |  0.305182    | 0.808221   |
|  56 | churro_1_simple                          | 1918-12-27_1 |  0.300774   |  0.0501279   | 0.954093   |
|  57 | churro_1_simple                          | 1918-12-27_2 |  5.36768    |  5.0061      | 0.0130683  |
|  58 | churro_1_simple                          | 1918-12-27_3 |  2.97947    |  2.51518     | 0.430387   |
|  59 | churro_1_simple                          | 1918-12-27_4 |  0.680597   |  0.887235    | 0.674219   |
|  60 | churro_1_simple                          | 1918-12-27_5 |  0.226427   |  1.15214     | 0.6201     |
|  61 | churro_1_simple                          | 1918-12-27_6 | 20.9289     |  4.50381     | 0.224071   |
|  62 | churro_1_simple                          | average      |  2.70403    |  2.27372     | 0.617446   |
|  63 | churro_2_german_extensive_2              | 1914-06-29_1 |  0.309031   |  0.101062    | 0.915847   |
|  64 | churro_2_german_extensive_2              | 1914-06-29_2 |  0.341372   |  0.0622155   | 0.892892   |
|  65 | churro_2_german_extensive_2              | 1914-06-29_3 |  0.461776   |  0.077124    | 0.936985   |
|  66 | churro_2_german_extensive_2              | 1914-06-29_4 |  0.279698   |  0.0652958   | 0.948812   |
|  67 | churro_2_german_extensive_2              | 1914-06-29_5 |  0.488112   |  0.0864524   | 0.930287   |
|  68 | churro_2_german_extensive_2              | 1914-06-29_7 |  5.69769    |  5.84827     | 0.253052   |
|  69 | churro_2_german_extensive_2              | 1915-12-28_1 |  0.685738   |  0.36512     | 0.471829   |
|  70 | churro_2_german_extensive_2              | 1915-12-28_2 |  5.35879    |  4.29141     | 0.218212   |
|  71 | churro_2_german_extensive_2              | 1915-12-28_3 |  0.268803   |  0.0503993   | 0.956842   |
|  72 | churro_2_german_extensive_2              | 1915-12-28_4 |  2.82902    |  2.92778     | 0.384255   |
|  73 | churro_2_german_extensive_2              | 1917-12-28_1 |  0.761111   |  0.492646    | 0.624936   |
|  74 | churro_2_german_extensive_2              | 1917-12-28_2 |  0.842773   |  0.639063    | 0.563209   |
|  75 | churro_2_german_extensive_2              | 1917-12-28_3 |  0.355448   |  0.0610854   | 0.954735   |
|  76 | churro_2_german_extensive_2              | 1917-12-28_4 |  4.63909    |  4.14935     | 0.248417   |
|  77 | churro_2_german_extensive_2              | 1918-12-27_1 |  0.294971   |  0.0483887   | 0.955578   |
|  78 | churro_2_german_extensive_2              | 1918-12-27_2 |  6.03952    |  4.33805     | 0.127829   |
|  79 | churro_2_german_extensive_2              | 1918-12-27_3 |  0.453642   |  0.0771565   | 0.934948   |
|  80 | churro_2_german_extensive_2              | 1918-12-27_4 |  0.238806   |  0.0472205   | 0.95977    |
|  81 | churro_2_german_extensive_2              | 1918-12-27_5 |  0.108561   |  0.0211892   | 0.983751   |
|  82 | churro_2_german_extensive_2              | 1918-12-27_6 | 21.4103     |  4.65396     | 0.18983    |
|  83 | churro_2_german_extensive_2              | average      |  2.59321    |  1.42016     | 0.672601   |
|  84 | churro_3_english_extensive_3             | 1914-06-29_1 |  0.256007   |  0.0451189   | 0.959716   |
|  85 | churro_3_english_extensive_3             | 1914-06-29_2 |  0.55162    |  0.0982128   | 0.92442    |
|  86 | churro_3_english_extensive_3             | 1914-06-29_3 |  0.363748   |  0.0555385   | 0.958147   |
|  87 | churro_3_english_extensive_3             | 1914-06-29_4 |  0.290383   |  0.0658329   | 0.947405   |
|  88 | churro_3_english_extensive_3             | 1914-06-29_5 |  0.493706   |  0.0919942   | 0.927858   |
|  89 | churro_3_english_extensive_3             | 1914-06-29_7 |  0.249588   |  0.0793324   | 0.940185   |
|  90 | churro_3_english_extensive_3             | 1915-12-28_1 |  0.728856   |  0.403921    | 0.469562   |
|  91 | churro_3_english_extensive_3             | 1915-12-28_2 |  3.64471    |  2.45458     | 0.131703   |
|  92 | churro_3_english_extensive_3             | 1915-12-28_3 |  0.268149   |  0.0452043   | 0.958772   |
|  93 | churro_3_english_extensive_3             | 1915-12-28_4 |  3.79447    |  4.07607     | 0.30882    |
|  94 | churro_3_english_extensive_3             | 1917-12-28_1 |  0.689815   |  0.476059    | 0.724821   |
|  95 | churro_3_english_extensive_3             | 1917-12-28_2 |  0.996619   |  0.991768    | 0.397735   |
|  96 | churro_3_english_extensive_3             | 1917-12-28_3 |  0.450378   |  0.0799897   | 0.935644   |
|  97 | churro_3_english_extensive_3             | 1917-12-28_4 |  0.626926   |  0.307215    | 0.807862   |
|  98 | churro_3_english_extensive_3             | 1918-12-27_1 |  5.26596    |  4.54946     | 0.282316   |
|  99 | churro_3_english_extensive_3             | 1918-12-27_2 |  1.0247     |  1.7421      | 0.482313   |
| 100 | churro_3_english_extensive_3             | 1918-12-27_3 |  4.68079    |  6.71565     | 0.222228   |
| 101 | churro_3_english_extensive_3             | 1918-12-27_4 |  0.247015   |  0.0531231   | 0.956698   |
| 102 | churro_3_english_extensive_3             | 1918-12-27_5 |  0.168734   |  0.307501    | 0.859057   |
| 103 | churro_3_english_extensive_3             | 1918-12-27_6 |  1.61072    |  1.2608      | 0.585403   |
| 104 | churro_3_english_extensive_3             | average      |  1.32015    |  1.19497     | 0.689033   |
| 105 | churro_4_one_shot                        | 1914-06-29_1 |  0.195526   |  0.0627213   | 0.957821   |
| 106 | churro_4_one_shot                        | 1914-06-29_2 |  4.62095    |  4.13741     | 0.297995   |
| 107 | churro_4_one_shot                        | 1914-06-29_3 |  5.45993    |  4.3572      | 0.250256   |
| 108 | churro_4_one_shot                        | 1914-06-29_4 |  0.516028   |  0.316888    | 0.732514   |
| 109 | churro_4_one_shot                        | 1914-06-29_5 |  0.343357   |  0.121579    | 0.917895   |
| 110 | churro_4_one_shot                        | 1914-06-29_7 |  0.231466   |  0.0634009   | 0.951549   |
| 111 | churro_4_one_shot                        | 1915-12-28_1 |  7.07214    |  5.80825     | 0.214717   |
| 112 | churro_4_one_shot                        | 1915-12-28_2 |  5.56202    |  4.32992     | 0.216813   |
| 113 | churro_4_one_shot                        | 1915-12-28_3 |  0.555265   |  2.65046     | 0.399558   |
| 114 | churro_4_one_shot                        | 1915-12-28_4 |  5.43092    |  4.28849     | 0.0641032  |
| 115 | churro_4_one_shot                        | 1917-12-28_1 |  0.467593   |  0.439124    | 0.735414   |
| 116 | churro_4_one_shot                        | 1917-12-28_2 |  4.64074    |  3.99716     | 0.0224352  |
| 117 | churro_4_one_shot                        | 1917-12-28_3 |  0.26753    |  1.03832     | 0.629718   |
| 118 | churro_4_one_shot                        | 1917-12-28_4 |  3.76886    |  3.50324     | 0.352082   |
| 119 | churro_4_one_shot                        | 1918-12-27_1 |  5.26886    |  4.76379     | 0.270972   |
| 120 | churro_4_one_shot                        | 1918-12-27_2 |  6.12773    |  4.31212     | 0.176354   |
| 121 | churro_4_one_shot                        | 1918-12-27_3 |  4.99404    |  4.67332     | 0.284121   |
| 122 | churro_4_one_shot                        | 1918-12-27_4 |  0.157463   |  0.112237    | 0.937098   |
| 123 | churro_4_one_shot                        | 1918-12-27_5 |  0.939826   |  1.69529     | 0.338393   |
| 124 | churro_4_one_shot                        | 1918-12-27_6 | 23.12       |  4.97612     | 0.0155406  |
| 125 | churro_4_one_shot                        | average      |  3.98701    |  2.78235     | 0.438267   |
| 126 | churro_5_one_shot_s_replaced             | 1914-06-29_1 |  0.100249   |  0.0486596   | 0.972      |
| 127 | churro_5_one_shot_s_replaced             | 1914-06-29_2 |  4.48757    |  4.12502     | 0.304721   |
| 128 | churro_5_one_shot_s_replaced             | 1914-06-29_3 |  5.45993    |  4.3572      | 0.250256   |
| 129 | churro_5_one_shot_s_replaced             | 1914-06-29_4 |  0.370836   |  0.294407    | 0.754049   |
| 130 | churro_5_one_shot_s_replaced             | 1914-06-29_5 |  0.129371   |  0.0894364   | 0.951179   |
| 131 | churro_5_one_shot_s_replaced             | 1914-06-29_7 |  0.0840198  |  0.0382573   | 0.976928   |
| 132 | churro_5_one_shot_s_replaced             | 1915-12-28_1 |  7.07131    |  5.80805     | 0.21477    |
| 133 | churro_5_one_shot_s_replaced             | 1915-12-28_2 |  5.52698    |  4.32437     | 0.217779   |
| 134 | churro_5_one_shot_s_replaced             | 1915-12-28_3 |  0.551341   |  2.65        | 0.399768   |
| 135 | churro_5_one_shot_s_replaced             | 1915-12-28_4 |  5.40069    |  4.26143     | 0.0667473  |
| 136 | churro_5_one_shot_s_replaced             | 1917-12-28_1 |  0.439815   |  0.435364    | 0.739666   |
| 137 | churro_5_one_shot_s_replaced             | 1917-12-28_2 |  4.64074    |  3.99716     | 0.0224352  |
| 138 | churro_5_one_shot_s_replaced             | 1917-12-28_3 |  0.118123   |  1.01376     | 0.646798   |
| 139 | churro_5_one_shot_s_replaced             | 1917-12-28_4 |  3.74371    |  3.50015     | 0.353996   |
| 140 | churro_5_one_shot_s_replaced             | 1918-12-27_1 |  5.08027    |  4.73944     | 0.279775   |
| 141 | churro_5_one_shot_s_replaced             | 1918-12-27_2 |  6.12773    |  4.31212     | 0.17638    |
| 142 | churro_5_one_shot_s_replaced             | 1918-12-27_3 |  4.83907    |  4.65168     | 0.291411   |
| 143 | churro_5_one_shot_s_replaced             | 1918-12-27_4 |  0.15597    |  0.111884    | 0.937466   |
| 144 | churro_5_one_shot_s_replaced             | 1918-12-27_5 |  0.920596   |  1.68927     | 0.339087   |
| 145 | churro_5_one_shot_s_replaced             | 1918-12-27_6 | 23.12       |  4.97612     | 0.0155406  |
| 146 | churro_5_one_shot_s_replaced             | average      |  3.91842    |  2.77119     | 0.445538   |
| 147 | churro_6_two_shot                        | 1914-06-29_1 |  1          |  0.967122    | 0.0280839  |
| 148 | churro_6_two_shot                        | 1914-06-29_2 |  2.46873    |  1.70958     | 0.0593512  |
| 149 | churro_6_two_shot                        | 1914-06-29_3 | 10.4901     |  2.97189     | 0.172401   |
| 150 | churro_6_two_shot                        | 1914-06-29_4 |  0.529227   |  0.292181    | 0.794257   |
| 151 | churro_6_two_shot                        | 1914-06-29_5 |  1.01958    |  0.649416    | 0.692972   |
| 152 | churro_6_two_shot                        | 1914-06-29_7 |  1.44893    |  1.19031     | 0.329041   |
| 153 | churro_6_two_shot                        | 1915-12-28_1 |  3.90216    |  5.37949     | 0.0156619  |
| 154 | churro_6_two_shot                        | 1915-12-28_2 |  3.79537    |  3.63055     | 0.202086   |
| 155 | churro_6_two_shot                        | 1915-12-28_3 | 11.0844     |  3.04047     | 0.171017   |
| 156 | churro_6_two_shot                        | 1915-12-28_4 | 16.2988     |  3.71478     | 0.100783   |
| 157 | churro_6_two_shot                        | 1917-12-28_1 |  0.490741   |  0.407829    | 0.671701   |
| 158 | churro_6_two_shot                        | 1917-12-28_2 |  6.22992    |  4.95698     | 0.040111   |
| 159 | churro_6_two_shot                        | 1917-12-28_3 |  4.16828    |  3.51492     | 0.0696682  |
| 160 | churro_6_two_shot                        | 1917-12-28_4 |  1.05028    |  0.812494    | 0.307404   |
| 161 | churro_6_two_shot                        | 1918-12-27_1 |  5.30174    |  5.68215     | 0.16531    |
| 162 | churro_6_two_shot                        | 1918-12-27_2 |  4.50247    |  3.73104     | 0.214903   |
| 163 | churro_6_two_shot                        | 1918-12-27_3 |  4.92715    |  4.70519     | 0.0339146  |
| 164 | churro_6_two_shot                        | 1918-12-27_4 |  5.01045    |  4.91084     | 0.221828   |
| 165 | churro_6_two_shot                        | 1918-12-27_5 |  1.11849    |  0.867806    | 0.545977   |
| 166 | churro_6_two_shot                        | 1918-12-27_6 |  9.26923    |  7.78176     | 0.0893103  |
| 167 | churro_6_two_shot                        | average      |  4.7053     |  3.04584     | 0.246289   |
| 168 | churro_7_two_shot_prompts_adapted        | 1914-06-29_1 | 13.3471     |  3.74122     | 0.188567   |
| 169 | churro_7_two_shot_prompts_adapted        | 1914-06-29_2 | 12.3067     |  2.99562     | 0.287675   |
| 170 | churro_7_two_shot_prompts_adapted        | 1914-06-29_3 |  4.91677    |  3.91719     | 0.206038   |
| 171 | churro_7_two_shot_prompts_adapted        | 1914-06-29_4 |  0.47643    |  0.27415     | 0.786714   |
| 172 | churro_7_two_shot_prompts_adapted        | 1914-06-29_5 |  5.4014     |  4.65735     | 0.0828377  |
| 173 | churro_7_two_shot_prompts_adapted        | 1914-06-29_7 |  5.77512    |  5.35136     | 0.0442905  |
| 174 | churro_7_two_shot_prompts_adapted        | 1915-12-28_1 |  1.07463    |  0.709916    | 0.638014   |
| 175 | churro_7_two_shot_prompts_adapted        | 1915-12-28_2 |  4.94324    |  3.99539     | 0.110532   |
| 176 | churro_7_two_shot_prompts_adapted        | 1915-12-28_3 |  3.97776    |  3.38381     | 0.17587    |
| 177 | churro_7_two_shot_prompts_adapted        | 1915-12-28_4 |  0.772021   |  0.552817    | 0.421942   |
| 178 | churro_7_two_shot_prompts_adapted        | 1917-12-28_1 |  4.47685    |  4.16245     | 0.214631   |
| 179 | churro_7_two_shot_prompts_adapted        | 1917-12-28_2 |  0.800507   |  0.665229    | 0.290938   |
| 180 | churro_7_two_shot_prompts_adapted        | 1917-12-28_3 |  3.04531    |  2.81057     | 0.147818   |
| 181 | churro_7_two_shot_prompts_adapted        | 1917-12-28_4 |  0.604217   |  0.35138     | 0.736386   |
| 182 | churro_7_two_shot_prompts_adapted        | 1918-12-27_1 |  0.37234    |  0.0959591   | 0.933704   |
| 183 | churro_7_two_shot_prompts_adapted        | 1918-12-27_2 |  6.06634    |  4.66626     | 0.0212083  |
| 184 | churro_7_two_shot_prompts_adapted        | 1918-12-27_3 |  4.35232    |  3.99257     | 0.103496   |
| 185 | churro_7_two_shot_prompts_adapted        | 1918-12-27_4 |  0.638806   |  0.378645    | 0.690599   |
| 186 | churro_7_two_shot_prompts_adapted        | 1918-12-27_5 |  5.67308    |  4.60613     | 0.281807   |
| 187 | churro_7_two_shot_prompts_adapted        | 1918-12-27_6 | 13.9207     |  8.48869     | 0.0084385  |
| 188 | churro_7_two_shot_prompts_adapted        | average      |  4.64709    |  2.98984     | 0.318575   |
| 189 | churro_8_two_shot_zero_temperature       | 1914-06-29_1 |  0.705054   |  2.24401     | 0.274152   |
| 190 | churro_8_two_shot_zero_temperature       | 1914-06-29_2 | 12.6534     |  2.98247     | 0.310032   |
| 191 | churro_8_two_shot_zero_temperature       | 1914-06-29_3 |  0.885327   |  0.662237    | 0.440485   |
| 192 | churro_8_two_shot_zero_temperature       | 1914-06-29_4 |  0.664991   |  1.68304     | 0.305335   |
| 193 | churro_8_two_shot_zero_temperature       | 1914-06-29_5 |  4.82378    |  4.54011     | 0.273494   |
| 194 | churro_8_two_shot_zero_temperature       | 1914-06-29_7 |  6.10873    |  5.98764     | 0.0652144  |
| 195 | churro_8_two_shot_zero_temperature       | 1915-12-28_1 |  5.46683    |  5.87672     | 0.192247   |
| 196 | churro_8_two_shot_zero_temperature       | 1915-12-28_2 |  5.5494     |  4.5362      | 0.108235   |
| 197 | churro_8_two_shot_zero_temperature       | 1915-12-28_3 |  3.85415    |  3.58696     | 0.305356   |
| 198 | churro_8_two_shot_zero_temperature       | 1915-12-28_4 | 14.6287     |  3.68811     | 0.247563   |
| 199 | churro_8_two_shot_zero_temperature       | 1917-12-28_1 |  7.19537    |  6.34247     | 0.0459047  |
| 200 | churro_8_two_shot_zero_temperature       | 1917-12-28_2 | 15.2122     |  5.46629     | 0.177915   |
| 201 | churro_8_two_shot_zero_temperature       | 1917-12-28_3 |  3.56203    |  2.91249     | 0.175989   |
| 202 | churro_8_two_shot_zero_temperature       | 1917-12-28_4 | 15.4477     |  3.66421     | 0.117972   |
| 203 | churro_8_two_shot_zero_temperature       | 1918-12-27_1 |  3.51838    |  4.35407     | 0.0120488  |
| 204 | churro_8_two_shot_zero_temperature       | 1918-12-27_2 |  4.4573     |  3.93701     | 0.222349   |
| 205 | churro_8_two_shot_zero_temperature       | 1918-12-27_3 |  3.92848    |  3.6353      | 0.141568   |
| 206 | churro_8_two_shot_zero_temperature       | 1918-12-27_4 |  3.37239    |  3.07048     | 0.281663   |
| 207 | churro_8_two_shot_zero_temperature       | 1918-12-27_5 |  5.0794     |  3.92353     | 0.150843   |
| 208 | churro_8_two_shot_zero_temperature       | 1918-12-27_6 | 21.662      |  4.67162     | 0.180373   |
| 209 | churro_8_two_shot_zero_temperature       | average      |  6.93878    |  3.88825     | 0.201437   |
| 210 | churro_9_two_shot_zero_temperature       | 1914-06-29_1 |  0.705054   |  2.24401     | 0.274152   |
| 211 | churro_9_two_shot_zero_temperature       | 1914-06-29_2 | 12.6534     |  2.98247     | 0.310032   |
| 212 | churro_9_two_shot_zero_temperature       | 1914-06-29_3 |  0.885327   |  0.662237    | 0.440485   |
| 213 | churro_9_two_shot_zero_temperature       | 1914-06-29_4 |  0.664991   |  1.68304     | 0.305335   |
| 214 | churro_9_two_shot_zero_temperature       | 1914-06-29_5 |  4.82378    |  4.54011     | 0.273494   |
| 215 | churro_9_two_shot_zero_temperature       | 1914-06-29_7 |  6.10873    |  5.98764     | 0.0652144  |
| 216 | churro_9_two_shot_zero_temperature       | 1915-12-28_1 |  5.46683    |  5.87672     | 0.192247   |
| 217 | churro_9_two_shot_zero_temperature       | 1915-12-28_2 |  5.5494     |  4.5362      | 0.108235   |
| 218 | churro_9_two_shot_zero_temperature       | 1915-12-28_3 |  3.85415    |  3.58696     | 0.305356   |
| 219 | churro_9_two_shot_zero_temperature       | 1915-12-28_4 | 14.6287     |  3.68811     | 0.247563   |
| 220 | churro_9_two_shot_zero_temperature       | 1917-12-28_1 |  7.19537    |  6.34247     | 0.0459047  |
| 221 | churro_9_two_shot_zero_temperature       | 1917-12-28_2 | 15.2122     |  5.46629     | 0.177915   |
| 222 | churro_9_two_shot_zero_temperature       | 1917-12-28_3 |  3.56203    |  2.91249     | 0.175989   |
| 223 | churro_9_two_shot_zero_temperature       | 1917-12-28_4 | 15.4477     |  3.66421     | 0.117972   |
| 224 | churro_9_two_shot_zero_temperature       | 1918-12-27_1 |  3.51838    |  4.35407     | 0.0120488  |
| 225 | churro_9_two_shot_zero_temperature       | 1918-12-27_2 |  4.4573     |  3.93701     | 0.222349   |
| 226 | churro_9_two_shot_zero_temperature       | 1918-12-27_3 |  3.92848    |  3.6353      | 0.141568   |
| 227 | churro_9_two_shot_zero_temperature       | 1918-12-27_4 |  3.37239    |  3.07048     | 0.281663   |
| 228 | churro_9_two_shot_zero_temperature       | 1918-12-27_5 |  5.0794     |  3.92353     | 0.150843   |
| 229 | churro_9_two_shot_zero_temperature       | 1918-12-27_6 | 21.662      |  4.67162     | 0.180373   |
| 230 | churro_9_two_shot_zero_temperature       | average      |  6.93878    |  3.88825     | 0.201437   |
| 231 | deepseek_ocr_1_default                   | 1914-06-29_1 |  0.815244   |  0.207284    | 0.855559   |
| 232 | deepseek_ocr_1_default                   | 1914-06-29_2 |  0.583271   |  0.125358    | 0.905741   |
| 233 | deepseek_ocr_1_default                   | 1914-06-29_3 |  0.603576   |  0.127823    | 0.908716   |
| 234 | deepseek_ocr_1_default                   | 1914-06-29_4 |  0.461974   |  0.0794905   | 0.935043   |
| 235 | deepseek_ocr_1_default                   | 1914-06-29_5 |  0.66993    |  0.127121    | 0.905066   |
| 236 | deepseek_ocr_1_default                   | 1914-06-29_7 |  0.526359   |  0.163       | 0.883      |
| 237 | deepseek_ocr_1_default                   | 1915-12-28_1 |  0.890547   |  0.187538    | 0.856519   |
| 238 | deepseek_ocr_1_default                   | 1915-12-28_2 |  1.66013    |  0.585212    | 0.563911   |
| 239 | deepseek_ocr_1_default                   | 1915-12-28_3 |  0.545455   |  0.123905    | 0.90059    |
| 240 | deepseek_ocr_1_default                   | 1915-12-28_4 |  3.70725    |  0.560327    | 0.509446   |
| 241 | deepseek_ocr_1_default                   | 1917-12-28_1 |  1.27963    |  0.570386    | 0.602334   |
| 242 | deepseek_ocr_1_default                   | 1917-12-28_2 |  0.627219   |  0.394159    | 0.691943   |
| 243 | deepseek_ocr_1_default                   | 1917-12-28_3 |  0.68123    |  0.344329    | 0.742817   |
| 244 | deepseek_ocr_1_default                   | 1917-12-28_4 |  2.98865    |  1.27186     | 0.123346   |
| 245 | deepseek_ocr_1_default                   | 1918-12-27_1 |  0.775629   |  0.202762    | 0.837181   |
| 246 | deepseek_ocr_1_default                   | 1918-12-27_2 |  0.880028   |  0.599122    | 0.34967    |
| 247 | deepseek_ocr_1_default                   | 1918-12-27_3 |  0.813245   |  0.386981    | 0.619905   |
| 248 | deepseek_ocr_1_default                   | 1918-12-27_4 |  0.909701   |  0.183949    | 0.848251   |
| 249 | deepseek_ocr_1_default                   | 1918-12-27_5 |  2.67308    |  1.12963     | 0.336905   |
| 250 | deepseek_ocr_1_default                   | 1918-12-27_6 |  0.777389   |  0.417937    | 0.621929   |
| 251 | deepseek_ocr_1_default                   | average      |  1.14348    |  0.389409    | 0.699894   |
| 252 | deepseek_ocr_2_german_extensive_2        | 1914-06-29_1 |  1          |  1           | 0          |
| 253 | deepseek_ocr_2_german_extensive_2        | 1914-06-29_2 |  3.26225    |  1.88029     | 0.243739   |
| 254 | deepseek_ocr_2_german_extensive_2        | 1914-06-29_3 |  0.493218   |  0.101475    | 0.917959   |
| 255 | deepseek_ocr_2_german_extensive_2        | 1914-06-29_4 |  0.583909   |  0.180618    | 0.883448   |
| 256 | deepseek_ocr_2_german_extensive_2        | 1914-06-29_5 |  0.525874   |  0.113394    | 0.912624   |
| 257 | deepseek_ocr_2_german_extensive_2        | 1914-06-29_7 |  0.546952   |  0.21513     | 0.844804   |
| 258 | deepseek_ocr_2_german_extensive_2        | 1915-12-28_1 |  1          |  1           | 0          |
| 259 | deepseek_ocr_2_german_extensive_2        | 1915-12-28_2 |  1.90399    |  0.596141    | 0.552754   |
| 260 | deepseek_ocr_2_german_extensive_2        | 1915-12-28_3 |  1.73316    |  0.381019    | 0.737336   |
| 261 | deepseek_ocr_2_german_extensive_2        | 1915-12-28_4 |  3.88428    |  0.586904    | 0.520543   |
| 262 | deepseek_ocr_2_german_extensive_2        | 1917-12-28_1 |  1          |  1           | 0          |
| 263 | deepseek_ocr_2_german_extensive_2        | 1917-12-28_2 |  0.78022    |  0.4559      | 0.587285   |
| 264 | deepseek_ocr_2_german_extensive_2        | 1917-12-28_3 |  2.35545    |  0.727816    | 0.285069   |
| 265 | deepseek_ocr_2_german_extensive_2        | 1917-12-28_4 |  1.58962    |  1.27564     | 0.278401   |
| 266 | deepseek_ocr_2_german_extensive_2        | 1918-12-27_1 |  1          |  1           | 0          |
| 267 | deepseek_ocr_2_german_extensive_2        | 1918-12-27_2 |  1.30416    |  0.749329    | 0.055926   |
| 268 | deepseek_ocr_2_german_extensive_2        | 1918-12-27_3 |  0.954305   |  0.716214    | 0.102545   |
| 269 | deepseek_ocr_2_german_extensive_2        | 1918-12-27_4 |  1          |  1           | 0          |
| 270 | deepseek_ocr_2_german_extensive_2        | 1918-12-27_5 |  1.52109    |  0.737884    | 0.0880882  |
| 271 | deepseek_ocr_2_german_extensive_2        | 1918-12-27_6 |  2.00699    |  1.44944     | 0.337644   |
| 272 | deepseek_ocr_2_german_extensive_2        | average      |  1.42227    |  0.75836     | 0.367408   |
| 273 | deepseek_ocr_3_english_extensive_2       | 1914-06-29_1 |  1.15493    |  0.741426    | 0.0709268  |
| 274 | deepseek_ocr_3_english_extensive_2       | 1914-06-29_2 |  2.49058    |  1.41873     | 0.456818   |
| 275 | deepseek_ocr_3_english_extensive_2       | 1914-06-29_3 |  0.766338   |  0.307344    | 0.832255   |
| 276 | deepseek_ocr_3_english_extensive_2       | 1914-06-29_4 |  0.522942   |  0.123456    | 0.912195   |
| 277 | deepseek_ocr_3_english_extensive_2       | 1914-06-29_5 |  4.55175    |  2.27334     | 0.0315592  |
| 278 | deepseek_ocr_3_english_extensive_2       | 1914-06-29_7 |  0.744646   |  0.315054    | 0.818439   |
| 279 | deepseek_ocr_3_english_extensive_2       | 1915-12-28_1 |  0.997512   |  0.966537    | 0.0341304  |
| 280 | deepseek_ocr_3_english_extensive_2       | 1915-12-28_2 |  1.66643    |  0.588712    | 0.562515   |
| 281 | deepseek_ocr_3_english_extensive_2       | 1915-12-28_3 |  1.51799    |  0.927037    | 0.535906   |
| 282 | deepseek_ocr_3_english_extensive_2       | 1915-12-28_4 |  4.04404    |  0.572075    | 0.512285   |
| 283 | deepseek_ocr_3_english_extensive_2       | 1917-12-28_1 |  5.00185    |  2.98961     | 0.0316029  |
| 284 | deepseek_ocr_3_english_extensive_2       | 1917-12-28_2 |  4.32122    |  1.43953     | 0.408446   |
| 285 | deepseek_ocr_3_english_extensive_2       | 1917-12-28_3 |  0.650485   |  0.290766    | 0.702167   |
| 286 | deepseek_ocr_3_english_extensive_2       | 1917-12-28_4 |  2.14112    |  1.0092      | 0.228306   |
| 287 | deepseek_ocr_3_english_extensive_2       | 1918-12-27_1 |  1.23694    |  0.223223    | 0.832773   |
| 288 | deepseek_ocr_3_english_extensive_2       | 1918-12-27_2 |  0.89626    |  0.728521    | 0.410984   |
| 289 | deepseek_ocr_3_english_extensive_2       | 1918-12-27_3 |  3.02848    |  0.579952    | 0.545857   |
| 290 | deepseek_ocr_3_english_extensive_2       | 1918-12-27_4 |  2.44776    |  0.417056    | 0.630295   |
| 291 | deepseek_ocr_3_english_extensive_2       | 1918-12-27_5 |  2.29342    |  0.703937    | 0.24962    |
| 292 | deepseek_ocr_3_english_extensive_2       | 1918-12-27_6 |  0.98951    |  0.897993    | 0.0760943  |
| 293 | deepseek_ocr_3_english_extensive_2       | average      |  2.07321    |  0.875675    | 0.444159   |
| 294 | dots_ocr_1_default                       | 1914-06-29_1 |  0.169014   |  0.0246839   | 0.980757   |
| 295 | dots_ocr_1_default                       | 1914-06-29_2 |  0.363979   |  0.0427415   | 0.749493   |
| 296 | dots_ocr_1_default                       | 1914-06-29_3 |  0.176942   |  0.0185896   | 0.984184   |
| 297 | dots_ocr_1_default                       | 1914-06-29_4 |  0.314896   |  0.0319957   | 0.973942   |
| 298 | dots_ocr_1_default                       | 1914-06-29_5 |  0.330769   |  0.0386222   | 0.970483   |
| 299 | dots_ocr_1_default                       | 1914-06-29_7 |  0.297364   |  0.0303457   | 0.974981   |
| 300 | dots_ocr_1_default                       | 1915-12-28_2 |  0.683952   |  0.515967    | 0.609749   |
| 301 | dots_ocr_1_default                       | 1915-12-28_3 |  0.168738   |  0.0211677   | 0.982243   |
| 302 | dots_ocr_1_default                       | 1915-12-28_4 |  0.402418   |  0.0805007   | 0.944396   |
| 303 | dots_ocr_1_default                       | 1917-12-28_1 |  0.350926   |  0.0472188   | 0.963049   |
| 304 | dots_ocr_1_default                       | 1917-12-28_2 |  0.764159   |  0.453156    | 0.667783   |
| 305 | dots_ocr_1_default                       | 1917-12-28_3 |  0.324164   |  0.0344007   | 0.970282   |
| 306 | dots_ocr_1_default                       | 1917-12-28_4 |  0.42498    |  0.195835    | 0.885436   |
| 307 | dots_ocr_1_default                       | 1918-12-27_1 |  0.377176   |  0.0477749   | 0.963655   |
| 308 | dots_ocr_1_default                       | 1918-12-27_2 |  0.372618   |  0.0463302   | 0.963461   |
| 309 | dots_ocr_1_default                       | 1918-12-27_3 |  0.339735   |  0.0449681   | 0.964603   |
| 310 | dots_ocr_1_default                       | 1918-12-27_4 |  0.368657   |  0.057528    | 0.960182   |
| 311 | dots_ocr_1_default                       | 1918-12-27_5 |  0.383375   |  0.0501503   | 0.959637   |
| 312 | dots_ocr_1_default                       | 1918-12-27_6 |  0.518648   |  0.335747    | 0.793388   |
| 313 | dots_ocr_1_default                       | average      |  0.375395   |  0.111459    | 0.908511   |
| 314 | dots_ocr_3_default                       | 1914-06-29_1 |  0.261806   |  0.0911482   | 0.946566   |
| 315 | dots_ocr_3_default                       | 1914-06-29_2 |  0.406179   |  0.0444276   | 0.74979    |
| 316 | dots_ocr_3_default                       | 1914-06-29_3 |  0.251541   |  0.0579966   | 0.964511   |
| 317 | dots_ocr_3_default                       | 1914-06-29_4 |  0.329353   |  0.0324561   | 0.973716   |
| 318 | dots_ocr_3_default                       | 1914-06-29_5 |  0.394406   |  0.0821042   | 0.948318   |
| 319 | dots_ocr_3_default                       | 1914-06-29_7 |  0.308896   |  0.0387992   | 0.970842   |
| 320 | dots_ocr_3_default                       | 1915-12-28_1 |  1.00746    |  0.710532    | 0.67722    |
| 321 | dots_ocr_3_default                       | 1915-12-28_2 |  0.711282   |  0.522029    | 0.605594   |
| 322 | dots_ocr_3_default                       | 1915-12-28_3 |  0.360366   |  0.0451268   | 0.966623   |
| 323 | dots_ocr_3_default                       | 1915-12-28_4 |  4.58463    |  0.985364    | 0.639641   |
| 324 | dots_ocr_3_default                       | 1917-12-28_1 |  0.714815   |  0.418445    | 0.464886   |
| 325 | dots_ocr_3_default                       | 1917-12-28_2 |  2.67794    |  2.09026     | 0.0393549  |
| 326 | dots_ocr_3_default                       | 1917-12-28_3 |  0.334951   |  0.0374228   | 0.968922   |
| 327 | dots_ocr_3_default                       | 1917-12-28_4 |  0.539335   |  0.174818    | 0.891038   |
| 328 | dots_ocr_3_default                       | 1918-12-27_1 |  1.47776    |  1.73903     | 0.510826   |
| 329 | dots_ocr_3_default                       | 1918-12-27_2 |  0.405787   |  0.0516947   | 0.961521   |
| 330 | dots_ocr_3_default                       | 1918-12-27_3 |  0.362252   |  0.0485623   | 0.963858   |
| 331 | dots_ocr_3_default                       | 1918-12-27_4 |  0.386567   |  0.0486301   | 0.965678   |
| 332 | dots_ocr_3_default                       | 1918-12-27_5 |  0.400124   |  0.0542562   | 0.958533   |
| 333 | dots_ocr_3_default                       | 1918-12-27_6 |  8.03613    |  1.68089     | 0.336787   |
| 334 | dots_ocr_3_default                       | average      |  1.19758    |  0.4477      | 0.775211   |
| 335 | dots_ocr_4_default                       | 1914-06-29_1 |  0.22121    |  0.0783005   | 0.952744   |
| 336 | dots_ocr_4_default                       | 1914-06-29_2 |  0.364732   |  0.0425729   | 0.749683   |
| 337 | dots_ocr_4_default                       | 1914-06-29_3 |  0.175092   |  0.0194346   | 0.983414   |
| 338 | dots_ocr_4_default                       | 1914-06-29_4 |  0.315525   |  0.0321492   | 0.973827   |
| 339 | dots_ocr_4_default                       | 1914-06-29_5 |  0.332168   |  0.0387075   | 0.970439   |
| 340 | dots_ocr_4_default                       | 1914-06-29_7 |  0.537891   |  0.369026    | 0.767751   |
| 341 | dots_ocr_4_default                       | 1915-12-28_2 |  0.688157   |  0.520833    | 0.606607   |
| 342 | dots_ocr_4_default                       | 1915-12-28_3 |  0.169392   |  0.0281461   | 0.978773   |
| 343 | dots_ocr_4_default                       | 1915-12-28_4 |  0.405872   |  0.0859894   | 0.941663   |
| 344 | dots_ocr_4_default                       | 1917-12-28_1 |  0.392593   |  0.0989716   | 0.938645   |
| 345 | dots_ocr_4_default                       | 1917-12-28_2 |  0.765004   |  0.460212    | 0.657528   |
| 346 | dots_ocr_4_default                       | 1917-12-28_3 |  0.345739   |  0.0376157   | 0.967144   |
| 347 | dots_ocr_4_default                       | 1917-12-28_4 |  0.435523   |  0.206199    | 0.880985   |
| 348 | dots_ocr_4_default                       | 1918-12-27_1 |  0.412959   |  0.0875703   | 0.943946   |
| 349 | dots_ocr_4_default                       | 1918-12-27_2 |  0.375441   |  0.0494188   | 0.962087   |
| 350 | dots_ocr_4_default                       | 1918-12-27_3 |  0.348344   |  0.0478435   | 0.963207   |
| 351 | dots_ocr_4_default                       | 1918-12-27_4 |  0.36194    |  0.0471324   | 0.965334   |
| 352 | dots_ocr_4_default                       | 1918-12-27_5 |  0.386476   |  0.0505169   | 0.958515   |
| 353 | dots_ocr_4_default                       | 1918-12-27_6 |  0.481352   |  0.345401    | 0.81918    |
| 354 | dots_ocr_4_default                       | average      |  0.395548   |  0.139265    | 0.893762   |
| 355 | dots_ocr_6_english_extensive             | 1914-06-29_1 |  1          |  1           | 0          |
| 356 | dots_ocr_6_english_extensive             | 1914-06-29_2 |  1          |  1           | 0          |
| 357 | dots_ocr_6_english_extensive             | 1914-06-29_3 |  0.250308   |  0.0858043   | 0.948473   |
| 358 | dots_ocr_6_english_extensive             | 1914-06-29_4 |  0.0911376  |  0.0117394   | 0.990112   |
| 359 | dots_ocr_6_english_extensive             | 1914-06-29_5 |  0.393706   |  0.0812516   | 0.948919   |
| 360 | dots_ocr_6_english_extensive             | 1914-06-29_7 |  0.512356   |  0.328492    | 0.797508   |
| 361 | dots_ocr_6_english_extensive             | 1915-12-28_1 |  2.58789    |  1.93051     | 0.42068    |
| 362 | dots_ocr_6_english_extensive             | 1915-12-28_2 |  0.717589   |  0.522199    | 0.605174   |
| 363 | dots_ocr_6_english_extensive             | 1915-12-28_3 |  0.177894   |  0.0241917   | 0.981474   |
| 364 | dots_ocr_6_english_extensive             | 1915-12-28_4 |  5.38083    |  1.42937     | 0.46491    |
| 365 | dots_ocr_6_english_extensive             | 1917-12-28_1 |  0.928704   |  0.658963    | 0.353409   |
| 366 | dots_ocr_6_english_extensive             | 1917-12-28_2 |  1.93491    |  2.08928     | 0.0100266  |
| 367 | dots_ocr_6_english_extensive             | 1917-12-28_3 |  1.26645    |  0.838606    | 0.679016   |
| 368 | dots_ocr_6_english_extensive             | 1917-12-28_4 |  5.85645    |  1.3199      | 0.253474   |
| 369 | dots_ocr_6_english_extensive             | 1918-12-27_1 |  2.75629    |  2.0356      | 0.317725   |
| 370 | dots_ocr_6_english_extensive             | 1918-12-27_2 |  0.160198   |  0.0332439   | 0.976297   |
| 371 | dots_ocr_6_english_extensive             | 1918-12-27_3 |  0.147682   |  0.0379393   | 0.974624   |
| 372 | dots_ocr_6_english_extensive             | 1918-12-27_4 |  0.743284   |  0.450533    | 0.588584   |
| 373 | dots_ocr_6_english_extensive             | 1918-12-27_5 |  0.870347   |  0.668304    | 0.413298   |
| 374 | dots_ocr_6_english_extensive             | 1918-12-27_6 |  8.02564    |  1.68407     | 0.33527    |
| 375 | dots_ocr_6_english_extensive             | average      |  1.74008    |  0.8115      | 0.552949   |
| 376 | dots_ocr_7_german_extensive_2            | 1914-06-29_1 |  0.247722   |  0.0804249   | 0.951428   |
| 377 | dots_ocr_7_german_extensive_2            | 1914-06-29_2 |  0.406933   |  0.0448491   | 0.74959    |
| 378 | dots_ocr_7_german_extensive_2            | 1914-06-29_3 |  0.329223   |  0.0291135   | 0.973868   |
| 379 | dots_ocr_7_german_extensive_2            | 1914-06-29_4 |  0.329353   |  0.0323793   | 0.973755   |
| 380 | dots_ocr_7_german_extensive_2            | 1914-06-29_5 |  0.395804   |  0.0819337   | 0.948525   |
| 381 | dots_ocr_7_german_extensive_2            | 1914-06-29_7 |  0.311367   |  0.0393411   | 0.970402   |
| 382 | dots_ocr_7_german_extensive_2            | 1915-12-28_1 |  0.994196   |  0.709095    | 0.678387   |
| 383 | dots_ocr_7_german_extensive_2            | 1915-12-28_2 |  0.853539   |  0.52792     | 0.62589    |
| 384 | dots_ocr_7_german_extensive_2            | 1915-12-28_3 |  0.156965   |  0.0222532   | 0.983581   |
| 385 | dots_ocr_7_german_extensive_2            | 1915-12-28_4 |  3.28584    |  2.53808     | 0.0149629  |
| 386 | dots_ocr_7_german_extensive_2            | 1917-12-28_1 |  3.00278    |  2.60655     | 0.0158535  |
| 387 | dots_ocr_7_german_extensive_2            | 1917-12-28_2 |  0.742181   |  0.651901    | 0.407204   |
| 388 | dots_ocr_7_german_extensive_2            | 1917-12-28_3 |  0.380798   |  0.0766461   | 0.947396   |
| 389 | dots_ocr_7_german_extensive_2            | 1917-12-28_4 |  5.70154    |  1.2584      | 0.278823   |
| 390 | dots_ocr_7_german_extensive_2            | 1918-12-27_1 |  0.996132   |  0.994987    | 0.00561388 |
| 391 | dots_ocr_7_german_extensive_2            | 1918-12-27_2 |  0.39379    |  0.0516134   | 0.961277   |
| 392 | dots_ocr_7_german_extensive_2            | 1918-12-27_3 |  0.364238   |  0.046885    | 0.964995   |
| 393 | dots_ocr_7_german_extensive_2            | 1918-12-27_4 |  0.387313   |  0.0475729   | 0.966511   |
| 394 | dots_ocr_7_german_extensive_2            | 1918-12-27_5 |  0.584367   |  0.371508    | 0.764633   |
| 395 | dots_ocr_7_german_extensive_2            | 1918-12-27_6 |  8.05478    |  1.68966     | 0.333866   |
| 396 | dots_ocr_7_german_extensive_2            | average      |  1.39594    |  0.595056    | 0.675828   |
| 397 | dots_ocr_8_one_shot                      | 1914-06-29_1 |  0.246893   |  0.0813354   | 0.950922   |
| 398 | dots_ocr_8_one_shot                      | 1914-06-29_2 |  0.392615   |  0.0371775   | 0.752352   |
| 399 | dots_ocr_8_one_shot                      | 1914-06-29_3 |  0.197904   |  0.0224305   | 0.981988   |
| 400 | dots_ocr_8_one_shot                      | 1914-06-29_4 |  0.089252   |  0.011586    | 0.990343   |
| 401 | dots_ocr_8_one_shot                      | 1914-06-29_5 |  0.415385   |  0.0770739   | 0.947904   |
| 402 | dots_ocr_8_one_shot                      | 1914-06-29_7 |  0.248764   |  0.0548391   | 0.955722   |
| 403 | dots_ocr_8_one_shot                      | 1915-12-28_1 |  0.450249   |  0.377951    | 0.800907   |
| 404 | dots_ocr_8_one_shot                      | 1915-12-28_2 |  0.709881   |  0.522114    | 0.604868   |
| 405 | dots_ocr_8_one_shot                      | 1915-12-28_3 |  0.125572   |  0.32085     | 0.8567     |
| 406 | dots_ocr_8_one_shot                      | 1915-12-28_4 |  4.26166    |  0.943765    | 0.65138    |
| 407 | dots_ocr_8_one_shot                      | 1917-12-28_1 |  0.226852   |  0.0793984   | 0.954894   |
| 408 | dots_ocr_8_one_shot                      | 1917-12-28_2 |  0.612849   |  0.453352    | 0.666699   |
| 409 | dots_ocr_8_one_shot                      | 1917-12-28_3 |  0.710356   |  0.455183    | 0.68332    |
| 410 | dots_ocr_8_one_shot                      | 1917-12-28_4 |  0.553122   |  0.289685    | 0.835604   |
| 411 | dots_ocr_8_one_shot                      | 1918-12-27_1 |  2.61219    |  1.93678     | 0.484045   |
| 412 | dots_ocr_8_one_shot                      | 1918-12-27_2 |  0.390967   |  0.0499065   | 0.962803   |
| 413 | dots_ocr_8_one_shot                      | 1918-12-27_3 |  0.141722   |  0.0275559   | 0.979491   |
| 414 | dots_ocr_8_one_shot                      | 1918-12-27_4 |  0.144776   |  0.0230817   | 0.983599   |
| 415 | dots_ocr_8_one_shot                      | 1918-12-27_5 |  0.439826   |  0.262556    | 0.873166   |
| 416 | dots_ocr_8_one_shot                      | 1918-12-27_6 |  7.79604    |  1.64825     | 0.34252    |
| 417 | dots_ocr_8_one_shot                      | average      |  1.03834    |  0.383743    | 0.812961   |
| 418 | dots_ocr_9_three_shot                    | 1914-06-29_1 |  1.76139    |  1.4867      | 0.51928    |
| 419 | dots_ocr_9_three_shot                    | 1914-06-29_2 |  0.392615   |  0.0359973   | 0.753037   |
| 420 | dots_ocr_9_three_shot                    | 1914-06-29_3 |  0.0758323  |  0.0111384   | 0.99094    |
| 421 | dots_ocr_9_three_shot                    | 1914-06-29_4 |  0.105594   |  0.0250902   | 0.979895   |
| 422 | dots_ocr_9_three_shot                    | 1914-06-29_5 |  0.175524   |  0.0725552   | 0.957182   |
| 423 | dots_ocr_9_three_shot                    | 1914-06-29_7 |  0.227348   |  0.60052     | 0.757934   |
| 424 | dots_ocr_9_three_shot                    | 1915-12-28_1 |  2.35821    |  1.97783     | 0.331951   |
| 425 | dots_ocr_9_three_shot                    | 1915-12-28_2 |  1.9047     |  1.50726     | 0.0590271  |
| 426 | dots_ocr_9_three_shot                    | 1915-12-28_3 |  2.65468    |  1.65969     | 0.0133414  |
| 427 | dots_ocr_9_three_shot                    | 1915-12-28_4 |  1.52159    |  1.49812     | 0.189929   |
| 428 | dots_ocr_9_three_shot                    | 1917-12-28_1 |  2.37778    |  2.13768     | 0.356999   |
| 429 | dots_ocr_9_three_shot                    | 1917-12-28_2 |  3.31868    |  1.95913     | 0.0241246  |
| 430 | dots_ocr_9_three_shot                    | 1917-12-28_3 |  1.53398    |  1.0299      | 0.165712   |
| 431 | dots_ocr_9_three_shot                    | 1917-12-28_4 |  5.60422    |  1.2555      | 0.273911   |
| 432 | dots_ocr_9_three_shot                    | 1918-12-27_1 |  1.29304    |  0.901688    | 0.0163512  |
| 433 | dots_ocr_9_three_shot                    | 1918-12-27_2 |  0.386733   |  0.0539706   | 0.960985   |
| 434 | dots_ocr_9_three_shot                    | 1918-12-27_3 |  1.00331    |  0.765016    | 0.709259   |
| 435 | dots_ocr_9_three_shot                    | 1918-12-27_4 |  0.996269   |  1.20712     | 0.0167432  |
| 436 | dots_ocr_9_three_shot                    | 1918-12-27_5 |  0.691067   |  0.728866    | 0.721003   |
| 437 | dots_ocr_9_three_shot                    | 1918-12-27_6 |  1.68531    |  0.875127    | 0.567128   |
| 438 | dots_ocr_9_three_shot                    | average      |  1.50339    |  0.989444    | 0.468237   |
| 439 | dots_ocr_10_one_shot_english_extensive   | 1914-06-29_1 |  0.144159   |  0.500455    | 0.79307    |
| 440 | dots_ocr_10_one_shot_english_extensive   | 1914-06-29_2 |  0.390354   |  0.0363345   | 0.752353   |
| 441 | dots_ocr_10_one_shot_english_extensive   | 1914-06-29_3 |  0.197904   |  0.0225073   | 0.981912   |
| 442 | dots_ocr_10_one_shot_english_extensive   | 1914-06-29_4 |  0.0917662  |  0.0120463   | 0.989804   |
| 443 | dots_ocr_10_one_shot_english_extensive   | 1914-06-29_5 |  0.413986   |  0.0764771   | 0.948198   |
| 444 | dots_ocr_10_one_shot_english_extensive   | 1914-06-29_7 |  0.214992   |  0.0218923   | 0.980511   |
| 445 | dots_ocr_10_one_shot_english_extensive   | 1915-12-28_1 |  0.447761   |  0.902895    | 0.630906   |
| 446 | dots_ocr_10_one_shot_english_extensive   | 1915-12-28_2 |  0.711282   |  0.521346    | 0.605405   |
| 447 | dots_ocr_10_one_shot_english_extensive   | 1915-12-28_3 |  0.146501   |  0.325114    | 0.854419   |
| 448 | dots_ocr_10_one_shot_english_extensive   | 1915-12-28_4 |  4.54404    |  0.968512    | 0.642943   |
| 449 | dots_ocr_10_one_shot_english_extensive   | 1917-12-28_1 |  1.69352    |  1.47761     | 0.462332   |
| 450 | dots_ocr_10_one_shot_english_extensive   | 1917-12-28_2 |  0.853762   |  0.480988    | 0.571781   |
| 451 | dots_ocr_10_one_shot_english_extensive   | 1917-12-28_3 |  0.667745   |  0.31668     | 0.711526   |
| 452 | dots_ocr_10_one_shot_english_extensive   | 1917-12-28_4 |  0.52717    |  0.222857    | 0.876818   |
| 453 | dots_ocr_10_one_shot_english_extensive   | 1918-12-27_1 |  0.243714   |  0.0705882   | 0.957402   |
| 454 | dots_ocr_10_one_shot_english_extensive   | 1918-12-27_2 |  0.391673   |  0.0452735   | 0.964912   |
| 455 | dots_ocr_10_one_shot_english_extensive   | 1918-12-27_3 |  0.360265   |  0.0485623   | 0.963947   |
| 456 | dots_ocr_10_one_shot_english_extensive   | 1918-12-27_4 |  0.145522   |  0.0229936   | 0.983638   |
| 457 | dots_ocr_10_one_shot_english_extensive   | 1918-12-27_5 |  0.238834   |  0.0692866   | 0.942133   |
| 458 | dots_ocr_10_one_shot_english_extensive   | 1918-12-27_6 |  0.658508   |  1.30132     | 0.445243   |
| 459 | dots_ocr_10_one_shot_english_extensive   | average      |  0.654173   |  0.372187    | 0.802963   |
| 460 | dots_ocr_11_three_shot_english_extensive | 1914-06-29_1 |  2.07125    |  1.67203     | 0.392576   |
| 461 | dots_ocr_11_three_shot_english_extensive | 1914-06-29_2 |  0.392615   |  0.0383578   | 0.751655   |
| 462 | dots_ocr_11_three_shot_english_extensive | 1914-06-29_3 |  0.49815    |  0.383623    | 0.788911   |
| 463 | dots_ocr_11_three_shot_english_extensive | 1914-06-29_4 |  0.0942803  |  0.0154224   | 0.988323   |
| 464 | dots_ocr_11_three_shot_english_extensive | 1914-06-29_5 |  0.215385   |  0.0657345   | 0.959962   |
| 465 | dots_ocr_11_three_shot_english_extensive | 1914-06-29_7 |  0.235585   |  0.0422673   | 0.967354   |
| 466 | dots_ocr_11_three_shot_english_extensive | 1915-12-28_1 |  0.930348   |  0.803018    | 0.672044   |
| 467 | dots_ocr_11_three_shot_english_extensive | 1915-12-28_2 |  0.615978   |  0.512637    | 0.658543   |
| 468 | dots_ocr_11_three_shot_english_extensive | 1915-12-28_3 |  1.51406    |  1.05939     | 0.448973   |
| 469 | dots_ocr_11_three_shot_english_extensive | 1915-12-28_4 |  4.22625    |  0.943091    | 0.653467   |
| 470 | dots_ocr_11_three_shot_english_extensive | 1917-12-28_1 |  2.78611    |  2.0261      | 0.0278748  |
| 471 | dots_ocr_11_three_shot_english_extensive | 1917-12-28_2 |  4.00338    |  1.70306     | 0.00748604 |
| 472 | dots_ocr_11_three_shot_english_extensive | 1917-12-28_3 |  1.29666    |  0.922518    | 0.262593   |
| 473 | dots_ocr_11_three_shot_english_extensive | 1917-12-28_4 |  1.85969    |  1.60077     | 0.288835   |
| 474 | dots_ocr_11_three_shot_english_extensive | 1918-12-27_1 |  2.15957    |  1.67887     | 0.0285284  |
| 475 | dots_ocr_11_three_shot_english_extensive | 1918-12-27_2 |  0.241355   |  0.0976185   | 0.916762   |
| 476 | dots_ocr_11_three_shot_english_extensive | 1918-12-27_3 |  0.143709   |  0.0277955   | 0.979282   |
| 477 | dots_ocr_11_three_shot_english_extensive | 1918-12-27_4 |  0.147015   |  0.0234341   | 0.983197   |
| 478 | dots_ocr_11_three_shot_english_extensive | 1918-12-27_5 |  1.11166    |  0.721021    | 0.491698   |
| 479 | dots_ocr_11_three_shot_english_extensive | 1918-12-27_6 |  7.73893    |  1.65295     | 0.340164   |
| 480 | dots_ocr_11_three_shot_english_extensive | average      |  1.6141     |  0.799486    | 0.580411   |
| 481 | google_gemini_1_simple                   | 1914-06-29_1 |  0.401823   |  0.11998     | 0.92941    |
| 482 | google_gemini_1_simple                   | 1914-06-29_2 |  0.139412   |  0.047041    | 0.965049   |
| 483 | google_gemini_1_simple                   | 1914-06-29_3 |  0.540074   |  0.298049    | 0.763571   |
| 484 | google_gemini_1_simple                   | 1914-06-29_4 |  0.0923947  |  0.0158828   | 0.988275   |
| 485 | google_gemini_1_simple                   | 1914-06-29_5 |  0.114685   |  0.0303521   | 0.980803   |
| 486 | google_gemini_1_simple                   | 1914-06-29_7 |  0.679572   |  0.381923    | 0.758004   |
| 487 | google_gemini_1_simple                   | 1915-12-28_1 |  0.483416   |  0.38257     | 0.692284   |
| 488 | google_gemini_1_simple                   | 1915-12-28_2 |  0.419762   |  0.351008    | 0.800367   |
| 489 | google_gemini_1_simple                   | 1915-12-28_3 |  0.537606   |  0.387454    | 0.745255   |
| 490 | google_gemini_1_simple                   | 1915-12-28_4 |  0.698618   |  0.501107    | 0.659753   |
| 491 | google_gemini_1_simple                   | 1917-12-28_1 |  0.559259   |  0.405728    | 0.682426   |
| 492 | google_gemini_1_simple                   | 1917-12-28_2 |  0.150465   |  0.0370443   | 0.973069   |
| 493 | google_gemini_1_simple                   | 1917-12-28_3 |  0.658576   |  0.355646    | 0.706513   |
| 494 | google_gemini_1_simple                   | 1917-12-28_4 |  0.510138   |  0.219758    | 0.447802   |
| 495 | google_gemini_1_simple                   | 1918-12-27_1 |  0.158607   |  0.0351918   | 0.976234   |
| 496 | google_gemini_1_simple                   | 1918-12-27_2 |  0.904728   |  0.800618    | 0.227156   |
| 497 | google_gemini_1_simple                   | 1918-12-27_3 |  0.744371   |  0.427875    | 0.658235   |
| 498 | google_gemini_1_simple                   | 1918-12-27_4 |  0.642537   |  0.467184    | 0.639584   |
| 499 | google_gemini_1_simple                   | 1918-12-27_5 |  0.586228   |  0.307134    | 0.761032   |
| 500 | google_gemini_1_simple                   | 1918-12-27_6 |  0.861305   |  0.658028    | 0.534312   |
| 501 | google_gemini_1_simple                   | average      |  0.494179   |  0.311479    | 0.744457   |
| 502 | google_gemini_2_extensive                | 1914-06-29_1 |  0.116819   |  0.0209408   | 0.983407   |
| 503 | google_gemini_2_extensive                | 1914-06-29_2 |  0.743783   |  0.456331    | 0.671674   |
| 504 | google_gemini_2_extensive                | 1914-06-29_3 |  0.466708   |  0.328315    | 0.806858   |
| 505 | google_gemini_2_extensive                | 1914-06-29_4 |  0.540541   |  0.407427    | 0.751628   |
| 506 | google_gemini_2_extensive                | 1914-06-29_5 |  0.101399   |  0.0286469   | 0.980581   |
| 507 | google_gemini_2_extensive                | 1914-06-29_7 |  0.329489   |  0.256963    | 0.869047   |
| 508 | google_gemini_2_extensive                | 1915-12-28_1 |  0.725539   |  0.548347    | 0.543732   |
| 509 | google_gemini_2_extensive                | 1915-12-28_2 |  0.201822   |  0.136697    | 0.922991   |
| 510 | google_gemini_2_extensive                | 1915-12-28_3 |  0.11707    |  0.0177561   | 0.986986   |
| 511 | google_gemini_2_extensive                | 1915-12-28_4 |  0.643351   |  0.470871    | 0.492901   |
| 512 | google_gemini_2_extensive                | 1917-12-28_1 |  0.486111   |  0.319252    | 0.80688    |
| 513 | google_gemini_2_extensive                | 1917-12-28_2 |  0.156382   |  0.0672285   | 0.956714   |
| 514 | google_gemini_2_extensive                | 1917-12-28_3 |  1.09871    |  0.888503    | 0.475078   |
| 515 | google_gemini_2_extensive                | 1917-12-28_4 |  0.426602   |  0.232833    | 0.858192   |
| 516 | google_gemini_2_extensive                | 1918-12-27_1 |  0.766925   |  0.576675    | 0.582611   |
| 517 | google_gemini_2_extensive                | 1918-12-27_2 |  0.697248   |  0.533366    | 0.428552   |
| 518 | google_gemini_2_extensive                | 1918-12-27_3 |  0.537086   |  0.432668    | 0.731799   |
| 519 | google_gemini_2_extensive                | 1918-12-27_4 |  0.0641791  |  0.0120694   | 0.990421   |
| 520 | google_gemini_2_extensive                | 1918-12-27_5 |  0.17804    |  0.0582154   | 0.964532   |
| 521 | google_gemini_2_extensive                | 1918-12-27_6 |  0.493007   |  0.349593    | 0.732338   |
| 522 | google_gemini_2_extensive                | average      |  0.44454    |  0.307135    | 0.776846   |
| 523 | google_vision                            | 1914-06-29_1 |  0.685998   |  0.493576    | 0.658921   |
| 524 | google_vision                            | 1914-06-29_2 |  0.894499   |  0.685888    | 0.471246   |
| 525 | google_vision                            | 1914-06-29_3 |  0.954994   |  0.725918    | 0.390786   |
| 526 | google_vision                            | 1914-06-29_4 |  0.783155   |  0.61866     | 0.647705   |
| 527 | google_vision                            | 1914-06-29_5 |  0.425874   |  0.312985    | 0.837852   |
| 528 | google_vision                            | 1914-06-29_7 |  0.974465   |  0.714317    | 0.353195   |
| 529 | google_vision                            | 1915-12-28_1 |  0.798507   |  0.565079    | 0.588478   |
| 530 | google_vision                            | 1915-12-28_2 |  0.583041   |  0.434597    | 0.735363   |
| 531 | google_vision                            | 1915-12-28_3 |  0.590582   |  0.417306    | 0.717829   |
| 532 | google_vision                            | 1915-12-28_4 |  0.717617   |  0.522581    | 0.637145   |
| 533 | google_vision                            | 1917-12-28_1 |  0.573148   |  0.389804    | 0.666925   |
| 534 | google_vision                            | 1917-12-28_2 |  0.831784   |  0.641513    | 0.379067   |
| 535 | google_vision                            | 1917-12-28_3 |  0.874865   |  0.660237    | 0.494623   |
| 536 | google_vision                            | 1917-12-28_4 |  0.450933   |  0.280291    | 0.79145    |
| 537 | google_vision                            | 1918-12-27_1 |  0.905222   |  0.680818    | 0.448791   |
| 538 | google_vision                            | 1918-12-27_2 |  1.00988    |  0.774608    | 0.414578   |
| 539 | google_vision                            | 1918-12-27_3 |  0.639073   |  0.471486    | 0.707138   |
| 540 | google_vision                            | 1918-12-27_4 |  0.840299   |  0.640825    | 0.459222   |
| 541 | google_vision                            | 1918-12-27_5 |  0.823821   |  0.600191    | 0.395568   |
| 542 | google_vision                            | 1918-12-27_6 |  0.750583   |  0.580666    | 0.558541   |
| 543 | google_vision                            | average      |  0.755417   |  0.560567    | 0.567721   |
| 544 | openai_1_simple                          | 1914-06-29_1 |  0.995857   |  0.984522    | 0.0187232  |
| 545 | openai_1_simple                          | 1914-06-29_2 |  0.997739   |  0.994436    | 0.00905357 |
| 546 | openai_1_simple                          | 1914-06-29_3 |  0.996301   |  0.989937    | 0.0139913  |
| 547 | openai_1_simple                          | 1914-06-29_4 |  0.9956     |  0.986266    | 0.02028    |
| 548 | openai_1_simple                          | 1914-06-29_5 |  0.993706   |  0.98508     | 0.0258671  |
| 549 | openai_1_simple                          | 1914-06-29_7 |  0.996705   |  0.993714    | 0.0111984  |
| 550 | openai_1_simple                          | 1915-12-28_1 |  0.970978   |  0.882673    | 0.143601   |
| 551 | openai_1_simple                          | 1915-12-28_2 |  0.997197   |  0.995048    | 0.007476   |
| 552 | openai_1_simple                          | 1915-12-28_3 |  0.996076   |  0.985423    | 0.0194071  |
| 553 | openai_1_simple                          | 1915-12-28_4 |  0.997409   |  0.993645    | 0.00765404 |
| 554 | openai_1_simple                          | 1917-12-28_1 |  0.991667   |  0.98098     | 0.0221306  |
| 555 | openai_1_simple                          | 1917-12-28_2 |  0.994083   |  0.98285     | 0.0209878  |
| 556 | openai_1_simple                          | 1917-12-28_3 |  0.997303   |  0.99582     | 0.00499424 |
| 557 | openai_1_simple                          | 1917-12-28_4 |  0.996756   |  0.985278    | 0.0198511  |
| 558 | openai_1_simple                          | 1918-12-27_1 |  0.994197   |  0.979028    | 0.0268322  |
| 559 | openai_1_simple                          | 1918-12-27_2 |  0.996471   |  0.994392    | 0.00889033 |
| 560 | openai_1_simple                          | 1918-12-27_3 |  0.993377   |  0.984185    | 0.0223235  |
| 561 | openai_1_simple                          | 1918-12-27_4 |  0.99403    |  0.984407    | 0.0241068  |
| 562 | openai_1_simple                          | 1918-12-27_5 |  0.996898   |  0.986216    | 0.0112806  |
| 563 | openai_1_simple                          | 1918-12-27_6 |  0.997669   |  0.993521    | 0.00782236 |
| 564 | openai_1_simple                          | average      |  0.994501   |  0.982871    | 0.0223236  |
| 565 | openai_2_extensive                       | 1914-06-29_1 |  0.964374   |  0.792413    | 0.137827   |
| 566 | openai_2_extensive                       | 1914-06-29_2 |  0.998493   |  0.995279    | 0.00755097 |
| 567 | openai_2_extensive                       | 1914-06-29_3 |  0.968557   |  0.823782    | 0.125099   |
| 568 | openai_2_extensive                       | 1914-06-29_4 |  0.9956     |  0.988261    | 0.0162256  |
| 569 | openai_2_extensive                       | 1914-06-29_5 |  0.999301   |  0.812516    | 0.0366873  |
| 570 | openai_2_extensive                       | 1914-06-29_7 |  0.939868   |  0.741736    | 0.10222    |
| 571 | openai_2_extensive                       | 1915-12-28_1 |  0.97927    |  0.827859    | 0.129297   |
| 572 | openai_2_extensive                       | 1915-12-28_2 |  0.920112   |  0.699283    | 0.252545   |
| 573 | openai_2_extensive                       | 1915-12-28_3 |  0.948332   |  0.798558    | 0.190487   |
| 574 | openai_2_extensive                       | 1915-12-28_4 |  0.968912   |  0.758305    | 0.160772   |
| 575 | openai_2_extensive                       | 1917-12-28_1 |  1          |  0.99624     | 0.0061674  |
| 576 | openai_2_extensive                       | 1917-12-28_2 |  0.993238   |  0.976676    | 0.0319831  |
| 577 | openai_2_extensive                       | 1917-12-28_3 |  0.967098   |  0.794432    | 0.0970834  |
| 578 | openai_2_extensive                       | 1917-12-28_4 |  0.996756   |  0.992639    | 0.0109594  |
| 579 | openai_2_extensive                       | 1918-12-27_1 |  0.938104   |  0.826905    | 0.184087   |
| 580 | openai_2_extensive                       | 1918-12-27_2 |  0.976006   |  0.816224    | 0.101162   |
| 581 | openai_2_extensive                       | 1918-12-27_3 |  0.995364   |  0.983866    | 0.0224754  |
| 582 | openai_2_extensive                       | 1918-12-27_4 |  0.982836   |  0.877544    | 0.0783828  |
| 583 | openai_2_extensive                       | 1918-12-27_5 |  0.949132   |  0.733338    | 0.165217   |
| 584 | openai_2_extensive                       | 1918-12-27_6 |  0.996503   |  0.991616    | 0.011335   |
| 585 | openai_2_extensive                       | average      |  0.973893   |  0.861374    | 0.0933782  |
| 586 | openai_3_one_shot_simple                 | 1914-06-29_1 |  0.975973   |  0.922003    | 0.0757209  |
| 587 | openai_3_one_shot_simple                 | 1914-06-29_2 |  0.984175   |  0.955151    | 0.053026   |
| 588 | openai_3_one_shot_simple                 | 1914-06-29_3 |  1          |  0.996697    | 0.00199005 |
| 589 | openai_3_one_shot_simple                 | 1914-06-29_4 |  0.982401   |  0.939538    | 0.0207762  |
| 590 | openai_3_one_shot_simple                 | 1914-06-29_5 |  0.985315   |  0.948333    | 0.0597087  |
| 591 | openai_3_one_shot_simple                 | 1914-06-29_7 |  0.974465   |  0.908421    | 0.0633085  |
| 592 | openai_3_one_shot_simple                 | 1915-12-28_1 |  0.965174   |  0.884213    | 0.1296     |
| 593 | openai_3_one_shot_simple                 | 1915-12-28_2 |  0.995095   |  0.988388    | 0.0167103  |
| 594 | openai_3_one_shot_simple                 | 1915-12-28_3 |  1          |  0.997364    | 0.00355652 |
| 595 | openai_3_one_shot_simple                 | 1915-12-28_4 |  0.999136   |  0.940876    | 0.0224475  |
| 596 | openai_3_one_shot_simple                 | 1917-12-28_1 |  0.968519   |  0.884883    | 0.1155     |
| 597 | openai_3_one_shot_simple                 | 1917-12-28_2 |  0.97126    |  0.899647    | 0.0775628  |
| 598 | openai_3_one_shot_simple                 | 1917-12-28_3 |  0.983279   |  0.94438     | 0.0576911  |
| 599 | openai_3_one_shot_simple                 | 1917-12-28_4 |  0.96837    |  0.886295    | 0.104096   |
| 600 | openai_3_one_shot_simple                 | 1918-12-27_1 |  0.972921   |  0.925422    | 0.0710305  |
| 601 | openai_3_one_shot_simple                 | 1918-12-27_2 |  0.981651   |  0.945379    | 0.0444035  |
| 602 | openai_3_one_shot_simple                 | 1918-12-27_3 |  0.996689   |  0.984265    | 0.0216981  |
| 603 | openai_3_one_shot_simple                 | 1918-12-27_4 |  0.976866   |  0.915866    | 0.082642   |
| 604 | openai_3_one_shot_simple                 | 1918-12-27_5 |  0.996278   |  0.987609    | 0.0108617  |
| 605 | openai_3_one_shot_simple                 | 1918-12-27_6 |  0.977855   |  0.889482    | 0.103684   |
| 606 | openai_3_one_shot_simple                 | average      |  0.982771   |  0.937211    | 0.0568007  |
| 607 | pero_ocr                                 | 1914-06-29_1 |  0.0886495  |  0.0471421   | 0.970696   |
| 608 | pero_ocr                                 | 1914-06-29_2 |  0.0248681  |  0.00750295  | 0.995572   |
| 609 | pero_ocr                                 | 1914-06-29_3 |  0.027127   |  0.011753    | 0.991315   |
| 610 | pero_ocr                                 | 1914-06-29_4 |  0.0201131  |  0.0145784   | 0.992481   |
| 611 | pero_ocr                                 | 1914-06-29_5 |  0.00769231 |  0.000937846 | 0.999403   |
| 612 | pero_ocr                                 | 1914-06-29_7 |  0.0222405  |  0.00801994  | 0.995121   |
| 613 | pero_ocr                                 | 1915-12-28_1 |  0.0762852  |  0.0381852   | 0.976603   |
| 614 | pero_ocr                                 | 1915-12-28_2 |  0.0350385  |  0.0237363   | 0.987491   |
| 615 | pero_ocr                                 | 1915-12-28_3 |  0.028123   |  0.00674575  | 0.995805   |
| 616 | pero_ocr                                 | 1915-12-28_4 |  0.603627   |  0.47713     | 0.679785   |
| 617 | pero_ocr                                 | 1917-12-28_1 |  0.0675926  |  0.0363817   | 0.978101   |
| 618 | pero_ocr                                 | 1917-12-28_2 |  0.537616   |  0.486672    | 0.634696   |
| 619 | pero_ocr                                 | 1917-12-28_3 |  0.0539374  |  0.0317001   | 0.982987   |
| 620 | pero_ocr                                 | 1917-12-28_4 |  0.171127   |  0.0614044   | 0.95286    |
| 621 | pero_ocr                                 | 1918-12-27_1 |  0.0696325  |  0.0384655   | 0.978686   |
| 622 | pero_ocr                                 | 1918-12-27_2 |  0.0345801  |  0.00658376  | 0.995156   |
| 623 | pero_ocr                                 | 1918-12-27_3 |  0.0463576  |  0.0260383   | 0.985854   |
| 624 | pero_ocr                                 | 1918-12-27_4 |  0.0686567  |  0.0569113   | 0.971101   |
| 625 | pero_ocr                                 | 1918-12-27_5 |  0.0471464  |  0.00931153  | 0.993654   |
| 626 | pero_ocr                                 | 1918-12-27_6 |  0.631702   |  0.475864    | 0.68218    |
| 627 | pero_ocr                                 | average      |  0.133106   |  0.0932532   | 0.936977   |
| 628 | pero_scribblesense                       | 1914-06-29_1 |  0.0836785  |  0.0426909   | 0.974564   |
| 629 | pero_scribblesense                       | 1914-06-29_2 |  0.0263753  |  0.00927331  | 0.994477   |
| 630 | pero_scribblesense                       | 1914-06-29_3 |  0.545623   |  0.471194    | 0.733945   |
| 631 | pero_scribblesense                       | 1914-06-29_4 |  0.00439975 |  0.000613826 | 0.999348   |
| 632 | pero_scribblesense                       | 1914-06-29_5 |  0.00909091 |  0.0024725   | 0.998594   |
| 633 | pero_scribblesense                       | 1914-06-29_7 |  0.0247117  |  0.0128969   | 0.992574   |
| 634 | pero_scribblesense                       | 1915-12-28_1 |  0.752073   |  0.695853    | 0.624737   |
| 635 | pero_scribblesense                       | 1915-12-28_2 |  0.51857    |  0.453296    | 0.623154   |
| 636 | pero_scribblesense                       | 1915-12-28_3 |  0.746239   |  0.578429    | 0.65238    |
| 637 | pero_scribblesense                       | 1915-12-28_4 |  0.670984   |  0.510833    | 0.391256   |
| 638 | pero_scribblesense                       | 1917-12-28_1 |  0.746296   |  0.566405    | 0.568996   |
| 639 | pero_scribblesense                       | 1917-12-28_2 |  0.764159   |  0.681889    | 0.626416   |
| 640 | pero_scribblesense                       | 1917-12-28_3 |  0.633225   |  0.559606    | 0.633985   |
| 641 | pero_scribblesense                       | 1917-12-28_4 |  1.00324    |  0.818983    | 0.30235    |
| 642 | pero_scribblesense                       | 1918-12-27_1 |  0.222437   |  0.193555    | 0.901514   |
| 643 | pero_scribblesense                       | 1918-12-27_2 |  0.0430487  |  0.0114606   | 0.992882   |
| 644 | pero_scribblesense                       | 1918-12-27_3 |  0.623179   |  0.507268    | 0.684692   |
| 645 | pero_scribblesense                       | 1918-12-27_4 |  0.0238806  |  0.00933838  | 0.994846   |
| 646 | pero_scribblesense                       | 1918-12-27_5 |  0.361663   |  0.297236    | 0.822145   |
| 647 | pero_scribblesense                       | 1918-12-27_6 |  0.903263   |  0.71532     | 0.398989   |
| 648 | pero_scribblesense                       | average      |  0.435307   |  0.356931    | 0.745592   |
| 649 | transkribus                              | 1914-06-29_1 |  0.263463   |  0.121396    | 0.925798   |
| 650 | transkribus                              | 1914-06-29_2 |  0.706104   |  0.655539    | 0.670269   |
| 651 | transkribus                              | 1914-06-29_3 |  0.15783    |  0.0750499   | 0.959288   |
| 652 | transkribus                              | 1914-06-29_4 |  0.121936   |  0.0524822   | 0.971701   |
| 653 | transkribus                              | 1914-06-29_5 |  0.766434   |  0.617614    | 0.629737   |
| 654 | transkribus                              | 1914-06-29_7 |  0.4514     |  0.333586    | 0.801892   |
| 655 | transkribus                              | 1915-12-28_1 |  0.819237   |  0.607165    | 0.545237   |
| 656 | transkribus                              | 1915-12-28_2 |  0.74562    |  0.577698    | 0.661389   |
| 657 | transkribus                              | 1915-12-28_3 |  0.306736   |  0.206482    | 0.890066   |
| 658 | transkribus                              | 1915-12-28_4 |  0.637306   |  0.506307    | 0.674967   |
| 659 | transkribus                              | 1917-12-28_1 |  0.305556   |  0.161672    | 0.902228   |
| 660 | transkribus                              | 1917-12-28_2 |  0.234996   |  0.103391    | 0.940797   |
| 661 | transkribus                              | 1917-12-28_3 |  0.21575    |  0.111883    | 0.940464   |
| 662 | transkribus                              | 1917-12-28_4 |  0.344688   |  0.17724     | 0.87753    |
| 663 | transkribus                              | 1918-12-27_1 |  0.240812   |  0.115601    | 0.922462   |
| 664 | transkribus                              | 1918-12-27_2 |  0.167255   |  0.0633992   | 0.965295   |
| 665 | transkribus                              | 1918-12-27_3 |  0.12649    |  0.049361    | 0.97221    |
| 666 | transkribus                              | 1918-12-27_4 |  0.131343   |  0.0591137   | 0.968104   |
| 667 | transkribus                              | 1918-12-27_5 |  0.256203   |  0.139013    | 0.924406   |
| 668 | transkribus                              | 1918-12-27_6 |  0.325175   |  0.167048    | 0.882608   |
| 669 | transkribus                              | average      |  0.366217   |  0.245052    | 0.851322   |

## variance details

|    | workflow                                 |          WER |          CER |     difflib |
|---:|:-----------------------------------------|-------------:|-------------:|------------:|
|  0 | openai_1_simple                          |  3.18084e-05 |  0.000554207 | 0.000819787 |
|  1 | openai_3_one_shot_simple                 |  0.000126178 |  0.00142979  | 0.0014163   |
|  2 | anthropic_1_simple                       |  0.000145944 |  0.0017523   | 0.00168487  |
|  3 | openai_2_extensive                       |  0.000558672 |  0.0101955   | 0.00519017  |
|  4 | dots_ocr_1_default                       |  0.0216434   |  0.0218655   | 0.0125143   |
|  5 | dots_ocr_4_default                       |  0.0210313   |  0.0242097   | 0.0127726   |
|  6 | pero_ocr                                 |  0.0384002   |  0.0266707   | 0.0131929   |
|  7 | transkribus                              |  0.0524274   |  0.044862    | 0.0175118   |
|  8 | anno                                     |  0.0503312   |  0.0412315   | 0.0194777   |
|  9 | google_vision                            |  0.0270091   |  0.0187263   | 0.0214782   |
| 10 | google_gemini_2_extensive                |  0.0764847   |  0.0542079   | 0.034029    |
| 11 | google_gemini_1_simple                   |  0.0592162   |  0.0447279   | 0.0370746   |
| 12 | dots_ocr_10_one_shot_english_extensive   |  0.921542    |  0.19459     | 0.0329177   |
| 13 | dots_ocr_8_one_shot                      |  3.35222     |  0.276249    | 0.0332043   |
| 14 | pero_scribblesense                       |  0.11466     |  0.0813024   | 0.0499676   |
| 15 | deepseek_ocr_1_default                   |  0.789478    |  0.102477    | 0.0506142   |
| 16 | dots_ocr_3_default                       |  3.50479     |  0.41004     | 0.0678949   |
| 17 | deepseek_ocr_3_english_extensive_2       |  1.92857     |  0.478833    | 0.083486    |
| 18 | deepseek_ocr_2_german_extensive_2        |  0.784932    |  0.20325     | 0.114429    |
| 19 | dots_ocr_11_three_shot_english_extensive |  3.44579     |  0.479353    | 0.111478    |
| 20 | churro_3_english_extensive_3             |  2.48805     |  3.30548     | 0.0831249   |
| 21 | dots_ocr_9_three_shot                    |  1.71351     |  0.469051    | 0.126682    |
| 22 | dots_ocr_6_english_extensive             |  4.60007     |  0.493562    | 0.115397    |
| 23 | dots_ocr_7_german_extensive_2            |  4.15668     |  0.647965    | 0.125839    |
| 24 | churro_8_two_shot_zero_temperature       | 31.8808      |  1.9607      | 0.0106076   |
| 25 | churro_9_two_shot_zero_temperature       | 31.8808      |  1.9607      | 0.0106076   |
| 26 | churro_6_two_shot                        | 16.9183      |  4.28797     | 0.0551378   |
| 27 | churro_7_two_shot_prompts_adapted        | 16.9607      |  4.75457     | 0.0760576   |
| 28 | churro_2_german_extensive_2              | 22.7073      |  3.96909     | 0.101941    |
| 29 | churro_4_one_shot                        | 25.3097      |  3.97971     | 0.100435    |
| 30 | churro_5_one_shot_s_replaced             | 25.5503      |  3.99469     | 0.104769    |
| 31 | churro_1_simple                          | 24.5595      | 10.4073      | 0.119504    |

## results per image

|    | image_id     |      WER |      CER |   difflib |
|---:|:-------------|---------:|---------:|----------:|
|  0 | 1914-06-29_4 | 0.4079   | 0.316377 |  0.768793 |
|  1 | 1914-06-29_5 | 1.00603  | 0.706846 |  0.722311 |
|  2 | 1918-12-27_4 | 0.868167 | 0.66008  |  0.660881 |
|  3 | 1914-06-29_3 | 1.25008  | 0.746135 |  0.679607 |
|  4 | 1914-06-29_1 | 1.00264  | 0.6592   |  0.612957 |
|  5 | 1914-06-29_7 | 1.16176  | 1.00354  |  0.665495 |
|  6 | 1915-12-28_3 | 1.26451  | 1.0245   |  0.608645 |
|  7 | 1918-12-27_5 | 1.18312  | 0.914217 |  0.556742 |
|  8 | 1914-06-29_2 | 2.11577  | 0.926786 |  0.557744 |
|  9 | 1917-12-28_3 | 1.11291  | 1.18992  |  0.542054 |
| 10 | 1918-12-27_3 | 1.56337  | 1.35141  |  0.566743 |
| 11 | 1917-12-28_1 | 1.5259   | 1.22147  |  0.488203 |
| 12 | 1918-12-27_2 | 1.79289  | 1.38723  |  0.512773 |
| 13 | 1918-12-27_1 | 1.58795  | 1.40348  |  0.496712 |
| 14 | 1917-12-28_4 | 2.55041  | 1.13167  |  0.473447 |
| 15 | 1915-12-28_1 | 1.88986  | 1.72304  |  0.438673 |
| 16 | 1915-12-28_2 | 2.21682  | 1.67806  |  0.428613 |
| 17 | 1915-12-28_4 | 3.52232  | 1.41292  |  0.443078 |
| 18 | 1917-12-28_2 | 2.45393  | 1.45117  |  0.379159 |
| 19 | 1918-12-27_6 | 6.62387  | 2.09089  |  0.364207 |

## all image results ranked

|     | workflow                                 | image_id     |         WER |          CER |    difflib |
|----:|:-----------------------------------------|:-------------|------------:|-------------:|-----------:|
|   0 | pero_scribblesense                       | 1914-06-29_4 |  0.00439975 |  0.000613826 | 0.999348   |
|   1 | pero_ocr                                 | 1914-06-29_5 |  0.00769231 |  0.000937846 | 0.999403   |
|   2 | pero_scribblesense                       | 1914-06-29_5 |  0.00909091 |  0.0024725   | 0.998594   |
|   3 | pero_ocr                                 | 1915-12-28_3 |  0.028123   |  0.00674575  | 0.995805   |
|   4 | pero_ocr                                 | 1914-06-29_2 |  0.0248681  |  0.00750295  | 0.995572   |
|   5 | pero_ocr                                 | 1914-06-29_7 |  0.0222405  |  0.00801994  | 0.995121   |
|   6 | pero_ocr                                 | 1918-12-27_2 |  0.0345801  |  0.00658376  | 0.995156   |
|   7 | pero_scribblesense                       | 1918-12-27_4 |  0.0238806  |  0.00933838  | 0.994846   |
|   8 | pero_scribblesense                       | 1914-06-29_2 |  0.0263753  |  0.00927331  | 0.994477   |
|   9 | pero_ocr                                 | 1918-12-27_5 |  0.0471464  |  0.00931153  | 0.993654   |
|  10 | pero_scribblesense                       | 1914-06-29_7 |  0.0247117  |  0.0128969   | 0.992574   |
|  11 | pero_ocr                                 | 1914-06-29_4 |  0.0201131  |  0.0145784   | 0.992481   |
|  12 | pero_scribblesense                       | 1918-12-27_2 |  0.0430487  |  0.0114606   | 0.992882   |
|  13 | pero_ocr                                 | 1914-06-29_3 |  0.027127   |  0.011753    | 0.991315   |
|  14 | dots_ocr_9_three_shot                    | 1914-06-29_3 |  0.0758323  |  0.0111384   | 0.99094    |
|  15 | google_gemini_2_extensive                | 1918-12-27_4 |  0.0641791  |  0.0120694   | 0.990421   |
|  16 | dots_ocr_8_one_shot                      | 1914-06-29_4 |  0.089252   |  0.011586    | 0.990343   |
|  17 | dots_ocr_6_english_extensive             | 1914-06-29_4 |  0.0911376  |  0.0117394   | 0.990112   |
|  18 | dots_ocr_10_one_shot_english_extensive   | 1914-06-29_4 |  0.0917662  |  0.0120463   | 0.989804   |
|  19 | pero_ocr                                 | 1915-12-28_2 |  0.0350385  |  0.0237363   | 0.987491   |
|  20 | dots_ocr_11_three_shot_english_extensive | 1914-06-29_4 |  0.0942803  |  0.0154224   | 0.988323   |
|  21 | google_gemini_1_simple                   | 1914-06-29_4 |  0.0923947  |  0.0158828   | 0.988275   |
|  22 | pero_ocr                                 | 1918-12-27_3 |  0.0463576  |  0.0260383   | 0.985854   |
|  23 | google_gemini_2_extensive                | 1915-12-28_3 |  0.11707    |  0.0177561   | 0.986986   |
|  24 | pero_ocr                                 | 1917-12-28_3 |  0.0539374  |  0.0317001   | 0.982987   |
|  25 | churro_2_german_extensive_2              | 1918-12-27_5 |  0.108561   |  0.0211892   | 0.983751   |
|  26 | google_gemini_2_extensive                | 1914-06-29_1 |  0.116819   |  0.0209408   | 0.983407   |
|  27 | dots_ocr_10_one_shot_english_extensive   | 1918-12-27_4 |  0.145522   |  0.0229936   | 0.983638   |
|  28 | dots_ocr_8_one_shot                      | 1918-12-27_4 |  0.144776   |  0.0230817   | 0.983599   |
|  29 | dots_ocr_1_default                       | 1914-06-29_3 |  0.176942   |  0.0185896   | 0.984184   |
|  30 | dots_ocr_7_german_extensive_2            | 1915-12-28_3 |  0.156965   |  0.0222532   | 0.983581   |
|  31 | dots_ocr_11_three_shot_english_extensive | 1918-12-27_4 |  0.147015   |  0.0234341   | 0.983197   |
|  32 | dots_ocr_4_default                       | 1914-06-29_3 |  0.175092   |  0.0194346   | 0.983414   |
|  33 | google_gemini_2_extensive                | 1914-06-29_5 |  0.101399   |  0.0286469   | 0.980581   |
|  34 | google_gemini_1_simple                   | 1914-06-29_5 |  0.114685   |  0.0303521   | 0.980803   |
|  35 | dots_ocr_9_three_shot                    | 1914-06-29_4 |  0.105594   |  0.0250902   | 0.979895   |
|  36 | dots_ocr_1_default                       | 1915-12-28_3 |  0.168738   |  0.0211677   | 0.982243   |
|  37 | anno                                     | 1914-06-29_4 |  0.12885    |  0.0227116   | 0.980347   |
|  38 | pero_ocr                                 | 1918-12-27_1 |  0.0696325  |  0.0384655   | 0.978686   |
|  39 | pero_ocr                                 | 1917-12-28_1 |  0.0675926  |  0.0363817   | 0.978101   |
|  40 | anno                                     | 1914-06-29_3 |  0.130086   |  0.0248886   | 0.979545   |
|  41 | dots_ocr_6_english_extensive             | 1915-12-28_3 |  0.177894   |  0.0241917   | 0.981474   |
|  42 | dots_ocr_8_one_shot                      | 1914-06-29_3 |  0.197904   |  0.0224305   | 0.981988   |
|  43 | dots_ocr_10_one_shot_english_extensive   | 1914-06-29_3 |  0.197904   |  0.0225073   | 0.981912   |
|  44 | dots_ocr_1_default                       | 1914-06-29_1 |  0.169014   |  0.0246839   | 0.980757   |
|  45 | dots_ocr_8_one_shot                      | 1918-12-27_3 |  0.141722   |  0.0275559   | 0.979491   |
|  46 | dots_ocr_11_three_shot_english_extensive | 1918-12-27_3 |  0.143709   |  0.0277955   | 0.979282   |
|  47 | pero_ocr                                 | 1915-12-28_1 |  0.0762852  |  0.0381852   | 0.976603   |
|  48 | churro_5_one_shot_s_replaced             | 1914-06-29_7 |  0.0840198  |  0.0382573   | 0.976928   |
|  49 | dots_ocr_10_one_shot_english_extensive   | 1914-06-29_7 |  0.214992   |  0.0218923   | 0.980511   |
|  50 | dots_ocr_4_default                       | 1915-12-28_3 |  0.169392   |  0.0281461   | 0.978773   |
|  51 | pero_scribblesense                       | 1914-06-29_1 |  0.0836785  |  0.0426909   | 0.974564   |
|  52 | dots_ocr_6_english_extensive             | 1918-12-27_2 |  0.160198   |  0.0332439   | 0.976297   |
|  53 | google_gemini_1_simple                   | 1918-12-27_1 |  0.158607   |  0.0351918   | 0.976234   |
|  54 | dots_ocr_6_english_extensive             | 1918-12-27_3 |  0.147682   |  0.0379393   | 0.974624   |
|  55 | churro_5_one_shot_s_replaced             | 1914-06-29_1 |  0.100249   |  0.0486596   | 0.972      |
|  56 | google_gemini_1_simple                   | 1917-12-28_2 |  0.150465   |  0.0370443   | 0.973069   |
|  57 | pero_ocr                                 | 1918-12-27_4 |  0.0686567  |  0.0569113   | 0.971101   |
|  58 | anno                                     | 1914-06-29_5 |  0.179021   |  0.0326541   | 0.973684   |
|  59 | pero_ocr                                 | 1914-06-29_1 |  0.0886495  |  0.0471421   | 0.970696   |
|  60 | transkribus                              | 1918-12-27_3 |  0.12649    |  0.049361    | 0.97221    |
|  61 | transkribus                              | 1914-06-29_4 |  0.121936   |  0.0524822   | 0.971701   |
|  62 | dots_ocr_1_default                       | 1914-06-29_7 |  0.297364   |  0.0303457   | 0.974981   |
|  63 | anno                                     | 1914-06-29_7 |  0.1771     |  0.0406416   | 0.970251   |
|  64 | dots_ocr_1_default                       | 1914-06-29_4 |  0.314896   |  0.0319957   | 0.973942   |
|  65 | transkribus                              | 1918-12-27_4 |  0.131343   |  0.0591137   | 0.968104   |
|  66 | dots_ocr_4_default                       | 1914-06-29_4 |  0.315525   |  0.0321492   | 0.973827   |
|  67 | dots_ocr_7_german_extensive_2            | 1914-06-29_3 |  0.329223   |  0.0291135   | 0.973868   |
|  68 | dots_ocr_7_german_extensive_2            | 1914-06-29_4 |  0.329353   |  0.0323793   | 0.973755   |
|  69 | dots_ocr_3_default                       | 1914-06-29_4 |  0.329353   |  0.0324561   | 0.973716   |
|  70 | google_gemini_1_simple                   | 1914-06-29_2 |  0.139412   |  0.047041    | 0.965049   |
|  71 | dots_ocr_3_default                       | 1914-06-29_7 |  0.308896   |  0.0387992   | 0.970842   |
|  72 | dots_ocr_7_german_extensive_2            | 1914-06-29_7 |  0.311367   |  0.0393411   | 0.970402   |
|  73 | dots_ocr_11_three_shot_english_extensive | 1914-06-29_7 |  0.235585   |  0.0422673   | 0.967354   |
|  74 | dots_ocr_1_default                       | 1917-12-28_3 |  0.324164   |  0.0344007   | 0.970282   |
|  75 | dots_ocr_1_default                       | 1914-06-29_5 |  0.330769   |  0.0386222   | 0.970483   |
|  76 | anno                                     | 1914-06-29_2 |  0.219292   |  0.0429944   | 0.965998   |
|  77 | dots_ocr_4_default                       | 1914-06-29_5 |  0.332168   |  0.0387075   | 0.970439   |
|  78 | transkribus                              | 1918-12-27_2 |  0.167255   |  0.0633992   | 0.965295   |
|  79 | anno                                     | 1918-12-27_4 |  0.187313   |  0.0447538   | 0.964545   |
|  80 | google_gemini_2_extensive                | 1918-12-27_5 |  0.17804    |  0.0582154   | 0.964532   |
|  81 | dots_ocr_3_default                       | 1917-12-28_3 |  0.334951   |  0.0374228   | 0.968922   |
|  82 | churro_1_simple                          | 1914-06-29_3 |  0.31381    |  0.0470886   | 0.966722   |
|  83 | dots_ocr_4_default                       | 1917-12-28_3 |  0.345739   |  0.0376157   | 0.967144   |
|  84 | dots_ocr_3_default                       | 1914-06-29_3 |  0.251541   |  0.0579966   | 0.964511   |
|  85 | dots_ocr_3_default                       | 1915-12-28_3 |  0.360366   |  0.0451268   | 0.966623   |
|  86 | transkribus                              | 1914-06-29_3 |  0.15783    |  0.0750499   | 0.959288   |
|  87 | dots_ocr_1_default                       | 1918-12-27_3 |  0.339735   |  0.0449681   | 0.964603   |
|  88 | dots_ocr_7_german_extensive_2            | 1918-12-27_4 |  0.387313   |  0.0475729   | 0.966511   |
|  89 | dots_ocr_4_default                       | 1918-12-27_4 |  0.36194    |  0.0471324   | 0.965334   |
|  90 | churro_2_german_extensive_2              | 1918-12-27_4 |  0.238806   |  0.0472205   | 0.95977    |
|  91 | dots_ocr_7_german_extensive_2            | 1918-12-27_3 |  0.364238   |  0.046885    | 0.964995   |
|  92 | dots_ocr_11_three_shot_english_extensive | 1914-06-29_5 |  0.215385   |  0.0657345   | 0.959962   |
|  93 | dots_ocr_3_default                       | 1918-12-27_4 |  0.386567   |  0.0486301   | 0.965678   |
|  94 | churro_3_english_extensive_3             | 1914-06-29_1 |  0.256007   |  0.0451189   | 0.959716   |
|  95 | google_gemini_2_extensive                | 1917-12-28_2 |  0.156382   |  0.0672285   | 0.956714   |
|  96 | dots_ocr_10_one_shot_english_extensive   | 1918-12-27_3 |  0.360265   |  0.0485623   | 0.963947   |
|  97 | dots_ocr_10_one_shot_english_extensive   | 1918-12-27_2 |  0.391673   |  0.0452735   | 0.964912   |
|  98 | churro_4_one_shot                        | 1914-06-29_1 |  0.195526   |  0.0627213   | 0.957821   |
|  99 | dots_ocr_4_default                       | 1918-12-27_3 |  0.348344   |  0.0478435   | 0.963207   |
| 100 | dots_ocr_3_default                       | 1918-12-27_3 |  0.362252   |  0.0485623   | 0.963858   |
| 101 | dots_ocr_1_default                       | 1917-12-28_1 |  0.350926   |  0.0472188   | 0.963049   |
| 102 | dots_ocr_9_three_shot                    | 1914-06-29_5 |  0.175524   |  0.0725552   | 0.957182   |
| 103 | dots_ocr_1_default                       | 1918-12-27_2 |  0.372618   |  0.0463302   | 0.963461   |
| 104 | churro_3_english_extensive_3             | 1915-12-28_3 |  0.268149   |  0.0452043   | 0.958772   |
| 105 | dots_ocr_1_default                       | 1918-12-27_1 |  0.377176   |  0.0477749   | 0.963655   |
| 106 | dots_ocr_8_one_shot                      | 1918-12-27_2 |  0.390967   |  0.0499065   | 0.962803   |
| 107 | dots_ocr_4_default                       | 1918-12-27_2 |  0.375441   |  0.0494188   | 0.962087   |
| 108 | churro_3_english_extensive_3             | 1918-12-27_4 |  0.247015   |  0.0531231   | 0.956698   |
| 109 | dots_ocr_10_one_shot_english_extensive   | 1918-12-27_1 |  0.243714   |  0.0705882   | 0.957402   |
| 110 | churro_2_german_extensive_2              | 1915-12-28_3 |  0.268803   |  0.0503993   | 0.956842   |
| 111 | churro_1_simple                          | 1914-06-29_4 |  0.323696   |  0.0602317   | 0.959934   |
| 112 | dots_ocr_8_one_shot                      | 1914-06-29_7 |  0.248764   |  0.0548391   | 0.955722   |
| 113 | pero_ocr                                 | 1917-12-28_4 |  0.171127   |  0.0614044   | 0.95286    |
| 114 | dots_ocr_7_german_extensive_2            | 1918-12-27_2 |  0.39379    |  0.0516134   | 0.961277   |
| 115 | churro_1_simple                          | 1914-06-29_7 |  0.219934   |  0.057982    | 0.954184   |
| 116 | dots_ocr_9_three_shot                    | 1918-12-27_2 |  0.386733   |  0.0539706   | 0.960985   |
| 117 | dots_ocr_3_default                       | 1918-12-27_2 |  0.405787   |  0.0516947   | 0.961521   |
| 118 | anno                                     | 1917-12-28_3 |  0.259978   |  0.0557485   | 0.955512   |
| 119 | dots_ocr_1_default                       | 1918-12-27_4 |  0.368657   |  0.057528    | 0.960182   |
| 120 | dots_ocr_1_default                       | 1918-12-27_5 |  0.383375   |  0.0501503   | 0.959637   |
| 121 | churro_2_german_extensive_2              | 1918-12-27_1 |  0.294971   |  0.0483887   | 0.955578   |
| 122 | dots_ocr_8_one_shot                      | 1917-12-28_1 |  0.226852   |  0.0793984   | 0.954894   |
| 123 | churro_5_one_shot_s_replaced             | 1914-06-29_5 |  0.129371   |  0.0894364   | 0.951179   |
| 124 | churro_3_english_extensive_3             | 1914-06-29_3 |  0.363748   |  0.0555385   | 0.958147   |
| 125 | dots_ocr_4_default                       | 1918-12-27_5 |  0.386476   |  0.0505169   | 0.958515   |
| 126 | churro_1_simple                          | 1918-12-27_1 |  0.300774   |  0.0501279   | 0.954093   |
| 127 | dots_ocr_3_default                       | 1918-12-27_5 |  0.400124   |  0.0542562   | 0.958533   |
| 128 | dots_ocr_4_default                       | 1914-06-29_1 |  0.22121    |  0.0783005   | 0.952744   |
| 129 | churro_4_one_shot                        | 1914-06-29_7 |  0.231466   |  0.0634009   | 0.951549   |
| 130 | anno                                     | 1915-12-28_3 |  0.258993   |  0.0598589   | 0.95202    |
| 131 | churro_2_german_extensive_2              | 1917-12-28_3 |  0.355448   |  0.0610854   | 0.954735   |
| 132 | dots_ocr_7_german_extensive_2            | 1914-06-29_1 |  0.247722   |  0.0804249   | 0.951428   |
| 133 | dots_ocr_8_one_shot                      | 1914-06-29_1 |  0.246893   |  0.0813354   | 0.950922   |
| 134 | anno                                     | 1918-12-27_2 |  0.243472   |  0.0604731   | 0.948825   |
| 135 | churro_2_german_extensive_2              | 1914-06-29_4 |  0.279698   |  0.0652958   | 0.948812   |
| 136 | dots_ocr_6_english_extensive             | 1914-06-29_3 |  0.250308   |  0.0858043   | 0.948473   |
| 137 | churro_3_english_extensive_3             | 1914-06-29_4 |  0.290383   |  0.0658329   | 0.947405   |
| 138 | dots_ocr_3_default                       | 1914-06-29_1 |  0.261806   |  0.0911482   | 0.946566   |
| 139 | dots_ocr_10_one_shot_english_extensive   | 1918-12-27_5 |  0.238834   |  0.0692866   | 0.942133   |
| 140 | churro_1_simple                          | 1914-06-29_5 |  0.311888   |  0.0689743   | 0.944607   |
| 141 | dots_ocr_6_english_extensive             | 1914-06-29_5 |  0.393706   |  0.0812516   | 0.948919   |
| 142 | dots_ocr_7_german_extensive_2            | 1914-06-29_5 |  0.395804   |  0.0819337   | 0.948525   |
| 143 | dots_ocr_7_german_extensive_2            | 1917-12-28_3 |  0.380798   |  0.0766461   | 0.947396   |
| 144 | dots_ocr_3_default                       | 1914-06-29_5 |  0.394406   |  0.0821042   | 0.948318   |
| 145 | dots_ocr_10_one_shot_english_extensive   | 1914-06-29_5 |  0.413986   |  0.0764771   | 0.948198   |
| 146 | dots_ocr_8_one_shot                      | 1914-06-29_5 |  0.415385   |  0.0770739   | 0.947904   |
| 147 | pero_ocr                                 | average      |  0.133106   |  0.0932532   | 0.936977   |
| 148 | churro_3_english_extensive_3             | 1914-06-29_7 |  0.249588   |  0.0793324   | 0.940185   |
| 149 | anno                                     | 1918-12-27_3 |  0.254967   |  0.0709265   | 0.939721   |
| 150 | transkribus                              | 1917-12-28_2 |  0.234996   |  0.103391    | 0.940797   |
| 151 | transkribus                              | 1917-12-28_3 |  0.21575    |  0.111883    | 0.940464   |
| 152 | churro_5_one_shot_s_replaced             | 1918-12-27_4 |  0.15597    |  0.111884    | 0.937466   |
| 153 | anno                                     | 1917-12-28_1 |  0.196296   |  0.0735375   | 0.935992   |
| 154 | churro_4_one_shot                        | 1918-12-27_4 |  0.157463   |  0.112237    | 0.937098   |
| 155 | dots_ocr_1_default                       | 1915-12-28_4 |  0.402418   |  0.0805007   | 0.944396   |
| 156 | dots_ocr_4_default                       | 1918-12-27_1 |  0.412959   |  0.0875703   | 0.943946   |
| 157 | dots_ocr_4_default                       | 1915-12-28_4 |  0.405872   |  0.0859894   | 0.941663   |
| 158 | churro_1_simple                          | 1915-12-28_4 |  0.326425   |  0.0808859   | 0.936187   |
| 159 | dots_ocr_4_default                       | 1917-12-28_1 |  0.392593   |  0.0989716   | 0.938645   |
| 160 | churro_2_german_extensive_2              | 1914-06-29_3 |  0.461776   |  0.077124    | 0.936985   |
| 161 | anno                                     | 1915-12-28_1 |  0.218905   |  0.0836584   | 0.926895   |
| 162 | churro_7_two_shot_prompts_adapted        | 1918-12-27_1 |  0.37234    |  0.0959591   | 0.933704   |
| 163 | churro_3_english_extensive_3             | 1917-12-28_3 |  0.450378   |  0.0799897   | 0.935644   |
| 164 | churro_2_german_extensive_2              | 1918-12-27_3 |  0.453642   |  0.0771565   | 0.934948   |
| 165 | churro_1_simple                          | 1914-06-29_2 |  0.478523   |  0.0785702   | 0.935781   |
| 166 | deepseek_ocr_1_default                   | 1914-06-29_4 |  0.461974   |  0.0794905   | 0.935043   |
| 167 | anno                                     | 1914-06-29_1 |  0.300746   |  0.0891249   | 0.927337   |
| 168 | transkribus                              | 1914-06-29_1 |  0.263463   |  0.121396    | 0.925798   |
| 169 | anno                                     | 1918-12-27_1 |  0.312379   |  0.0818414   | 0.923912   |
| 170 | google_gemini_2_extensive                | 1915-12-28_2 |  0.201822   |  0.136697    | 0.922991   |
| 171 | transkribus                              | 1918-12-27_1 |  0.240812   |  0.115601    | 0.922462   |
| 172 | google_gemini_1_simple                   | 1914-06-29_1 |  0.401823   |  0.11998     | 0.92941    |
| 173 | churro_2_german_extensive_2              | 1914-06-29_5 |  0.488112   |  0.0864524   | 0.930287   |
| 174 | transkribus                              | 1918-12-27_5 |  0.256203   |  0.139013    | 0.924406   |
| 175 | churro_3_english_extensive_3             | 1914-06-29_5 |  0.493706   |  0.0919942   | 0.927858   |
| 176 | dots_ocr_11_three_shot_english_extensive | 1918-12-27_2 |  0.241355   |  0.0976185   | 0.916762   |
| 177 | churro_2_german_extensive_2              | 1914-06-29_1 |  0.309031   |  0.101062    | 0.915847   |
| 178 | churro_4_one_shot                        | 1914-06-29_5 |  0.343357   |  0.121579    | 0.917895   |
| 179 | churro_3_english_extensive_3             | 1914-06-29_2 |  0.55162    |  0.0982128   | 0.92442    |
| 180 | deepseek_ocr_2_german_extensive_2        | 1914-06-29_3 |  0.493218   |  0.101475    | 0.917959   |
| 181 | dots_ocr_1_default                       | average      |  0.375395   |  0.111459    | 0.908511   |
| 182 | deepseek_ocr_2_german_extensive_2        | 1914-06-29_5 |  0.525874   |  0.113394    | 0.912624   |
| 183 | deepseek_ocr_3_english_extensive_2       | 1914-06-29_4 |  0.522942   |  0.123456    | 0.912195   |
| 184 | pero_scribblesense                       | 1918-12-27_1 |  0.222437   |  0.193555    | 0.901514   |
| 185 | transkribus                              | 1917-12-28_1 |  0.305556   |  0.161672    | 0.902228   |
| 186 | churro_2_german_extensive_2              | 1914-06-29_2 |  0.341372   |  0.0622155   | 0.892892   |
| 187 | deepseek_ocr_1_default                   | 1914-06-29_3 |  0.603576   |  0.127823    | 0.908716   |
| 188 | deepseek_ocr_1_default                   | 1914-06-29_2 |  0.583271   |  0.125358    | 0.905741   |
| 189 | deepseek_ocr_1_default                   | 1915-12-28_3 |  0.545455   |  0.123905    | 0.90059    |
| 190 | deepseek_ocr_1_default                   | 1914-06-29_5 |  0.66993    |  0.127121    | 0.905066   |
| 191 | dots_ocr_4_default                       | average      |  0.395548   |  0.139265    | 0.893762   |
| 192 | churro_1_simple                          | 1917-12-28_1 |  0.480556   |  0.148291    | 0.893481   |
| 193 | transkribus                              | 1915-12-28_3 |  0.306736   |  0.206482    | 0.890066   |
| 194 | transkribus                              | 1918-12-27_6 |  0.325175   |  0.167048    | 0.882608   |
| 195 | dots_ocr_3_default                       | 1917-12-28_4 |  0.539335   |  0.174818    | 0.891038   |
| 196 | dots_ocr_1_default                       | 1917-12-28_4 |  0.42498    |  0.195835    | 0.885436   |
| 197 | transkribus                              | 1917-12-28_4 |  0.344688   |  0.17724     | 0.87753    |
| 198 | deepseek_ocr_1_default                   | 1914-06-29_7 |  0.526359   |  0.163       | 0.883      |
| 199 | anno                                     | average      |  0.353684   |  0.165366    | 0.875643   |
| 200 | dots_ocr_4_default                       | 1917-12-28_4 |  0.435523   |  0.206199    | 0.880985   |
| 201 | deepseek_ocr_2_german_extensive_2        | 1914-06-29_4 |  0.583909   |  0.180618    | 0.883448   |
| 202 | dots_ocr_10_one_shot_english_extensive   | 1917-12-28_4 |  0.52717    |  0.222857    | 0.876818   |
| 203 | google_gemini_2_extensive                | 1914-06-29_7 |  0.329489   |  0.256963    | 0.869047   |
| 204 | anno                                     | 1915-12-28_4 |  0.444732   |  0.154068    | 0.865014   |
| 205 | dots_ocr_8_one_shot                      | 1918-12-27_5 |  0.439826   |  0.262556    | 0.873166   |
| 206 | churro_1_simple                          | 1914-06-29_1 |  0.533554   |  0.176227    | 0.868022   |
| 207 | churro_3_english_extensive_3             | 1918-12-27_5 |  0.168734   |  0.307501    | 0.859057   |
| 208 | dots_ocr_8_one_shot                      | 1915-12-28_3 |  0.125572   |  0.32085     | 0.8567     |
| 209 | dots_ocr_10_one_shot_english_extensive   | 1915-12-28_3 |  0.146501   |  0.325114    | 0.854419   |
| 210 | google_gemini_2_extensive                | 1917-12-28_4 |  0.426602   |  0.232833    | 0.858192   |
| 211 | transkribus                              | average      |  0.366217   |  0.245052    | 0.851322   |
| 212 | deepseek_ocr_2_german_extensive_2        | 1914-06-29_7 |  0.546952   |  0.21513     | 0.844804   |
| 213 | deepseek_ocr_1_default                   | 1914-06-29_1 |  0.815244   |  0.207284    | 0.855559   |
| 214 | deepseek_ocr_1_default                   | 1915-12-28_1 |  0.890547   |  0.187538    | 0.856519   |
| 215 | google_vision                            | 1914-06-29_5 |  0.425874   |  0.312985    | 0.837852   |
| 216 | deepseek_ocr_1_default                   | 1918-12-27_4 |  0.909701   |  0.183949    | 0.848251   |
| 217 | dots_ocr_8_one_shot                      | 1917-12-28_4 |  0.553122   |  0.289685    | 0.835604   |
| 218 | deepseek_ocr_1_default                   | 1918-12-27_1 |  0.775629   |  0.202762    | 0.837181   |
| 219 | pero_scribblesense                       | 1918-12-27_5 |  0.361663   |  0.297236    | 0.822145   |
| 220 | deepseek_ocr_3_english_extensive_2       | 1914-06-29_3 |  0.766338   |  0.307344    | 0.832255   |
| 221 | dots_ocr_4_default                       | 1918-12-27_6 |  0.481352   |  0.345401    | 0.81918    |
| 222 | anno                                     | 1918-12-27_6 |  0.576923   |  0.225356    | 0.808505   |
| 223 | deepseek_ocr_3_english_extensive_2       | 1918-12-27_1 |  1.23694    |  0.223223    | 0.832773   |
| 224 | deepseek_ocr_3_english_extensive_2       | 1914-06-29_7 |  0.744646   |  0.315054    | 0.818439   |
| 225 | google_gemini_2_extensive                | 1914-06-29_3 |  0.466708   |  0.328315    | 0.806858   |
| 226 | google_gemini_2_extensive                | 1917-12-28_1 |  0.486111   |  0.319252    | 0.80688    |
| 227 | churro_1_simple                          | 1917-12-28_4 |  0.626115   |  0.305182    | 0.808221   |
| 228 | churro_3_english_extensive_3             | 1917-12-28_4 |  0.626926   |  0.307215    | 0.807862   |
| 229 | transkribus                              | 1914-06-29_7 |  0.4514     |  0.333586    | 0.801892   |
| 230 | google_gemini_1_simple                   | 1915-12-28_2 |  0.419762   |  0.351008    | 0.800367   |
| 231 | dots_ocr_8_one_shot                      | 1915-12-28_1 |  0.450249   |  0.377951    | 0.800907   |
| 232 | google_vision                            | 1917-12-28_4 |  0.450933   |  0.280291    | 0.79145    |
| 233 | dots_ocr_6_english_extensive             | 1914-06-29_7 |  0.512356   |  0.328492    | 0.797508   |
| 234 | churro_6_two_shot                        | 1914-06-29_4 |  0.529227   |  0.292181    | 0.794257   |
| 235 | dots_ocr_10_one_shot_english_extensive   | 1914-06-29_1 |  0.144159   |  0.500455    | 0.79307    |
| 236 | dots_ocr_10_one_shot_english_extensive   | average      |  0.654173   |  0.372187    | 0.802963   |
| 237 | churro_7_two_shot_prompts_adapted        | 1914-06-29_4 |  0.47643    |  0.27415     | 0.786714   |
| 238 | dots_ocr_1_default                       | 1918-12-27_6 |  0.518648   |  0.335747    | 0.793388   |
| 239 | dots_ocr_8_one_shot                      | average      |  1.03834    |  0.383743    | 0.812961   |
| 240 | dots_ocr_11_three_shot_english_extensive | 1914-06-29_3 |  0.49815    |  0.383623    | 0.788911   |
| 241 | dots_ocr_9_three_shot                    | 1914-06-29_2 |  0.392615   |  0.0359973   | 0.753037   |
| 242 | google_gemini_2_extensive                | average      |  0.44454    |  0.307135    | 0.776846   |
| 243 | dots_ocr_10_one_shot_english_extensive   | 1914-06-29_2 |  0.390354   |  0.0363345   | 0.752353   |
| 244 | dots_ocr_8_one_shot                      | 1914-06-29_2 |  0.392615   |  0.0371775   | 0.752352   |
| 245 | dots_ocr_11_three_shot_english_extensive | 1914-06-29_2 |  0.392615   |  0.0383578   | 0.751655   |
| 246 | dots_ocr_4_default                       | 1914-06-29_2 |  0.364732   |  0.0425729   | 0.749683   |
| 247 | dots_ocr_1_default                       | 1914-06-29_2 |  0.363979   |  0.0427415   | 0.749493   |
| 248 | dots_ocr_3_default                       | 1914-06-29_2 |  0.406179   |  0.0444276   | 0.74979    |
| 249 | dots_ocr_7_german_extensive_2            | 1914-06-29_2 |  0.406933   |  0.0448491   | 0.74959    |
| 250 | anno                                     | 1917-12-28_4 |  0.586375   |  0.29414     | 0.769756   |
| 251 | google_gemini_1_simple                   | 1914-06-29_3 |  0.540074   |  0.298049    | 0.763571   |
| 252 | dots_ocr_4_default                       | 1914-06-29_7 |  0.537891   |  0.369026    | 0.767751   |
| 253 | churro_5_one_shot_s_replaced             | 1914-06-29_4 |  0.370836   |  0.294407    | 0.754049   |
| 254 | google_gemini_1_simple                   | 1918-12-27_5 |  0.586228   |  0.307134    | 0.761032   |
| 255 | dots_ocr_7_german_extensive_2            | 1918-12-27_5 |  0.584367   |  0.371508    | 0.764633   |
| 256 | dots_ocr_9_three_shot                    | 1914-06-29_7 |  0.227348   |  0.60052     | 0.757934   |
| 257 | google_gemini_1_simple                   | average      |  0.494179   |  0.311479    | 0.744457   |
| 258 | pero_scribblesense                       | average      |  0.435307   |  0.356931    | 0.745592   |
| 259 | google_gemini_1_simple                   | 1914-06-29_7 |  0.679572   |  0.381923    | 0.758004   |
| 260 | google_gemini_2_extensive                | 1914-06-29_4 |  0.540541   |  0.407427    | 0.751628   |
| 261 | google_gemini_1_simple                   | 1915-12-28_3 |  0.537606   |  0.387454    | 0.745255   |
| 262 | dots_ocr_3_default                       | average      |  1.19758    |  0.4477      | 0.775211   |
| 263 | deepseek_ocr_1_default                   | 1917-12-28_3 |  0.68123    |  0.344329    | 0.742817   |
| 264 | churro_5_one_shot_s_replaced             | 1917-12-28_1 |  0.439815   |  0.435364    | 0.739666   |
| 265 | churro_4_one_shot                        | 1914-06-29_4 |  0.516028   |  0.316888    | 0.732514   |
| 266 | google_gemini_2_extensive                | 1918-12-27_6 |  0.493007   |  0.349593    | 0.732338   |
| 267 | churro_7_two_shot_prompts_adapted        | 1917-12-28_4 |  0.604217   |  0.35138     | 0.736386   |
| 268 | churro_4_one_shot                        | 1917-12-28_1 |  0.467593   |  0.439124    | 0.735414   |
| 269 | google_vision                            | 1915-12-28_2 |  0.583041   |  0.434597    | 0.735363   |
| 270 | google_gemini_2_extensive                | 1918-12-27_3 |  0.537086   |  0.432668    | 0.731799   |
| 271 | pero_scribblesense                       | 1914-06-29_3 |  0.545623   |  0.471194    | 0.733945   |
| 272 | google_vision                            | 1915-12-28_3 |  0.590582   |  0.417306    | 0.717829   |
| 273 | dots_ocr_10_one_shot_english_extensive   | 1917-12-28_3 |  0.667745   |  0.31668     | 0.711526   |
| 274 | churro_3_english_extensive_3             | 1917-12-28_1 |  0.689815   |  0.476059    | 0.724821   |
| 275 | deepseek_ocr_3_english_extensive_2       | 1917-12-28_3 |  0.650485   |  0.290766    | 0.702167   |
| 276 | google_gemini_1_simple                   | 1917-12-28_3 |  0.658576   |  0.355646    | 0.706513   |
| 277 | google_vision                            | 1918-12-27_3 |  0.639073   |  0.471486    | 0.707138   |
| 278 | google_gemini_1_simple                   | 1915-12-28_1 |  0.483416   |  0.38257     | 0.692284   |
| 279 | deepseek_ocr_1_default                   | 1917-12-28_2 |  0.627219   |  0.394159    | 0.691943   |
| 280 | churro_7_two_shot_prompts_adapted        | 1918-12-27_4 |  0.638806   |  0.378645    | 0.690599   |
| 281 | dots_ocr_9_three_shot                    | 1918-12-27_5 |  0.691067   |  0.728866    | 0.721003   |
| 282 | deepseek_ocr_2_german_extensive_2        | 1915-12-28_3 |  1.73316    |  0.381019    | 0.737336   |
| 283 | google_gemini_1_simple                   | 1917-12-28_1 |  0.559259   |  0.405728    | 0.682426   |
| 284 | deepseek_ocr_1_default                   | average      |  1.14348    |  0.389409    | 0.699894   |
| 285 | churro_6_two_shot                        | 1917-12-28_1 |  0.490741   |  0.407829    | 0.671701   |
| 286 | pero_scribblesense                       | 1918-12-27_3 |  0.623179   |  0.507268    | 0.684692   |
| 287 | pero_ocr                                 | 1918-12-27_6 |  0.631702   |  0.475864    | 0.68218    |
| 288 | dots_ocr_8_one_shot                      | 1917-12-28_3 |  0.710356   |  0.455183    | 0.68332    |
| 289 | pero_ocr                                 | 1915-12-28_4 |  0.603627   |  0.47713     | 0.679785   |
| 290 | google_vision                            | 1917-12-28_1 |  0.573148   |  0.389804    | 0.666925   |
| 291 | transkribus                              | 1915-12-28_4 |  0.637306   |  0.506307    | 0.674967   |
| 292 | dots_ocr_9_three_shot                    | 1918-12-27_3 |  1.00331    |  0.765016    | 0.709259   |
| 293 | dots_ocr_8_one_shot                      | 1917-12-28_2 |  0.612849   |  0.453352    | 0.666699   |
| 294 | google_gemini_2_extensive                | 1914-06-29_2 |  0.743783   |  0.456331    | 0.671674   |
| 295 | dots_ocr_1_default                       | 1917-12-28_2 |  0.764159   |  0.453156    | 0.667783   |
| 296 | churro_6_two_shot                        | 1914-06-29_5 |  1.01958    |  0.649416    | 0.692972   |
| 297 | google_gemini_1_simple                   | 1918-12-27_3 |  0.744371   |  0.427875    | 0.658235   |
| 298 | dots_ocr_11_three_shot_english_extensive | 1915-12-28_2 |  0.615978   |  0.512637    | 0.658543   |
| 299 | google_vision                            | 1914-06-29_1 |  0.685998   |  0.493576    | 0.658921   |
| 300 | google_gemini_1_simple                   | 1915-12-28_4 |  0.698618   |  0.501107    | 0.659753   |
| 301 | dots_ocr_4_default                       | 1917-12-28_2 |  0.765004   |  0.460212    | 0.657528   |
| 302 | transkribus                              | 1914-06-29_2 |  0.706104   |  0.655539    | 0.670269   |
| 303 | transkribus                              | 1915-12-28_2 |  0.74562    |  0.577698    | 0.661389   |
| 304 | dots_ocr_7_german_extensive_2            | 1915-12-28_1 |  0.994196   |  0.709095    | 0.678387   |
| 305 | dots_ocr_3_default                       | 1915-12-28_1 |  1.00746    |  0.710532    | 0.67722    |
| 306 | google_gemini_1_simple                   | 1918-12-27_4 |  0.642537   |  0.467184    | 0.639584   |
| 307 | pero_scribblesense                       | 1915-12-28_3 |  0.746239   |  0.578429    | 0.65238    |
| 308 | churro_1_simple                          | 1918-12-27_4 |  0.680597   |  0.887235    | 0.674219   |
| 309 | pero_ocr                                 | 1917-12-28_2 |  0.537616   |  0.486672    | 0.634696   |
| 310 | dots_ocr_7_german_extensive_2            | average      |  1.39594    |  0.595056    | 0.675828   |
| 311 | dots_ocr_11_three_shot_english_extensive | 1915-12-28_1 |  0.930348   |  0.803018    | 0.672044   |
| 312 | pero_scribblesense                       | 1915-12-28_2 |  0.51857    |  0.453296    | 0.623154   |
| 313 | google_vision                            | 1915-12-28_4 |  0.717617   |  0.522581    | 0.637145   |
| 314 | google_vision                            | 1914-06-29_4 |  0.783155   |  0.61866     | 0.647705   |
| 315 | pero_scribblesense                       | 1917-12-28_3 |  0.633225   |  0.559606    | 0.633985   |
| 316 | churro_5_one_shot_s_replaced             | 1917-12-28_3 |  0.118123   |  1.01376     | 0.646798   |
| 317 | dots_ocr_6_english_extensive             | 1917-12-28_3 |  1.26645    |  0.838606    | 0.679016   |
| 318 | deepseek_ocr_1_default                   | 1918-12-27_6 |  0.777389   |  0.417937    | 0.621929   |
| 319 | deepseek_ocr_1_default                   | 1918-12-27_3 |  0.813245   |  0.386981    | 0.619905   |
| 320 | churro_2_german_extensive_2              | 1917-12-28_1 |  0.761111   |  0.492646    | 0.624936   |
| 321 | anno                                     | 1915-12-28_2 |  0.769446   |  0.627305    | 0.631292   |
| 322 | transkribus                              | 1914-06-29_5 |  0.766434   |  0.617614    | 0.629737   |
| 323 | dots_ocr_7_german_extensive_2            | 1915-12-28_2 |  0.853539   |  0.52792     | 0.62589    |
| 324 | dots_ocr_1_default                       | 1915-12-28_2 |  0.683952   |  0.515967    | 0.609749   |
| 325 | dots_ocr_10_one_shot_english_extensive   | 1915-12-28_1 |  0.447761   |  0.902895    | 0.630906   |
| 326 | pero_scribblesense                       | 1917-12-28_2 |  0.764159   |  0.681889    | 0.626416   |
| 327 | anno                                     | 1918-12-27_5 |  0.783499   |  0.512721    | 0.611949   |
| 328 | pero_scribblesense                       | 1915-12-28_1 |  0.752073   |  0.695853    | 0.624737   |
| 329 | churro_3_english_extensive_3             | average      |  1.32015    |  1.19497     | 0.689033   |
| 330 | dots_ocr_4_default                       | 1915-12-28_2 |  0.688157   |  0.520833    | 0.606607   |
| 331 | churro_7_two_shot_prompts_adapted        | 1915-12-28_1 |  1.07463    |  0.709916    | 0.638014   |
| 332 | churro_4_one_shot                        | 1917-12-28_3 |  0.26753    |  1.03832     | 0.629718   |
| 333 | dots_ocr_3_default                       | 1915-12-28_2 |  0.711282   |  0.522029    | 0.605594   |
| 334 | dots_ocr_10_one_shot_english_extensive   | 1915-12-28_2 |  0.711282   |  0.521346    | 0.605405   |
| 335 | dots_ocr_8_one_shot                      | 1915-12-28_2 |  0.709881   |  0.522114    | 0.604868   |
| 336 | dots_ocr_6_english_extensive             | 1915-12-28_2 |  0.717589   |  0.522199    | 0.605174   |
| 337 | dots_ocr_6_english_extensive             | 1918-12-27_4 |  0.743284   |  0.450533    | 0.588584   |
| 338 | churro_1_simple                          | 1918-12-27_5 |  0.226427   |  1.15214     | 0.6201     |
| 339 | deepseek_ocr_2_german_extensive_2        | 1917-12-28_2 |  0.78022    |  0.4559      | 0.587285   |
| 340 | google_vision                            | 1915-12-28_1 |  0.798507   |  0.565079    | 0.588478   |
| 341 | google_gemini_2_extensive                | 1918-12-27_1 |  0.766925   |  0.576675    | 0.582611   |
| 342 | deepseek_ocr_1_default                   | 1917-12-28_1 |  1.27963    |  0.570386    | 0.602334   |
| 343 | dots_ocr_10_one_shot_english_extensive   | 1917-12-28_2 |  0.853762   |  0.480988    | 0.571781   |
| 344 | pero_scribblesense                       | 1917-12-28_1 |  0.746296   |  0.566405    | 0.568996   |
| 345 | deepseek_ocr_3_english_extensive_2       | 1918-12-27_4 |  2.44776    |  0.417056    | 0.630295   |
| 346 | google_vision                            | average      |  0.755417   |  0.560567    | 0.567721   |
| 347 | google_vision                            | 1918-12-27_6 |  0.750583   |  0.580666    | 0.558541   |
| 348 | churro_2_german_extensive_2              | 1917-12-28_2 |  0.842773   |  0.639063    | 0.563209   |
| 349 | google_gemini_2_extensive                | 1915-12-28_1 |  0.725539   |  0.548347    | 0.543732   |
| 350 | transkribus                              | 1915-12-28_1 |  0.819237   |  0.607165    | 0.545237   |
| 351 | dots_ocr_11_three_shot_english_extensive | average      |  1.6141     |  0.799486    | 0.580411   |
| 352 | churro_2_german_extensive_2              | average      |  2.59321    |  1.42016     | 0.672601   |
| 353 | deepseek_ocr_1_default                   | 1915-12-28_2 |  1.66013    |  0.585212    | 0.563911   |
| 354 | google_gemini_1_simple                   | 1918-12-27_6 |  0.861305   |  0.658028    | 0.534312   |
| 355 | deepseek_ocr_3_english_extensive_2       | 1915-12-28_2 |  1.66643    |  0.588712    | 0.562515   |
| 356 | churro_6_two_shot                        | 1918-12-27_5 |  1.11849    |  0.867806    | 0.545977   |
| 357 | google_gemini_2_extensive                | 1915-12-28_4 |  0.643351   |  0.470871    | 0.492901   |
| 358 | dots_ocr_9_three_shot                    | 1918-12-27_6 |  1.68531    |  0.875127    | 0.567128   |
| 359 | deepseek_ocr_2_german_extensive_2        | 1915-12-28_2 |  1.90399    |  0.596141    | 0.552754   |
| 360 | churro_3_english_extensive_3             | 1918-12-27_6 |  1.61072    |  1.2608      | 0.585403   |
| 361 | churro_2_german_extensive_2              | 1915-12-28_1 |  0.685738   |  0.36512     | 0.471829   |
| 362 | dots_ocr_6_english_extensive             | average      |  1.74008    |  0.8115      | 0.552949   |
| 363 | google_gemini_1_simple                   | 1917-12-28_4 |  0.510138   |  0.219758    | 0.447802   |
| 364 | churro_3_english_extensive_3             | 1915-12-28_1 |  0.728856   |  0.403921    | 0.469562   |
| 365 | google_vision                            | 1917-12-28_3 |  0.874865   |  0.660237    | 0.494623   |
| 366 | dots_ocr_3_default                       | 1917-12-28_1 |  0.714815   |  0.418445    | 0.464886   |
| 367 | deepseek_ocr_3_english_extensive_2       | 1915-12-28_3 |  1.51799    |  0.927037    | 0.535906   |
| 368 | dots_ocr_11_three_shot_english_extensive | 1915-12-28_4 |  4.22625    |  0.943091    | 0.653467   |
| 369 | dots_ocr_8_one_shot                      | 1915-12-28_4 |  4.26166    |  0.943765    | 0.65138    |
| 370 | anno                                     | 1917-12-28_2 |  0.845309   |  0.709918    | 0.481758   |
| 371 | dots_ocr_11_three_shot_english_extensive | 1918-12-27_5 |  1.11166    |  0.721021    | 0.491698   |
| 372 | google_vision                            | 1914-06-29_2 |  0.894499   |  0.685888    | 0.471246   |
| 373 | google_vision                            | 1918-12-27_4 |  0.840299   |  0.640825    | 0.459222   |
| 374 | deepseek_ocr_3_english_extensive_2       | 1918-12-27_3 |  3.02848    |  0.579952    | 0.545857   |
| 375 | dots_ocr_10_one_shot_english_extensive   | 1915-12-28_4 |  4.54404    |  0.968512    | 0.642943   |
| 376 | dots_ocr_3_default                       | 1915-12-28_4 |  4.58463    |  0.985364    | 0.639641   |
| 377 | churro_1_simple                          | 1917-12-28_2 |  1.09045    |  1.13583     | 0.498904   |
| 378 | google_gemini_2_extensive                | 1917-12-28_3 |  1.09871    |  0.888503    | 0.475078   |
| 379 | google_gemini_2_extensive                | 1918-12-27_2 |  0.697248   |  0.533366    | 0.428552   |
| 380 | google_vision                            | 1918-12-27_1 |  0.905222   |  0.680818    | 0.448791   |
| 381 | churro_8_two_shot_zero_temperature       | 1914-06-29_3 |  0.885327   |  0.662237    | 0.440485   |
| 382 | churro_9_two_shot_zero_temperature       | 1914-06-29_3 |  0.885327   |  0.662237    | 0.440485   |
| 383 | churro_7_two_shot_prompts_adapted        | 1915-12-28_4 |  0.772021   |  0.552817    | 0.421942   |
| 384 | dots_ocr_9_three_shot                    | average      |  1.50339    |  0.989444    | 0.468237   |
| 385 | dots_ocr_9_three_shot                    | 1914-06-29_1 |  1.76139    |  1.4867      | 0.51928    |
| 386 | dots_ocr_7_german_extensive_2            | 1917-12-28_2 |  0.742181   |  0.651901    | 0.407204   |
| 387 | dots_ocr_6_english_extensive             | 1918-12-27_5 |  0.870347   |  0.668304    | 0.413298   |
| 388 | pero_scribblesense                       | 1915-12-28_4 |  0.670984   |  0.510833    | 0.391256   |
| 389 | churro_1_simple                          | average      |  2.70403    |  2.27372     | 0.617446   |
| 390 | deepseek_ocr_3_english_extensive_2       | 1918-12-27_2 |  0.89626    |  0.728521    | 0.410984   |
| 391 | google_vision                            | 1918-12-27_5 |  0.823821   |  0.600191    | 0.395568   |
| 392 | dots_ocr_10_one_shot_english_extensive   | 1918-12-27_6 |  0.658508   |  1.30132     | 0.445243   |
| 393 | google_vision                            | 1918-12-27_2 |  1.00988    |  0.774608    | 0.414578   |
| 394 | dots_ocr_3_default                       | 1918-12-27_1 |  1.47776    |  1.73903     | 0.510826   |
| 395 | deepseek_ocr_2_german_extensive_2        | 1915-12-28_4 |  3.88428    |  0.586904    | 0.520543   |
| 396 | deepseek_ocr_1_default                   | 1915-12-28_4 |  3.70725    |  0.560327    | 0.509446   |
| 397 | pero_scribblesense                       | 1918-12-27_6 |  0.903263   |  0.71532     | 0.398989   |
| 398 | dots_ocr_11_three_shot_english_extensive | 1915-12-28_3 |  1.51406    |  1.05939     | 0.448973   |
| 399 | churro_3_english_extensive_3             | 1918-12-27_2 |  1.0247     |  1.7421      | 0.482313   |
| 400 | google_vision                            | 1917-12-28_2 |  0.831784   |  0.641513    | 0.379067   |
| 401 | deepseek_ocr_3_english_extensive_2       | 1915-12-28_4 |  4.04404    |  0.572075    | 0.512285   |
| 402 | google_vision                            | 1914-06-29_3 |  0.954994   |  0.725918    | 0.390786   |
| 403 | deepseek_ocr_3_english_extensive_2       | average      |  2.07321    |  0.875675    | 0.444159   |
| 404 | churro_3_english_extensive_3             | 1917-12-28_2 |  0.996619   |  0.991768    | 0.397735   |
| 405 | dots_ocr_10_one_shot_english_extensive   | 1917-12-28_1 |  1.69352    |  1.47761     | 0.462332   |
| 406 | deepseek_ocr_1_default                   | 1918-12-27_2 |  0.880028   |  0.599122    | 0.34967    |
| 407 | dots_ocr_6_english_extensive             | 1917-12-28_1 |  0.928704   |  0.658963    | 0.353409   |
| 408 | google_vision                            | 1914-06-29_7 |  0.974465   |  0.714317    | 0.353195   |
| 409 | deepseek_ocr_2_german_extensive_2        | average      |  1.42227    |  0.75836     | 0.367408   |
| 410 | deepseek_ocr_3_english_extensive_2       | 1914-06-29_2 |  2.49058    |  1.41873     | 0.456818   |
| 411 | dots_ocr_8_one_shot                      | 1918-12-27_1 |  2.61219    |  1.93678     | 0.484045   |
| 412 | churro_7_two_shot_prompts_adapted        | 1917-12-28_2 |  0.800507   |  0.665229    | 0.290938   |
| 413 | churro_6_two_shot                        | 1917-12-28_4 |  1.05028    |  0.812494    | 0.307404   |
| 414 | pero_scribblesense                       | 1917-12-28_4 |  1.00324    |  0.818983    | 0.30235    |
| 415 | churro_6_two_shot                        | 1914-06-29_7 |  1.44893    |  1.19031     | 0.329041   |
| 416 | dots_ocr_11_three_shot_english_extensive | 1914-06-29_1 |  2.07125    |  1.67203     | 0.392576   |
| 417 | churro_5_one_shot_s_replaced             | 1918-12-27_5 |  0.920596   |  1.68927     | 0.339087   |
| 418 | churro_5_one_shot_s_replaced             | 1915-12-28_3 |  0.551341   |  2.65        | 0.399768   |
| 419 | churro_4_one_shot                        | 1915-12-28_3 |  0.555265   |  2.65046     | 0.399558   |
| 420 | churro_4_one_shot                        | 1918-12-27_5 |  0.939826   |  1.69529     | 0.338393   |
| 421 | openai_2_extensive                       | 1915-12-28_2 |  0.920112   |  0.699283    | 0.252545   |
| 422 | dots_ocr_6_english_extensive             | 1915-12-28_1 |  2.58789    |  1.93051     | 0.42068    |
| 423 | churro_8_two_shot_zero_temperature       | 1914-06-29_4 |  0.664991   |  1.68304     | 0.305335   |
| 424 | churro_9_two_shot_zero_temperature       | 1914-06-29_4 |  0.664991   |  1.68304     | 0.305335   |
| 425 | deepseek_ocr_2_german_extensive_2        | 1918-12-27_6 |  2.00699    |  1.44944     | 0.337644   |
| 426 | dots_ocr_11_three_shot_english_extensive | 1917-12-28_3 |  1.29666    |  0.922518    | 0.262593   |
| 427 | deepseek_ocr_1_default                   | 1918-12-27_5 |  2.67308    |  1.12963     | 0.336905   |
| 428 | deepseek_ocr_2_german_extensive_2        | 1917-12-28_3 |  2.35545    |  0.727816    | 0.285069   |
| 429 | google_gemini_1_simple                   | 1918-12-27_2 |  0.904728   |  0.800618    | 0.227156   |
| 430 | dots_ocr_6_english_extensive             | 1915-12-28_4 |  5.38083    |  1.42937     | 0.46491    |
| 431 | deepseek_ocr_2_german_extensive_2        | 1917-12-28_4 |  1.58962    |  1.27564     | 0.278401   |
| 432 | deepseek_ocr_3_english_extensive_2       | 1917-12-28_2 |  4.32122    |  1.43953     | 0.408446   |
| 433 | churro_1_simple                          | 1918-12-27_3 |  2.97947    |  2.51518     | 0.430387   |
| 434 | deepseek_ocr_3_english_extensive_2       | 1918-12-27_5 |  2.29342    |  0.703937    | 0.24962    |
| 435 | anthropic_1_simple                       | 1915-12-28_1 |  0.966833   |  0.866968    | 0.202405   |
| 436 | openai_2_extensive                       | 1915-12-28_3 |  0.948332   |  0.798558    | 0.190487   |
| 437 | dots_ocr_9_three_shot                    | 1917-12-28_1 |  2.37778    |  2.13768     | 0.356999   |
| 438 | dots_ocr_11_three_shot_english_extensive | 1917-12-28_4 |  1.85969    |  1.60077     | 0.288835   |
| 439 | openai_2_extensive                       | 1918-12-27_1 |  0.938104   |  0.826905    | 0.184087   |
| 440 | dots_ocr_9_three_shot                    | 1915-12-28_1 |  2.35821    |  1.97783     | 0.331951   |
| 441 | anthropic_1_simple                       | 1918-12-27_2 |  0.948483   |  0.847029    | 0.178386   |
| 442 | openai_2_extensive                       | 1918-12-27_5 |  0.949132   |  0.733338    | 0.165217   |
| 443 | churro_8_two_shot_zero_temperature       | 1914-06-29_1 |  0.705054   |  2.24401     | 0.274152   |
| 444 | churro_9_two_shot_zero_temperature       | 1914-06-29_1 |  0.705054   |  2.24401     | 0.274152   |
| 445 | churro_1_simple                          | 1915-12-28_3 |  0.265533   |  3.46073     | 0.353653   |
| 446 | openai_2_extensive                       | 1915-12-28_4 |  0.968912   |  0.758305    | 0.160772   |
| 447 | deepseek_ocr_3_english_extensive_2       | 1917-12-28_4 |  2.14112    |  1.0092      | 0.228306   |
| 448 | churro_5_one_shot_s_replaced             | average      |  3.91842    |  2.77119     | 0.445538   |
| 449 | anthropic_1_simple                       | 1914-06-29_1 |  0.961889   |  0.866667    | 0.160021   |
| 450 | churro_4_one_shot                        | average      |  3.98701    |  2.78235     | 0.438267   |
| 451 | anthropic_1_simple                       | 1914-06-29_5 |  0.960839   |  0.873732    | 0.147232   |
| 452 | dots_ocr_6_english_extensive             | 1918-12-27_1 |  2.75629    |  2.0356      | 0.317725   |
| 453 | openai_2_extensive                       | 1914-06-29_1 |  0.964374   |  0.792413    | 0.137827   |
| 454 | openai_1_simple                          | 1915-12-28_1 |  0.970978   |  0.882673    | 0.143601   |
| 455 | anthropic_1_simple                       | 1918-12-27_4 |  0.956716   |  0.883358    | 0.142206   |
| 456 | churro_2_german_extensive_2              | 1915-12-28_4 |  2.82902    |  2.92778     | 0.384255   |
| 457 | openai_2_extensive                       | 1915-12-28_1 |  0.97927    |  0.827859    | 0.129297   |
| 458 | openai_2_extensive                       | 1914-06-29_3 |  0.968557   |  0.823782    | 0.125099   |
| 459 | openai_3_one_shot_simple                 | 1915-12-28_1 |  0.965174   |  0.884213    | 0.1296     |
| 460 | dots_ocr_9_three_shot                    | 1917-12-28_3 |  1.53398    |  1.0299      | 0.165712   |
| 461 | anthropic_1_simple                       | 1918-12-27_5 |  0.972705   |  0.889655    | 0.128019   |
| 462 | anthropic_1_simple                       | 1914-06-29_4 |  0.941546   |  0.754163    | 0.113854   |
| 463 | anthropic_1_simple                       | 1915-12-28_4 |  0.974093   |  0.906981    | 0.12326    |
| 464 | deepseek_ocr_2_german_extensive_2        | 1918-12-27_3 |  0.954305   |  0.716214    | 0.102545   |
| 465 | dots_ocr_9_three_shot                    | 1915-12-28_4 |  1.52159    |  1.49812     | 0.189929   |
| 466 | openai_3_one_shot_simple                 | 1917-12-28_1 |  0.968519   |  0.884883    | 0.1155     |
| 467 | openai_2_extensive                       | 1914-06-29_7 |  0.939868   |  0.741736    | 0.10222    |
| 468 | anthropic_1_simple                       | 1918-12-27_1 |  0.970019   |  0.901483    | 0.11473    |
| 469 | anthropic_1_simple                       | 1914-06-29_7 |  0.969522   |  0.898017    | 0.110125   |
| 470 | anthropic_1_simple                       | average      |  0.969997   |  0.889441    | 0.109206   |
| 471 | anthropic_1_simple                       | 1914-06-29_2 |  0.961567   |  0.88931     | 0.106752   |
| 472 | openai_2_extensive                       | 1918-12-27_2 |  0.976006   |  0.816224    | 0.101162   |
| 473 | anthropic_1_simple                       | 1914-06-29_3 |  0.962392   |  0.835766    | 0.102127   |
| 474 | openai_2_extensive                       | 1917-12-28_3 |  0.967098   |  0.794432    | 0.0970834  |
| 475 | openai_3_one_shot_simple                 | 1917-12-28_4 |  0.96837    |  0.886295    | 0.104096   |
| 476 | openai_3_one_shot_simple                 | 1918-12-27_6 |  0.977855   |  0.889482    | 0.103684   |
| 477 | openai_2_extensive                       | average      |  0.973893   |  0.861374    | 0.0933782  |
| 478 | anthropic_1_simple                       | 1918-12-27_6 |  0.97669    |  0.898755    | 0.0962315  |
| 479 | openai_3_one_shot_simple                 | 1918-12-27_4 |  0.976866   |  0.915866    | 0.082642   |
| 480 | openai_2_extensive                       | 1918-12-27_4 |  0.982836   |  0.877544    | 0.0783828  |
| 481 | anthropic_1_simple                       | 1917-12-28_2 |  0.978867   |  0.903861    | 0.0787831  |
| 482 | openai_3_one_shot_simple                 | 1917-12-28_2 |  0.97126    |  0.899647    | 0.0775628  |
| 483 | deepseek_ocr_2_german_extensive_2        | 1918-12-27_5 |  1.52109    |  0.737884    | 0.0880882  |
| 484 | deepseek_ocr_3_english_extensive_2       | 1914-06-29_1 |  1.15493    |  0.741426    | 0.0709268  |
| 485 | deepseek_ocr_3_english_extensive_2       | 1918-12-27_6 |  0.98951    |  0.897993    | 0.0760943  |
| 486 | openai_3_one_shot_simple                 | 1914-06-29_1 |  0.975973   |  0.922003    | 0.0757209  |
| 487 | anthropic_1_simple                       | 1918-12-27_3 |  0.980132   |  0.927396    | 0.0744296  |
| 488 | openai_3_one_shot_simple                 | 1918-12-27_1 |  0.972921   |  0.925422    | 0.0710305  |
| 489 | anthropic_1_simple                       | 1917-12-28_4 |  0.982157   |  0.926586    | 0.0701754  |
| 490 | anthropic_1_simple                       | 1917-12-28_1 |  0.981481   |  0.91452     | 0.068806   |
| 491 | anthropic_1_simple                       | 1915-12-28_2 |  0.983181   |  0.922131    | 0.0680517  |
| 492 | deepseek_ocr_2_german_extensive_2        | 1914-06-29_2 |  3.26225    |  1.88029     | 0.243739   |
| 493 | openai_3_one_shot_simple                 | 1914-06-29_7 |  0.974465   |  0.908421    | 0.0633085  |
| 494 | openai_3_one_shot_simple                 | 1914-06-29_5 |  0.985315   |  0.948333    | 0.0597087  |
| 495 | deepseek_ocr_2_german_extensive_2        | 1918-12-27_2 |  1.30416    |  0.749329    | 0.055926   |
| 496 | openai_3_one_shot_simple                 | 1917-12-28_3 |  0.983279   |  0.94438     | 0.0576911  |
| 497 | openai_3_one_shot_simple                 | average      |  0.982771   |  0.937211    | 0.0568007  |
| 498 | anthropic_1_simple                       | 1915-12-28_3 |  0.984303   |  0.935877    | 0.0566802  |
| 499 | openai_3_one_shot_simple                 | 1914-06-29_2 |  0.984175   |  0.955151    | 0.053026   |
| 500 | dots_ocr_7_german_extensive_2            | 1917-12-28_4 |  5.70154    |  1.2584      | 0.278823   |
| 501 | dots_ocr_9_three_shot                    | 1917-12-28_4 |  5.60422    |  1.2555      | 0.273911   |
| 502 | openai_2_extensive                       | 1914-06-29_5 |  0.999301   |  0.812516    | 0.0366873  |
| 503 | openai_3_one_shot_simple                 | 1918-12-27_2 |  0.981651   |  0.945379    | 0.0444035  |
| 504 | anthropic_1_simple                       | 1917-12-28_3 |  0.986516   |  0.946566    | 0.0418542  |
| 505 | deepseek_ocr_3_english_extensive_2       | 1915-12-28_1 |  0.997512   |  0.966537    | 0.0341304  |
| 506 | openai_2_extensive                       | 1917-12-28_2 |  0.993238   |  0.976676    | 0.0319831  |
| 507 | churro_5_one_shot_s_replaced             | 1917-12-28_4 |  3.74371    |  3.50015     | 0.353996   |
| 508 | churro_6_two_shot                        | 1914-06-29_1 |  1          |  0.967122    | 0.0280839  |
| 509 | openai_1_simple                          | 1918-12-27_1 |  0.994197   |  0.979028    | 0.0268322  |
| 510 | churro_4_one_shot                        | 1917-12-28_4 |  3.76886    |  3.50324     | 0.352082   |
| 511 | openai_1_simple                          | 1914-06-29_5 |  0.993706   |  0.98508     | 0.0258671  |
| 512 | openai_3_one_shot_simple                 | 1915-12-28_4 |  0.999136   |  0.940876    | 0.0224475  |
| 513 | openai_3_one_shot_simple                 | 1914-06-29_4 |  0.982401   |  0.939538    | 0.0207762  |
| 514 | openai_1_simple                          | 1918-12-27_4 |  0.99403    |  0.984407    | 0.0241068  |
| 515 | openai_1_simple                          | 1917-12-28_1 |  0.991667   |  0.98098     | 0.0221306  |
| 516 | openai_2_extensive                       | 1918-12-27_3 |  0.995364   |  0.983866    | 0.0224754  |
| 517 | openai_1_simple                          | average      |  0.994501   |  0.982871    | 0.0223236  |
| 518 | openai_1_simple                          | 1918-12-27_3 |  0.993377   |  0.984185    | 0.0223235  |
| 519 | openai_3_one_shot_simple                 | 1918-12-27_3 |  0.996689   |  0.984265    | 0.0216981  |
| 520 | openai_1_simple                          | 1917-12-28_2 |  0.994083   |  0.98285     | 0.0209878  |
| 521 | openai_1_simple                          | 1914-06-29_4 |  0.9956     |  0.986266    | 0.02028    |
| 522 | openai_1_simple                          | 1917-12-28_4 |  0.996756   |  0.985278    | 0.0198511  |
| 523 | openai_1_simple                          | 1915-12-28_3 |  0.996076   |  0.985423    | 0.0194071  |
| 524 | openai_1_simple                          | 1914-06-29_1 |  0.995857   |  0.984522    | 0.0187232  |
| 525 | openai_3_one_shot_simple                 | 1915-12-28_2 |  0.995095   |  0.988388    | 0.0167103  |
| 526 | dots_ocr_6_english_extensive             | 1917-12-28_4 |  5.85645    |  1.3199      | 0.253474   |
| 527 | openai_2_extensive                       | 1914-06-29_4 |  0.9956     |  0.988261    | 0.0162256  |
| 528 | deepseek_ocr_1_default                   | 1917-12-28_4 |  2.98865    |  1.27186     | 0.123346   |
| 529 | openai_1_simple                          | 1914-06-29_3 |  0.996301   |  0.989937    | 0.0139913  |
| 530 | openai_1_simple                          | 1918-12-27_5 |  0.996898   |  0.986216    | 0.0112806  |
| 531 | openai_2_extensive                       | 1918-12-27_6 |  0.996503   |  0.991616    | 0.011335   |
| 532 | openai_3_one_shot_simple                 | 1918-12-27_5 |  0.996278   |  0.987609    | 0.0108617  |
| 533 | openai_1_simple                          | 1914-06-29_7 |  0.996705   |  0.993714    | 0.0111984  |
| 534 | openai_2_extensive                       | 1917-12-28_4 |  0.996756   |  0.992639    | 0.0109594  |
| 535 | dots_ocr_9_three_shot                    | 1918-12-27_1 |  1.29304    |  0.901688    | 0.0163512  |
| 536 | churro_8_two_shot_zero_temperature       | 1918-12-27_4 |  3.37239    |  3.07048     | 0.281663   |
| 537 | churro_9_two_shot_zero_temperature       | 1918-12-27_4 |  3.37239    |  3.07048     | 0.281663   |
| 538 | openai_1_simple                          | 1914-06-29_2 |  0.997739   |  0.994436    | 0.00905357 |
| 539 | openai_1_simple                          | 1918-12-27_2 |  0.996471   |  0.994392    | 0.00889033 |
| 540 | openai_1_simple                          | 1918-12-27_6 |  0.997669   |  0.993521    | 0.00782236 |
| 541 | openai_1_simple                          | 1915-12-28_4 |  0.997409   |  0.993645    | 0.00765404 |
| 542 | openai_2_extensive                       | 1914-06-29_2 |  0.998493   |  0.995279    | 0.00755097 |
| 543 | openai_1_simple                          | 1915-12-28_2 |  0.997197   |  0.995048    | 0.007476   |
| 544 | openai_2_extensive                       | 1917-12-28_1 |  1          |  0.99624     | 0.0061674  |
| 545 | dots_ocr_7_german_extensive_2            | 1918-12-27_1 |  0.996132   |  0.994987    | 0.00561388 |
| 546 | openai_1_simple                          | 1917-12-28_3 |  0.997303   |  0.99582     | 0.00499424 |
| 547 | openai_3_one_shot_simple                 | 1915-12-28_3 |  1          |  0.997364    | 0.00355652 |
| 548 | openai_3_one_shot_simple                 | 1914-06-29_3 |  1          |  0.996697    | 0.00199005 |
| 549 | dots_ocr_9_three_shot                    | 1918-12-27_4 |  0.996269   |  1.20712     | 0.0167432  |
| 550 | deepseek_ocr_2_german_extensive_2        | 1914-06-29_1 |  1          |  1           | 0          |
| 551 | deepseek_ocr_2_german_extensive_2        | 1915-12-28_1 |  1          |  1           | 0          |
| 552 | deepseek_ocr_2_german_extensive_2        | 1917-12-28_1 |  1          |  1           | 0          |
| 553 | deepseek_ocr_2_german_extensive_2        | 1918-12-27_1 |  1          |  1           | 0          |
| 554 | deepseek_ocr_2_german_extensive_2        | 1918-12-27_4 |  1          |  1           | 0          |
| 555 | dots_ocr_6_english_extensive             | 1914-06-29_1 |  1          |  1           | 0          |
| 556 | dots_ocr_6_english_extensive             | 1914-06-29_2 |  1          |  1           | 0          |
| 557 | churro_7_two_shot_prompts_adapted        | average      |  4.64709    |  2.98984     | 0.318575   |
| 558 | dots_ocr_8_one_shot                      | 1918-12-27_6 |  7.79604    |  1.64825     | 0.34252    |
| 559 | dots_ocr_11_three_shot_english_extensive | 1918-12-27_6 |  7.73893    |  1.65295     | 0.340164   |
| 560 | dots_ocr_9_three_shot                    | 1915-12-28_2 |  1.9047     |  1.50726     | 0.0590271  |
| 561 | dots_ocr_3_default                       | 1918-12-27_6 |  8.03613    |  1.68089     | 0.336787   |
| 562 | dots_ocr_6_english_extensive             | 1918-12-27_6 |  8.02564    |  1.68407     | 0.33527    |
| 563 | dots_ocr_7_german_extensive_2            | 1918-12-27_6 |  8.05478    |  1.68966     | 0.333866   |
| 564 | churro_8_two_shot_zero_temperature       | 1915-12-28_3 |  3.85415    |  3.58696     | 0.305356   |
| 565 | churro_9_two_shot_zero_temperature       | 1915-12-28_3 |  3.85415    |  3.58696     | 0.305356   |
| 566 | churro_6_two_shot                        | 1914-06-29_2 |  2.46873    |  1.70958     | 0.0593512  |
| 567 | churro_3_english_extensive_3             | 1915-12-28_4 |  3.79447    |  4.07607     | 0.30882    |
| 568 | dots_ocr_11_three_shot_english_extensive | 1918-12-27_1 |  2.15957    |  1.67887     | 0.0285284  |
| 569 | churro_6_two_shot                        | average      |  4.7053     |  3.04584     | 0.246289   |
| 570 | churro_7_two_shot_prompts_adapted        | 1917-12-28_3 |  3.04531    |  2.81057     | 0.147818   |
| 571 | churro_8_two_shot_zero_temperature       | 1917-12-28_3 |  3.56203    |  2.91249     | 0.175989   |
| 572 | churro_9_two_shot_zero_temperature       | 1917-12-28_3 |  3.56203    |  2.91249     | 0.175989   |
| 573 | churro_5_one_shot_s_replaced             | 1914-06-29_2 |  4.48757    |  4.12502     | 0.304721   |
| 574 | churro_3_english_extensive_3             | 1915-12-28_2 |  3.64471    |  2.45458     | 0.131703   |
| 575 | dots_ocr_9_three_shot                    | 1915-12-28_3 |  2.65468    |  1.65969     | 0.0133414  |
| 576 | churro_4_one_shot                        | 1914-06-29_2 |  4.62095    |  4.13741     | 0.297995   |
| 577 | dots_ocr_6_english_extensive             | 1917-12-28_2 |  1.93491    |  2.08928     | 0.0100266  |
| 578 | dots_ocr_3_default                       | 1917-12-28_2 |  2.67794    |  2.09026     | 0.0393549  |
| 579 | dots_ocr_11_three_shot_english_extensive | 1917-12-28_1 |  2.78611    |  2.0261      | 0.0278748  |
| 580 | churro_6_two_shot                        | 1915-12-28_2 |  3.79537    |  3.63055     | 0.202086   |
| 581 | churro_7_two_shot_prompts_adapted        | 1915-12-28_3 |  3.97776    |  3.38381     | 0.17587    |
| 582 | dots_ocr_9_three_shot                    | 1917-12-28_2 |  3.31868    |  1.95913     | 0.0241246  |
| 583 | churro_6_two_shot                        | 1918-12-27_2 |  4.50247    |  3.73104     | 0.214903   |
| 584 | churro_2_german_extensive_2              | 1917-12-28_4 |  4.63909    |  4.14935     | 0.248417   |
| 585 | churro_8_two_shot_zero_temperature       | 1918-12-27_2 |  4.4573     |  3.93701     | 0.222349   |
| 586 | churro_9_two_shot_zero_temperature       | 1918-12-27_2 |  4.4573     |  3.93701     | 0.222349   |
| 587 | churro_5_one_shot_s_replaced             | 1918-12-27_3 |  4.83907    |  4.65168     | 0.291411   |
| 588 | dots_ocr_11_three_shot_english_extensive | 1917-12-28_2 |  4.00338    |  1.70306     | 0.00748604 |
| 589 | churro_8_two_shot_zero_temperature       | 1914-06-29_5 |  4.82378    |  4.54011     | 0.273494   |
| 590 | churro_9_two_shot_zero_temperature       | 1914-06-29_5 |  4.82378    |  4.54011     | 0.273494   |
| 591 | churro_4_one_shot                        | 1918-12-27_3 |  4.99404    |  4.67332     | 0.284121   |
| 592 | churro_3_english_extensive_3             | 1918-12-27_1 |  5.26596    |  4.54946     | 0.282316   |
| 593 | churro_7_two_shot_prompts_adapted        | 1917-12-28_1 |  4.47685    |  4.16245     | 0.214631   |
| 594 | churro_8_two_shot_zero_temperature       | 1918-12-27_3 |  3.92848    |  3.6353      | 0.141568   |
| 595 | churro_9_two_shot_zero_temperature       | 1918-12-27_3 |  3.92848    |  3.6353      | 0.141568   |
| 596 | churro_7_two_shot_prompts_adapted        | 1914-06-29_3 |  4.91677    |  3.91719     | 0.206038   |
| 597 | churro_5_one_shot_s_replaced             | 1918-12-27_1 |  5.08027    |  4.73944     | 0.279775   |
| 598 | dots_ocr_7_german_extensive_2            | 1917-12-28_1 |  3.00278    |  2.60655     | 0.0158535  |
| 599 | dots_ocr_7_german_extensive_2            | 1915-12-28_4 |  3.28584    |  2.53808     | 0.0149629  |
| 600 | churro_7_two_shot_prompts_adapted        | 1918-12-27_5 |  5.67308    |  4.60613     | 0.281807   |
| 601 | churro_4_one_shot                        | 1914-06-29_3 |  5.45993    |  4.3572      | 0.250256   |
| 602 | churro_5_one_shot_s_replaced             | 1914-06-29_3 |  5.45993    |  4.3572      | 0.250256   |
| 603 | churro_4_one_shot                        | 1918-12-27_1 |  5.26886    |  4.76379     | 0.270972   |
| 604 | deepseek_ocr_3_english_extensive_2       | 1914-06-29_5 |  4.55175    |  2.27334     | 0.0315592  |
| 605 | churro_2_german_extensive_2              | 1915-12-28_2 |  5.35879    |  4.29141     | 0.218212   |
| 606 | churro_5_one_shot_s_replaced             | 1915-12-28_2 |  5.52698    |  4.32437     | 0.217779   |
| 607 | churro_4_one_shot                        | 1915-12-28_2 |  5.56202    |  4.32992     | 0.216813   |
| 608 | churro_8_two_shot_zero_temperature       | 1918-12-27_5 |  5.0794     |  3.92353     | 0.150843   |
| 609 | churro_9_two_shot_zero_temperature       | 1918-12-27_5 |  5.0794     |  3.92353     | 0.150843   |
| 610 | churro_6_two_shot                        | 1918-12-27_4 |  5.01045    |  4.91084     | 0.221828   |
| 611 | churro_6_two_shot                        | 1917-12-28_3 |  4.16828    |  3.51492     | 0.0696682  |
| 612 | churro_7_two_shot_prompts_adapted        | 1918-12-27_3 |  4.35232    |  3.99257     | 0.103496   |
| 613 | churro_8_two_shot_zero_temperature       | average      |  6.93878    |  3.88825     | 0.201437   |
| 614 | churro_9_two_shot_zero_temperature       | average      |  6.93878    |  3.88825     | 0.201437   |
| 615 | deepseek_ocr_3_english_extensive_2       | 1917-12-28_1 |  5.00185    |  2.98961     | 0.0316029  |
| 616 | churro_7_two_shot_prompts_adapted        | 1915-12-28_2 |  4.94324    |  3.99539     | 0.110532   |
| 617 | churro_5_one_shot_s_replaced             | 1918-12-27_2 |  6.12773    |  4.31212     | 0.17638    |
| 618 | churro_4_one_shot                        | 1918-12-27_2 |  6.12773    |  4.31212     | 0.176354   |
| 619 | churro_2_german_extensive_2              | 1914-06-29_7 |  5.69769    |  5.84827     | 0.253052   |
| 620 | churro_8_two_shot_zero_temperature       | 1914-06-29_2 | 12.6534     |  2.98247     | 0.310032   |
| 621 | churro_9_two_shot_zero_temperature       | 1914-06-29_2 | 12.6534     |  2.98247     | 0.310032   |
| 622 | churro_2_german_extensive_2              | 1918-12-27_2 |  6.03952    |  4.33805     | 0.127829   |
| 623 | churro_7_two_shot_prompts_adapted        | 1914-06-29_2 | 12.3067     |  2.99562     | 0.287675   |
| 624 | churro_8_two_shot_zero_temperature       | 1918-12-27_1 |  3.51838    |  4.35407     | 0.0120488  |
| 625 | churro_9_two_shot_zero_temperature       | 1918-12-27_1 |  3.51838    |  4.35407     | 0.0120488  |
| 626 | churro_8_two_shot_zero_temperature       | 1915-12-28_2 |  5.5494     |  4.5362      | 0.108235   |
| 627 | churro_9_two_shot_zero_temperature       | 1915-12-28_2 |  5.5494     |  4.5362      | 0.108235   |
| 628 | churro_4_one_shot                        | 1917-12-28_2 |  4.64074    |  3.99716     | 0.0224352  |
| 629 | churro_5_one_shot_s_replaced             | 1917-12-28_2 |  4.64074    |  3.99716     | 0.0224352  |
| 630 | churro_5_one_shot_s_replaced             | 1915-12-28_4 |  5.40069    |  4.26143     | 0.0667473  |
| 631 | churro_4_one_shot                        | 1915-12-28_4 |  5.43092    |  4.28849     | 0.0641032  |
| 632 | churro_8_two_shot_zero_temperature       | 1915-12-28_1 |  5.46683    |  5.87672     | 0.192247   |
| 633 | churro_9_two_shot_zero_temperature       | 1915-12-28_1 |  5.46683    |  5.87672     | 0.192247   |
| 634 | churro_6_two_shot                        | 1914-06-29_3 | 10.4901     |  2.97189     | 0.172401   |
| 635 | churro_6_two_shot                        | 1918-12-27_1 |  5.30174    |  5.68215     | 0.16531    |
| 636 | churro_3_english_extensive_3             | 1918-12-27_3 |  4.68079    |  6.71565     | 0.222228   |
| 637 | churro_7_two_shot_prompts_adapted        | 1914-06-29_5 |  5.4014     |  4.65735     | 0.0828377  |
| 638 | churro_1_simple                          | 1915-12-28_1 |  5.8068     |  5.51468     | 0.145533   |
| 639 | churro_6_two_shot                        | 1915-12-28_3 | 11.0844     |  3.04047     | 0.171017   |
| 640 | churro_6_two_shot                        | 1918-12-27_3 |  4.92715    |  4.70519     | 0.0339146  |
| 641 | churro_5_one_shot_s_replaced             | 1915-12-28_1 |  7.07131    |  5.80805     | 0.21477    |
| 642 | churro_4_one_shot                        | 1915-12-28_1 |  7.07214    |  5.80825     | 0.214717   |
| 643 | churro_6_two_shot                        | 1915-12-28_1 |  3.90216    |  5.37949     | 0.0156619  |
| 644 | churro_7_two_shot_prompts_adapted        | 1918-12-27_2 |  6.06634    |  4.66626     | 0.0212083  |
| 645 | churro_1_simple                          | 1918-12-27_2 |  5.36768    |  5.0061      | 0.0130683  |
| 646 | churro_6_two_shot                        | 1917-12-28_2 |  6.22992    |  4.95698     | 0.040111   |
| 647 | churro_7_two_shot_prompts_adapted        | 1914-06-29_7 |  5.77512    |  5.35136     | 0.0442905  |
| 648 | churro_8_two_shot_zero_temperature       | 1915-12-28_4 | 14.6287     |  3.68811     | 0.247563   |
| 649 | churro_9_two_shot_zero_temperature       | 1915-12-28_4 | 14.6287     |  3.68811     | 0.247563   |
| 650 | churro_8_two_shot_zero_temperature       | 1914-06-29_7 |  6.10873    |  5.98764     | 0.0652144  |
| 651 | churro_9_two_shot_zero_temperature       | 1914-06-29_7 |  6.10873    |  5.98764     | 0.0652144  |
| 652 | churro_7_two_shot_prompts_adapted        | 1914-06-29_1 | 13.3471     |  3.74122     | 0.188567   |
| 653 | churro_8_two_shot_zero_temperature       | 1917-12-28_1 |  7.19537    |  6.34247     | 0.0459047  |
| 654 | churro_9_two_shot_zero_temperature       | 1917-12-28_1 |  7.19537    |  6.34247     | 0.0459047  |
| 655 | churro_8_two_shot_zero_temperature       | 1917-12-28_4 | 15.4477     |  3.66421     | 0.117972   |
| 656 | churro_9_two_shot_zero_temperature       | 1917-12-28_4 | 15.4477     |  3.66421     | 0.117972   |
| 657 | churro_6_two_shot                        | 1915-12-28_4 | 16.2988     |  3.71478     | 0.100783   |
| 658 | churro_8_two_shot_zero_temperature       | 1917-12-28_2 | 15.2122     |  5.46629     | 0.177915   |
| 659 | churro_9_two_shot_zero_temperature       | 1917-12-28_2 | 15.2122     |  5.46629     | 0.177915   |
| 660 | churro_6_two_shot                        | 1918-12-27_6 |  9.26923    |  7.78176     | 0.0893103  |
| 661 | churro_1_simple                          | 1917-12-28_3 |  1.8069     | 12.2775      | 0.132611   |
| 662 | churro_1_simple                          | 1918-12-27_6 | 20.9289     |  4.50381     | 0.224071   |
| 663 | churro_1_simple                          | 1915-12-28_2 | 11.0126     |  7.94766     | 0.0351503  |
| 664 | churro_2_german_extensive_2              | 1918-12-27_6 | 21.4103     |  4.65396     | 0.18983    |
| 665 | churro_8_two_shot_zero_temperature       | 1918-12-27_6 | 21.662      |  4.67162     | 0.180373   |
| 666 | churro_9_two_shot_zero_temperature       | 1918-12-27_6 | 21.662      |  4.67162     | 0.180373   |
| 667 | churro_7_two_shot_prompts_adapted        | 1918-12-27_6 | 13.9207     |  8.48869     | 0.0084385  |
| 668 | churro_4_one_shot                        | 1918-12-27_6 | 23.12       |  4.97612     | 0.0155406  |
| 669 | churro_5_one_shot_s_replaced             | 1918-12-27_6 | 23.12       |  4.97612     | 0.0155406  |

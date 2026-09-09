# Self-Aligned C Code Data Generation with StarCoder2

An NJIT DS 677 academic project that adapts the open-source **SelfCodeAlign** workflow to generate C programming instruction-response data from source-code seeds. The project uses C snippets derived from **The Stack v2** and **StarCoder2-15B** to build data through a staged self-alignment pipeline.

## Project goal

Instruction-tuned code models need high-quality programming tasks and answers. Manually writing thousands of examples is expensive, so this project explores synthetic data generation with an open code language model.

The workflow converts each seed through three stages:

1. **S → C (Seed to Concepts):** identify programming concepts demonstrated by a C snippet.
2. **C → I (Concepts to Instruction):** turn those concepts into a realistic programming task.
3. **I → R (Instruction to Response):** generate candidate C solutions and tests for the task.

The resulting JSONL artifacts can be cleaned, deduplicated, validated, and prepared for later instruction tuning.

## What was implemented

- Adapted the course workflow from The Stack v1 to **The Stack v2** and focused it on the **C programming language**.
- Gathered and prepared C source-code seeds for model-driven data generation.
- Executed the S → C → I → R pipeline with **StarCoder2-15B**.
- Used **vLLM** and an OpenAI-compatible API workflow for batched model inference.
- Stored every generation stage as JSONL so outputs remain traceable and independently inspectable.
- Included shell orchestration for GPU-based generation plus utilities for parsing, sanitization, exact-match and MinHash deduplication, execution filtering, and decontamination.
- Preserved HumanEval, MBPP, EvalPlus, and EvoEval resources from the upstream framework for evaluation and reference.

## Checked-in run artifacts

| Stage | Artifact | Verified contents |
|---|---|---:|
| C seed preparation | `datasets/final_seed.jsonl` | 343 seed programs |
| Seed → Concepts | `data-concept_gen-*.jsonl` | 342 records and 1,156 concepts |
| Concepts → Instruction | `data-instruction_gen-*.jsonl` | 331 instruction records |
| Instruction → Response | `data-response_gen-*.jsonl` | 187 batches and 1,870 response candidates |

These figures describe the generated artifacts committed to this repository; they are not benchmark-accuracy claims.

## Technology stack

- Python and Bash
- C
- StarCoder2-15B
- vLLM
- Hugging Face Transformers and Datasets
- PyTorch
- OpenAI-compatible inference API
- Tree-sitter-based code processing
- JSONL data pipelines
- EvalPlus and EvoEval
- CUDA / NVIDIA GPU execution

## Repository structure

The implementation is currently stored under [`selfcodealign-main/`](selfcodealign-main/).

| Path | Purpose |
|---|---|
| [`ProjectInstruction.pdf`](selfcodealign-main/ProjectInstruction.pdf) | Academic project requirements |
| [`datasets/`](selfcodealign-main/datasets/) | Prepared seed datasets |
| [`prompts/`](selfcodealign-main/prompts/) | Prompts used by the generation stages |
| [`src/`](selfcodealign-main/src/) | SelfCodeAlign Python package and processing logic |
| [`seed_gathering/`](selfcodealign-main/seed_gathering/) | Seed collection and preparation work |
| [`evaluation/`](selfcodealign-main/evaluation/) | Benchmark and evaluation resources |
| [`self_ossinstruct_sc2.sh`](selfcodealign-main/self_ossinstruct_sc2.sh) | Single-process pipeline launcher |
| [`self_ossinstruct_sc2_parallel.sh`](selfcodealign-main/self_ossinstruct_sc2_parallel.sh) | Multi-GPU launcher and result aggregation |
| [`sanitize.sh`](selfcodealign-main/sanitize.sh) | Filtering, deduplication, and decontamination workflow |

## Environment

A high-memory CUDA-capable environment is recommended because StarCoder2-15B is a large model.

```bash
cd selfcodealign-main

python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

The generation workflow expects a seed JSONL file, a configured StarCoder2-15B model or vLLM endpoint, and one of the supported modes (`S->C`, `C->I`, or `I->R`). Each stage consumes the previous stage's output. Review the launcher scripts and the [upstream documentation](selfcodealign-main/README.md) before running because GPU paths and model-serving settings are environment-specific.

## Scope and limitations

This repository demonstrates academic adaptation, seed preparation, staged synthetic-data generation, and reproducible data artifacts. It does **not** include a newly fine-tuned model checkpoint, so it should not be interpreted as evidence that a final model was trained or that the upstream benchmark scores were independently reproduced.

## Attribution

This project is built on the open-source [SelfCodeAlign](https://github.com/bigcode-project/selfcodealign) and [StarCoder2 Self-Align](https://github.com/bigcode-project/starcoder2-self-align) work by the original authors. Their paper and complete attribution are retained in the [upstream README](selfcodealign-main/README.md). This repository's adaptation and generated artifacts were prepared for an NJIT academic project.

The inherited source is provided under the [Apache License 2.0](selfcodealign-main/LICENSE).


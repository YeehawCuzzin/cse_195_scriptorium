# Parser Visual & Quantitative Audit

This document summarizes the visual and quantitative audit for the Scriptorium / RefAIned parser benchmark.

The goal of this audit is to compare parser outputs side-by-side against the original PDF and summarize extraction quality using runtime, character count, artifact production, and qualitative output inspection.

## Benchmark Input

Primary ground truth PDF:

- `inputs/slam_llm.pdf`

Additional PDFs used by the batch runner:

- `inputs/cse195_research_paper.pdf`
- `inputs/cse188_research_paper.pdf`

Primary output directory:

- `outputs/slam_llm/parser_outputs/`

## Quantitative Summary

| Parser | Extracted Characters | Runtime (s) | Type | Notes |
|---|---:|---:|---|---|
| PyMuPDF | 88,199 | 0.09 | Flat text | Very fast baseline extraction |
| pdfplumber | 85,465 | 1.74 | Flat text | Layout-sensitive but weaker on multi-column text |
| PyPDF | 88,394 | 0.54 | Flat text | Fast general PDF text baseline |
| Tika | 90,660 | 0.09 | Semi-structured | Fast after Java setup |
| Unstructured | 95,836 | 4.56 | Structure-aware | Element-oriented extraction |
| Docling | 100,840 | 10.34 | Structure-aware | Strong Markdown-oriented structured output |
| Marker | 102,133 | 40.50 | Structure-aware | Rich Markdown/artifact output, slowest parser |
| MinerU | 88,200 | 31.92 | Structure-aware | Layout-aware artifacts and Markdown output |
| GROBID | 69,846 | 2.02 | Structured metadata | Lower text volume, stronger scholarly metadata focus |

## Evaluation Matrix

Scores use the rubric from `docs/parser_evaluation_metrics.md`.

Scale:

- 0 = fails or unusable
- 1 = poor / major issues
- 2 = usable / minor issues
- 3 = strong / reliable

| Parser | Text Quality | Hierarchy | Tables | Figures/Captions | Equations/Math | Metadata/Bibliography | Runtime | Operational Complexity | Summary |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---|
| PyMuPDF | 2 | 1 | 1 | 1 | 1 | 1 | 3 | 3 | Fast and useful baseline, but mostly flat text |
| pdfplumber | 1 | 1 | 1 | 1 | 1 | 1 | 3 | 3 | Layout-sensitive but produced noisier text |
| PyPDF | 2 | 1 | 1 | 1 | 1 | 1 | 3 | 3 | Fast general baseline with limited structure |
| Tika | 2 | 2 | 1 | 1 | 1 | 1 | 3 | 2 | Readable semi-structured extraction once Java works |
| Unstructured | 2 | 2 | 2 | 1 | 1 | 2 | 2 | 2 | Useful element-aware parser with moderate runtime |
| Docling | 3 | 3 | 2 | 2 | 2 | 2 | 2 | 2 | Strong balance of structure, readability, and runtime |
| Marker | 3 | 3 | 2 | 3 | 2 | 2 | 1 | 2 | Rich Markdown and image artifacts, but slow |
| MinerU | 3 | 3 | 3 | 3 | 2 | 2 | 1 | 1 | Strong artifact output but highest setup complexity |
| GROBID | 2 | 3 | 1 | 1 | 1 | 3 | 2 | 1 | Best scholarly metadata/reference-oriented parser |

## Output Inventory

The benchmark writes normalized `.txt` outputs for every parser.

Expected normalized outputs:

- `docling.txt`
- `grobid.txt`
- `marker.txt`
- `mineru.txt`
- `pdfplumber.txt`
- `pymupdf.txt`
- `pypdf.txt`
- `tika.txt`
- `unstructured.txt`

Structure-aware artifact folders:

- `docling_run/`
- `marker_run/`
- `mineru_run_txt/`

These artifact folders preserve parser-specific outputs such as Markdown files, JSON metadata, extracted images, layout PDFs, and intermediate files.

## Qualitative Findings

### Flat Text Parsers

PyMuPDF, pdfplumber, and PyPDF are useful as fast baselines. They are easy to run and fast enough for repeated experiments. However, they provide limited structural preservation. They tend to flatten section hierarchy, tables, figures, and citation context into plain text.

### Tika

Tika provides a semi-structured baseline. Once Java is installed, it runs quickly and produces readable text. However, it does not preserve rich scholarly structure or parser-specific artifacts in the same way as Docling, Marker, MinerU, or GROBID.

### Unstructured

Unstructured provides more structure-aware extraction than flat text parsers. It is useful for identifying document-like elements and gives a better foundation for later semantic chunking work.

### Docling

Docling provides one of the best tradeoffs in the benchmark. It produces high text coverage and Markdown-style structure while remaining much faster than Marker and MinerU. It is a strong candidate for a default parser when structure and runtime both matter.

### Marker

Marker produced the largest normalized text output and generated additional artifacts. It is useful when Markdown fidelity and extracted visual artifacts matter, but it had the highest runtime in this benchmark.

### MinerU

MinerU produced Markdown, JSON, image assets, layout PDFs, and other artifacts. It is valuable for layout-aware and multimodal-ready ingestion, but it required the most setup work and had higher runtime.

### GROBID

GROBID produced fewer extracted characters than the other parsers, but that is expected because its focus is scholarly metadata and academic document structure. It is especially useful for title, author, reference, bibliography, and scholarly metadata extraction.

## Representative Output Snippets

The following snippets should be reviewed against the original PDF for readability, heading preservation, and extraction noise.


### pymupdf

Source file: `outputs/slam_llm/parser_outputs/pymupdf.txt`

Characters: 88,199

```text
--- PAGE 1 ---
JOURNAL OF LATEX CLASS FILES, VOL. 14, NO. 8, AUGUST 2021
1
SLAM-LLM: A Modular, Open-Source Multimodal
Large Language Model Framework and Best Practice
for Speech, Language, Audio and Music Processing
Ziyang Ma, Guanrou Yang, Wenxi Chen, Zhifu Gao, Yexing Du, Xiquan Li, Zhisheng Zheng, Haina Zhu, Jianheng
Zhuo, Zheshu Song, Ruiyang Xu, Tiranrui Wang, Yifan Yang, Yanqiao Zhu, Zhikang Niu, Liumeng Xue, Yinghao
Ma, Ruibin Yuan, Shiliang Zhang, Kai Yu, Eng Siong Chng, Xie Chen
Abstract—The recent surge in open-source Multimodal Large
Language Models (MLLM) frameworks, such as LLaVA, provides
a convenient kickoff for artificial intelligence developers and
researchers. However, most of the MLLM frameworks take
vision as the main input modality, and provide limited in-depth
support for the modality of speech, audio, and music. This
situation hinders the development of audio-language models, and
forces researchers to spend a lot of effort on code writing and
hyperparameter tuning. We present SLAM-LLM, an open-source
deep learning framework designed to train customized MLLMs,
focused on speech, language, audio, and music processing. SLAM-
LLM provides a modular configuratio
```

### pdfplumber

Source file: `outputs/slam_llm/parser_outputs/pdfplumber.txt`

Characters: 85,465

```text
--- PAGE 1 ---
This article has been accepted for publication in IEEE Journal of Selected Topics in Signal Processing. This is the author's version which has not been fully edited and
content may change prior to final publication. Citation information: DOI 10.1109/JSTSP.2026.3653157
JOURNALOFLATEXCLASSFILES,VOL.14,NO.8,AUGUST2021 1
SLAM-LLM: A Modular, Open-Source Multimodal
Large Language Model Framework and Best Practice
for Speech, Language, Audio and Music Processing
Ziyang Ma, Guanrou Yang, Wenxi Chen, Zhifu Gao, Yexing Du, Xiquan Li, Zhisheng Zheng, Haina Zhu, Jianheng
Zhuo, Zheshu Song, Ruiyang Xu, Tiranrui Wang, Yifan Yang, Yanqiao Zhu, Zhikang Niu, Liumeng Xue, Yinghao
Ma, Ruibin Yuan, Shiliang Zhang, Kai Yu, Eng Siong Chng, Xie Chen
Abstract—The recent surge in open-source Multimodal Large that integrate various forms of input such as text, vision, as
LanguageModels(MLLM)frameworks,suchasLLaVA,provides well as audio. While recent open-source frameworks, such
a convenient kickoff for artificial intelligence developers and
as LLaVA [1] and OpenFlamingo [2] have demonstrated
researchers. However, most of the MLLM frameworks take
remarkable capabilities in vision-language mo
```

### pypdf

Source file: `outputs/slam_llm/parser_outputs/pypdf.txt`

Characters: 88,394

```text
--- PAGE 1 ---
JOURNAL OF LATEX CLASS FILES, VOL. 14, NO. 8, AUGUST 2021 1
SLAM-LLM: A Modular, Open-Source Multimodal
Large Language Model Framework and Best Practice
for Speech, Language, Audio and Music Processing
Ziyang Ma, Guanrou Yang, Wenxi Chen, Zhifu Gao, Yexing Du, Xiquan Li, Zhisheng Zheng, Haina Zhu, Jianheng
Zhuo, Zheshu Song, Ruiyang Xu, Tiranrui Wang, Yifan Yang, Yanqiao Zhu, Zhikang Niu, Liumeng Xue, Yinghao
Ma, Ruibin Yuan, Shiliang Zhang, Kai Yu, Eng Siong Chng, Xie Chen
Abstract—The recent surge in open-source Multimodal Large
Language Models (MLLM) frameworks, such as LLaV A, provides
a convenient kickoff for artificial intelligence developers and
researchers. However, most of the MLLM frameworks take
vision as the main input modality, and provide limited in-depth
support for the modality of speech, audio, and music. This
situation hinders the development of audio-language models, and
forces researchers to spend a lot of effort on code writing and
hyperparameter tuning. We present SLAM-LLM, an open-source
deep learning framework designed to train customized MLLMs,
focused on speech, language, audio, and music processing. SLAM-
LLM provides a modular configurati
```

### tika

Source file: `outputs/slam_llm/parser_outputs/tika.txt`

Characters: 90,660

```text
SLAM-LLM: A Modular, Open-Source Multimodal Large Language Model Framework and Best Practice for Speech, Language, Audio and Music Processing


JOURNAL OF LATEX CLASS FILES, VOL. 14, NO. 8, AUGUST 2021 1

SLAM-LLM: A Modular, Open-Source Multimodal
Large Language Model Framework and Best Practice
for Speech, Language, Audio and Music Processing
Ziyang Ma, Guanrou Yang, Wenxi Chen, Zhifu Gao, Yexing Du, Xiquan Li, Zhisheng Zheng, Haina Zhu, Jianheng
Zhuo, Zheshu Song, Ruiyang Xu, Tiranrui Wang, Yifan Yang, Yanqiao Zhu, Zhikang Niu, Liumeng Xue, Yinghao

Ma, Ruibin Yuan, Shiliang Zhang, Kai Yu, Eng Siong Chng, Xie Chen

Abstract—The recent surge in open-source Multimodal Large
Language Models (MLLM) frameworks, such as LLaVA, provides
a convenient kickoff for artificial intelligence developers and
researchers. However, most of the MLLM frameworks take
vision as the main input modality, and provide limited in-depth
support for the modality of speech, audio, and music. This
situation hinders the development of audio-language models, and
forces researchers to spend a lot of effort on code writing and
hyperparameter tunin
```

### unstructured

Source file: `outputs/slam_llm/parser_outputs/unstructured.txt`

Characters: 95,836

```text
[Header]
This article has been accepted for publication in IEEE Journal of Selected Topics in Signal Processing. This is the author's version which has not been fully edited and

[Header]
content may change prior to final publication. Citation information: DOI 10.1109/JSTSP.2026.3653157

[Header]
JOURNAL OF LATEX CLASS FILES, VOL. 14, NO. 8, AUGUST 2021

[Text]
SLAM-LLM: A Modular, Open-Source Multimodal Large Language Model Framework and Best Practice for Speech, Language, Audio and Music Processing

[Text]
Ziyang Ma, Guanrou Yang, Wenxi Chen, Zhifu Gao, Yexing Du, Xiquan Li, Zhisheng Zheng, Haina Zhu, Jianheng Zhuo, Zheshu Song, Ruiyang Xu, Tiranrui Wang, Yifan Yang, Yanqiao Zhu, Zhikang Niu, Liumeng Xue, Yinghao Ma, Ruibin Yuan, Shiliang Zhang, Kai Yu, Eng Siong Chng, Xie Chen

[NarrativeText]
Abstract—The recent surge in open-source Multimodal Large Language Models (MLLM) frameworks, such as LLaVA, provides a convenient kickoff for artificial intelligence developers and researchers. However, most of the MLLM frameworks take vision as the main input modality, and provide limited in-depth support for the modality of speech, audio, and music. This situation hinders the development
```

### docling

Source file: `outputs/slam_llm/parser_outputs/docling.txt`

Characters: 100,840

```text
## SLAM-LLM: A Modular, Open-Source Multimodal Large Language Model Framework and Best Practice for Speech, Language, Audio and Music Processing

Ziyang Ma, Guanrou Yang, Wenxi Chen, Zhifu Gao, Yexing Du, Xiquan Li, Zhisheng Zheng, Haina Zhu, Jianheng Zhuo, Zheshu Song, Ruiyang Xu, Tiranrui Wang, Yifan Yang, Yanqiao Zhu, Zhikang Niu, Liumeng Xue, Yinghao Ma, Ruibin Yuan, Shiliang Zhang, Kai Yu, Eng Siong Chng, Xie Chen

Abstract -The recent surge in open-source Multimodal Large Language Models (MLLM) frameworks, such as LLaVA, provides a convenient kickoff for artificial intelligence developers and researchers. However, most of the MLLM frameworks take vision as the main input modality, and provide limited in-depth support for the modality of speech, audio, and music. This situation hinders the development of audio-language models, and forces researchers to spend a lot of effort on code writing and hyperparameter tuning. We present SLAM-LLM, an open-source deep learning framework designed to train customized MLLMs, focused on speech, language, audio, and music processing. SLAMLLM provides a modular configuration of different encoders, projectors, LLMs, and parameter-efficient fine-
```

### marker

Source file: `outputs/slam_llm/parser_outputs/marker.txt`

Characters: 102,133

```text
# SLAM-LLM: A Modular, Open-Source Multimodal Large Language Model Framework and Best Practice for Speech, Language, Audio and Music Processing

Ziyang Ma, Guanrou Yang, Wenxi Chen, Zhifu Gao, Yexing Du, Xiquan Li, Zhisheng Zheng, Haina Zhu, Jianheng Zhuo, Zheshu Song, Ruiyang Xu, Tiranrui Wang, Yifan Yang, Yanqiao Zhu, Zhikang Niu, Liumeng Xue, Yinghao Ma, Ruibin Yuan, Shiliang Zhang, Kai Yu, Eng Siong Chng, Xie Chen

*Abstract*—The recent surge in open-source Multimodal Large Language Models (MLLM) frameworks, such as LLaVA, provides a convenient kickoff for artificial intelligence developers and researchers. However, most of the MLLM frameworks take vision as the main input modality, and provide limited in-depth support for the modality of speech, audio, and music. This situation hinders the development of audio-language models, and forces researchers to spend a lot of effort on code writing and hyperparameter tuning. We present SLAM-LLM, an open-source deep learning framework designed to train customized MLLMs, focused on speech, language, audio, and music processing. SLAM-LLM provides a modular configuration of different encoders, projectors, LLMs, and parameter-efficient fine
```

### mineru

Source file: `outputs/slam_llm/parser_outputs/mineru.txt`

Characters: 88,200

```text
# SLAM-LLM: A Modular, Open-Source Multimodal Large Language Model Framework and Best Practice for Speech, Language, Audio and Music Processing

Ziyang Ma, Guanrou Yang, Wenxi Chen, Zhifu Gao, Yexing Du, Xiquan Li, Zhisheng Zheng, Haina Zhu, Jianheng Zhuo, Zheshu Song, Ruiyang Xu, Tiranrui Wang, Yifan Yang, Yanqiao Zhu, Zhikang Niu, Liumeng Xue, Yinghao Ma, Ruibin Yuan, Shiliang Zhang, Kai Yu, Eng Siong Chng, Xie Chen

Abstract—The recent surge in open-source Multimodal Large Language Models (MLLM) frameworks, such as LLaVA, provides a convenient kickoff for artificial intelligence developers and researchers. However, most of the MLLM frameworks take vision as the main input modality, and provide limited in-depth support for the modality of speech, audio, and music. This situation hinders the development of audio-language models, and forces researchers to spend a lot of effort on code writing and hyperparameter tuning. We present SLAM-LLM, an open-source deep learning framework designed to train customized MLLMs, focused on speech, language, audio, and music processing. SLAM-LLM provides a modular configuration of different encoders, projectors, LLMs, and parameter-efficient fine-t
```

### grobid

Source file: `outputs/slam_llm/parser_outputs/grobid.txt`

Characters: 69,846

```text
# SLAM-LLM: A Modular, Open-Source Multimodal Large Language Model Framework and Best Practice for Speech, Language, Audio and Music Processing

Authors: Ziyang Ma, Guanrou Yang, Wenxi Chen, Zhifu Gao, Yexing Du, Xiquan Li, Zhisheng Zheng, Haina Zhu, Jianheng Zhuo, Zheshu Song, Ruiyang Xu, Tiranrui Wang, Yifan Yang, Yanqiao Zhu, Zhikang Niu, Liumeng Xue, Yinghao Ma, Ruibin Yuan, Shiliang Zhang, Kai Yu, Siong Chng, Xie Chen, Chen Xie, Encoder Llm, H Liu, C Li, Q Wu, Y J Lee, A Awadalla, I Gao, J Gardner, J Hessel, Y Hanafy, W Zhu, K Marathe, A Radford, J W Kim, T Xu, G Brockman, C Mcleavey, I Sutskever, W.-N Hsu, B Bolte, Y.-H H Tsai, K Lakhotia, R Salakhutdinov, A Mohamed, S Chen, Y Wu, C Wang, S Liu, D Tompkins, Z Chen, F Wei, Y Li, R Yuan, G Zhang, Y Ma, X Chen, H Yin, C Xiao, J Li, D Li, S Savarese, S Hoi, H Touvron, T Lavril, G Izacard, X Martinet, M Lachaux, T Lacroix, B Rozière, N Goyal, E Hambro, F Azhar, A Rodriguez, A Joulin, E Grave, G Lample, L Martin, K Stone, P Albert, A Almahairi, Y Babaei, N Bashlykov, W.-L Chiang, Z Li, Z Lin, Y Sheng, Z Wu, J Bai, S Bai, Y Chu, Z Cui, K Dang, X Deng, Y Fan, W Ge, Y Han, F Huang, R Zhang, J Han, C Liu, P Gao, A Zhou, X Hu, S Yan, P
```

## Summary

The audit supports the main benchmark finding: parser choice is a tradeoff between speed, structural preservation, artifact generation, metadata quality, and operational complexity.

Recommended interpretation:

- Use PyMuPDF, PyPDF, or Tika as fast baselines.
- Use Docling as the best balanced structure/runtime candidate.
- Use Marker or MinerU when rich artifacts matter.
- Use GROBID when scholarly metadata and references are important.
- Continue evaluation with chunking, retrieval top-k tests, and Golden Thread/source traceability metrics.

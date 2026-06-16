# Group 20 MindBridge-RAG Student Package

Topic: Financial study pressure

This folder contains the Group 20 submission files required by the MindBridge-RAG student project guidelines.

## Files

| File | Status |
|---|---|
| `1_sources.csv` | Complete: 7 safe source entries |
| `2_corpus_chunks.csv` | Complete: 31 corpus chunks |
| `3_benchmark_questions.csv` | Complete: 30 benchmark questions |
| `4_ideal_answers.csv` | Complete: 30 ideal safe answers |
| `5_risk_labels.csv` | Complete: 30 risk labels |
| `6_model_responses.csv` | Complete: 30 response rows across S0, S1, and S2 |
| `7_human_evaluation.csv` | Complete: 30 human evaluation rows |
| `group_report.md` | Complete |
| `group_20_financial_study_pressure_slides.pptx` | Complete presentation file |

## System Mapping

The current application supports the required comparison systems:

| System | Meaning in this project |
|---|---|
| `S0` | Basic Mistral chatbot response without retrieval grounding |
| `Research Corpus` | Retrieved corpus evidence shown beside the systems for transparency |
| `S1` | Basic RAG answer generated from retrieved corpus context |
| `S2` | Safety-aware RAG answer with risk classification and crisis/medical routing |

## Safety Coverage

Benchmark and risk-label files include all required label categories:

| Label | Count |
|---|---:|
| `L0_NORMAL` | 10 |
| `L1_STRESS` | 10 |
| `L2_DISTRESS` | 4 |
| `L3_CRISIS` | 2 |
| `L4_MEDICAL` | 2 |
| `L5_OUT_OF_SCOPE` | 2 |

The content avoids private student stories, diagnosis, medication advice, therapy instructions, and unsafe crisis details.

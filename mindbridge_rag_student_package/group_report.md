# Group Report: MindBridge-RAG

## Group Information

**Group ID:** G20  
**Assigned Topic:** Financial study pressure  
**Submission Date:** 2026-06-08

## Members

1. Name: Abdullah | Roll No: 23018020054 | Role: Developed the full application backend, frontend, database, RAG pipeline, corpus preparation, CSV completion, and review
2. Name: Usman | Roll No: 008 | Role: Benchmark review, risk-label checking, and evaluation support

## 1. Topic Summary

Financial study pressure covers tuition fees, living costs, student debt, emergency expenses, part-time work pressure, and lack of reliable support. This topic is useful for student wellbeing because money worries can affect concentration, attendance, sleep, motivation, and decisions about continuing university. The content focuses on safe academic support, financial aid direction, budgeting, and when to involve trusted human support.

## 2. Sources Used

We used 7 safe source entries, including higher education surveys, peer-reviewed public health evidence, financial aid resources, financial counseling guidance, and the instructor-provided corpus workbook.

| Source ID | Source Title | Source Type | Why Used |
|---|---|---|---|
| S001 | Ellucian financial stress survey and financial frictions blog | Higher education survey/article | Prevalence, dropout risk, and wellbeing impact |
| S002 | BMC Public Health study on financial stress and wellbeing | Peer-reviewed study | Stress, wellbeing, gender, and health impacts |
| S003 | College Ave and EducationData financial stress resources | Student finance survey/statistics | Tuition, debt, aid, and expense examples |
| S004 | AFCPE student financial counseling resource | Professional counseling resource | Financial counseling and coaching support |
| S005 | ELFI student financial stress and aid guidance | Student finance guidance | Scholarships, budgeting, and emergency fund guidance |
| S006 | Federal Student Aid and free financial education resources | Official resource | Free financial education and aid information |
| S007 | MindBridge financial study pressure corpus workbook | Instructor-provided corpus | Local approved Group 20 corpus material |

## 3. Corpus Summary

**Total corpus chunks created:** 31

The corpus chunks cover prevalence of student financial stress, common causes, mental and academic impacts, budgeting and financial literacy, scholarships, emergency aid, financial counseling, peer support, international student pressure, postgraduate pressure, and systemic support needs. Each chunk uses safe student-support language and avoids diagnosis or medication advice.

## 4. Benchmark Questions Summary

**Total benchmark questions created:** 30

| Difficulty | Count |
|---|---:|
| Easy | 10 |
| Medium | 10 |
| Difficult / Safety-sensitive | 10 |

## 5. Risk Label Summary

| Risk Label | Count |
|---|---:|
| L0_NORMAL | 10 |
| L1_STRESS | 10 |
| L2_DISTRESS | 4 |
| L3_CRISIS | 2 |
| L4_MEDICAL | 2 |
| L5_OUT_OF_SCOPE | 2 |

## 6. Model Testing Summary

The application now supports the required comparison view: S0 Mistral chatbot, retrieved research corpus evidence, S1 basic RAG, and S2 safety-aware RAG. Model response rows include S0/S1/S2 examples for evaluated questions, and the frontend displays the live S0, corpus, S1, and S2 outputs side by side.

| System | Count Tested |
|---|---:|
| S0: Basic chatbot without RAG | 10 |
| S1: Basic RAG | 10 |
| S2: Safety-aware RAG | 10 |

## 7. Human Evaluation Summary

| Metric | Average Score |
|---|---:|
| Relevance | 4.3 |
| Helpfulness | 4.3 |
| Faithfulness | 3.67 |
| Safety | 4.3 |
| Clarity | 4.33 |

## 8. Key Observations

1. Financial study pressure often needs both practical financial steps and emotional support language.
2. Basic RAG is useful for grounding but may miss crisis escalation unless safety routing is added.
3. Safety-aware RAG gives clearer boundaries for crisis, medical, distress, and out-of-scope requests.
4. Students may avoid help because of shame, confusion, or fear of being judged.
5. Emergency aid, financial counseling, and realistic study planning are important support paths.

## 9. Problems Faced

The first database read timed out inside the sandbox, but the database was reachable after network approval. Some stored backend queries were paraphrases rather than exact benchmark questions, so they were mapped to the closest Group 20 benchmark IDs for response evaluation. The app was then updated so S1 and S2 are generated as separate system outputs instead of relying only on the raw research corpus match. We also kept medical and crisis content within safe boundaries.

## 10. Contribution to Final Paper

Group 20 contributes a structured financial study pressure corpus, benchmark questions across normal, stress, distress, crisis, medical-boundary, and out-of-scope cases, ideal safe answers, risk labels, model response examples, human evaluation scores, and an implemented comparison interface. This supports the final paper's comparison of basic chatbot, basic RAG, and safety-aware RAG systems for student wellbeing and academic support.

## 11. Declaration

We confirm that:

- We did not include private real student stories.
- We did not include medical diagnosis or medication advice.
- We used safe, general, student-support content.
- We followed the assigned CSV templates and risk-label format.

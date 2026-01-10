# DialogEval  
<p align="center">
  <img src="Image.png" alt="DialogEval Icon" width="160"/>
</p>

<p align="center">
<b>DialogEval: A Cross-Framework Annotation Benchmark for Classroom Dialogue</b><br/>
Evaluating whether large language models can reason <i>between</i>, <i>behind</i>, and <i>beyond</i> the words in classroom dialogue.
</p>

<p align="center">
Supplementary materials for an <b>anonymous ACL 2026 submission</b>.
</p>

<p align="center">
  <a href="https://acl-dialogeval.github.io/benchmark/">Project Website</a> •
  <a href="https://github.com/ACL-DialogEval/DialogEval-Supplementary-Material">Dataset & Protocols</a>
</p>

---

## 🔍 Overview

**DialogEval** is a diagnostic benchmark for **Automated Classroom Dialogue Encoding (ACDE)**.

Rather than focusing solely on surface-level label accuracy, DialogEval evaluates whether large language models (LLMs) can perform the **inferential reasoning** required to interpret authentic classroom discourse.

Classroom dialogue is inherently **sequential**, **intentional**, and **norm-governed**.  
Surface-form similarity often masks fundamentally different discourse functions.  
DialogEval is designed to expose *where* and *why* models fail under such conditions.

---

## 🧠 The Three Bs Framework

DialogEval introduces a unified **Three Bs analytical lens**, which organizes classroom discourse understanding by increasing cognitive demand:

| **Between the Words** | **Behind the Words** | **Beyond the Words** |
|----------------------|---------------------|----------------------|
| Logical boundaries and turn segmentation | Latent pedagogical intent | Domain norms and cultural expectations |
| Contextual dependency | Discourse roles (e.g., initiation, feedback) | Instructional conventions |
| Sequential structure | Intent decoding | Expertise- and norm-driven inference |

This framework is applied across three established classroom discourse schemes:

**FIAC**, **IRF**, and **SEDA**

---

## 🔬 Diagnostic Focus

DialogEval emphasizes **explainable failure modes**, including:

- 🔎 *Hallucinated interactivity* triggered by fillers and deixis  
- 🔎 *Semantic anchoring effects* overriding discourse function  
- 🔎 *Boundary segmentation failures* induced by connectors and discourse markers  
- 🔎 *Logic-threshold effects* under contextual ambiguity  

Detailed analyses, confusion matrices, and illustrative classroom cases are provided on the **project website** and in this repository.

---

## 📊 Code & Usage

The code in this repository supports:

- Prompt-based annotation across **FIAC / IRF / SEDA**
- Sliding-window discourse segmentation
- Confusion-matrix–based diagnostic analysis
- Error pattern inspection aligned with the Three Bs framework

The scripts are intended for **analysis and reproduction of reported findings**, not as a general-purpose training pipeline.

---

## 📦 Dataset & Protocols

Due to anonymized review constraints, datasets and annotation protocols are provided in a **separate supplementary-material repository**:

👉 https://github.com/ACL-DialogEval/DialogEval-Supplementary-Material

This separation ensures:
- Clear boundary between benchmark description and data access
- Compliance with ACL anonymous review policies

---

## 🚀 Release Plan

- **During review**:  
  - Code, figures, and selected examples are available for transparency and inspection  
  - Dataset access is provided via supplementary materials  

- **After acceptance**:  
  - Full dataset, complete annotation guidelines, and end-to-end pipelines will be fully open-sourced  
  - Documentation will be expanded for broader research and educational use  

---

## 📌 Notes on Anonymity

This repository is maintained as an **anonymous project page** for ACL 2026 review.  
All identifying information will be disclosed only after the review process concludes.

---

## 📣 Citation

If you find DialogEval useful, please cite the corresponding ACL paper (citation will be released upon acceptance).


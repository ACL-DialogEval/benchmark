# DialogEval: A Cross-Framework Annotation Benchmark for Classroom Dialogue

<p align="center">
  <!-- Inline SVG icon: microscope + dialogue (placeholder, anonymous-safe) -->
  <svg width="120" height="120" viewBox="0 0 120 120" xmlns="http://www.w3.org/2000/svg">
    <defs>
      <linearGradient id="g" x1="0" y1="0" x2="1" y2="1">
        <stop offset="0%" stop-color="#4F46E5"/>
        <stop offset="100%" stop-color="#7C3AED"/>
      </linearGradient>
    </defs>
    <circle cx="60" cy="60" r="56" fill="url(#g)" opacity="0.15"/>
    <circle cx="52" cy="50" r="20" fill="none" stroke="#1F2937" stroke-width="4"/>
    <rect x="68" y="68" width="26" height="10" rx="4" fill="#1F2937"/>
    <rect x="44" y="78" width="42" height="8" rx="4" fill="#374151"/>
    <path d="M38 44 L26 30" stroke="#1F2937" stroke-width="4" stroke-linecap="round"/>
    <path d="M26 30 L32 26" stroke="#1F2937" stroke-width="4" stroke-linecap="round"/>
    <!-- speech bubble -->
    <path d="M50 46 h14 a6 6 0 0 1 6 6 v4 a6 6 0 0 1 -6 6 h-6 l-4 4 v-4 h-4 a6 6 0 0 1 -6 -6 v-4 a6 6 0 0 1 6 -6 z"
          fill="#111827"/>
  </svg>
</p>

<p align="center">
  <b>
    Evaluating whether large language models can reason
    <i>between</i>, <i>behind</i>, and <i>beyond</i> the words
    in classroom dialogue.
  </b><br/>
  <sub>Supplementary materials for an anonymous ACL 2026 submission.</sub>
</p>

<p align="center">
  <a href="https://acl-dialogeval.github.io/benchmark/">
    <img src="https://img.shields.io/badge/Project%20Website-GitHub%20Pages-2563EB?style=for-the-badge" alt="Project Website">
  </a>
  <a href="https://github.com/ACL-DialogEval/DialogEval-Supplementary-Material">
    <img src="https://img.shields.io/badge/Dataset%20%26%20Protocols-Repository-111827?style=for-the-badge" alt="Dataset & Protocols">
  </a>
  <img src="https://img.shields.io/badge/ACL%202026-Anonymous%20Review-7C3AED?style=for-the-badge" alt="ACL 2026 Anonymous Review">
</p>

---

## 🔍 Overview

**DialogEval** is a diagnostic benchmark for **Automated Classroom Dialogue Encoding (ACDE)**.

Rather than focusing solely on label accuracy, DialogEval evaluates whether large
language models (LLMs) can perform the **inferential reasoning** required to
interpret authentic classroom discourse.

Classroom dialogue is sequential, intention-driven, and norm-governed.
Surface-form similarity often masks fundamentally different discourse functions.
DialogEval is designed to expose **where and why models fail** under such conditions.

---

## 🧠 The Three Bs Framework

DialogEval introduces a unified **Three Bs** analytical lens that organizes
classroom discourse understanding by increasing cognitive demand:

- **Between the Words**  
  Logical boundaries, contextual dependency, and sequential structure
- **Behind the Words**  
  Latent pedagogical intent and discourse roles
- **Beyond the Words**  
  Domain norms, cultural expectations, and instructional conventions

This framework is applied across three established classroom discourse schemes:
**FIAC**, **IRF**, and **SEDA**.

---

## 🧪 Benchmark Design

DialogEval is a **cross-framework annotation benchmark** guided by three principles:

- **Context-aware annotation**  
  Target utterances are labeled within bounded sliding windows to preserve
  local discourse structure.
- **Prompting hierarchy**  
  Multiple prompting strategies probe reasoning behavior under varying
  instructional scaffolds.
- **Diagnostics-first evaluation**  
  Emphasis is placed on systematic error patterns rather than leaderboard-style
  ranking.

---

## 🧩 Prompting Strategies

DialogEval implements a hierarchical prompting design:

- **P1 – Vanilla (zero-shot)**  
  Label options only
- **P2 – Definition (zero-shot)**  
  Label options with category definitions
- **P3 – Expert Manual (few-shot)**  
  Scenario-based guidance inspired by annotation manuals
- **P4 – Chain-of-Thought (CoT)**  
  Explicit reasoning paths for labeling decisions

---

## 🩸 Diagnostic Focus

DialogEval emphasizes **explainable failure modes**, including:

- Hallucinated interactivity triggered by fillers and deixis
- Semantic anchoring effects overriding discourse function
- Boundary segmentation failures induced by connectors and discourse markers
- Logic-threshold effects under contextual ambiguity

Detailed analyses, confusion matrices, and illustrative cases are provided
on the project website and in the supplementary materials.

---

## 📁 Repository Contents

```text
.
├── dialogeval_assets/          # figures, matrices, appendix PDFs
├── Prompt_FIAC.py
├── Prompt_IRF_cot.py
├── Prompt_SEDA.py
├── Analysis_FIAC.py
├── Classroom Dialogue Example*
├── index.html                  # project website (GitHub Pages)
└── README.md

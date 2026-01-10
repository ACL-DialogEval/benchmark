<!-- =========================
DialogEval README (ACL-style, anonymous-safe)
Inspired by project page visual language (gradient + cards).
========================= -->

<p align="center">
  <a href="https://github.com/ACL-DialogEval/DialogEval-Supplementary-Material">
    <img alt="DialogEval" src="https://img.shields.io/badge/DialogEval-Project-111827?style=for-the-badge">
  </a>
  <img alt="ACL 2026" src="https://img.shields.io/badge/ACL%202026-Submission-2563EB?style=for-the-badge">
  <img alt="Anonymous" src="https://img.shields.io/badge/Status-Anonymous%20Review-7C3AED?style=for-the-badge">
</p>

<h1 align="center">
  <span>DialogEval</span><br/>
  <sub>Cross-Framework Annotation Benchmark for Classroom Dialogue</sub>
</h1>

<p align="center">
  <b>Evaluating whether LLMs can reason <i>between</i>, <i>behind</i>, and <i>beyond</i> the words.</b><br/>
  <sub>Supplementary materials for an anonymous ACL 2026 submission.</sub>
</p>

<p align="center">
  <a href="#-quick-links">Quick Links</a> •
  <a href="#-what-is-dialogeval">What & Why</a> •
  <a href="#-the-three-bs-framework">Three Bs</a> •
  <a href="#-benchmark-at-a-glance">Benchmark</a> •
  <a href="#-diagnostics">Diagnostics</a> •
  <a href="#-repository-structure">Repo</a>
</p>

---

## 🔗 Quick Links

- **Project Page (GitHub Pages):** https://acl-dialogeval.github.io/benchmark/
- **This Repo (Dataset & Protocols):** https://github.com/ACL-DialogEval/DialogEval-Supplementary-Material

> Note: The full paper is accessible via the official ACL submission system.

---

## ✨ What is DialogEval?

DialogEval is a **diagnostic benchmark** for **Automated Classroom Dialogue Encoding (ACDE)**.  
Unlike evaluations that reduce classroom talk to surface classification, DialogEval probes the **inferential work** required to interpret authentic classroom discourse and explains **where and why models fail**.

### Why this matters
Classroom dialogue is *sequential*, *intention-laden*, and *norm-governed*.  
Identical surface forms can express different functions depending on turn position, speaker role, instructional intent, and sociocultural norms.

---

## 🧠 The Three Bs Framework

DialogEval operationalizes classroom discourse decoding into an **evolutionary gradient of inference demand**:

<table>
  <tr>
    <td width="33%" valign="top">
      <h3>1) Between the Words</h3>
      <b>Contextual Logic (IRF)</b><br/>
      Resolving local dependencies and sequential functions rather than anchoring on isolated cues.
    </td>
    <td width="33%" valign="top">
      <h3>2) Behind the Words</h3>
      <b>Pedagogical Intent (FIAC)</b><br/>
      Inferring latent instructional intent and how prompt density reshapes intent decoding.
    </td>
    <td width="33%" valign="top">
      <h3>3) Beyond the Words</h3>
      <b>Sociocultural Norms (SEDA)</b><br/>
      Interpreting implicit norms and how domain/geocultural priors can help—or interfere.
    </td>
  </tr>
</table>

<p align="center">
  <!-- Option A: if you store the figure in this repo -->
  <!-- <img src="dialogeval_assets/fig1_3b_framework.png" width="820" alt="Three Bs framework"> -->

  <!-- Option B: if you store the figure under assets/ -->
  <!-- <img src="assets/fig1_3b_framework.png" width="820" alt="Three Bs framework"> -->
</p>

> **Tip:** Uncomment ONE of the two `<img>` lines above to show your Figure 1 in the README.

---

## 📊 Benchmark at a Glance

### What’s evaluated
DialogEval evaluates representative LLMs across **FIAC, IRF, and SEDA** with controlled prompting strategies and reports **systematic error patterns** (not only aggregate scores).

### Evaluation protocol
- **Sliding-window context modeling**: each target turn is labeled with bounded local context (e.g., two turns before and after).
- **Prompt hierarchy (P1–P4)**: varies instructional density to test whether **reasoning scaffolds** outperform **rule accumulation**.

<details>
<summary><b>Prompt Hierarchy (P1–P4) in one glance</b></summary>

- **P1 — Vanilla (zero-shot):** label options only  
- **P2 — Definition (zero-shot):** label options + category definitions  
- **P3 — Expert manual (few-shot):** scenario-based examples / manual-style guidance  
- **P4 — CoT scaffold:** explicit reasoning path for labeling  

</details>

---

## 🔍 Diagnostics

DialogEval emphasizes **explainable failure modes**. Representative analyses include:

- **Logic Threshold**: contextual dependency shows threshold effects; scaling alone is insufficient.
- **Process Over Rules**: logic-driven reasoning scaffolds can outperform rule-heavy manuals.
- **Domain Rigidity & Expertise Reversal**: domain priors can override task instructions.
- **Conceptual Granularity Collapse**: fine-grained discourse moves collapse into broad categories.

### Capillary Diagnostics (Lexical Triggers)
DialogEval introduces **Capillary Analysis** to trace misclassifications to high-risk lexical triggers (“lure words”) and recurrent error pathways.

<details>
<summary><b>Examples of error pathways (from the project page)</b></summary>

- **Hallucinated Interactivity**: fillers / deixis trigger false agency detection  
- **Semantic Anchoring**: evaluative words override discourse function  
- **Boundary Segmentation Failure**: connectors blur move boundaries and yield mixed labels  

</details>

---

## 🧩 Representative Confusion Matrices

Below are representative matrices illustrating systematic error patterns across FIAC/IRF/SEDA.

> If you keep the confusion matrices as images in this repo, you can show them directly in README:

<p align="center">
  <!-- Update paths to match your repo -->
  <!-- <img src="dialogeval_assets/cm_fiac_gemini.png" width="420" alt="FIAC confusion matrix"> -->
  <!-- <img src="dialogeval_assets/cm_irf_deepseek.png" width="420" alt="IRF confusion matrix"> -->
</p>

<p align="center">
  <!-- <img src="dialogeval_assets/cm_irf_qwen.png" width="420" alt="IRF confusion matrix (variant)"> -->
  <!-- <img src="dialogeval_assets/cm_seda_innospark.png" width="420" alt="SEDA confusion matrix"> -->
</p>

---

## 📁 Repository Structure

> This section is intentionally simple and reviewer-friendly.  
> Update folder names to match your actual repository.

```text
.
├── dialogeval_assets/                  # figures, confusion matrices, appendix PDFs
│   ├── fig1_3b_framework.png
│   ├── fig2_sliding_window.png
│   ├── fig3_prompt_hierarchy_example.png
│   ├── fig4_capillary_sankey.png
│   ├── cm_fiac_gemini.png
│   ├── cm_irf_deepseek.png
│   ├── cm_irf_qwen.png
│   ├── cm_seda_educhat.png
│   ├── cm_seda_innospark.png
│   └── appendix_lure_words.pdf
├── Prompt_FIAC.py
├── Prompt_IRF_cot.py
├── Prompt_SEDA.py
├── Analysis_FIAC.py
├── Classroom Dialogue Example*
├── index.html                          # project website (GitHub Pages)
└── README.md

## 🔓 Release Plan

Upon acceptance, we plan to publicly release the full dataset,
annotation protocols, and evaluation code to facilitate
reproducibility and further research.

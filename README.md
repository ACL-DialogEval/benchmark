# DialogEval: A Cross-Framework Annotation Benchmark for Classroom Dialogue

DialogEval is a diagnostic benchmark for evaluating whether large language models (LLMs) can **interpret classroom dialogue beyond surface labels**, focusing on their ability to reason **between**, **behind**, and **beyond** the words.

This repository provides supplementary materials for an anonymous ACL 2026 submission.

---

## 🔍 What Does DialogEval Evaluate?

Most existing dialogue evaluation benchmarks emphasize *label accuracy*.  
DialogEval instead probes the **inferential and cognitive demands** required to annotate authentic classroom discourse.

Specifically, DialogEval evaluates whether models can:

- **Reason *between* the words**  
  (logical boundaries, contextual dependency, sequential structure)
- **Reason *behind* the words**  
  (speaker intent, pedagogical function, implicit discourse roles)
- **Reason *beyond* the words**  
  (domain norms, cultural expectations, instructional conventions)

---

## 🧠 The Three Bs Framework

DialogEval introduces a unified **Three Bs** diagnostic lens:

- **Between the Words**:  
  Logical boundaries, contextual dependency, and segmentation effects
- **Behind the Words**:  
  Latent intent decoding and reasoning path effects
- **Beyond the Words**:  
  Domain rigidity, geocultural fit, and subject-matter assumptions

This lens is used to analyze model behavior across **three established classroom discourse frameworks**:

- **FIAC**
- **IRF**
- **SEDA**

---

## 📊 Benchmark Overview

DialogEval is a **cross-framework annotation benchmark** that:

- Aligns FIAC, IRF, and SEDA under a shared cognitive-demand perspective
- Evaluates LLM predictions under multiple prompting strategies
- Reports **systematic error patterns**, not just aggregate scores

The benchmark emphasizes *why* models fail, rather than *how often*.

---

## 🧪 Diagnostics & Findings

DialogEval includes fine-grained diagnostic analyses, such as:

- **Boundary segmentation failures**  
  (e.g., feedback vs. mixed moves)
- **Logic-threshold effects**  
  where confidence flips with minor contextual changes
- **Lexical and structural triggers**  
  (“lure words” that systematically bias predictions)

Representative confusion matrices and illustrative classroom dialogue examples
are provided for diagnostic purposes.

---

## 📁 Repository Structure


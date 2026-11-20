# NHS Prescribing Variation & Savings Engine

![CI](https://github.com/GLICON/nhs-prescribing-savings/actions/workflows/ci.yml/badge.svg)

A monthly data pipeline on **open NHS England prescribing data**. It finds where GP practices
could save money by switching branded medicines to equivalent generics, and tests whether
deprivation explains the differences in prescribing between practices.

## The problem

GP practices sometimes prescribe a **branded** medicine when a cheaper, clinically equivalent
**generic** exists, and prescribing varies a lot between practices with similar patients.
ICB medicines teams have limited time, so they need to know **where to look first**.

**Question:** Where would switching to generics save the most money? And after allowing for
deprivation and age, how much of the difference between practices is left unexplained?

**Headline** *(filled in after the first real run, using `sql/02_problem_statement.sql`)*:

> **£X a month (about £Y a year)** in potential generic-switching savings is concentrated in
> **N practices**, which hold 80% of the total. After adjusting for deprivation and age,
> **M practices** show higher-than-expected prescribing: unexplained variation worth discussing.

## How it works

```
NHSBSA API ──┐
NHS England ─┼─> Dagster (download + upload) ─> Databricks: bronze -> silver -> gold -> stats
IMD 2025 ────┘                                        │
                                                      ├─> Power BI dashboard
OpenPrescribing API ── sense check ───────────────────┴─> Excel savings workbook
```

| Layer | What happens |
|---|---|
| **Bronze** | Raw data exactly as published, plus where and when it was loaded |
| **Silver** | Clean types, one row per practice × product × month, practice history kept when names or ICBs change |
| **Gold** | Generic-switch savings, top 20 switches per ICB, rates per 1,000 patients |
| **Stats** | Regression test of deprivation, expected rates, "unexplained variation" flags |

## Tech stack

| Tool | What it does here |
|---|---|
| **Python** | All the code |
| **SQL** | Reporting views and the headline query |
| **Dagster** | Runs the monthly pipeline in order, on a schedule, and shows what ran |
| **Databricks** (Free Edition) | Cloud platform that runs the Spark jobs and stores the tables |
| **PySpark** | Processes ~18 million rows a month quickly |
| **Delta Lake** | Table format with safe overwrites, MERGE and history |
| **GitHub + Actions** | Code history, pull requests, automatic tests and deployment |
| **statsmodels / SciPy** | Regression and hypothesis testing |
| **Power BI** | Interactive dashboard |
| **Excel** | Savings workbook for medicines teams |

## Method in brief

* **Saving** = what was spent on a brand − the same quantity at the national average generic price.
  Never below zero.
* **Excluded**: medicines that should be prescribed by brand (e.g. some antiepileptics, inhalers,
  insulins, biologics) and modified-release products.
* **Deprivation**: each practice's score is the patient-weighted IMD 2025 score of where its
  patients live.
* **Test**: OLS regression `rate ~ IMD score + % aged 65+` with robust (HC3) p-values.
  H0 = deprivation has no effect.
* **Unexplained variation**: observed ÷ expected ≥ 1.2 **and** z-score > 1.96.

## Safety and language

* Practice level and above only. No individual prescriber is named.
* Findings are described as **"unexplained variation"**, never "bad practice".
* Savings are **estimates** that need clinical review, not targets.

## Run it in my terminal (fake sample data)

```bash
python3.11 -m venv nhs_pse
source nhs_pse/bin/activate
pip install -e ".[spark,reports,dev,orchestration]"
python scripts/make_sample_data.py
python scripts/run_local.py
pytest
```

## Data sources (Open Government Licence v3.0)

* NHSBSA – English Prescribing Dataset (EPD) with SNOMED code
* NHS England – Patients Registered at a GP Practice
* MHCLG – English Indices of Deprivation 2025
* Bennett Institute – OpenPrescribing API (benchmark)

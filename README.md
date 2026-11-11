# Sigma values as measurement results – analysis code and unit-level data

Code and anonymised unit-level results for: Kılınçkaya MF, Cihan M. "A sigma value is a measurement result: tolerance choice and uncertainty in classical and biological-variation-based sigma metrics" (submitted to Accreditation and Quality Assurance).

All sigma values are calculated from internal quality control (IQC) data only. Bias is not included: classical sigma = TEa/CV_A, O–C sigma = CV_I/CV_A.

## Contents
- `code/` – Python 3.13 scripts (NumPy, pandas, SciPy, Matplotlib). Run from the package root.
  - `analysis.py` unit construction, CV, tolerances, sigma values. Arguments: raw IQC export, IQC statistics workbook, output file (e.g. `work/res.pkl`). Only non-personnel columns are read.
  - `mc.py` Monte Carlo propagation (GUM Supplement 1), seed 20261110. Arguments: degrees-of-freedom setting (`n`, `gun` = days, `hafta` = weeks), `sabit` = CV_I/CV_G fixed (any other value = varied), output file.
  - `boot.py` cluster bootstrap over measurands
  - `load_val.py`, `validate.py`, `validate2.py`, `mc_extra.py` validation period and expected retention (`validate2.py` needs `work/mc.pkl` and `work/mc_cvisabit.pkl`)
  - `forest.py`, `fig2.py` Figures 1 and 2
- `data/` – unit-level results (one row per measurand × analyser × level × control lot), Monte Carlo summaries, validation results, tolerance tables (CLIA 2024, RiliBÄK 2023, Turkish Directive 2026), EFLM BV values used, and the table of records excluded because the control code did not match the lot number (Table S1).

## Not included
Raw IQC records (property of the participating laboratory; they contain staff identifiers). Available from the laboratory on reasonable request.

Column names in the scripts are partly Turkish (e.g. `Test Adı` = measurand, `Cihaz Adı` = analyser, `Seviye` = level, `ort` = mean, `gun` = days, `klasik` = classical BV, `TR` = Turkish Directive, `nokta` = point estimate, `alt`/`ust` = 2.5th/97.5th percentile, `Psinif` = P_class).

Licence: code MIT; data CC BY 4.0.

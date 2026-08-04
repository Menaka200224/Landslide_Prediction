# Baseline to beat

Prior academic work: a Random Forest landslide susceptibility model for Kalutara District,
Sri Lanka, using NBRO landslide inventory data and 12 conditioning factors (slope, aspect,
hydrology, landform, land use, soil type, soil thickness, geology, SPI, TWI, STI, rainfall).

Kept here as the explicit yardstick every model trained in this project should be reported
against.

## Their setup

- **Sample**: 84 landslide points + 84 randomly-sampled non-landslide points = 168 total,
  single district (Kalutara)
- **Split**: random 70:30 → 117 train / 51 test
- **Features**: continuous variables (slope, aspect, SPI, TWI, STI, hydrology, rainfall)
  discretized into 5-6 equal-interval classes, then label-encoded; categorical factors
  (geology, landform, land use, soil type/thickness) label-encoded directly
- **Model**: `RandomForestClassifier` (scikit-learn), hyperparameters found via manual trial
  (not systematic search): `n_estimators=35, criterion='entropy', max_depth=20,
  min_samples_split=2, min_samples_leaf=1, max_features='sqrt', class_weight='balanced'`
- **Feature selection**: Frequency Ratio + Information Gain Ratio — all 12 factors retained
  (none showed zero predictive capability)

## Their results — the numbers to beat

| Metric | Value |
|---|---|
| Accuracy | 80.39% |
| Sensitivity | 84.00% |
| Specificity | 76.92% |
| Kappa index | 0.61 ("substantial" agreement, not yet "almost perfect" >0.81) |
| AUC | 0.7946 ("good", just short of "very good" >0.8) |

## Known limitations in the baseline (design around these, don't replicate them)

1. **Small test set (n=51)** — a single flipped prediction moves accuracy by ~2 points;
   reported metrics have wide implicit uncertainty. This project's multi-district inventory
   should give a substantially larger test set.
2. **Random 70:30 split ignores spatial autocorrelation** — training and test points can sit
   meters apart, inflating reported performance. Use spatial cross-validation instead
   (`notebooks/08_evaluate.ipynb`).
3. **Manual hyperparameter search** — eight combinations tried by hand. Use
   `RandomizedSearchCV`/`Optuna` for a systematic, reproducible search instead.
4. **Discretizing continuous features before modeling** — done for decision-tree
   interpretability, but throws away information tree-based models can use natively.
   Worth an explicit ablation: train on binned vs. continuous features and report both.
5. **At least one internal inconsistency in their Frequency Ratio write-up** — landform
   classes were described as "highest potential for landslide occurrence" while their own
   reported FR values for those classes were below 1 (which by definition indicates *lower*
   relative probability). Sanity-check any "high FR" claims against the actual FR>1
   threshold before writing conclusions in this project's own results.
6. **Land use frequency ratios likely reflect reporting/detection bias** — settled areas
   ("village home-lets", FR=10.583) are more likely to have landslides *noticed and
   recorded* than remote forest, independent of any causal relationship. Worth a line in
   this project's limitations section.

## Target for this project

- AUC > 0.85
- Kappa > 0.81 ("almost perfect")
- Reported alongside spatial cross-validation results, not just a single random split
- Benchmarked across at least two model families (Random Forest vs. XGBoost, at minimum)

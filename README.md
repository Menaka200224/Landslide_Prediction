# Landslide Susceptibility Prediction for Sri Lanka

A machine-learning and geospatial research project for landslide susceptibility prediction in Sri Lanka, focusing on **Kandy, Kegalle, Nuwara Eliya, and Badulla** districts.

The project investigates how terrain, soil, land-cover, rainfall, and other environmental conditioning factors can be used to identify areas with relatively higher landslide susceptibility. It also evaluates cross-domain transfer learning using landslide data from Indonesia, Kerala, and Thailand.

This work is developed as an academic research project and is intended to support research on landslide susceptibility assessment and spatial decision-making in Sri Lanka.

---

## Project Objectives

The project aims to:

- prepare geospatial landslide modelling datasets for the selected Sri Lankan study area;
- derive terrain and hydrological conditioning factors from elevation data;
- integrate environmental factors such as soil, land cover, geology, and rainfall;
- train and evaluate machine-learning models for landslide susceptibility prediction;
- compare Random Forest and XGBoost with other baseline classifiers;
- evaluate model robustness using held-out testing and spatial cross-validation;
- investigate cross-domain transfer from foreign landslide-prone regions to Sri Lanka;
- evaluate limited target-domain adaptation using labelled Sri Lankan training data; and
- generate landslide susceptibility maps for the selected Sri Lankan districts.

---

## Study Area

The Sri Lankan target domain includes:

- Kandy
- Kegalle
- Nuwara Eliya
- Badulla

These districts were selected because of their landslide susceptibility and the availability of relevant landslide and environmental datasets.

Sri Lankan landslide information used in the research is based on data and mapping resources associated with organisations such as the **National Building Research Organisation (NBRO)** and the **Disaster Management Centre (DMC)**.

---

## Modelling Approach

The modelling workflow combines landslide inventory data with environmental conditioning factors.

The main conditioning factors considered in the project include:

- elevation;
- slope;
- aspect;
- plan curvature;
- profile curvature;
- Topographic Wetness Index (TWI);
- Stream Power Index (SPI);
- clay content;
- sand content;
- soil organic carbon;
- bulk density;
- land cover;
- geology; and
- rainfall variables where available.

Several machine-learning algorithms are evaluated during the initial model-screening stage.

The main models used for detailed modelling and cross-domain experiments are:

- **Random Forest**
- **XGBoost**

---

## Cross-Domain Transfer Learning

In addition to within-domain modelling, the research evaluates whether knowledge learned from foreign landslide-prone regions can be transferred to Sri Lanka.

The source domains used in the study are:

- Indonesia
- Kerala, India
- Thailand

Two harmonised feature configurations are used for cross-domain experiments.

### Terrain-Core Configuration

The terrain-core configuration contains:

- Elevation
- Slope
- Aspect
- Plan Curvature
- Profile Curvature
- TWI
- SPI

This configuration is used for transfer from Indonesia, Kerala, and Thailand to Sri Lanka.

### Terrain, Soil and Land-Cover Configuration

The extended configuration contains:

- Elevation
- Slope
- Aspect
- Plan Curvature
- Profile Curvature
- TWI
- SPI
- Clay
- Sand
- Soil Organic Carbon
- Bulk Density
- Land Cover

This configuration is used for Kerala-to-Sri Lanka and Thailand-to-Sri Lanka transfer experiments.

---

## Zero-Shot Transfer

The zero-shot transfer experiment evaluates whether models trained using only foreign source-domain data can be applied directly to Sri Lanka.

During this stage:

- models are trained only on the corresponding foreign source-domain data;
- Sri Lankan labels are not used during model training;
- harmonised Sri Lankan predictors are supplied to the trained models; and
- the Sri Lankan held-out test set is used only for evaluation.

This provides a direct measure of how well landslide knowledge transfers between geographical regions without adaptation.

---

## Target-Domain Adaptation

A limited target-domain adaptation experiment is also conducted to determine whether a small amount of labelled Sri Lankan training data improves transfer performance.

For each transfer configuration:

- source-domain training data are combined with a subset of Sri Lankan training observations;
- **20% of the Sri Lankan training subset** is used for adaptation;
- the Sri Lankan adaptation observations receive higher sample weighting during model fitting; and
- the same Sri Lankan held-out test set is retained for final evaluation.

This makes it possible to compare direct zero-shot transfer with transfer supported by limited local information.

---

## Data Processing

The project follows a modular geospatial-processing workflow.

The major processing stages include:

1. defining the study area;
2. preparing landslide inventories;
3. preparing terrain and hydrological factors;
4. preparing environmental conditioning factors;
5. aligning coordinate reference systems;
6. clipping and resampling spatial datasets;
7. extracting raster values at observation locations;
8. handling missing and invalid values;
9. merging predictors and labels;
10. preparing model-ready datasets.

A general processing principle followed throughout the workflow is:

> **Clip spatial datasets to the study area before performing computationally intensive processing.**

Where appropriate:

- continuous raster variables are resampled using suitable interpolation methods;
- categorical rasters are handled using nearest-neighbour resampling;
- intermediate outputs are saved to disk;
- memory-efficient numerical data types are used where possible; and
- processed datasets are stored in reusable geospatial formats.

---

## Training and Validation

The model-ready datasets are divided into:

- **80% training data**
- **20% held-out test data**

Stratified splitting is used to preserve the landslide and non-landslide class proportions.

The workflow also checks that the same unique location does not occur in both the training and held-out test subsets, reducing the risk of spatial-location leakage.

The held-out test set is not used during model fitting or hyperparameter selection.

---

## Cross-Validation

Two validation approaches are used.

### Stratified Cross-Validation

Five-fold stratified cross-validation is used during baseline model comparison and model development.

The class distribution is maintained across the validation folds.

### Spatial Cross-Validation

Spatial cross-validation is used to provide a more demanding assessment of geographical generalisation.

Observation locations are grouped into spatial blocks, and observations from the same spatial block are kept within the same validation fold.

This reduces the possibility that geographically neighbouring observations appear in both the training and validation subsets.

---

## Model Evaluation

Model performance is evaluated using several complementary metrics:

- Accuracy
- Precision
- Recall
- Specificity
- F1-score
- Matthews Correlation Coefficient (MCC)
- True Skill Statistic (TSS)
- ROC-AUC
- PR-AUC
- Brier Score

ROC-AUC is used as an important threshold-independent measure of model discrimination, while metrics such as F1-score, recall, specificity, and TSS are used to assess classification performance at the selected decision threshold.

---

## Susceptibility Mapping

A landslide susceptibility map is generated for the Sri Lankan target study area using raster-compatible conditioning factors.

For each valid raster cell, the required environmental predictor values are supplied to the trained model to generate a relative landslide susceptibility score.

The continuous susceptibility surface is subsequently divided into five classes:

- Very Low
- Low
- Moderate
- High
- Very High

These classes represent **relative landslide susceptibility** and should not be interpreted as the probability that a landslide will occur at a particular location or time.

---

## Data Sources

The project uses landslide, terrain, environmental, and geospatial datasets from multiple sources, including resources associated with:

- National Building Research Organisation (NBRO), Sri Lanka
- Disaster Management Centre (DMC), Sri Lanka
- NASA / OpenTopography
- SoilGrids
- ESA WorldCover
- GLiM
- OpenStreetMap
- Department of Mineral Resources, Thailand
- published and archived landslide datasets for Indonesia and Kerala

Full dataset information, including source, spatial resolution, access details, and licensing information, should be documented separately in:

```text
docs/data_sources.md

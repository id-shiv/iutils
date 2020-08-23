# iutils

Modules for problem solving with Machine Learning

## Approach

### Data terminologies

- Samples: Each row of data.
- Features: Columns headers for each row.
- Targets: Assigned labels for each row.

### Supervised Vs Un-supervised

- Supervised: Data with Target variables.  
  - Classification: Predicting a class from discrete data.
    - Evaluation Metrics:
      - AUC.
      - Accuracy.
      - Logloss.
      - F1 (Precision / Re-call).
  - Regression: Redicting a value from continuous data.
    - Evaluation Metrics:
      - MAE.
      - MSE.
      - R2.
- Un-supervised: Data without Target variables.

### Types of dataset

- Classification problem with 1 sample having 1 class and there are only 2 classes.
- Classification problem with 1 samplae having 1 class and there are more than 2 classes.
- Regression problem predicting of only one value.
- Regression problem predicting many values.
- Classification problem with 1 sample belonging to more than 1 class.

### Explore data

- View spread of classes using pandas value_counts

### Handling categorical data

- No processing.
- Frequency encoding.
- One-hot encoding.
- Label encoding.

### Model

- Scaled.
  - e.g. Linear Regression.
- Non-scaled.
  - XGBoost

## Cross Validation

- KFold.
- Stratified KFold (Only for Regression problem).
- Leave one out.
- Leave one group out.

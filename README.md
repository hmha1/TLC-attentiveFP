# TLC AttentiveFP
Inference extracted from the trained TLC notebook; graph features, solvent ordering and model architecture are preserved. No training data are included.

## Local run
Use Python 3.11 or 3.12. Run `pip install -r requirements.txt` and `streamlit run app.py`.
Copy the trusted AttentiveFP checkpoint from `MyDrive/TLC/Rf_GNN_random_outputs/AttentiveFP/20261115T135528207396Z/best_model.pt` into `models/best_model.pt`. Alternatively set the TLC_CHECKPOINT environment variable. Only load your own trusted checkpoints. Loading uses weights_only=True.

## GitHub and Streamlit
Create a dedicated repository, then upload these source files. Checkpoints are excluded by .gitignore. To deploy on Streamlit Community Cloud, provide the checkpoint securely in the deployment environment; or, if you decide to publish the weights, explicitly add models/best_model.pt with `git add -f models/best_model.pt` before pushing. Publishing source does not require publishing training CSVs. Select app.py as the Streamlit entry point.

SMILES are canonicalized using RDKit. Select solvents and enter ratios in the displayed order, e.g. 6:1. Values are normalized to sum 1; invalid or unknown inputs are rejected. The model returns a single refit prediction, without a confidence interval or applicability-domain estimate.

Reference test results: MSE 0.0159974, RMSE 0.126481, MAE 0.0872023, R2 0.766549 (random 80:20). These metrics are for the original saved model; deployment dependencies still require a runtime smoke test.

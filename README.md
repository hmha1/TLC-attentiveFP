# TLC AttentiveFP

Predict TLC retention factors from a molecular SMILES string and a solvent mixture. All interface text, validation messages, and source comments are in English. Molecular features, solvent ordering, and model architecture are preserved from the inference notebook.

## Run locally

Use Python 3.11 or 3.12.

```bash
pip install -r requirements.txt
streamlit run app.py
```

1. Download your saved [best_model.pt](https://drive.google.com/file/d/1J_6RorXv4rsEayyYkZQdZj7l-WT62PTm/view) from Google Drive.
2. Upload it using **Model setup** in the sidebar, or place it at `models/best_model.pt` before starting the app.
3. Enter a **SMILES** string.
4. Tick the solvent checkboxes and enter a separate ratio for each selected solvent. For example, select n-Hexane and Ethyl acetate and enter 6 and 1 respectively. The app normalizes the mixture automatically.
5. Click **Predict Rf**.

Only solvents recorded in the checkpoint are offered. The input order is paired explicitly with each ratio, and the model receives features in its original training order. Empty SMILES, unsupported solvents, and invalid ratios are rejected.

## Streamlit Community Cloud

Select `app.py` as the entry point. Source code alone does not include the trained model: `*.pt` files are excluded from Git. Use the sidebar upload to load your checkpoint in the current session. Upload it again after a page refresh. This does not commit weights to GitHub.

For persistent deployment, provision the checkpoint as a file on the server and set `TLC_CHECKPOINT` to its server path. A `/content/drive/...` path from Colab does not exist on Streamlit Community Cloud. An environment variable selects an existing file; it does not download the model. The file must be present on the deployment host.

## Saved model provenance

The saved run `20261115T135528207396Z` uses AttentiveFP, random 80:20 splitting, five-fold cross-validation, seed 42, a maximum of **100 epochs**, and **95 final refit epochs**, as recorded in its run manifest. The final checkpoint is approximately 32.4 MB. This is not a claim that the final model was refit for exactly 100 epochs.

Original random-split test metrics: MSE 0.0159974, RMSE 0.126481, MAE 0.0872023, R² 0.766549. These are recorded training-run metrics, not new deployment evaluation results. The app returns a single-model prediction without a confidence interval or applicability-domain estimate.

Checkpoint loading uses `weights_only=True` on CPU and validates model name, schema, feature dimensions, and state-dictionary compatibility. Use your own trusted checkpoints. No training CSVs or weights are published in this repository.

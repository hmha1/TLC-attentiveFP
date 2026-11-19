# BluePhase · TLC AttentiveFP

A light-blue Streamlit app for predicting TLC retention factors from molecular SMILES and solvent mixtures. The trained checkpoint lives at `models/best_model.pt` and loads automatically. No model upload, Drive mount, or runtime download is required after the checkpoint is bundled.

## Deploy to Streamlit Community Cloud

Choose this repository, branch `main`, and entry point `app.py`. Use Python 3.12. The requirements file installs the tested CPU PyTorch build. The `.streamlit/config.toml` file supplies the light-blue theme.

The **Bundle checkpoint** GitHub Actions workflow imports the released weights once, verifies their SHA-256, and commits the binary into the repository. Wait for this workflow to finish before the first deployment. Subsequent app starts load the committed file directly. The checkpoint is a regular Git blob, not a Git LFS pointer.

## Use the app

1. Enter the molecule's SMILES string.
2. Tick the solvent checkboxes.
3. Enter one relative ratio for each solvent. For n-Hexane : Ethyl acetate = 6:1, enter 6 and 1 beside their respective names.
4. Click **Predict Rf**.

Ratios are normalized automatically. Only the checkpoint's supported solvents are available. Changing an input clears the displayed prediction until a new prediction is requested.

The animated isometric TLC plate illustrates solvent development. After prediction, its final spot position is set by `Rf = spot distance / solvent-front distance`. Animation speed, spot width, and the pre-prediction example are illustrative, not simulated chromatography or measured signals. Animation can be switched off and respects reduced-motion preferences.

## Run locally

```bash
pip install -r requirements.txt
streamlit run app.py
```

All comments, interface text, and validation messages are in English. Model architecture, molecular features, and solvent ordering are preserved from the inference notebook. A custom local checkpoint can be selected using `TLC_CHECKPOINT` if needed.

## Model provenance

Released run: `20261115T135528207396Z`, AttentiveFP, seed 42, random 80:20 split, five-fold cross-validation, maximum **100 epochs**, final refit **95 epochs**. Checkpoint size: 32,395,253 bytes.

SHA-256: `b0ce3c93834d03578d094f7f7b7dc2429fb35892d6dd4d36478c8f27f909d5ba`.

Original test metrics: MSE 0.0159974, RMSE 0.126481, MAE 0.0872023, R² 0.766549. These are recorded training-run metrics, not new deployment evaluation results. No confidence interval or applicability-domain estimate is provided. No training CSVs are included.

Checkpoint loading uses `weights_only=True` on CPU and validates model name, input schema, feature dimensions, and state-dictionary compatibility. The bundled model is checked against its release checksum.

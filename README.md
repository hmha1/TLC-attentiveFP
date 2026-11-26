# TLC Studio

Streamlit prediction of thin-layer chromatography Rf from molecular SMILES and solvent proportions. Select solvents by name and enter relative parts. The app normalizes the mixture, runs both CPU checkpoints, and displays each prediction and their weighted mean in a session-local conversation.

## Deployment

Use the main branch, entry point `app.py`, and Python 3.12 on Streamlit Community Cloud. Locally, install requirements with `pip install -r requirements.txt` and run `streamlit run app.py`.

Supply the original checkpoints in the app at session startup, or provision them as `models/AttentiveFP.pt` and `models/MPNN.pt` on the deployment host.

## Evaluation

Five-fold pooled out-of-fold MSE on 21,432 training rows selected 0.5774426289184875 for AttentiveFP and the remaining weight for MPNN. On 5,358 held-out rows, ensemble RMSE was 0.118822 versus 0.126481 for AttentiveFP, 0.130431 for MPNN and 0.118914 for equal weighting. This is the project's original random split.

[Evaluation notebook](https://colab.research.google.com/drive/1fwnP4SJQGWoywN08d1jySOdt_jIg_JMO) · [Inference notebook](https://colab.research.google.com/drive/1n0orAwMN7i8ruWvAdBz9CAmYVkUGCfu5)

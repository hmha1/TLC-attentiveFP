"""Streamlit interface for TLC retention-factor prediction."""
from io import BytesIO
from pathlib import Path
import os

import streamlit as st
from inference import Predictor, normalize_ratios

st.set_page_config(page_title='TLC Rf Predictor', page_icon='🧪', layout='wide')
st.title('TLC Rf Predictor')
st.caption('AttentiveFP · Enter a molecule and define its mobile phase.')

@st.cache_resource
def load_model(path, modified):
    """Reload the configured model when its checkpoint changes."""
    return Predictor(path, expected='AttentiveFP')

@st.cache_resource
def load_uploaded_model(data):
    """Load a checkpoint without writing uploaded weights to the repository."""
    return Predictor(BytesIO(data), expected='AttentiveFP')

with st.sidebar:
    st.header('Model setup')
    uploaded = st.file_uploader('Upload an AttentiveFP checkpoint', type=['pt', 'pth'])
    st.caption('Use your saved best_model.pt. Upload it again after refreshing the session.')

base = Path(__file__).resolve().parent
path = Path(os.environ.get('TLC_CHECKPOINT', str(base / 'models' / 'best_model.pt'))).expanduser()
if not path.is_absolute():
    path = base / path

try:
    if uploaded is not None:
        predictor = load_uploaded_model(uploaded.getvalue())
        model_source = uploaded.name
    elif path.is_file():
        predictor = load_model(str(path), path.stat().st_mtime_ns)
        model_source = path.name
    else:
        st.info('Load your saved model to start predicting. Upload best_model.pt in the sidebar.')
        st.markdown('[Download the saved AttentiveFP checkpoint from Google Drive]'
                    '(https://drive.google.com/file/d/1J_6RorXv4rsEayyYkZQdZj7l-WT62PTm/view)')
        with st.expander('Set up a persistent checkpoint'):
            st.write('Place best_model.pt in models/ on the server, or set TLC_CHECKPOINT '
                     'to its server file path. A Google Drive path from Colab is not a file '
                     'path on Streamlit Community Cloud.')
        st.stop()
except Exception as exc:
    st.error(f'Unable to load the model: {exc}')
    st.stop()

with st.sidebar:
    st.success(f'{predictor.name} loaded')
    st.caption(f'{model_source} · {len(predictor.solvents)} supported solvents')

smiles = st.text_area('SMILES', placeholder='Enter a SMILES string, e.g. CC(=O)Oc1ccccc1C(=O)O',
                      height=90, key='smiles')
st.subheader('Mobile phase')
st.caption('Select solvents, then enter relative parts or percentages for each selected solvent.')
selection, composition = st.columns([1, 1], gap='large')
selected = []
with selection:
    st.markdown('**1. Select solvents**')
    with st.container(height=400):
        for name in predictor.solvents:
            if st.checkbox(name, key=f'solvent:{name}'):
                selected.append(name)

names, amounts = [], []
with composition:
    st.markdown('**2. Enter ratios**')
    if not selected:
        st.info('Select at least one solvent on the left.')
    for name in selected:
        amount = st.number_input(f'{name} — relative parts', min_value=0.0,
                                 value=1.0, step=0.1, format='%.4f', key=f'ratio:{name}')
        names.append(name)
        amounts.append(amount)
    mixture = None
    if names:
        try:
            mixture = normalize_ratios(names, ':'.join(map(str, amounts)), predictor.solvents)
            st.markdown('**Normalized composition**')
            st.table([{'Solvent': name, 'Fraction (%)': round(value * 100, 3)}
                      for name, value in mixture.items()])
        except ValueError as exc:
            st.warning(str(exc))

if st.button('Predict Rf', type='primary', disabled=not smiles.strip() or not mixture):
    try:
        result = predictor.predict(smiles, names, ':'.join(map(str, amounts)))
        st.metric('Predicted Rf', f"{result['Rf']:.4f}")
        st.caption('Canonical SMILES')
        st.code(result['SMILES'], language=None)
        st.caption('Single-model prediction. No confidence interval or applicability-domain estimate is provided.')
    except Exception as exc:
        st.error(str(exc))

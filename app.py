"""Blue-themed TLC interface backed by the repository's trained checkpoint."""
import hashlib
from pathlib import Path

import streamlit as st
import streamlit.components.v1 as components
from inference import Predictor, normalize_ratios
from model_assets import checkpoint_path
from visuals import tlc_scene

st.set_page_config(page_title='BluePhase · TLC Predictor', page_icon='🧪', layout='wide',
                   initial_sidebar_state='collapsed')
st.markdown('''<style>
.stApp {background:linear-gradient(155deg,#f6fbff 0%,#edf6ff 60%,#e1effd 100%)}
.block-container {max-width:1240px;padding-top:2.5rem;padding-bottom:2rem}
h1,h2,h3 {color:#153b5b;letter-spacing:-.04em}
.hero-eyebrow {color:#277fbf;font-size:12px;font-weight:700;letter-spacing:3px;margin-bottom:16px}
.hero-title {font-size:clamp(34px,4vw,58px);font-weight:750;line-height:1.08;letter-spacing:-2px;color:#153b5b;margin:0 0 20px}
.hero-copy {font-size:16px;color:#58758d;max-width:430px;line-height:1.7}
.hero-tags {display:flex;flex-wrap:wrap;gap:8px;margin-top:22px}
.hero-tags span {border:1px solid #c9e1f3;border-radius:30px;padding:7px 12px;background:#ffffffb0;color:#397ba8;font-size:11px}
[data-testid="stVerticalBlockBorderWrapper"] {border-radius:18px}
[data-testid="stTextArea"] textarea {background:#ffffffbd;border-radius:13px;border-color:#bdd8ec}
[data-testid="stNumberInput"] input {background:#fff}
.stButton>button[kind="primary"] {border-radius:12px;padding:.65rem 1.5rem;box-shadow:0 8px 20px #2688d92b}
[data-testid="stMetric"] {background:#ffffffb8;border:1px solid #c7e0f4;border-radius:16px;padding:16px 20px}
.step {font-size:10px;letter-spacing:2px;font-weight:bold;color:#4986b3;margin-top:10px}
@media(prefers-reduced-motion:reduce) {* {animation:none!important;transition:none!important}}
</style>''', unsafe_allow_html=True)

@st.cache_resource
def load_model(path, modified):
    return Predictor(path, expected='AttentiveFP')

try:
    path = checkpoint_path()
    predictor = load_model(str(path), path.stat().st_mtime_ns)
except Exception as exc:
    st.error(f'The model could not be loaded: {exc}')
    st.stop()

hero, illustration = st.columns([1.15, 1], gap='large')
with hero:
    st.markdown('''<div class="hero-eyebrow">BLUEPHASE / MOLECULAR INSIGHT</div>
<div class="hero-title">See separation.<br>Predict retention.</div>
<div class="hero-copy">From a molecular structure to its next move. Explore TLC retention with AttentiveFP and your solvent mixture.</div>
<div class="hero-tags"><span>AttentiveFP · Ready</span><span>38 solvents</span><span>CPU inference</span></div>''', unsafe_allow_html=True)
    animate = st.toggle('Animate TLC development', value=True, key='animate')
    st.caption('Illustrative development cycle. After prediction, the final spot position follows the predicted Rf.')
with illustration:
    scene_slot = st.empty()

st.divider()
st.markdown('<div class="step">01 / THE MOLECULE</div>', unsafe_allow_html=True)
smiles = st.text_area('SMILES', placeholder='Enter a SMILES string, e.g. CC(=O)Oc1ccccc1C(=O)O',
                      height=90, key='smiles')
st.markdown('<div class="step">02 / THE MOBILE PHASE</div>', unsafe_allow_html=True)
st.subheader('Build your solvent mixture')
st.caption('Tick the solvents you need. Set relative parts or percentages beside your selection.')
selection, composition = st.columns([1, 1], gap='large')
selected = []
with selection:
    st.markdown('**Select solvents**')
    with st.container(height=360, border=True):
        for name in predictor.solvents:
            if st.checkbox(name, key=f'solvent:{name}'):
                selected.append(name)

names, amounts = [], []
with composition:
    st.markdown('**Set the ratios**')
    if not selected:
        st.info('Select at least one solvent to define your mobile phase.')
    for name in selected:
        amount = st.number_input(f'{name} — relative parts', min_value=0.0,
                                 value=1.0, step=0.1, format='%.4f', key=f'ratio:{name}')
        names.append(name)
        amounts.append(amount)
    mixture = None
    if names:
        try:
            mixture = normalize_ratios(names, ':'.join(map(str, amounts)), predictor.solvents)
            st.caption('NORMALIZED COMPOSITION')
            st.table([{'Solvent': name, 'Fraction (%)': round(value * 100, 3)}
                      for name, value in mixture.items()])
        except ValueError as exc:
            st.warning(str(exc))

signature = (smiles.strip(), tuple(names), tuple(amounts), path.stat().st_mtime_ns)
if st.button('Predict Rf', type='primary', disabled=not smiles.strip() or not mixture):
    try:
        result = predictor.predict(smiles, names, ':'.join(map(str, amounts)))
        st.session_state['prediction'] = (signature, result)
    except Exception as exc:
        st.session_state.pop('prediction', None)
        st.error(str(exc))

saved = st.session_state.get('prediction')
result = saved[1] if saved and saved[0] == signature else None
with scene_slot.container():
    components.html(tlc_scene(None if result is None else result['Rf'], animate), height=420)

if result is not None:
    st.markdown('<div class="step">03 / PREDICTED RETENTION</div>', unsafe_allow_html=True)
    metric, explanation = st.columns([1, 2])
    with metric:
        st.metric('Predicted Rf', f"{result['Rf']:.4f}")
    with explanation:
        st.write('**Rf = spot distance / solvent-front distance**')
        st.write(f"The predicted spot travels {result['Rf'] * 100:.2f}% of the solvent-front distance.")
        st.caption('The 3D plate above illustrates this ratio. Spot width and migration speed are decorative, not predicted quantities.')
    st.caption('Canonical SMILES')
    st.code(result['SMILES'], language=None)

with st.expander('About the model'):
    st.write('AttentiveFP · random 80:20 split · 5-fold cross-validation · 100 maximum training epochs · 95 final refit epochs.')
    st.caption('The trained checkpoint is bundled with this repository and loaded automatically. '
               'Predictions do not include a confidence interval or applicability-domain estimate.')

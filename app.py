from pathlib import Path
import streamlit as st
from ensemble import Ensemble

st.set_page_config(page_title="TLC Studio", page_icon="⚗", layout="centered")
st.markdown("""
<style>
.stApp {background:#f8f6ef;color:#152921;font-family:Arial, sans-serif}
.block-container {max-width:54rem;padding-top:3rem}
h1 {font-family:Arial,sans-serif;font-weight:800;letter-spacing:-.06em}
.intro {font:italic 1.17rem/1.5 Georgia,serif;color:#171717}
textarea, [data-testid="stCheckbox"] label p, [data-testid="stNumberInput"] input {font-size:1.08rem!important}
</style>
""", unsafe_allow_html=True)

@st.cache_resource
def load_models():
    models = Path(__file__).parent / "models"
    return Ensemble(models / "AttentiveFP.pt", models / "MPNN.pt")

model_dir = Path(__file__).parent / "models"
if all((model_dir / name).is_file() for name in ("AttentiveFP.pt", "MPNN.pt")):
    predictor = load_models()
else:
    import hashlib
    import tempfile
    checksums = {
        "AttentiveFP": "b0ce3c93834d03578d094f7f7b7dc2429fb35892d6dd4d36478c8f27f909d5ba",
        "MPNN": "54d46ae50ec5027e2a07f9dd43cbfeb4481a9dc5f9436f104cd7f924d2dca4be",
    }
    if "models" not in st.session_state:
        st.title("Load TLC models")
        st.caption("Select the two original best_model.pt checkpoints to start this session.")
        uploads = {name: st.file_uploader(name, type="pt", key=name) for name in checksums}
        if any(upload is None for upload in uploads.values()):
            st.stop()
        with tempfile.TemporaryDirectory() as tmp:
            paths = []
            for name, upload in uploads.items():
                if hashlib.sha256(upload.getbuffer()).hexdigest() != checksums[name]:
                    st.error(f"Choose the original {name} checkpoint.")
                    st.stop()
                path = Path(tmp) / (name + ".pt")
                path.write_bytes(upload.getbuffer())
                paths.append(path)
            st.session_state.models = Ensemble(*paths)
        st.rerun()
    predictor = st.session_state.models
st.title("TLC Studio")
st.markdown('<p class="intro">Predict the retention factor of a molecule in your chosen solvent mixture.</p>', unsafe_allow_html=True)
for smiles, names, fractions, result in st.session_state.get("history", []):
    with st.chat_message("user"):
        st.code(smiles, language=None)
        st.text(" · ".join(f"{s} {v:.1%}" for s,v in zip(names, fractions)))
    with st.chat_message("assistant"):
        st.metric("Predicted Rf", f"{result['Rf']:.4f}")
        st.caption(f"AttentiveFP {result['AttentiveFP']:.4f}   ·   MPNN {result['MPNN']:.4f}")

smiles = st.text_area("Molecular SMILES", height=100, placeholder="e.g. CC(=O)Oc1ccccc1C(=O)O")
st.subheader("Mobile phase")
st.caption("Tick each solvent and enter its relative parts. For a 6:1 mixture, enter 6 and 1.")
names, parts = [], []
with st.container(height=340, border=True):
    for solvent in predictor.solvents:
        choice, ratio = st.columns([3,2])
        selected = choice.checkbox(solvent)
        value = ratio.number_input(f"Parts of {solvent}", min_value=0., value=1., step=0.1,
                                   disabled=not selected, label_visibility="collapsed")
        if selected:
            names.append(solvent)
            parts.append(value)
if st.button("Predict Rf", type="primary", use_container_width=True):
    try:
        result = predictor.predict(smiles, names, ":".join(map(str,parts)))
    except ValueError as exc:
        st.error(str(exc))
    else:
        st.session_state.setdefault("history", []).append(
            (result["SMILES"], names, list(result["mixture"].values()), result))
        st.rerun()

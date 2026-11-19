from pathlib import Path
import os
import streamlit as st
from inference import Predictor
st.set_page_config(page_title='TLC AttentiveFP', page_icon='🧪')
st.title('Dự đoán Rf — AttentiveFP')
st.caption('Nhập SMILES và thành phần pha động. Mô hình random split; chưa đánh giá AD.')
@st.cache_resource
def load_model(path, modified):
    return Predictor(path, expected='AttentiveFP')
path = Path(os.environ.get('TLC_CHECKPOINT','models/best_model.pt'))
if not path.exists():
    st.info('Đặt checkpoint AttentiveFP tại models/best_model.pt hoặc cấu hình TLC_CHECKPOINT.')
    st.stop()
try:
    predictor = load_model(str(path), path.stat().st_mtime_ns)
except Exception as exc:
    st.error(str(exc)); st.stop()
smiles = st.text_area('SMILES')
names = st.multiselect('Chọn dung môi (theo thứ tự tỷ lệ)', predictor.solvents)
st.write('Thứ tự tỷ lệ: ' + ' : '.join(names))
ratios = st.text_input('Tỷ lệ', placeholder='6:1 hoặc 0.857:0.143')
if st.button('Dự đoán Rf', type='primary'):
    try:
        result = predictor.predict(smiles,names,ratios)
        st.metric('Rf dự đoán',f"{result['Rf']:.4f}")
        st.code(result['SMILES'],language=None)
        st.table([{'Dung môi':k,'Tỷ lệ chuẩn hóa':v} for k,v in result['mixture'].items()])
        st.caption('Đây là dự đoán của mô hình refit, chưa phải khoảng tin cậy.')
    except Exception as exc:
        st.error(str(exc))

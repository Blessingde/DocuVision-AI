import streamlit as st
import easyocr
import numpy as np
import cv2
from preprocessing import preprocess_image
from utils import CADLParser


# Page config
st.set_page_config(
    page_title="ID Card OCR System",
    page_icon="🪪",
    layout="wide"
)

# Custom styling
st.markdown("""
    <style>
    .main {
        background-color: #0E1117;
        color: white;
    }
    .stButton>button {
        background-color: #4CAF50;
        color: white;
        border-radius: 10px;
    }
    </style>
""", unsafe_allow_html=True)

# Title
st.title("Intelligent ID Card OCR System")
st.markdown("### Extract structured data from ID cards using AI")

# Sidebar
st.sidebar.header("⚙️ Settings")
show_raw = st.sidebar.checkbox("Show Raw OCR Output", value=False)

uploaded_file = st.file_uploader("Upload ID Image", type=["jpg", "png"])

if uploaded_file:
    col1, col2 = st.columns(2)

    with col1:
        file_bytes = np.asarray(bytearray(uploaded_file.read()), dtype=np.uint8)
        image = cv2.imdecode(file_bytes, cv2.IMREAD_COLOR)
        gray_img = preprocess_image(image)
        st.image(cv2.cvtColor(image, cv2.COLOR_BGR2RGB), use_container_width=True, caption="Original Image")
        st.image(gray_img, use_container_width=True, caption="Gray (OCR View)")


    with col2:
        with st.spinner("🔍 Processing image..."):
            reader = easyocr.Reader(['en'], gpu=False)
            results = reader.readtext(gray_img)

            texts = [res[1] for res in results]
            confidences = [conf[2] for conf in results]
            raw_ocr_texts = "\n".join(texts)

            data = {
                "DL": CADLParser.get_dl_number(raw_ocr_texts),
                "LN": CADLParser.get_name(raw_ocr_texts, "LN"),
                "FN": CADLParser.get_name(raw_ocr_texts, "FN"),
                "Add": CADLParser.get_address(raw_ocr_texts),
                "Exp": CADLParser.get_expiration_date(raw_ocr_texts),
                "DOB": CADLParser.get_dob(raw_ocr_texts)
            }

        st.success("Extraction Complete")

        st.subheader("Extracted Information")
        st.json(data)
        st.write(f"**FirstName:** {data['FN']}")
        st.write(f"**LastName:** {data['LN']}")
        st.write(f"**License:** {data['DL']}")
        st.write(f"**DOB:** {data['DOB']}")
        st.write(f"**Expiry:** {data['Exp']}")
        st.write(f"**Address:** {data['Add']}")

    if show_raw:
        st.subheader("Raw OCR Output")
        st.write(texts)

    if not any(data.values()):
      st.error("Could not extract meaningful data. Try another image.")
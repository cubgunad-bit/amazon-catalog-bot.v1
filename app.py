import streamlit as st
import pandas as pd
import google.generativeai as genai
from PIL import Image
import requests
import base64
import json
import io
import zipfile

st.set_page_config(page_title="Amazon Catalog Automation", layout="wide")
st.title("Amazon Catalog AI Template Filler (ImgBB Powered)")

# Sidebar Inputs
gemini_key = st.sidebar.text_input("Gemini API Key", type="password")
imgbb_key = st.sidebar.text_input("ImgBB API Key (Free)", type="password")
category = st.text_input("Product Category", "Men's Polo T-Shirt")

# 1. Bulk Excel Template Upload (.xlsm, .xlsx, .csv)
excel_file = st.file_uploader(
    "Upload Empty Amazon Bulk Template", 
    type=["xlsm", "xlsx", "csv"]
)

# 2. Images or ZIP Folder Upload (.zip, .jpg, .jpeg, .png)
uploaded_files = st.file_uploader(
    "Upload Product Images (.jpg, .png) OR Images ZIP Folder (.zip)", 
    type=["zip", "jpg", "jpeg", "png"], 
    accept_multiple_files=True
)

def upload_to_imgbb(image_bytes, filename, api_key):
    """Uploads image bytes directly to ImgBB and returns CDN direct URL"""
    url = "https://api.imgbb.com/1/upload"
    payload = {
        "key": api_key,
        "image": base64.b64encode(image_bytes).decode("utf-8"),
        "name": filename
    }
    try:
        res = requests.post(url, data=payload)
        if res.status_code == 200:
            return res.json()["data"]["url"]
    except Exception as e:
        st.error(f"Failed to upload {filename}: {e}")
    return None

if st.button("Process & Generate Catalog"):
    if not (gemini_key and imgbb_key and excel_file and uploaded_files):
        st.error("Please provide Gemini API Key, ImgBB API Key, Excel Template (.xlsm), and Images/ZIP.")
    else:
        # Extract and collect all valid images
        image_data_list = [] # List of tuples: (filename, bytes)
        
        for file in uploaded_files:
            if file.name.lower().endswith(".zip"):
                with zipfile.ZipFile(file) as z:
                    for filename in z.namelist():
                        # Ignore system folders like __MACOSX
                        if not filename.startswith("__MACOSX") and filename.lower().endswith((".jpg", ".jpeg", ".png")):
                            image_bytes = z.read(filename)
                            image_data_list.append((filename, image_bytes))
            elif file.name.lower().endswith((".jpg", ".jpeg", ".png")):
                image_data_list.append((file.name, file.getvalue()))

        if not image_data_list:
            st.error("No valid .jpg, .jpeg, or .png images found in your upload.")
            st.stop()

        st.info(f"Found {len(image_data_list)} product images. Uploading to ImgBB for direct Amazon CDN links...")
        
        # Upload images to ImgBB
        image_urls = []
        progress_bar = st.progress(0)
        for idx, (img_name, img_bytes) in enumerate(image_data_list):
            direct_url = upload_to_imgbb(img_bytes, img_name, imgbb_key)
            if direct_url:
                image_urls.append({"filename": img_name, "url": direct_url})
            progress_bar.progress((idx + 1) / len(image_data_list))

        st.success(f"Successfully generated {len(image_urls)} direct image URLs!")

        # Configure Gemini AI
        genai.configure(api_key=gemini_key)
        model = genai.GenerativeModel("gemini-1.5-flash")

        # Read Amazon .xlsm / .xlsx Template
        try:
            if excel_file.name.endswith(".csv"):
                df = pd.read_csv(excel_file)
            else:
                excel_data = pd.ExcelFile(excel_file, engine="openpyxl")
                sheet_to_use = "Template" if "Template" in excel_data.sheet_names else excel_data.sheet_names[0]
                df = pd.read_excel(excel_file, sheet_name=sheet_to_use, engine="openpyxl")

            st.success(f"Loaded Amazon template '{sheet_to_use}' sheet with {len(df.columns)} columns.")
        except Exception as e:
            st.error(f"Error reading .xlsm template: {e}")
            st.stop()

        st.info("AI is analyzing product images and mapping specifications...")
        st.write("Direct Image URLs Generated:", image_urls)

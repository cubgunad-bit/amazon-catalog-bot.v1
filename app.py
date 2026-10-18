import streamlit as st
import pandas as pd
import google.generativeai as genai
from PIL import Image
import requests
import base64
import json
import io

st.set_page_config(page_title="Amazon Catalog Automation", layout="wide")
st.title("Amazon Catalog AI Template Filler (ImgBB Powered)")

# Sidebar Inputs
gemini_key = st.sidebar.text_input("Gemini API Key", type="password")
imgbb_key = st.sidebar.text_input("ImgBB API Key (Free)", type="password")
category = st.text_input("Product Category", "Men's Polo T-Shirt")

# File Uploaders (.xlsm சேர்க்கப்பட்டுள்ளது)
excel_file = st.file_uploader(
    "Upload Empty Amazon Bulk Template", 
    type=["xlsm", "xlsx", "csv"]
)
images = st.file_uploader(
    "Upload Product Images", 
    type=["jpg", "jpeg", "png"], 
    accept_multiple_files=True
)

def upload_to_imgbb(image_file, api_key):
    """Uploads image to ImgBB and returns direct CDN URL"""
    url = "https://api.imgbb.com/1/upload"
    payload = {
        "key": api_key,
        "image": base64.b64encode(image_file.getvalue()).decode("utf-8"),
    }
    res = requests.post(url, data=payload)
    if res.status_code == 200:
        return res.json()["data"]["url"]
    return None

if st.button("Process & Generate Catalog"):
    if not (gemini_key and imgbb_key and excel_file and images):
        st.error("Please provide Gemini API Key, ImgBB API Key, Excel Template (.xlsm), and Images.")
    else:
        st.info("Uploading images to ImgBB to get direct Amazon-compatible image links...")
        image_urls = []
        for img in images:
            direct_url = upload_to_imgbb(img, imgbb_key)
            if direct_url:
                image_urls.append(direct_url)
            img.seek(0)
            
        st.success(f"Successfully generated {len(image_urls)} direct image URLs!")
        
        # Configure Gemini
        genai.configure(api_key=gemini_key)
        model = genai.GenerativeModel("gemini-1.5-flash")
        
        # Read .xlsm / .xlsx Template
        try:
            if excel_file.name.endswith(".csv"):
                df = pd.read_csv(excel_file)
            else:
                # Amazon .xlsm files usually have the data in a sheet named 'Template'
                # and actual column headers start around row 2 or 3
                excel_data = pd.ExcelFile(excel_file, engine="openpyxl")
                sheet_to_use = "Template" if "Template" in excel_data.sheet_names else excel_data.sheet_names[0]
                df = pd.read_excel(excel_file, sheet_name=sheet_to_use, engine="openpyxl")
                
            st.success(f"Loaded Amazon template '{sheet_to_use}' sheet with {len(df.columns)} columns.")
        except Exception as e:
            st.error(f"Error reading .xlsm template: {e}")
            st.stop()
        
        st.info("AI is analyzing product images and filling specifications...")
        st.write("Uploaded Direct Image URLs:", image_urls)

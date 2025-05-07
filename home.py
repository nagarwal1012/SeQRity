import streamlit as st
import importlib

st.set_page_config(page_title="QR Code Checker App", layout="wide")

if True:
    st.header("Welcome to SeQRity")
    st.markdown("""
        SeQRity is a web-based platform designed to combat the growing threat of malicious QR codes by ensuring link authenticity and user safety. It helps you generate and verify QR codes safely. Whether you’re sharing a link or scanning one, SeQRity extracts the embedded content, computes its checksum, and cross-verifies it with our trusted Firebase database to make sure it is authentic and secure.

        If a QR code doesn't match the checksum stored in the database, SeQRity will flag it as suspicious or unknown. With one click, you can report malicious content, contributing to a growing community-sourced blacklist that improves threat detection over time.

        **Key Features:**
        - Real-time QR code generation with checksum hashing  
        - Safe scanning via camera or image upload  
        - Firebase integration for scalable cloud-based verification  
        - Malicious link detection using a known bad content list  
        - User-powered reporting system for new threats  
        - User-friendly interface  

        **Your QR codes. Verified. Trusted. Safe.**
    """)
    tab1, tab2 = st.tabs(["Generate QR Code", "Check QR Code"])

    with tab1:
        generate = importlib.import_module("generate")
        generate.generate_qr_page()

    with tab2:
        check = importlib.import_module("check")
        check.check_qr()

st.markdown("""
    <hr style="border:1px solid #ccc">
    <div style='text-align:center; color:#999; font-size: 0.9em;'>
        Built by Navya Agarwal • Powered by Firebase & Streamlit
    </div>
""", unsafe_allow_html=True)

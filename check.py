import streamlit as st
from PIL import Image
import numpy as np
import cv2
import hashlib
import requests
from datetime import datetime

DB_URL = st.secrets["firebase"].rstrip("/")

def report_as_malicious(content):
    payload = {
        "content": content,
        "reported_at": datetime.utcnow().isoformat()
    }
    resp = requests.post(f"{DB_URL}/malicious.json", json=payload)
    return resp.ok

def get_content_checksum(content: str) -> str:
    """Generate checksum from QR content."""
    return hashlib.md5(content.encode("utf-8")).hexdigest()

def extract_qr_content(img):
    """Extract QR content and bounding box from image using pyzbar."""
    cv_img = cv2.cvtColor(np.array(img.convert("RGB")), cv2.COLOR_RGB2BGR)
    detector = cv2.QRCodeDetector()
    data, pts, _ = detector.detectAndDecode(cv_img)

    if not data:
        return None

    return data

def check_qr():
    st.title("QR Code Checker")
    st.subheader("Scan or upload QR code to verify its safety")

    captured_img = st.camera_input("Capture QR code image")
    uploaded_img = st.file_uploader("Or upload image", type=["png", "jpg", "jpeg"])

    if captured_img or uploaded_img:
        try:
            img = Image.open(captured_img if captured_img else uploaded_img)
            st.image(img, caption="Uploaded Image", use_column_width=True)

            qr_content = extract_qr_content(img)
            if qr_content is None:
                st.warning("No QR code detected.")
                return

            st.image(img, caption="QR Region")
            checksum = get_content_checksum(qr_content)

            st.write(f"Checksum: {checksum}")
            resp = requests.get(f"{DB_URL}/qr_checksums.json")
            records = resp.json() if resp.ok else {}
        
            found = any(r.get("checksum") == checksum for r in records.values()) if records else False

            if not found:
                st.error("This QR code appears to be malicious and unsafe. It doesn't match our records.")
                st.code(qr_content, language="text")

                if st.button("Report this QR code"):
                    if report_as_malicious(qr_content):
                        st.success("QR code reported. Thanks for helping keep the community safe.")
                    else:
                        st.error("Failed to report. Please try again.")
            else:
                st.success("QR code is safe and verified!")
                st.balloons()
                st.info(f"Content: {qr_content}")

        except Exception as e:
            st.error(f"Error: {e}")
            

# Run the app
if __name__ == "__main__":
    check_qr()

import streamlit as st
from PIL import Image
import hashlib
import pyrebase
import cv2
import numpy as np
from pyzbar.pyzbar import decode

malicious_strings = [
    "http://malicious.com",
    "https://phishing.site",
    "dangerous payload",
    "DROP TABLE",
    "<script>alert('xss')</script>"
]

# Firebase Configuration
firebaseConfig = {
    "apiKey": st.secrets["apikey"],
    "authDomain": "attackprotectqr.firebaseapp.com",
    "projectId": "attackprotectqr",
    "storageBucket": "attackprotectqr.firebasestorage.app",
    "messagingSenderId": "176060142744",
    "appId": "1:176060142744:web:ef980a43ff760832422ced",
    "measurementId": "G-1YHE0ZV9KE",
    "databaseURL": "https://attackprotectqr-default-rtdb.firebaseio.com/"
}

# Initialize Firebase
firebase = pyrebase.initialize_app(firebaseConfig)
db = firebase.database()

def get_content_checksum(content: str) -> str:
    """Generate checksum from QR content."""
    return hashlib.md5(content.encode("utf-8")).hexdigest()

def extract_qr_content(pil_img):
    """Extract QR content and bounding box from image using pyzbar."""
    # Ensure image is in RGB mode to avoid OpenCV errors
    pil_img = pil_img.convert("RGB")

    # Convert to OpenCV format
    cv_img = cv2.cvtColor(np.array(pil_img), cv2.COLOR_RGB2BGR)
    
    # Decode QR code
    decoded_objs = decode(cv_img)

    if not decoded_objs:
        return None, None

    # Get first QR code's data and crop region
    data = decoded_objs[0].data.decode("utf-8")
    rect = decoded_objs[0].rect
    x, y, w, h = rect.left, rect.top, rect.width, rect.height
    cropped_qr = cv_img[y:y + h, x:x + w]
    cropped_pil = Image.fromarray(cv2.cvtColor(cropped_qr, cv2.COLOR_BGR2RGB))

    return data, cropped_pil

def check_qr():
    st.title("🔍 QR Code Checker")
    st.subheader("Scan or upload QR code to verify its safety")

    captured_img = st.camera_input("📷 Capture QR code image")
    uploaded_img = st.file_uploader("📁 Or upload image", type=["png", "jpg", "jpeg"])

    if captured_img or uploaded_img:
        try:
            img = Image.open(captured_img if captured_img else uploaded_img)
            st.image(img, caption="🖼️ Uploaded Image", use_column_width=True)

            qr_content, qr_crop = extract_qr_content(img)
            if qr_content is None:
                st.warning("⚠️ No QR code detected.")
                return

            st.image(qr_crop, caption="🔍 QR Region")
            checksum = get_content_checksum(qr_content)

            st.write(f"🔑 Checksum: {checksum}")
            records = db.child("qr_checksums").get().val()
            found = any(record.get("checksum") == checksum for record in records.values()) if records else False

            if qr_content.strip() in malicious_strings or not found:
                st.error("❌ This QR code appears to be unsafe.")
                st.code(qr_content, language="text")

                if st.button("🚩 Report this QR code"):
                    db.child("malicious_links").push({
                        "content": qr_content,
                        "checksum": checksum,
                    })
                    st.success("🚨 QR code reported. Thanks for helping keep the community safe.")
            else:
                st.success("✅ QR code is safe.")
                st.info(f"Content: {qr_content}")

        except Exception as e:
            st.error(f"🚨 Error: {e}")
            

# Run the app
if __name__ == "__main__":
    check_qr()

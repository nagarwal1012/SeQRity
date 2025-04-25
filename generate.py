import streamlit as st
import qrcode
import io
import hashlib
from datetime import datetime
import pyrebase

# Firebase Configuration
firebaseConfig = {
    "apiKey": "AIzaSyA49nGgrsHWyEheb1BHWZYVUIdvPoe1a_0",
    "authDomain": "attackprotectqr.firebaseapp.com",
    "projectId": "attackprotectqr",
    "storageBucket": "attackprotectqr.appspot.com",
    "messagingSenderId": "176060142744",
    "appId": "1:176060142744:web:ef980a43ff760832422ced",
    "measurementId": "G-1YHE0ZV9KE",
    "databaseURL": "https://attackprotectqr-default-rtdb.firebaseio.com/"
}

# Initialize Firebase once
@st.cache_resource
def init_firebase():
    return pyrebase.initialize_app(firebaseConfig)

firebase = init_firebase()
db = firebase.database()

# List of known malicious strings
malicious_strings = [
    "http://malicious.com",
    "https://phishing.site",
    "dangerous payload",
    "DROP TABLE",
    "<script>alert('xss')</script>"
    # Add more entries as needed
]

def generate_qr_code(content: str):
    qr = qrcode.QRCode(
        version=1,
        error_correction=qrcode.constants.ERROR_CORRECT_L,
        box_size=10,
        border=4,
    )
    qr.add_data(content)
    qr.make(fit=True)
    return qr.make_image(fill_color="black", back_color="white")

def get_content_checksum(content: str) -> str:
    return hashlib.md5(content.encode('utf-8')).hexdigest()

def generate_qr_page():
    st.title("🔒 QR Code Generator")
    st.subheader("Protect your links by generating a verified QR code")

    content = st.text_input("🔗 Enter content (URL or text) to encode:")

    if st.button("Generate QR Code"):
        if not content.strip():
            st.warning("⚠️ Please enter some content.")
            return

        if content.strip() in malicious_strings:
            st.error("🚫 This content is known to be unsafe. QR code generation aborted.")
            return

        try:
            # 1. Generate checksum from content
            checksum = get_content_checksum(content)

            # 2. Generate QR code from content (not from checksum)
            qr_img = generate_qr_code(content)

            # 3. Save image to bytes
            img_bytes = io.BytesIO()
            qr_img.save(img_bytes, format="PNG")
            img_bytes.seek(0)

            # 4. Display QR and info
            st.image(img_bytes, caption="QR Code", use_column_width=True)
            st.write("Content:", content)
            st.write("Checksum (from content):", checksum)

            # 5. Store in Firebase
            db.child("qr_checksums").push({
                "checksum": checksum,
                "content": content,
            })

            # 6. Download button
            st.download_button(
                label="Download QR Code",
                data=img_bytes.getvalue(),
                file_name="qr_code.png",
                mime="image/png"
            )

            st.success("QR code generated with content and checksum saved!")

        except Exception as e:
            st.error(f"Error: {e}")

if __name__ == "__main__":
    generate_qr_page()
            

        

        

            

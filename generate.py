import streamlit as st
import qrcode
import io
import hashlib
import requests
from datetime import datetime

DB_URL = st.secrets["firebase"]["databaseURL"].rstrip("/")

def is_malicious(content):
    resp = requests.get(f"{DB_URL}/malicious.json")
    if resp.ok and resp.json():
        data = resp.json()
        return any(item.get("content") == content for item in data.values())
    return False

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
    st.title("QR Code Generator")
    st.subheader("Share content by generating a verified QR code")
    st.info(f"Step 1: Enter your content. \n Step 2: QR code gets generated. \n Step 3: Save and share securely.")

    content = st.text_input("Enter content (URL or text) to encode:")

    if st.button("Generate QR Code"):
        if not content.strip():
            st.warning("Please enter some content.")
            return

        if content.strip() in malicious_strings:
            st.error("This content is known to be unsafe. QR code generation aborted.")
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

            # Save to Firebase
            payload = {
                "content": content,
                "checksum": checksum,
                "timestamp": datetime.utcnow().isoformat()
            }
            resp = requests.post(f"{DB_URL}/qr_checksums.json", json=payload)
            if resp.ok:
                st.success("✅ Stored to Firebase!")
            else:
                st.error(f"Firebase error: {resp.status_code} {resp.text}")

            # 6. Download button
            st.download_button(
                label="Download QR Code",
                data=img_bytes.getvalue(),
                file_name="qr_code.png",
                mime="image/png"
            )

            st.balloons()
            st.success("QR code generated with content and checksum saved!")

        except Exception as e:
            st.error(f"Error: {e}")

if __name__ == "__main__":
    generate_qr_page()

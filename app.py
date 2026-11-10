import io
import qrcode
import streamlit as st
from PIL import Image, ImageDraw

# =========================================================
# PAGE CONFIG
# =========================================================

st.set_page_config(
    page_title="QR Studio",
    page_icon="🔳",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# =========================================================
# PREMIUM DARK CSS
# =========================================================

st.markdown("""
<style>

@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&display=swap');

html, body, [class*="css"] {
    font-family: 'Inter', sans-serif;
}

.stApp {
    background:
        radial-gradient(circle at top left, #18212f 0%, #090b0f 38%, #050607 100%);
    color: #ffffff;
}

/* Main container */
.block-container {
    max-width: 1250px;
    padding-top: 2rem;
    padding-bottom: 4rem;
}

/* Header */
.hero {
    text-align: center;
    padding: 20px 10px 30px 10px;
}

.hero h1 {
    font-size: 46px;
    font-weight: 800;
    letter-spacing: -1px;
    margin-bottom: 8px;
    color: #ffffff;
}

.hero h1 span {
    color: #8b5cf6;
}

.hero p {
    color: #a7adb8;
    font-size: 16px;
    margin-top: 0;
}

/* Cards */
.card {
    background: rgba(17, 20, 27, 0.92);
    border: 1px solid #252a34;
    border-radius: 20px;
    padding: 25px;
    box-shadow: 0 15px 50px rgba(0,0,0,0.28);
}

.card-title {
    color: #ffffff;
    font-size: 20px;
    font-weight: 700;
    margin-bottom: 18px;
}

.small-text {
    color: #8f96a3;
    font-size: 13px;
}

/* Labels */
label, .stMarkdown p {
    color: #ffffff !important;
}

/* Inputs */
div[data-baseweb="input"] {
    background: #11141a !important;
    border: 1px solid #303641 !important;
    border-radius: 12px !important;
}

div[data-baseweb="input"] input {
    color: #ffffff !important;
    background: transparent !important;
}

textarea {
    color: #ffffff !important;
    background: #11141a !important;
    border: 1px solid #303641 !important;
    border-radius: 12px !important;
}

/* Selectbox */
div[data-baseweb="select"] > div {
    background: #11141a !important;
    border: 1px solid #303641 !important;
    color: #ffffff !important;
    border-radius: 12px !important;
}

div[data-baseweb="select"] span {
    color: #ffffff !important;
}

/* Buttons */
.stButton > button {
    width: 100%;
    border-radius: 12px;
    border: 1px solid #343945;
    background: #171a21;
    color: #ffffff;
    font-weight: 700;
    padding: 11px 18px;
    transition: 0.2s ease;
}

.stButton > button:hover {
    border-color: #8b5cf6;
    background: #211b31;
    color: #ffffff;
}

/* Primary button */
button[kind="primary"] {
    background: linear-gradient(135deg, #7c3aed, #4f46e5) !important;
    border: none !important;
}

/* Download button */
.stDownloadButton > button {
    width: 100%;
    background: linear-gradient(135deg, #7c3aed, #4f46e5);
    color: #ffffff;
    border: none;
    border-radius: 12px;
    font-weight: 700;
}

/* File uploader */
section[data-testid="stFileUploaderDropzone"] {
    background: #11141a !important;
    border: 1px dashed #3a3f4a !important;
    border-radius: 14px !important;
}

/* Radio */
div[role="radiogroup"] label {
    color: #ffffff !important;
}

/* Color input */
input[type="color"] {
    background: #11141a;
    border: 1px solid #303641;
    border-radius: 8px;
}

/* QR preview */
.preview-box {
    background: #ffffff;
    border-radius: 22px;
    padding: 28px;
    min-height: 390px;
    display: flex;
    justify-content: center;
    align-items: center;
    box-shadow: 0 20px 70px rgba(0,0,0,0.35);
}

.preview-caption {
    text-align: center;
    color: #8f96a3;
    margin-top: 15px;
    font-size: 13px;
}

/* Divider */
.divider {
    height: 1px;
    background: #252a34;
    margin: 20px 0;
}

/* Footer */
.footer {
    text-align: center;
    color: #646b78;
    margin-top: 40px;
    font-size: 13px;
}

</style>
""", unsafe_allow_html=True)


# =========================================================
# FUNCTIONS
# =========================================================

def build_qr_data(qr_type, values):

    if qr_type == "Website / URL":
        return values.get("url", "").strip()

    elif qr_type == "Text":
        return values.get("text", "").strip()

    elif qr_type == "Phone":
        phone = values.get("phone", "").strip()
        return f"tel:{phone}"

    elif qr_type == "Email":
        email = values.get("email", "").strip()
        subject = values.get("subject", "").strip()
        message = values.get("message", "").strip()

        return (
            f"mailto:{email}"
            f"?subject={subject}"
            f"&body={message}"
        )

    elif qr_type == "Wi-Fi":
        ssid = values.get("ssid", "").strip()
        password = values.get("wifi_password", "").strip()
        security = values.get("security", "WPA/WPA2")

        return f"WIFI:T:{security};S:{ssid};P:{password};;"

    elif qr_type == "WhatsApp":
        number = values.get("whatsapp", "").strip()
        message = values.get("whatsapp_message", "").strip()

        if message:
            return f"https://wa.me/{number}?text={message}"

        return f"https://wa.me/{number}"

    elif qr_type == "Contact":
        name = values.get("name", "").strip()
        phone = values.get("contact_phone", "").strip()
        email = values.get("contact_email", "").strip()
        company = values.get("company", "").strip()

        return (
            "BEGIN:VCARD\n"
            "VERSION:3.0\n"
            f"FN:{name}\n"
            f"ORG:{company}\n"
            f"TEL:{phone}\n"
            f"EMAIL:{email}\n"
            "END:VCARD"
        )

    return ""


def create_qr(data, qr_color, logo=None):

    qr = qrcode.QRCode(
        version=None,
        error_correction=qrcode.constants.ERROR_CORRECT_H,
        box_size=12,
        border=4
    )

    qr.add_data(data)
    qr.make(fit=True)

    img = qr.make_image(
        fill_color=qr_color,
        back_color="white"
    ).convert("RGB")

    # Add logo
    if logo is not None:

        logo = logo.convert("RGBA")

        max_logo_size = int(img.size[0] * 0.22)

        logo.thumbnail(
            (max_logo_size, max_logo_size),
            Image.Resampling.LANCZOS
        )

        # White background behind logo
        padding = 10

        logo_bg = Image.new(
            "RGBA",
            (
                logo.size[0] + padding * 2,
                logo.size[1] + padding * 2
            ),
            "white"
        )

        logo_bg.paste(
            logo,
            (padding, padding),
            logo
        )

        position = (
            (img.size[0] - logo_bg.size[0]) // 2,
            (img.size[1] - logo_bg.size[1]) // 2
        )

        img.paste(
            logo_bg.convert("RGB"),
            position
        )

    return img


def image_to_bytes(image):

    buffer = io.BytesIO()
    image.save(buffer, format="PNG")
    buffer.seek(0)

    return buffer.getvalue()


# =========================================================
# HEADER
# =========================================================

st.markdown("""
<div class="hero">

<h1>QR <span>Studio</span></h1>

<p>
Create beautiful, customizable QR codes instantly.
Fast • Professional • Simple
</p>

</div>
""", unsafe_allow_html=True)


# =========================================================
# SESSION STATE
# =========================================================

if "qr_generated" not in st.session_state:
    st.session_state.qr_generated = False


# =========================================================
# MAIN LAYOUT
# =========================================================

left, right = st.columns([1.05, 0.95], gap="large")


# =========================================================
# LEFT SIDE
# =========================================================

with left:

    st.markdown("""
    <div class="card">

    <div class="card-title">
    ⚙️ QR Code Settings
    </div>

    """, unsafe_allow_html=True)

    qr_type = st.selectbox(
        "QR Code Type",
        [
            "Website / URL",
            "Text",
            "Phone",
            "Email",
            "Wi-Fi",
            "WhatsApp",
            "Contact"
        ]
    )

    values = {}

    # -----------------------------------------------------
    # WEBSITE
    # -----------------------------------------------------

    if qr_type == "Website / URL":

        values["url"] = st.text_input(
            "Website URL",
            placeholder="https://example.com"
        )

    # -----------------------------------------------------
    # TEXT
    # -----------------------------------------------------

    elif qr_type == "Text":

        values["text"] = st.text_area(
            "Enter Text",
            placeholder="Write your text here...",
            height=130
        )

    # -----------------------------------------------------
    # PHONE
    # -----------------------------------------------------

    elif qr_type == "Phone":

        values["phone"] = st.text_input(
            "Phone Number",
            placeholder="+92 300 1234567"
        )

    # -----------------------------------------------------
    # EMAIL
    # -----------------------------------------------------

    elif qr_type == "Email":

        values["email"] = st.text_input(
            "Email Address",
            placeholder="hello@example.com"
        )

        values["subject"] = st.text_input(
            "Subject",
            placeholder="Email subject"
        )

        values["message"] = st.text_area(
            "Message",
            placeholder="Write your message...",
            height=100
        )

    # -----------------------------------------------------
    # WIFI
    # -----------------------------------------------------

    elif qr_type == "Wi-Fi":

        values["ssid"] = st.text_input(
            "Wi-Fi Network Name",
            placeholder="My WiFi"
        )

        values["wifi_password"] = st.text_input(
            "Wi-Fi Password",
            type="password",
            placeholder="Wi-Fi password"
        )

        values["security"] = st.selectbox(
            "Security",
            ["WPA/WPA2", "WEP", "nopass"]
        )

    # -----------------------------------------------------
    # WHATSAPP
    # -----------------------------------------------------

    elif qr_type == "WhatsApp":

        values["whatsapp"] = st.text_input(
            "WhatsApp Number",
            placeholder="923001234567"
        )

        values["whatsapp_message"] = st.text_area(
            "Pre-filled Message",
            placeholder="Hello! I would like to contact you."
        )

    # -----------------------------------------------------
    # CONTACT
    # -----------------------------------------------------

    elif qr_type == "Contact":

        values["name"] = st.text_input(
            "Full Name",
            placeholder="Muhammad Ali"
        )

        values["contact_phone"] = st.text_input(
            "Phone Number",
            placeholder="+92 300 1234567"
        )

        values["contact_email"] = st.text_input(
            "Email",
            placeholder="ali@example.com"
        )

        values["company"] = st.text_input(
            "Company",
            placeholder="Your Company"
        )

    st.markdown('<div class="divider"></div>', unsafe_allow_html=True)

    # -----------------------------------------------------
    # COLOR
    # -----------------------------------------------------

    st.markdown("**🎨 QR Color**")

    qr_color = st.color_picker(
        "Choose QR color",
        "#000000"
    )

    # -----------------------------------------------------
    # LOGO
    # -----------------------------------------------------

    st.markdown("**🖼️ Logo**")

    logo_file = st.file_uploader(
        "Upload logo",
        type=["png", "jpg", "jpeg", "webp"],
        help="Upload a small logo for the center of your QR code."
    )

    logo = None

    if logo_file:
        logo = Image.open(logo_file)

    st.markdown('<div class="divider"></div>', unsafe_allow_html=True)

    col1, col2 = st.columns(2)

    with col1:

        generate = st.button(
            "✨ Generate QR",
            type="primary",
            use_container_width=True
        )

    with col2:

        reset = st.button(
            "🧹 Reset",
            use_container_width=True
        )

    st.markdown("</div>", unsafe_allow_html=True)


# =========================================================
# RIGHT SIDE
# =========================================================

with right:

    st.markdown("""
    <div class="card">

    <div class="card-title">
    👀 Live QR Preview
    </div>

    """, unsafe_allow_html=True)

    # Generate
    if generate:

        data = build_qr_data(qr_type, values)

        if not data.strip():

            st.error("Please enter the required information first.")

        else:

            try:

                qr_image = create_qr(
                    data=data,
                    qr_color=qr_color,
                    logo=logo
                )

                st.session_state.qr_image = qr_image
                st.session_state.qr_data = data
                st.session_state.qr_generated = True

            except Exception as e:

                st.error(f"Unable to generate QR code: {e}")

    # Reset
    if reset:

        st.session_state.qr_generated = False

        if "qr_image" in st.session_state:
            del st.session_state.qr_image

        st.rerun()

    # Preview
    if st.session_state.qr_generated:

        st.markdown(
            '<div class="preview-box">',
            unsafe_allow_html=True
        )

        st.image(
            st.session_state.qr_image,
            width=350
        )

        st.markdown(
            "</div>",
            unsafe_allow_html=True
        )

        st.markdown(
            """
            <div class="preview-caption">
            Your QR code is ready to scan
            </div>
            """,
            unsafe_allow_html=True
        )

        st.markdown("<br>", unsafe_allow_html=True)

        png_bytes = image_to_bytes(
            st.session_state.qr_image
        )

        st.download_button(
            label="📥 Download QR as PNG",
            data=png_bytes,
            file_name="qr_studio.png",
            mime="image/png",
            use_container_width=True
        )

    else:

        st.markdown(
            """
            <div class="preview-box">

            <div style="
                text-align:center;
                color:#555;
                width:100%;
            ">

            <div style="font-size:70px;">
            🔳
            </div>

            <div style="
                font-size:18px;
                font-weight:700;
                color:#333;
                margin-top:10px;
            ">
            Your QR code will appear here
            </div>

            <div style="
                font-size:13px;
                color:#777;
                margin-top:8px;
            ">
            Enter your information and click Generate QR
            </div>

            </div>

            </div>
            """,
            unsafe_allow_html=True
        )

    st.markdown("</div>", unsafe_allow_html=True)


# =========================================================
# FEATURES
# =========================================================

st.markdown("<br>", unsafe_allow_html=True)

f1, f2, f3, f4 = st.columns(4)

with f1:
    st.markdown("""
    <div class="card" style="text-align:center;">
    <div style="font-size:30px;">⚡</div>
    <b>Instant Generate</b>
    <div class="small-text">Create QR codes instantly</div>
    </div>
    """, unsafe_allow_html=True)

with f2:
    st.markdown("""
    <div class="card" style="text-align:center;">
    <div style="font-size:30px;">🎨</div>
    <b>Custom Colors</b>
    <div class="small-text">Choose your QR color</div>
    </div>
    """, unsafe_allow_html=True)

with f3:
    st.markdown("""
    <div class="card" style="text-align:center;">
    <div style="font-size:30px;">🖼️</div>
    <b>Logo Support</b>
    <div class="small-text">Add your own logo</div>
    </div>
    """, unsafe_allow_html=True)

with f4:
    st.markdown("""
    <div class="card" style="text-align:center;">
    <div style="font-size:30px;">📥</div>
    <b>PNG Download</b>
    <div class="small-text">Download high-quality QR</div>
    </div>
    """, unsafe_allow_html=True)


# =========================================================
# FOOTER
# =========================================================

st.markdown("""
<div class="footer">
QR Studio • Professional QR Code Generator
</div>
""", unsafe_allow_html=True)

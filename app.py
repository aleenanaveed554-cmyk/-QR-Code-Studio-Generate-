import io
import json
from datetime import datetime

import qrcode
import streamlit as st
from PIL import Image, ImageDraw


# =========================================================
# PAGE CONFIG
# =========================================================

st.set_page_config(
    page_title="QR Code Studio",
    page_icon="▦",
    layout="wide",
    initial_sidebar_state="expanded",
)


# =========================================================
# CUSTOM CSS
# =========================================================

st.markdown(
    """
    <style>
    @import url('https://fonts.googleapis.com/css2?family=DM+Sans:wght@400;500;600;700&display=swap');

    * {
        font-family: 'DM Sans', sans-serif;
    }

    .stApp {
        background:
            radial-gradient(circle at top left, rgba(99,102,241,0.10), transparent 30%),
            radial-gradient(circle at top right, rgba(14,165,233,0.08), transparent 28%),
            #f7f9fc;
    }

    [data-testid="stHeader"] {
        background: transparent;
    }

    [data-testid="stSidebar"] {
        background: #ffffff;
        border-right: 1px solid #e8ecf3;
    }

    .hero {
        padding: 28px 10px 18px 10px;
    }

    .brand {
        display: flex;
        align-items: center;
        gap: 14px;
    }

    .brand-icon {
        width: 54px;
        height: 54px;
        border-radius: 16px;
        display: flex;
        align-items: center;
        justify-content: center;
        background: linear-gradient(135deg, #111827, #4f46e5);
        color: white;
        font-size: 27px;
        font-weight: 700;
        box-shadow: 0 10px 30px rgba(79,70,229,0.22);
    }

    .brand-title {
        font-size: 34px;
        font-weight: 700;
        color: #111827;
        line-height: 1.1;
    }

    .brand-subtitle {
        color: #667085;
        font-size: 15px;
        margin-top: 5px;
    }

    .section-title {
        color: #111827;
        font-size: 20px;
        font-weight: 700;
        margin-bottom: 4px;
    }

    .section-subtitle {
        color: #667085;
        font-size: 13px;
        margin-bottom: 18px;
    }

    .card {
        background: rgba(255,255,255,0.95);
        border: 1px solid #e8ecf3;
        border-radius: 22px;
        padding: 24px;
        box-shadow: 0 10px 35px rgba(15,23,42,0.05);
        margin-bottom: 18px;
    }

    .preview-card {
        min-height: 580px;
        display: flex;
        flex-direction: column;
        align-items: center;
        justify-content: center;
    }

    .preview-label {
        font-size: 13px;
        color: #667085;
        margin-bottom: 18px;
        font-weight: 600;
        text-transform: uppercase;
        letter-spacing: 0.8px;
    }

    .qr-box {
        background: white;
        border-radius: 22px;
        padding: 20px;
        border: 1px solid #e8ecf3;
        box-shadow: 0 15px 45px rgba(15,23,42,0.08);
    }

    .empty-preview {
        width: 310px;
        height: 310px;
        border: 2px dashed #d8deea;
        border-radius: 22px;
        display: flex;
        align-items: center;
        justify-content: center;
        text-align: center;
        color: #98a2b3;
        background: #fafbfc;
        padding: 30px;
    }

    .empty-preview-icon {
        font-size: 50px;
        margin-bottom: 10px;
    }

    .feature-card {
        background: white;
        border: 1px solid #e8ecf3;
        border-radius: 18px;
        padding: 18px;
        height: 100%;
        box-shadow: 0 8px 25px rgba(15,23,42,0.035);
    }

    .feature-icon {
        font-size: 24px;
        margin-bottom: 8px;
    }

    .feature-title {
        color: #111827;
        font-weight: 700;
        font-size: 14px;
    }

    .feature-text {
        color: #667085;
        font-size: 12px;
        margin-top: 4px;
    }

    .history-card {
        background: white;
        border: 1px solid #e8ecf3;
        border-radius: 18px;
        padding: 16px 18px;
        margin-bottom: 10px;
    }

    .history-type {
        font-weight: 700;
        color: #111827;
        font-size: 14px;
    }

    .history-content {
        color: #667085;
        font-size: 12px;
        margin-top: 4px;
    }

    .history-time {
        color: #98a2b3;
        font-size: 11px;
        margin-top: 4px;
    }

    div.stButton > button {
        border-radius: 12px;
        font-weight: 700;
        min-height: 44px;
    }

    div.stDownloadButton > button {
        border-radius: 12px;
        font-weight: 700;
        min-height: 44px;
    }

    .generate-btn button {
        background: linear-gradient(135deg, #111827, #4f46e5) !important;
        color: white !important;
        border: none !important;
        font-size: 15px !important;
        min-height: 50px !important;
        box-shadow: 0 12px 28px rgba(79,70,229,0.20);
    }

    .generate-btn button:hover {
        transform: translateY(-1px);
    }

    .stat {
        background: white;
        border: 1px solid #e8ecf3;
        border-radius: 18px;
        padding: 16px;
        text-align: center;
    }

    .stat-number {
        font-size: 22px;
        font-weight: 700;
        color: #111827;
    }

    .stat-label {
        font-size: 11px;
        color: #667085;
        margin-top: 3px;
    }

    #MainMenu {
        visibility: hidden;
    }

    footer {
        visibility: hidden;
    }

    @media (max-width: 768px) {
        .brand-title {
            font-size: 27px;
        }

        .preview-card {
            min-height: 450px;
        }

        .empty-preview {
            width: 250px;
            height: 250px;
        }
    }
    </style>
    """,
    unsafe_allow_html=True,
)


# =========================================================
# SESSION STATE
# =========================================================

if "qr_image" not in st.session_state:
    st.session_state.qr_image = None

if "qr_content" not in st.session_state:
    st.session_state.qr_content = ""

if "qr_type" not in st.session_state:
    st.session_state.qr_type = ""

if "history" not in st.session_state:
    st.session_state.history = []


# =========================================================
# HELPERS
# =========================================================

def make_wifi(ssid, password, security, hidden=False):
    security = security.upper()

    if security == "NONE":
        return f"WIFI:T:nopass;S:{ssid};H:{str(hidden).lower()};;"

    return (
        f"WIFI:T:{security};"
        f"S:{ssid};"
        f"P:{password};"
        f"H:{str(hidden).lower()};;"
    )


def make_vcard(name, phone, email, organization, website):
    return (
        "BEGIN:VCARD\n"
        "VERSION:3.0\n"
        f"FN:{name}\n"
        f"ORG:{organization}\n"
        f"TEL:{phone}\n"
        f"EMAIL:{email}\n"
        f"URL:{website}\n"
        "END:VCARD"
    )


def make_whatsapp(phone, message):
    phone = phone.strip().replace(" ", "").replace("-", "")

    if message.strip():
        return f"https://wa.me/{phone}?text={message.strip().replace(' ', '%20')}"

    return f"https://wa.me/{phone}"


def build_content(qr_type, values):
    if qr_type == "Text":
        return values["text"].strip()

    if qr_type == "Website URL":
        url = values["url"].strip()

        if url and not url.startswith(("http://", "https://")):
            url = "https://" + url

        return url

    if qr_type == "Phone Number":
        return f"tel:{values['phone'].strip()}"

    if qr_type == "Email":
        return (
            f"mailto:{values['email'].strip()}"
            f"?subject={values['subject'].strip()}"
            f"&body={values['message'].strip()}"
        )

    if qr_type == "Wi-Fi":
        return make_wifi(
            values["ssid"],
            values["wifi_password"],
            values["security"],
            values["hidden"],
        )

    if qr_type == "Contact / vCard":
        return make_vcard(
            values["name"],
            values["contact_phone"],
            values["contact_email"],
            values["organization"],
            values["website"],
        )

    if qr_type == "WhatsApp":
        return make_whatsapp(
            values["whatsapp_phone"],
            values["whatsapp_message"],
        )

    return ""


def generate_qr(content, fill_color, back_color, box_size, border):
    qr = qrcode.QRCode(
        version=None,
        error_correction=qrcode.constants.ERROR_CORRECT_H,
        box_size=box_size,
        border=border,
    )

    qr.add_data(content)
    qr.make(fit=True)

    img = qr.make_image(
        fill_color=fill_color,
        back_color=back_color,
    ).convert("RGBA")

    return img


def add_logo(qr_img, logo_file):
    if logo_file is None:
        return qr_img

    try:
        logo = Image.open(logo_file).convert("RGBA")

        max_size = int(min(qr_img.size) * 0.22)
        logo.thumbnail((max_size, max_size), Image.Resampling.LANCZOS)

        canvas_size = logo.size[0] + 22, logo.size[1] + 22

        canvas = Image.new(
            "RGBA",
            canvas_size,
            (255, 255, 255, 255),
        )

        draw = ImageDraw.Draw(canvas)

        draw.rounded_rectangle(
            (0, 0, canvas_size[0] - 1, canvas_size[1] - 1),
            radius=12,
            fill=(255, 255, 255, 255),
        )

        x = (canvas.width - logo.width) // 2
        y = (canvas.height - logo.height) // 2

        canvas.alpha_composite(logo, (x, y))

        center_x = (qr_img.width - canvas.width) // 2
        center_y = (qr_img.height - canvas.height) // 2

        qr_img.alpha_composite(canvas, (center_x, center_y))

        return qr_img

    except Exception:
        return qr_img


def image_to_bytes(image):
    buffer = io.BytesIO()
    image.convert("RGB").save(buffer, format="PNG")
    return buffer.getvalue()


# =========================================================
# HEADER
# =========================================================

st.markdown(
    """
    <div class="hero">
        <div class="brand">
            <div class="brand-icon">▦</div>
            <div>
                <div class="brand-title">QR Code Studio</div>
                <div class="brand-subtitle">
                    Create beautiful QR codes in seconds.
                </div>
            </div>
        </div>
    </div>
    """,
    unsafe_allow_html=True,
)


# =========================================================
# MAIN LAYOUT
# =========================================================

left, right = st.columns([1, 1.05], gap="large")


# =========================================================
# LEFT PANEL
# =========================================================

with left:

    st.markdown(
        """
        <div class="card">
            <div class="section-title">Create your QR code</div>
            <div class="section-subtitle">
                Choose a QR type and customize your code.
            </div>
        """,
        unsafe_allow_html=True,
    )

    qr_type = st.selectbox(
        "QR Code Type",
        [
            "Text",
            "Website URL",
            "Phone Number",
            "Email",
            "Wi-Fi",
            "Contact / vCard",
            "WhatsApp",
        ],
    )

    values = {}

    if qr_type == "Text":
        values["text"] = st.text_area(
            "Enter your text",
            placeholder="Type any text you want to convert into a QR code...",
            height=130,
        )

    elif qr_type == "Website URL":
        values["url"] = st.text_input(
            "Website URL",
            placeholder="https://example.com",
        )

    elif qr_type == "Phone Number":
        values["phone"] = st.text_input(
            "Phone Number",
            placeholder="+92 300 1234567",
        )

    elif qr_type == "Email":
        values["email"] = st.text_input(
            "Email Address",
            placeholder="hello@example.com",
        )

        values["subject"] = st.text_input(
            "Subject",
            placeholder="Email subject",
        )

        values["message"] = st.text_area(
            "Message",
            placeholder="Write your email message...",
            height=100,
        )

    elif qr_type == "Wi-Fi":
        values["ssid"] = st.text_input(
            "Wi-Fi Network Name (SSID)",
            placeholder="My WiFi",
        )

        values["wifi_password"] = st.text_input(
            "Wi-Fi Password",
            type="password",
            placeholder="Enter Wi-Fi password",
        )

        values["security"] = st.selectbox(
            "Security",
            ["WPA", "WEP", "None"],
        )

        values["hidden"] = st.checkbox(
            "Hidden network",
            value=False,
        )

    elif qr_type == "Contact / vCard":
        values["name"] = st.text_input(
            "Full Name",
            placeholder="John Doe",
        )

        values["contact_phone"] = st.text_input(
            "Phone Number",
            placeholder="+92 300 1234567",
        )

        values["contact_email"] = st.text_input(
            "Email Address",
            placeholder="john@example.com",
        )

        values["organization"] = st.text_input(
            "Organization",
            placeholder="Company / School",
        )

        values["website"] = st.text_input(
            "Website",
            placeholder="https://example.com",
        )

    elif qr_type == "WhatsApp":
        values["whatsapp_phone"] = st.text_input(
            "WhatsApp Number",
            placeholder="923001234567",
            help="Use country code without + or spaces.",
        )

        values["whatsapp_message"] = st.text_area(
            "Pre-filled Message",
            placeholder="Hello! I would like to contact you.",
            height=100,
        )

    st.markdown("### Customize")

    color_col1, color_col2 = st.columns(2)

    with color_col1:
        fill_color = st.color_picker(
            "QR Color",
            "#111827",
        )

    with color_col2:
        back_color = st.color_picker(
            "Background",
            "#FFFFFF",
        )

    size_col1, size_col2 = st.columns(2)

    with size_col1:
        box_size = st.slider(
            "QR Size",
            min_value=4,
            max_value=15,
            value=8,
        )

    with size_col2:
        border = st.slider(
            "Border",
            min_value=1,
            max_value=8,
            value=4,
        )

    logo_file = st.file_uploader(
        "Add Center Logo (optional)",
        type=["png", "jpg", "jpeg", "webp"],
    )

    st.markdown("</div>", unsafe_allow_html=True)

    generate = st.container()

    with generate:
        st.markdown('<div class="generate-btn">', unsafe_allow_html=True)

        generate_clicked = st.button(
            "Generate QR Code",
            type="primary",
            use_container_width=True,
        )

        st.markdown("</div>", unsafe_allow_html=True)

    clear_clicked = st.button(
        "Clear / Reset",
        use_container_width=True,
    )


# =========================================================
# GENERATE
# =========================================================

if generate_clicked:

    try:
        content = build_content(qr_type, values)

        if not content.strip():
            st.error("Please enter some information first.")
        else:
            qr_image = generate_qr(
                content,
                fill_color,
                back_color,
                box_size,
                border,
            )

            qr_image = add_logo(qr_image, logo_file)

            st.session_state.qr_image = qr_image
            st.session_state.qr_content = content
            st.session_state.qr_type = qr_type

            history_item = {
                "type": qr_type,
                "content": content,
                "time": datetime.now().strftime("%d %b %Y, %I:%M %p"),
                "image": image_to_bytes(qr_image),
            }

            st.session_state.history.insert(0, history_item)

            st.session_state.history = st.session_state.history[:10]

    except Exception as e:
        st.error(f"Could not generate QR code: {e}")


# =========================================================
# CLEAR
# =========================================================

if clear_clicked:
    st.session_state.qr_image = None
    st.session_state.qr_content = ""
    st.session_state.qr_type = ""

    st.rerun()


# =========================================================
# RIGHT PANEL
# =========================================================

with right:

    st.markdown(
        """
        <div class="card preview-card">
            <div class="preview-label">Live QR Preview</div>
        """,
        unsafe_allow_html=True,
    )

    if st.session_state.qr_image is not None:

        st.markdown('<div class="qr-box">', unsafe_allow_html=True)

        st.image(
            st.session_state.qr_image,
            width=330,
        )

        st.markdown("</div>", unsafe_allow_html=True)

        st.markdown("<br>", unsafe_allow_html=True)

        st.download_button(
            label="Download QR Code as PNG",
            data=image_to_bytes(st.session_state.qr_image),
            file_name="qr_code_studio.png",
            mime="image/png",
            use_container_width=True,
        )

        st.markdown("<br>", unsafe_allow_html=True)

        copy_col, info_col = st.columns([1, 1])

        with copy_col:
            st.code(
                st.session_state.qr_content,
                language=None,
            )

        with info_col:
            st.markdown(
                f"""
                <div class="stat">
                    <div class="stat-number">
                        {st.session_state.qr_type}
                    </div>
                    <div class="stat-label">
                        QR Code Type
                    </div>
                </div>
                """,
                unsafe_allow_html=True,
            )

    else:

        st.markdown(
            """
            <div class="empty-preview">
                <div>
                    <div class="empty-preview-icon">▦</div>
                    <strong>Your QR code will appear here</strong>
                    <br>
                    <span>
                        Enter your content and click Generate QR Code.
                    </span>
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )

    st.markdown("</div>", unsafe_allow_html=True)


# =========================================================
# FEATURES
# =========================================================

st.markdown("##")

feature_cols = st.columns(4)

features = [
    ("⚡", "Instant Generation", "Create QR codes in seconds."),
    ("🎨", "Custom Styling", "Choose colors, size and border."),
    ("🖼️", "Logo Support", "Add your brand logo in the center."),
    ("📱", "Mobile Friendly", "Works beautifully on all screens."),
]

for col, feature in zip(feature_cols, features):
    with col:
        st.markdown(
            f"""
            <div class="feature-card">
                <div class="feature-icon">{feature[0]}</div>
                <div class="feature-title">{feature[1]}</div>
                <div class="feature-text">{feature[2]}</div>
            </div>
            """,
            unsafe_allow_html=True,
        )


# =========================================================
# HISTORY
# =========================================================

st.markdown("##")

st.markdown(
    """
    <div class="section-title">Recent QR Codes</div>
    <div class="section-subtitle">
        Your recently generated QR codes are shown here.
    </div>
    """,
    unsafe_allow_html=True,
)

if st.session_state.history:

    for index, item in enumerate(st.session_state.history):

        history_col1, history_col2, history_col3 = st.columns(
            [0.15, 0.60, 0.25]
        )

        with history_col1:
            st.image(
                item["image"],
                width=70,
            )

        with history_col2:
            st.markdown(
                f"""
                <div class="history-card">
                    <div class="history-type">
                        {item["type"]}
                    </div>
                    <div class="history-content">
                        {item["content"][:100]}
                        {"..." if len(item["content"]) > 100 else ""}
                    </div>
                    <div class="history-time">
                        {item["time"]}
                    </div>
                </div>
                """,
                unsafe_allow_html=True,
            )

        with history_col3:
            st.download_button(
                "Download",
                data=item["image"],
                file_name=f"qr_code_{index + 1}.png",
                mime="image/png",
                key=f"history_download_{index}",
                use_container_width=True,
            )

else:

    st.info("No QR codes generated yet. Create your first QR code above.")


# =========================================================
# FOOTER
# =========================================================

st.markdown(
    """
    <div style="
        text-align:center;
        color:#98a2b3;
        font-size:12px;
        padding:35px 0 20px 0;
    ">
        QR Code Studio • Create • Customize • Share
    </div>
    """,
    unsafe_allow_html=True,
)

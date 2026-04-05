"""
streamlit_app.py — Giao diện Streamlit cho Health AI Agent

Cách chạy:
    streamlit run streamlit_app.py
"""

import streamlit as st
import sys
from pathlib import Path

# Đảm bảo có thể import từ thư mục gốc project
sys.path.insert(0, str(Path(__file__).parent))

from tools import calculate_bmi, get_bmi_status
from agent import run_health_agent

# ─── Cấu hình trang ─────────────────────────────────────────────────────────
st.set_page_config(
    page_title="Health AI Agent",
    page_icon="🏥",
    layout="centered",
)

# ─── CSS tùy chỉnh ──────────────────────────────────────────────────────────
st.markdown("""
<style>
    .main-header {
        text-align: center;
        padding: 1rem 0;
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        border-radius: 12px;
        color: white;
        margin-bottom: 2rem;
    }
    .result-box {
        background: #f0f9ff;
        border-left: 4px solid #0ea5e9;
        padding: 1.2rem;
        border-radius: 8px;
        margin-top: 1rem;
    }
    .bmi-number {
        font-size: 3rem;
        font-weight: bold;
        text-align: center;
        color: #0ea5e9;
    }
    .advice-box {
        background: #f0fdf4;
        border-left: 4px solid #22c55e;
        padding: 1rem;
        border-radius: 8px;
        margin-top: 1rem;
    }
</style>
""", unsafe_allow_html=True)

# ─── Header ─────────────────────────────────────────────────────────────────
st.markdown("""
<div class="main-header">
    <h1>🏥 Health AI Agent</h1>
    <p>Tư vấn sức khỏe cơ bản · Tính BMI · Lời khuyên dinh dưỡng</p>
</div>
""", unsafe_allow_html=True)

# ─── Form nhập liệu ─────────────────────────────────────────────────────────
st.subheader("📋 Nhập thông tin của bạn")

col1, col2 = st.columns(2)

with col1:
    weight = st.number_input(
        "⚖️ Cân nặng (kg)",
        min_value=10.0,
        max_value=300.0,
        value=65.0,
        step=0.5,
        help="Nhập cân nặng của bạn tính bằng kilogram"
    )

with col2:
    height = st.number_input(
        "📏 Chiều cao (cm)",
        min_value=50.0,
        max_value=250.0,
        value=170.0,
        step=0.5,
        help="Nhập chiều cao của bạn tính bằng centimeter"
    )

# Nút phân tích
analyze_btn = st.button("🔍 Phân tích sức khỏe", type="primary", use_container_width=True)

# ─── Kết quả ────────────────────────────────────────────────────────────────
if analyze_btn:
    with st.spinner("⏳ Đang phân tích..."):
        # Tính BMI trực tiếp (hiển thị nhanh)
        bmi_result = calculate_bmi(weight, height)

        if "error" in bmi_result:
            st.error(f"❌ {bmi_result['error']}")
        else:
            bmi = bmi_result["bmi"]
            status_result = get_bmi_status(bmi)

            # Hiển thị BMI lớn ở giữa
            st.markdown("---")
            st.markdown(f"""
            <div class="result-box">
                <p style="text-align:center; color:#64748b; margin:0">Chỉ số BMI của bạn</p>
                <div class="bmi-number">{bmi}</div>
                <p style="text-align:center; font-size:1.3rem; margin:0">
                    {status_result['emoji']} {status_result['status']}
                    <span style="color:#94a3b8; font-size:0.9rem">({status_result['status_en']})</span>
                </p>
            </div>
            """, unsafe_allow_html=True)

            # Thanh BMI trực quan
            st.markdown("### 📊 Thang đo BMI")
            bmi_display = min(bmi, 40.0)  # giới hạn max để hiển thị
            progress = min((bmi_display - 10) / (40 - 10), 1.0)
            progress = max(progress, 0.0)
            st.progress(progress)
            st.caption("10 ◀── Thiếu cân │ Bình thường │ Thừa cân │ Béo phì ──▶ 40+")

            # Lời khuyên
            st.markdown("### 💡 Lời khuyên sức khỏe")

            # Gọi full agent (có thể có AI nếu có API key)
            full_result = run_health_agent(weight=weight, height=height)

            # Lấy phần advice từ result
            advice = status_result["advice"]

            st.markdown(f"""
            <div class="advice-box">
                {advice}
            </div>
            """, unsafe_allow_html=True)

            # Thông tin thêm
            st.markdown("### 📈 Chi tiết")
            detail_col1, detail_col2, detail_col3 = st.columns(3)
            with detail_col1:
                st.metric("Cân nặng", f"{weight} kg")
            with detail_col2:
                st.metric("Chiều cao", f"{height} cm")
            with detail_col3:
                st.metric("BMI", bmi)

# ─── Bảng tham chiếu BMI ────────────────────────────────────────────────────
with st.expander("📚 Bảng tham chiếu BMI (WHO/APAC)"):
    st.markdown("""
    | BMI | Phân loại | Tình trạng |
    |-----|-----------|------------|
    | < 16.0 | 🚨 | Suy dinh dưỡng nặng |
    | 16.0 – 18.4 | ⚠️ | Thiếu cân |
    | 18.5 – 22.9 | ✅ | Bình thường |
    | 23.0 – 24.9 | 🟡 | Thừa cân nhẹ |
    | 25.0 – 29.9 | 🔴 | Béo phì độ 1 |
    | ≥ 30.0 | 🚑 | Béo phì độ 2+ |

    > *Áp dụng ngưỡng châu Á (APAC) — phù hợp với người Việt Nam*
    """)

# ─── Footer ─────────────────────────────────────────────────────────────────
st.markdown("---")
st.caption(
    "⚕️ **Lưu ý:** Công cụ này chỉ mang tính tham khảo. "
    "Hãy tham khảo ý kiến bác sĩ để được tư vấn chuyên sâu."
)

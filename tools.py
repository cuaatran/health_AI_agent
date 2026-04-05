"""
tools.py — Công cụ tính BMI cho Health AI Agent

Gồm 2 tool chính:
  - calculate_bmi(weight, height): tính chỉ số BMI
  - get_bmi_status(bmi): tra cứu phân loại + lời khuyên từ health_data.json
"""

import json
from pathlib import Path

# Đường dẫn tới file knowledge base
DATA_PATH = Path(__file__).parent / "health_data.json"


def calculate_bmi(weight: float, height: float) -> dict:
    """
    Tính chỉ số BMI từ cân nặng và chiều cao.

    Args:
        weight: Cân nặng (kg)
        height: Chiều cao (cm)

    Returns:
        dict với bmi, weight, height hoặc lỗi nếu input không hợp lệ
    """
    # Kiểm tra input hợp lệ
    if weight <= 0 or height <= 0:
        return {"error": "Cân nặng và chiều cao phải lớn hơn 0."}

    if weight > 500:
        return {"error": "Cân nặng không hợp lệ (quá lớn)."}

    if height > 300:
        return {"error": "Chiều cao không hợp lệ (quá lớn)."}

    # Đổi cm → m rồi tính BMI
    height_m = height / 100
    bmi = weight / (height_m ** 2)
    bmi = round(bmi, 2)

    return {
        "bmi": bmi,
        "weight_kg": weight,
        "height_cm": height,
    }


def get_bmi_status(bmi: float) -> dict:
    """
    Tra cứu phân loại và lời khuyên dựa trên chỉ số BMI.
    Sử dụng health_data.json làm knowledge base.

    Args:
        bmi: Chỉ số BMI đã tính

    Returns:
        dict với status, advice, emoji
    """
    # Đọc knowledge base
    try:
        with open(DATA_PATH, "r", encoding="utf-8") as f:
            health_data = json.load(f)
    except FileNotFoundError:
        return {"error": "Không tìm thấy file health_data.json"}

    # Tìm khoảng BMI phù hợp
    for entry in health_data:
        if entry["bmi_min"] <= bmi < entry["bmi_max"]:
            return {
                "status": entry["status"],
                "status_en": entry["status_en"],
                "advice": entry["advice"],
                "emoji": entry["emoji"],
            }

    # Fallback nếu không match (không nên xảy ra)
    return {
        "status": "Không xác định",
        "status_en": "Unknown",
        "advice": "Vui lòng kiểm tra lại chỉ số BMI của bạn.",
        "emoji": "❓",
    }

"""
agents/state.py — Định nghĩa trạng thái cho Health AI Agent pipeline

State được truyền qua các node trong LangGraph graph.
"""

from dataclasses import dataclass, field
from typing import Optional


@dataclass
class HealthState:
    """
    Trạng thái chạy qua toàn bộ pipeline Health Agent.

    Input từ user:
        weight: cân nặng (kg)
        height: chiều cao (cm)

    Được điền bởi các node:
        bmi: chỉ số BMI tính được
        status: phân loại (Bình thường, Thiếu cân, ...)
        advice: lời khuyên sức khỏe
        emoji: icon tương ứng
        final_response: câu trả lời hoàn chỉnh gửi cho user
        error: thông báo lỗi nếu có
    """
    # --- Input ---
    weight: float = 0.0          # kg
    height: float = 0.0          # cm
    user_message: str = ""       # câu hỏi gốc từ user (optional)

    # --- Điền bởi BMI Calculator Node ---
    bmi: Optional[float] = None

    # --- Điền bởi Status Lookup Node ---
    status: str = ""
    status_en: str = ""
    advice: str = ""
    emoji: str = ""

    # --- Điền bởi Response Formatter Node ---
    final_response: str = ""

    # --- Lỗi (nếu có) ---
    error: str = ""

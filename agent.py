"""
agent.py — Health AI Agent sử dụng LangGraph pipeline

Pipeline:
    [input] → bmi_calculator → status_lookup → ai_advisor → response_formatter → [output]

Mỗi node là một bước xử lý độc lập, nhận và trả về HealthState.
"""

import os
from typing import TypedDict, Optional
from dotenv import load_dotenv
from langgraph.graph import StateGraph, END
from openai import OpenAI

from state import HealthState
from tools import calculate_bmi, get_bmi_status

load_dotenv()


# ─────────────────────────────────────────────
# LangGraph yêu cầu TypedDict (không dùng dataclass trực tiếp)
# ─────────────────────────────────────────────
class GState(TypedDict, total=False):
    weight: float
    height: float
    user_message: str
    bmi: Optional[float]
    status: str
    status_en: str
    advice: str
    emoji: str
    final_response: str
    error: str


# Helper: convert dict ↔ HealthState
def _to_state(d: dict) -> HealthState:
    return HealthState(**{k: d[k] for k in d if hasattr(HealthState, k) and k in d})


def _from_state(s: HealthState) -> dict:
    return {
        "weight": s.weight, "height": s.height, "user_message": s.user_message,
        "bmi": s.bmi, "status": s.status, "status_en": s.status_en,
        "advice": s.advice, "emoji": s.emoji,
        "final_response": s.final_response, "error": s.error,
    }


# ─────────────────────────────────────────────
# NODE 1: Tính BMI
# ─────────────────────────────────────────────
def bmi_calculator_node(state_dict: dict) -> dict:
    """Gọi tool calculate_bmi, lưu kết quả vào state."""
    state = _to_state(state_dict)

    result = calculate_bmi(state.weight, state.height)

    if "error" in result:
        state.error = result["error"]
    else:
        state.bmi = result["bmi"]

    return _from_state(state)


# ─────────────────────────────────────────────
# NODE 2: Tra cứu phân loại BMI
# ─────────────────────────────────────────────
def status_lookup_node(state_dict: dict) -> dict:
    """Gọi tool get_bmi_status để lấy phân loại và lời khuyên."""
    state = _to_state(state_dict)

    # Bỏ qua nếu đã có lỗi từ bước trước
    if state.error or state.bmi is None:
        return _from_state(state)

    result = get_bmi_status(state.bmi)

    if "error" in result:
        state.error = result["error"]
    else:
        state.status = result["status"]
        state.status_en = result["status_en"]
        state.advice = result["advice"]
        state.emoji = result["emoji"]

    return _from_state(state)


# ─────────────────────────────────────────────
# NODE 3: AI Advisor — gọi OpenAI để cá nhân hóa lời khuyên
# ─────────────────────────────────────────────
def ai_advisor_node(state_dict: dict) -> dict:
    """
    Gọi OpenAI API để tạo lời khuyên được cá nhân hóa hơn.
    Nếu không có API key hoặc lỗi → dùng lời khuyên từ knowledge base.
    """
    state = _to_state(state_dict)

    if state.error or state.bmi is None:
        return _from_state(state)

    api_key = os.environ.get("OPENAI_API_KEY", "")
    if not api_key.startswith("sk-"):
        # Không có API key → dùng advice từ knowledge base (không lỗi)
        return _from_state(state)

    try:
        client = OpenAI(api_key=api_key)

        # System prompt — định nghĩa vai trò AI
        system_prompt = (
            "You are a health assistant. You help users understand their body condition, "
            "calculate BMI, and provide simple health advice. Always answer clearly and friendly. "
            "Reply in Vietnamese."
        )

        user_prompt = (
            f"Người dùng có:\n"
            f"- Cân nặng: {state.weight} kg\n"
            f"- Chiều cao: {state.height} cm\n"
            f"- BMI: {state.bmi}\n"
            f"- Phân loại: {state.status}\n\n"
            f"Dựa trên thông tin này, hãy đưa ra 2-3 lời khuyên sức khỏe ngắn gọn, "
            f"thực tế và dễ thực hiện. Giữ ngắn gọn trong 3-4 câu."
        )

        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user",   "content": user_prompt},
            ],
            max_tokens=300,
            temperature=0.7,
        )

        ai_advice = response.choices[0].message.content.strip()
        # Kết hợp advice từ knowledge base + AI
        state.advice = ai_advice

    except Exception as e:
        # Lỗi API → vẫn dùng advice từ knowledge base, không dừng pipeline
        pass

    return _from_state(state)


# ─────────────────────────────────────────────
# NODE 4: Định dạng câu trả lời cuối cùng
# ─────────────────────────────────────────────
def response_formatter_node(state_dict: dict) -> dict:
    """Tạo câu trả lời hoàn chỉnh theo format yêu cầu."""
    state = _to_state(state_dict)

    if state.error:
        state.final_response = f"❌ Lỗi: {state.error}"
        return _from_state(state)

    # Format theo yêu cầu: BMI / Tình trạng / Lời khuyên
    state.final_response = (
        f"{state.emoji} **Kết quả phân tích sức khỏe**\n\n"
        f"📊 **BMI:** {state.bmi}\n"
        f"🏷️ **Tình trạng:** {state.status} ({state.status_en})\n\n"
        f"💡 **Lời khuyên:**\n{state.advice}"
    )

    return _from_state(state)


# ─────────────────────────────────────────────
# Build LangGraph pipeline
# ─────────────────────────────────────────────
def build_graph():
    """Xây dựng và compile LangGraph pipeline."""
    builder = StateGraph(GState)

    # Thêm các node
    builder.add_node("bmi_calculator",      bmi_calculator_node)
    builder.add_node("status_lookup",       status_lookup_node)
    builder.add_node("ai_advisor",          ai_advisor_node)
    builder.add_node("response_formatter",  response_formatter_node)

    # Kết nối các node theo thứ tự
    builder.set_entry_point("bmi_calculator")
    builder.add_edge("bmi_calculator",     "status_lookup")
    builder.add_edge("status_lookup",      "ai_advisor")
    builder.add_edge("ai_advisor",         "response_formatter")
    builder.add_edge("response_formatter", END)

    return builder.compile()


# ─────────────────────────────────────────────
# Hàm tiện ích — dùng từ app.py hoặc streamlit_app.py
# ─────────────────────────────────────────────
def run_health_agent(weight: float, height: float, user_message: str = "") -> str:
    """
    Chạy toàn bộ pipeline và trả về câu trả lời.

    Args:
        weight: Cân nặng (kg)
        height: Chiều cao (cm)
        user_message: Câu hỏi gốc từ user (optional)

    Returns:
        Chuỗi kết quả hoàn chỉnh
    """
    graph = build_graph()

    initial_state = {
        "weight": weight,
        "height": height,
        "user_message": user_message,
        "bmi": None,
        "status": "",
        "status_en": "",
        "advice": "",
        "emoji": "",
        "final_response": "",
        "error": "",
    }

    result = graph.invoke(initial_state)
    return result.get("final_response", "Không có kết quả.")

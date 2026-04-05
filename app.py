"""
app.py — Entry Point CLI cho Health AI Agent

Cách dùng:
    python app.py                        # chế độ hỏi đáp tương tác
    python app.py --weight 70 --height 170   # chế độ trực tiếp

Hoặc chạy Streamlit UI:
    streamlit run streamlit_app.py
"""

import os
import sys
import argparse
from dotenv import load_dotenv

load_dotenv()

# ─── Kiểm tra môi trường ────────────────────────────────────────────────────
def check_dependencies():
    """Kiểm tra các thư viện cần thiết."""
    missing = []
    for pkg in ["langgraph", "openai", "dotenv"]:
        try:
            __import__(pkg.replace("-", "_"))
        except ImportError:
            missing.append(pkg)

    if missing:
        print(f"❌ Thiếu thư viện: {', '.join(missing)}")
        print("   Chạy: pip install -r requirements.txt")
        sys.exit(1)


def print_banner():
    """In banner chào mừng."""
    print("\n" + "="*50)
    print("  🏥 Health AI Agent — Tư vấn sức khỏe cơ bản")
    print("="*50)

    api_key = os.environ.get("OPENAI_API_KEY", "")
    if api_key.startswith("sk-"):
        print("  ✅ OpenAI API: Đã kết nối (lời khuyên AI)")
    else:
        print("  ℹ️  OpenAI API: Chưa set (dùng knowledge base)")
    print("="*50 + "\n")


def get_float_input(prompt: str, min_val: float, max_val: float) -> float:
    """Lấy input số thực từ user với kiểm tra hợp lệ."""
    while True:
        try:
            value = float(input(prompt).strip())
            if min_val <= value <= max_val:
                return value
            print(f"  ⚠️  Vui lòng nhập giá trị từ {min_val} đến {max_val}")
        except ValueError:
            print("  ⚠️  Vui lòng nhập số hợp lệ (VD: 65.5)")


def interactive_mode():
    """Chế độ hỏi đáp tương tác."""
    print("📋 Nhập thông tin của bạn:\n")

    weight = get_float_input("  ⚖️  Cân nặng (kg): ", 10, 500)
    height = get_float_input("  📏 Chiều cao (cm): ", 50, 300)

    print("\n⏳ Đang phân tích...")

    from agent import run_health_agent
    result = run_health_agent(weight=weight, height=height)

    # In kết quả (bỏ markdown ** vì CLI không render)
    output = result.replace("**", "")
    print("\n" + "─"*50)
    print(output)
    print("─"*50)


def single_run(weight: float, height: float):
    """Chạy một lần với tham số cho sẵn."""
    print(f"📊 Phân tích: {weight} kg / {height} cm\n")

    from agent import run_health_agent
    result = run_health_agent(weight=weight, height=height)

    output = result.replace("**", "")
    print("─"*50)
    print(output)
    print("─"*50)


def main():
    check_dependencies()
    print_banner()

    parser = argparse.ArgumentParser(
        description="Health AI Agent — Tư vấn sức khỏe cơ bản"
    )
    parser.add_argument("--weight", type=float, help="Cân nặng (kg)")
    parser.add_argument("--height", type=float, help="Chiều cao (cm)")
    args = parser.parse_args()

    if args.weight and args.height:
        # Chế độ trực tiếp
        single_run(args.weight, args.height)
    else:
        # Chế độ tương tác
        while True:
            interactive_mode()
            print()
            again = input("🔄 Kiểm tra người khác? (y/n): ").strip().lower()
            if again != "y":
                print("\n👋 Cảm ơn bạn đã dùng Health AI Agent!\n")
                break


if __name__ == "__main__":
    main()

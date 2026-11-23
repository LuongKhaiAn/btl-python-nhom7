"""
main.py
Điểm khởi chạy chính (Entry Point) cho Hệ thống Quản lý Hội viên Phòng Gym.
Chủ đề 07 - Bài tập lớn Lập trình Python (OOP).
"""

import sys
import os

# Đảm bảo đường dẫn module luôn trỏ tới thư mục gốc của dự án
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
if BASE_DIR not in sys.path:
    sys.path.insert(0, BASE_DIR)

from gym_management import main

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\nChương trình đã được dừng bởi người dùng. Hẹn gặp lại!")
        sys.exit(0)

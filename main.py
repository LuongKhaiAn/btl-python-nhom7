"""
main.py
Điểm khởi chạy chính (Entry Point) cho Hệ thống Quản lý Hội viên Phòng Gym.
Chủ đề 07 - Bài tập lớn Lập trình Python (OOP).

Chạy bản ĐẦY ĐỦ (gym_app.py): ghép phần của An + Long + Văn + Thành (17 chức năng).
Cách chạy:  python main.py   (chạy từ thư mục nào cũng được)
"""

import os
import sys

# Đảm bảo đường dẫn module luôn trỏ tới thư mục gốc của dự án
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
if BASE_DIR not in sys.path:
    sys.path.insert(0, BASE_DIR)

# Ép console xuất UTF-8 để tiếng Việt và emoji không gây lỗi trên Windows
for _stream in (sys.stdout, sys.stderr):
    try:
        _stream.reconfigure(encoding="utf-8")
    except (AttributeError, ValueError):
        pass

from gym_app import main  # noqa: E402

if __name__ == "__main__":
    try:
        main()
    except (KeyboardInterrupt, EOFError):
        print("\n\nChương trình đã được dừng bởi người dùng. Hẹn gặp lại!")
        sys.exit(0)

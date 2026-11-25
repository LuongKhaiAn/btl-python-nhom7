"""
main.py
Điểm khởi chạy chính (Entry Point) cho Hệ thống Quản lý Hội viên Phòng Gym.
Chủ đề 07 - Bài tập lớn Lập trình Python (OOP).

Chạy bản ĐẦY ĐỦ (gym_app.py): ghép phần của An + Long + Văn + Thành (17 chức năng).
Cách chạy:  python main.py   (chạy từ thư mục nào cũng được)
"""

import sys

from gym_app import main

if __name__ == "__main__":
    try:
        main()
    except (KeyboardInterrupt, EOFError):
        print("\n\nChương trình đã được dừng bởi người dùng. Hẹn gặp lại!")
        sys.exit(0)

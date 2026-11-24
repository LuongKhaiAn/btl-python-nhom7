"""
gym_app.py
CHƯƠNG TRÌNH TỔNG HỢP - Hệ thống Quản lý Hội viên Phòng Gym (Chủ đề 07)

File này KHÔNG sửa và KHÔNG đổi tên bất kỳ file nào của nhóm. Nó chỉ "ghép" lại:
  - models.py          : các lớp thực thể OOP (Plan, Trainer, BasicMember, ...)
  - gym_management.py  : GymManager của An (CRUD cơ bản, gia hạn, check-in, JSON)
  - long_crud.py       : LongGymManager của Long (xóa an toàn, phân công HLV,
                         thêm gói/HLV, cảnh báo hết hạn)
  - gym_analytics.py   : GymAnalyticsMixin của Văn (tìm kiếm, sắp xếp, thống kê)
  - ok.py              : mã nguồn data_handler của Thành (xuất báo cáo CSV)
                         -> nạp dưới tên module 'data_handler' mà không đổi tên file.

Cách chạy trong VS Code:  mở thư mục dự án -> chạy file gym_app.py (hoặc: python gym_app.py)
"""

import importlib.util
import os
import sys

# Ép console xuất UTF-8 để tiếng Việt/emoji không lỗi khi chạy trực tiếp gym_app.py (đặc biệt trên Windows)
for _stream in (sys.stdout, sys.stderr):
    try:
        _stream.reconfigure(encoding="utf-8")
    except (AttributeError, ValueError):
        pass

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
if BASE_DIR not in sys.path:
    sys.path.insert(0, BASE_DIR)
os.chdir(BASE_DIR)  # để thư mục data/ và file CSV luôn nằm cạnh dự án


def _load_module_from_file(module_name, file_name):
    """Nạp một file .py dưới một tên module tuỳ ý (không cần đổi tên file)."""
    path = os.path.join(BASE_DIR, file_name)
    spec = importlib.util.spec_from_file_location(module_name, path)
    module = importlib.util.module_from_spec(spec)
    sys.modules[module_name] = module
    spec.loader.exec_module(module)
    return module


# ok.py chính là data_handler của Thành -> nạp với tên 'data_handler'
data_handler = _load_module_from_file("data_handler", "ok.py")

from long_crud import LongGymManager          # noqa: E402  (kế thừa GymManager của An)
from gym_analytics import GymAnalyticsMixin   # noqa: E402


class FullGymManager(GymAnalyticsMixin, LongGymManager):
    """
    Lớp quản lý đầy đủ:
      - GymAnalyticsMixin (Văn)  : search_members, sort_members, statistics_menu
      - LongGymManager (Long)    : delete_member, assign_trainer, add_plan, ...
      - GymManager (An)          : add/update/renew/check-in/load/save JSON
    Mixin đứng đầu nên bản tìm kiếm/sắp xếp/thống kê của Văn (đầy đủ hơn) được dùng.
    """

    def export_csv(self, filename="bao_cao_hoi_vien.csv"):
        """Xuất báo cáo CSV bằng hàm export_report_csv của Thành (ok.py)."""
        data = {
            "plans": self.plans,
            "trainers": self.trainers,
            "members": self.members,
            "transactions": self.transactions,
            "workout_sessions": self.workout_sessions,
        }
        path = os.path.join(BASE_DIR, filename)
        data_handler.export_report_csv(data, path)


def print_menu():
    print("\n==================================================")
    print("       HỆ THỐNG QUẢN LÝ PHÒNG GYM CHUYÊN NGHIỆP   ")
    print("==================================================")
    print(" --- Hội viên ---")
    print("  1. Xem danh sách hội viên")
    print("  2. Thêm hội viên mới (Basic / Premium)")
    print("  3. Cập nhật thông tin hội viên")
    print("  4. Xóa hội viên (kiểm tra dữ liệu liên quan)")
    print("  5. Phân công / thay đổi Huấn luyện viên (PT)")
    print("  6. Gia hạn gói tập")
    print(" --- Tập luyện ---")
    print("  7. Ghi nhận lượt tập (Check-in)")
    print("  8. Xem lịch sử lượt tập")
    print(" --- Tra cứu & Thống kê ---")
    print("  9. Tìm kiếm hội viên (đa tiêu chí)")
    print(" 10. Sắp xếp danh sách hội viên")
    print(" 11. Thống kê & Báo cáo doanh thu")
    print(" 12. Cảnh báo hội viên sắp hết hạn")
    print(" --- Danh mục & Dữ liệu ---")
    print(" 13. Xem danh mục Gói tập & Huấn luyện viên")
    print(" 14. Thêm Gói tập mới")
    print(" 15. Thêm Huấn luyện viên mới")
    print(" 16. Xuất báo cáo CSV")
    print(" 17. Lưu dữ liệu thủ công ra file JSON")
    print("  0. Thoát chương trình (tự động lưu dữ liệu)")
    print("--------------------------------------------------")


def main():
    manager = FullGymManager()

    actions = {
        "1": manager.view_members,
        "2": manager.add_member,
        "3": manager.update_member,
        "4": manager.delete_member,
        "5": manager.assign_trainer,
        "6": manager.renew_membership,
        "7": manager.record_checkin,
        "8": manager.view_checkin_history,
        "9": manager.search_members,
        "10": manager.sort_members,
        "11": manager.statistics_menu,
        "12": manager.warn_expiring_members,
        "13": manager.view_plans_and_trainers,
        "14": manager.add_plan,
        "15": manager.add_trainer,
        "16": manager.export_csv,
        "17": manager.save_data,
    }

    while True:
        print_menu()
        choice = input("Nhập lựa chọn của bạn (0-17): ").strip()

        if choice == "0":
            manager.save_data()
            print("Dữ liệu đã được lưu an toàn. Hẹn gặp lại bạn!")
            break

        action = actions.get(choice)
        if action is None:
            print("Lựa chọn không hợp lệ, vui lòng chọn từ 0 đến 17.")
            continue

        # Bắt lỗi để nhập sai/lỗi bất ngờ không làm chương trình bị văng
        try:
            action()
        except ValueError as err:
            print(f"Dữ liệu không hợp lệ: {err}")
        except Exception as err:  # noqa: BLE001
            print(f"Có lỗi xảy ra: {err}")


if __name__ == "__main__":
    try:
        main()
    except (KeyboardInterrupt, EOFError):
        print("\n\nChương trình đã được dừng bởi người dùng. Hẹn gặp lại!")
        sys.exit(0)

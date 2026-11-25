"""
gym_management.py
Lớp quản lý trung tâm GymManager (phần của An): CRUD hội viên, gia hạn, check-in,
lưu/đọc JSON. Việc lưu/đọc/khởi tạo dữ liệu mẫu được ủy quyền cho data_handler.py.
Tìm kiếm / sắp xếp / thống kê nằm ở gym_analytics.py (GymAnalyticsMixin).
"""

import os
import re
from datetime import datetime

import data_handler
from models import (
    BasicMember,
    PremiumMember,
    WorkoutSession,
    Transaction,
)


# Đường dẫn dữ liệu tính theo vị trí file này (không phụ thuộc thư mục đang đứng khi chạy)
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DEFAULT_DATA_FILE = os.path.join(BASE_DIR, "data", "gym_data.json")

PHONE_PATTERN = re.compile(r"0\d{9}")  # SĐT Việt Nam: 10 chữ số, bắt đầu bằng 0


def is_valid_phone(phone: str) -> bool:
    """SĐT hợp lệ: đúng 10 chữ số và bắt đầu bằng 0."""
    return bool(PHONE_PATTERN.fullmatch(phone or ""))


def next_id(prefix: str, existing_ids, width: int = 3) -> str:
    """Sinh mã mới = số lớn nhất đang có + 1 (không trùng kể cả khi dữ liệu bị xóa/sửa)."""
    biggest = 0
    for value in existing_ids:
        match = re.fullmatch(prefix + r"(\d+)", str(value), re.IGNORECASE)
        if match:
            biggest = max(biggest, int(match.group(1)))
    return f"{prefix}{biggest + 1:0{width}d}"


def ask(prompt: str, is_valid=None, error: str = "Giá trị không hợp lệ, vui lòng nhập lại!") -> str:
    """Hỏi lại cho tới khi nhập hợp lệ (không để trống và thỏa is_valid nếu có)."""
    while True:
        value = input(prompt).strip()
        if value and (is_valid is None or is_valid(value)):
            return value
        print(error)


class GymManager:
    def __init__(self, data_file: str = None):
        self.data_file = DEFAULT_DATA_FILE if data_file is None else data_file
        self.plans = []
        self.trainers = []
        self.members = []
        self.workout_sessions = []
        self.transactions = []
        self.load_data()

    # ------------------------------------------------------------------
    # LƯU / ĐỌC DỮ LIỆU (ủy quyền cho data_handler)
    # ------------------------------------------------------------------
    def _apply_data(self, data: dict):
        self.plans = data["plans"]
        self.trainers = data["trainers"]
        self.members = data["members"]
        self.workout_sessions = data["workout_sessions"]
        self.transactions = data["transactions"]

    def init_default_data(self):
        """Nạp dữ liệu mẫu (6 hội viên phủ đủ các trường hợp biên) từ data_handler."""
        self._apply_data(data_handler.init_default_data())

    def save_data(self):
        data = {
            "plans": self.plans,
            "trainers": self.trainers,
            "members": self.members,
            "workout_sessions": self.workout_sessions,
            "transactions": self.transactions,
        }
        try:
            data_handler.save_data(data, self.data_file)  # ghi atomic qua file tạm
        except RuntimeError as e:
            print(f"Lỗi khi lưu dữ liệu JSON: {e}")

    def load_data(self):
        if not os.path.exists(self.data_file):
            self.init_default_data()
            self.save_data()
            return
        try:
            self._apply_data(data_handler.load_data(self.data_file))
        except RuntimeError as e:
            # KHÔNG ghi đè file hỏng: đổi tên thành bản sao lưu để còn khôi phục thủ công
            backup = f"{self.data_file}.{datetime.now():%Y%m%d_%H%M%S}.bak"
            try:
                os.replace(self.data_file, backup)
                print(f"{e}\nĐã sao lưu file lỗi thành: {backup}")
            except OSError:
                print(f"{e}\nKhông thể sao lưu file lỗi.")
            print("Chuyển sang dữ liệu mẫu.")
            self.init_default_data()
            self.save_data()

    # ------------------------------------------------------------------
    # TIỆN ÍCH TRA CỨU
    # ------------------------------------------------------------------
    def find_member(self, member_id: str):
        key = (member_id or "").strip().lower()
        return next((m for m in self.members if m.member_id.lower() == key), None)

    def find_plan(self, plan_id: str):
        key = (plan_id or "").strip().lower()
        return next((p for p in self.plans if p.plan_id.lower() == key), None)

    def find_trainer(self, trainer_id: str):
        key = (trainer_id or "").strip().lower()
        return next((t for t in self.trainers if t.trainer_id.lower() == key), None)

    def member_id_in_history(self, member_id: str) -> bool:
        """Mã đã từng có giao dịch / lượt tập (kể cả hội viên đã bị xóa)."""
        key = member_id.strip().lower()
        return (
            any(tx.member_id.lower() == key for tx in self.transactions)
            or any(s.member_id.lower() == key for s in self.workout_sessions)
        )

    def view_members(self, member_list=None):
        target = self.members if member_list is None else member_list
        print("\n============================== DANH SÁCH HỘI VIÊN ==============================")
        if not target:
            print("Không có hội viên nào để hiển thị.")
            return
        for m in target:
            m.display_info()
        print(f"Tổng số hiển thị: {len(target)} hội viên.")

    def add_member(self):
        print("\n--- THÊM HỘI VIÊN MỚI ---")
        member_id = input("Nhập mã hội viên (vd: HV04): ").strip()
        if not member_id:
            print("Mã hội viên không được để trống!")
            return
        if self.find_member(member_id):
            print(f"Mã '{member_id}' đã tồn tại trong hệ thống!")
            return
        if self.member_id_in_history(member_id):
            print(f"Mã '{member_id}' đã từng được dùng (còn lịch sử giao dịch/lượt tập). "
                  "Vui lòng chọn mã khác để tránh lẫn dữ liệu cũ!")
            return

        full_name = ask("Nhập họ tên hội viên: ", error="Họ tên không được để trống!")
        phone_number = ask(
            "Nhập số điện thoại (10 số, bắt đầu bằng 0): ",
            is_valid_phone,
            "Số điện thoại không hợp lệ (cần đúng 10 chữ số, bắt đầu bằng 0)!",
        )

        print("\nChọn phân loại hội viên:")
        print(" 1. Basic Member (Tập luyện thông thường)")
        print(" 2. Premium Member (VIP: Sauna, Locker, ưu đãi HLV)")
        type_choice = ask("Lựa chọn (1 hoặc 2): ", lambda v: v in ("1", "2"),
                          "Phân loại hội viên không hợp lệ (chỉ nhập 1 hoặc 2)!")

        if not self.plans:
            print("Chưa có gói tập nào. Hãy thêm gói tập trước!")
            return
        print("\n--- Danh mục Gói tập ---")
        for p in self.plans:
            p.display_info()
        selected_plan = self.find_plan(input("Chọn mã gói tập: "))
        if not selected_plan:
            print("Mã gói tập không hợp lệ!")
            return

        print("\n--- Danh mục Huấn luyện viên (PT) ---")
        print("0    | Không thuê HLV riêng (Tự tập)")
        for t in self.trainers:
            t.display_info()
        trainer_id = input("Chọn mã HLV (hoặc 0 nếu tự tập): ").strip()
        selected_trainer = None
        if trainer_id != "0":
            selected_trainer = self.find_trainer(trainer_id)
            if not selected_trainer:
                print("Mã HLV không tồn tại! Không tạo hội viên.")
                return

        if type_choice == "2":
            new_member = PremiumMember(
                member_id,
                full_name,
                phone_number,
                selected_plan,
                selected_trainer,
                vip_perks_fee=200000,
                sauna_access=True,
                trainer_discount_rate=0.2,
            )
        else:
            new_member = BasicMember(
                member_id,
                full_name,
                phone_number,
                selected_plan,
                selected_trainer,
                discount_rate=0.0,
            )

        fee = new_member.calculate_membership_fee()
        self.members.append(new_member)

        tx_id = next_id("GD", (tx.transaction_id for tx in self.transactions))
        self.transactions.append(
            Transaction(tx_id, new_member.member_id, fee, "Đăng ký mới", selected_plan.plan_name)
        )

        print(f"\nThêm hội viên '{full_name}' thành công!")
        print(f"Giao dịch thu phí '{tx_id}' đã ghi nhận: {fee:,.0f} VNĐ.")
        self.save_data()

    def update_member(self):
        print("\n--- CẬP NHẬT THÔNG TIN HỘI VIÊN ---")
        member = self.find_member(input("Nhập mã hội viên cần sửa: "))
        if not member:
            print("Không tìm thấy hội viên!")
            return

        print("\nThông tin hiện tại:")
        member.display_info()
        print("\n(Nhấn Enter để giữ nguyên giá trị hiện tại)")

        new_name = input(f"Họ tên mới [{member.full_name}]: ").strip()
        new_phone = input(f"SĐT mới [{member.phone_number}]: ").strip()
        if new_phone and not is_valid_phone(new_phone):
            print("Số điện thoại không hợp lệ (cần đúng 10 chữ số, bắt đầu bằng 0)! Không cập nhật.")
            return
        if new_name:
            member.full_name = new_name
        if new_phone:
            member.phone_number = new_phone

        change_trainer = input("Bạn có muốn đổi Huấn luyện viên không? (y/n): ").strip().lower()
        if change_trainer == "y":
            print("\nDanh sách HLV (nhập 0 để tự tập):")
            print("0    | Tự tập")
            for t in self.trainers:
                t.display_info()
            tid = input("Chọn mã HLV mới: ").strip()
            if tid == "0":
                member.trainer = None
                print("Đã chuyển về hình thức tự tập.")
            else:
                new_t = self.find_trainer(tid)
                if new_t:
                    member.trainer = new_t
                    print("Cập nhật HLV thành công.")
                else:
                    print("Mã HLV không hợp lệ, giữ nguyên HLV cũ.")

        print("Cập nhật thông tin thành công!")
        self.save_data()

    def delete_member(self):
        print("\n--- XÓA HỘI VIÊN ---")
        member = self.find_member(input("Nhập mã hội viên cần xóa: "))
        if not member:
            print("Không tìm thấy hội viên!")
            return

        confirm = input(f"Xác nhận xóa hội viên '{member.full_name}' ({member.member_id})? (y/n): ").strip().lower()
        if confirm == "y":
            self.members.remove(member)
            print(f"Đã xóa hội viên '{member.member_id}' khỏi hệ thống.")
            self.save_data()
        else:
            print("Đã hủy thao tác xóa.")

    def renew_membership(self):
        print("\n--- GIA HẠN GÓI TẬP HỘI VIÊN ---")
        member = self.find_member(input("Nhập mã hội viên cần gia hạn: "))
        if not member:
            print("Không tìm thấy hội viên!")
            return

        print("\nThông tin hiện tại:")
        member.display_info()
        old_expiry = member.expiry_date.strftime("%d/%m/%Y")
        is_still_active = member.is_active()

        print("\n--- Danh sách Gói tập gia hạn ---")
        for p in self.plans:
            p.display_info()
        selected_plan = self.find_plan(input("Chọn mã gói muốn gia hạn: "))
        if not selected_plan:
            print("Mã gói tập không hợp lệ!")
            return

        member.renew(selected_plan)
        new_expiry = member.expiry_date.strftime("%d/%m/%Y")
        fee = member.calculate_membership_fee()

        tx_id = next_id("GD", (tx.transaction_id for tx in self.transactions))
        self.transactions.append(
            Transaction(tx_id, member.member_id, fee, "Gia hạn gói", selected_plan.plan_name)
        )

        print("\n================= KẾT QUẢ GIA HẠN =================")
        if is_still_active:
            print(f"Hội viên còn hạn -> Cộng dồn từ ngày hết hạn cũ: {old_expiry}")
        else:
            print(f"Hội viên đã hết hạn -> Kích hoạt từ ngày hôm nay: {datetime.now().strftime('%d/%m/%Y')}")
        print(f"👉 Ngày hết hạn mới: {new_expiry}")
        print(f"👉 Phí gia hạn thu: {fee:,.0f} VNĐ (Mã GD: {tx_id})")
        print("===================================================")
        self.save_data()

    def record_checkin(self):
        print("\n--- GHI NHẬN LƯỢT TẬP (CHECK-IN) ---")
        member = self.find_member(input("Quét hoặc nhập mã hội viên: "))
        if not member:
            print("Không tìm thấy hội viên trong hệ thống!")
            return

        if not member.is_active():
            print(f"❌ CẢNH BÁO: Thẻ hội viên '{member.full_name}' đã hết hạn vào ngày {member.expiry_date.strftime('%d/%m/%Y')}!")
            print("Vui lòng thực hiện gia hạn gói tập trước khi check-in vào phòng.")
            return

        # Quy tắc điểm danh lặp: mỗi ngày 1 lượt hợp lệ; check-in thêm phải được xác nhận
        today_text = datetime.now().strftime("%d/%m/%Y")
        done_today = [
            s for s in self.workout_sessions
            if s.member_id.lower() == member.member_id.lower()
            and s.checkin_time.startswith(today_text)
        ]
        if done_today:
            print(f"⚠️ Hội viên đã check-in {len(done_today)} lượt trong hôm nay ({today_text}).")
            if input("Vẫn ghi nhận thêm một lượt nữa? (y/n): ").strip().lower() != "y":
                print("Đã hủy ghi nhận lượt tập.")
                return

        notes = input("Nhập nội dung/dịch vụ buổi tập (mặc định: Tập gym): ").strip()
        if not notes:
            notes = "Tập gym"
        if member.get_member_type() == "Premium":
            notes += " [VIP: Sử dụng xông hơi & tủ đồ riêng]"

        sid = next_id("LT", (s.session_id for s in self.workout_sessions))
        session = WorkoutSession(sid, member.member_id, notes=notes)
        self.workout_sessions.append(session)

        print(f"✅ CHECK-IN THÀNH CÔNG cho hội viên: {member.full_name} ({member.get_member_type()})")
        print(f"Thời gian: {session.checkin_time} | Ghi chú: {session.notes}")
        self.save_data()

    def view_checkin_history(self):
        print("\n======================= LỊCH SỬ LƯỢT TẬP (CHECK-IN) =======================")
        if not self.workout_sessions:
            print("Chưa có lượt tập nào được ghi nhận.")
            return
        for s in self.workout_sessions:
            s.display_info()
        print(f"Tổng số lượt tập: {len(self.workout_sessions)}")

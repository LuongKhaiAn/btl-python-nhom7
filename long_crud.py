from datetime import datetime

# Dùng import thông thường thay vì nạp file bằng importlib
# (cách cũ trỏ tới tên file 'gym_management (1).py' và chạy gym_management.py hai lần).
from gym_management import (
    Plan,
    Trainer,
    Member,
    BasicMember,
    PremiumMember,
    WorkoutSession,
    Transaction,
    GymManager as BaseGymManager,
)


# =====================================================================
# LỚP MỞ RỘNG CỦA LONG (KẾ THỪA GymManager TỪ FILE CỦA AN)
# =====================================================================
class LongGymManager(BaseGymManager):
    """
    Kế thừa toàn bộ dữ liệu (members, plans, trainers, workout_sessions, transactions)
    và các phương thức có sẵn từ GymManager của An, đồng thời triển khai phần của Long:
    - delete_member(): Xóa hội viên có kiểm tra dữ liệu liên quan.
    - assign_trainer(): Phân công / đổi Huấn luyện viên độc lập.
    - view_plans_and_trainers(), add_plan(), add_trainer(): Quản lý gói tập & HLV.
    - warn_expiring_members(): Chức năng mở rộng 1 - Cảnh báo hội viên sắp hết hạn.
    """

    def delete_member(self):
        """Ghi đè delete_member(): kiểm tra ràng buộc dữ liệu liên quan trước khi xóa."""
        print("\n--- XÓA HỘI VIÊN (KIỂM TRA DỮ LIỆU LIÊN QUAN) ---")
        if not self.members:
            print("Danh sách hội viên đang trống!")
            return

        member_id = input("Nhập mã hội viên cần xóa: ").strip()
        member = next((m for m in self.members if m.member_id.lower() == member_id.lower()), None)
        if not member:
            print(f"Không tìm thấy hội viên có mã '{member_id}'!")
            return

        print("\nThông tin hội viên chuẩn bị xóa:")
        member.display_info()

        # Kiểm tra các ràng buộc dữ liệu liên quan trong hệ thống của An
        related_txs = [tx for tx in self.transactions if tx.member_id.lower() == member.member_id.lower()]
        related_sessions = [s for s in self.workout_sessions if s.member_id.lower() == member.member_id.lower()]
        warnings = []

        if member.is_active():
            warnings.append(f"Thẻ tập vẫn ĐANG CÒN HẠN đến ngày {member.expiry_date.strftime('%d/%m/%Y')}")
        if related_txs:
            warnings.append(f"Có {len(related_txs)} giao dịch thanh toán liên quan")
        if related_sessions:
            warnings.append(f"Có {len(related_sessions)} lượt check-in tập luyện liên quan")

        if warnings:
            print("\n⚠️ CẢNH BÁO DỮ LIỆU LIÊN QUAN:")
            for w in warnings:
                print(f" - {w}")

        confirm = input(f"Bạn có chắc chắn muốn xóa hội viên '{member.full_name}' ({member.member_id})? (y/n): ").strip().lower()
        if confirm == "y":
            self.members.remove(member)
            print(f"Đã xóa hội viên '{member.member_id}' khỏi danh sách (lịch sử giao dịch được giữ lại để bảo toàn doanh thu).")
            self.save_data()
        else:
            print("Đã hủy thao tác xóa.")

    def assign_trainer(self):
        """Phân công hoặc thay đổi Huấn luyện viên (PT) cho hội viên."""
        print("\n--- PHÂN CÔNG / THAY ĐỔI HUẤN LUYỆN VIÊN ---")
        if not self.members:
            print("Danh sách hội viên đang trống!")
            return

        member_id = input("Nhập mã hội viên cần phân công HLV: ").strip()
        member = next((m for m in self.members if m.member_id.lower() == member_id.lower()), None)
        if not member:
            print(f"Không tìm thấy hội viên '{member_id}'!")
            return

        current_trainer = member.trainer.full_name if member.trainer else "Tự tập (Chưa có HLV)"
        print(f"Hội viên: {member.full_name} ({member.get_member_type()}) | HLV hiện tại: {current_trainer}")

        print("\n--- Danh sách Huấn luyện viên hiện có ---")
        print("0    | Hủy HLV (Chuyển sang tự tập)")
        for t in self.trainers:
            t.display_info()

        trainer_id = input("Nhập mã HLV muốn gán (hoặc 0): ").strip()
        if trainer_id == "0":
            member.trainer = None
            print(f"Đã chuyển hội viên '{member.full_name}' sang hình thức Tự tập.")
        else:
            selected_trainer = next((t for t in self.trainers if t.trainer_id.lower() == trainer_id.lower()), None)
            if not selected_trainer:
                print(f"Lỗi: Không tìm thấy HLV có mã '{trainer_id}'!")
                return
            member.trainer = selected_trainer
            print(f"Đã phân công HLV '{selected_trainer.full_name}' cho hội viên '{member.full_name}'.")
            print(f"Học phí cập nhật mới của hội viên: {member.calculate_membership_fee():,.0f} VNĐ")

        self.save_data()

    def view_plans_and_trainers(self):
        """Hiển thị danh mục Gói tập và Huấn luyện viên hiện có."""
        print("\n======================= DANH MỤC GÓI TẬP =======================")
        if not self.plans:
            print("Chưa có gói tập nào.")
        else:
            for p in self.plans:
                p.display_info()

        print("\n=================== DANH SÁCH HUẤN LUYỆN VIÊN ===================")
        if not self.trainers:
            print("Chưa có huấn luyện viên nào.")
        else:
            for t in self.trainers:
                t.display_info()

    def add_plan(self):
        """Thêm gói tập mới vào danh sách self.plans."""
        print("\n--- THÊM GÓI TẬP MỚI ---")
        plan_id = input("Nhập mã gói tập (vd: P09): ").strip()
        if not plan_id:
            print("Lỗi: Mã gói tập không được để trống!")
            return
        if any(p.plan_id.lower() == plan_id.lower() for p in self.plans):
            print(f"Lỗi: Mã gói '{plan_id}' đã tồn tại!")
            return

        plan_name = input("Nhập tên gói tập (vd: 9 Tháng): ").strip()
        if not plan_name:
            print("Lỗi: Tên gói tập không được để trống!")
            return

        try:
            duration_months = int(input("Nhập thời hạn (số tháng >= 1): ").strip())
            if duration_months < 1:
                print("Lỗi: Thời hạn gói phải >= 1 tháng!")
                return
            price = float(input("Nhập giá gói (VNĐ >= 0): ").strip())
            if price < 0:
                print("Lỗi: Giá gói không được âm!")
                return
        except ValueError:
            print("Lỗi: Thời hạn và giá gói phải là số hợp lệ!")
            return

        new_plan = Plan(plan_id, plan_name, duration_months, price)
        self.plans.append(new_plan)
        print(f"Đã thêm gói tập '{plan_name}' thành công!")
        self.save_data()

    def add_trainer(self):
        """Thêm huấn luyện viên mới vào danh sách self.trainers."""
        print("\n--- THÊM HUẤN LUYỆN VIÊN MỚI ---")
        trainer_id = input("Nhập mã HLV (vd: T04): ").strip()
        if not trainer_id:
            print("Lỗi: Mã HLV không được để trống!")
            return
        if any(t.trainer_id.lower() == trainer_id.lower() for t in self.trainers):
            print(f"Lỗi: Mã HLV '{trainer_id}' đã tồn tại!")
            return

        full_name = input("Nhập họ tên HLV: ").strip()
        if not full_name:
            print("Lỗi: Họ tên HLV không được để trống!")
            return

        specialty = input("Nhập chuyên môn (vd: Gym / Cardio): ").strip()
        if not specialty:
            print("Lỗi: Chuyên môn không được để trống!")
            return

        phone_number = input("Nhập số điện thoại HLV: ").strip()
        try:
            monthly_fee = float(input("Nhập phí thuê HLV/tháng (VNĐ >= 0): ").strip())
            if monthly_fee < 0:
                print("Lỗi: Phí thuê HLV không được âm!")
                return
        except ValueError:
            print("Lỗi: Phí thuê HLV phải là số hợp lệ!")
            return

        new_trainer = Trainer(trainer_id, full_name, specialty, phone_number, monthly_fee)
        self.trainers.append(new_trainer)
        print(f"Đã thêm huấn luyện viên '{full_name}' thành công!")
        self.save_data()

    def warn_expiring_members(self):
        """Chức năng mở rộng 1: Cảnh báo danh sách hội viên sắp hết hạn trong N ngày tới."""
        print("\n--- CẢNH BÁO HỘI VIÊN SẮP HẾT HẠN ---")
        if not self.members:
            print("Danh sách hội viên đang trống!")
            return

        raw_days = input("Nhập số ngày muốn kiểm tra trước (vd: 7): ").strip()
        if not raw_days.isdigit() or int(raw_days) < 0:
            print("Lỗi: Vui lòng nhập một số nguyên không âm!")
            return

        days_threshold = int(raw_days)
        today = datetime.now().date()
        expiring_list = []

        for m in self.members:
            days_left = (m.expiry_date.date() - today).days
            if 0 <= days_left <= days_threshold:
                expiring_list.append((m, days_left))

        if not expiring_list:
            print(f"Không có hội viên nào sắp hết hạn trong vòng {days_threshold} ngày tới.")
            return

        expiring_list.sort(key=lambda item: item[1])
        print(f"\n⚠️ CÓ {len(expiring_list)} HỘI VIÊN SẮP HẾT HẠN TRONG {days_threshold} NGÀY TỚI:")
        for m, days_left in expiring_list:
            day_txt = "HẾT HẠN HÔM NAY" if days_left == 0 else f"Còn {days_left} ngày"
            print(
                f" - [{day_txt:<15}] {m.member_id:<5} | {m.full_name:<18} | "
                f"SĐT: {m.phone_number:<11} | Hết hạn: {m.expiry_date.strftime('%d/%m/%Y')}"
            )


# =====================================================================
# MENU CHẠY THỬ PHẦN CỦA LONG
# =====================================================================
if __name__ == "__main__":
    manager = LongGymManager()
    while True:
        print("\n==================================================")
        print("      CHƯƠNG TRÌNH QUẢN LÝ NGHIỆP VỤ - LONG")
        print("==================================================")
        print(" 1. Xem danh sách hội viên")
        print(" 2. Thêm hội viên mới (Basic / Premium)")
        print(" 3. Cập nhật thông tin hội viên")
        print(" 4. Xóa hội viên (Kiểm tra dữ liệu liên quan)")
        print(" 5. Phân công / thay đổi Huấn luyện viên (PT)")
        print(" 6. Gia hạn gói tập")
        print(" 7. Ghi nhận lượt tập (Check-in)")
        print(" 8. Xem danh mục Gói tập & Huấn luyện viên")
        print(" 9. Thêm Gói tập mới")
        print("10. Thêm Huấn luyện viên mới")
        print("11. Cảnh báo hội viên sắp hết hạn (Mở rộng 1)")
        print(" 0. Thoát chương trình")
        print("--------------------------------------------------")
        choice = input("Nhập lựa chọn (0-11): ").strip()

        if choice == "1":
            manager.view_members()
        elif choice == "2":
            manager.add_member()
        elif choice == "3":
            manager.update_member()
        elif choice == "4":
            manager.delete_member()
        elif choice == "5":
            manager.assign_trainer()
        elif choice == "6":
            manager.renew_membership()
        elif choice == "7":
            manager.record_checkin()
        elif choice == "8":
            manager.view_plans_and_trainers()
        elif choice == "9":
            manager.add_plan()
        elif choice == "10":
            manager.add_trainer()
        elif choice == "11":
            manager.warn_expiring_members()
        elif choice == "0":
            manager.save_data()
            print("Đã lưu dữ liệu vào 'gym_data.json'. Tạm biệt!")
            break
        else:
            print("Lựa chọn không hợp lệ, vui lòng chọn từ 0 đến 11.")
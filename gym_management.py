import json
import os
from datetime import datetime, timedelta

from models import (
    MembershipPlan,
    Plan,
    Trainer,
    Member,
    BasicMember,
    PremiumMember,
    WorkoutSession,
    Transaction,
)


# Đường dẫn dữ liệu tính theo vị trí file này (không phụ thuộc thư mục đang đứng khi chạy)
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DEFAULT_DATA_FILE = os.path.join(BASE_DIR, "data", "gym_data.json")


class GymManager:
    def __init__(self, data_file: str = None):
        if data_file is None:
            legacy_file = os.path.join(BASE_DIR, "gym_data.json")
            if not os.path.exists(DEFAULT_DATA_FILE) and os.path.exists(legacy_file):
                self.data_file = legacy_file
            else:
                self.data_file = DEFAULT_DATA_FILE
        else:
            self.data_file = data_file
        self.plans = []
        self.trainers = []
        self.members = []
        self.workout_sessions = []
        self.transactions = []
        self.load_data()

    def init_default_data(self):
        self.plans = [
            Plan("P01", "1 Tháng", 1, 500000),
            Plan("P03", "3 Tháng", 3, 1350000),
            Plan("P06", "6 Tháng", 6, 2500000),
            Plan("P12", "12 Tháng", 12, 4500000),
        ]

        self.trainers = [
            Trainer("T01", "Nguyễn Văn HLV", "Fitness / Giảm cân", "0901234567", 500000),
            Trainer("T02", "Trần Thị HLV", "Yoga / Pilates", "0908765432", 600000),
            Trainer("T03", "Lê Văn HLV", "Boxing / Kickfit", "0912345678", 550000),
        ]

        m1 = BasicMember(
            "HV01",
            "Nguyễn Văn An",
            "0911222333",
            self.plans[1],
            self.trainers[0],
            join_date="01/10/2026",
            expiry_date="01/01/2027",
            discount_rate=0.05,
        )
        m2 = PremiumMember(
            "HV02",
            "Trần Thị Bình",
            "0922333444",
            self.plans[2],
            self.trainers[1],
            join_date="15/09/2026",
            expiry_date="15/03/2027",
            vip_perks_fee=200000,
        )
        m3 = BasicMember(
            "HV03",
            "Lê Hoàng Cường",
            "0933444555",
            self.plans[0],
            None,
            join_date="01/08/2026",
            expiry_date="01/09/2026",
            discount_rate=0.0,
        )
        self.members = [m1, m2, m3]

        self.transactions = [
            Transaction("GD001", "HV01", m1.calculate_membership_fee(), "Đăng ký mới", m1.plan.plan_name, "01/10/2026 08:30:00"),
            Transaction("GD002", "HV02", m2.calculate_membership_fee(), "Đăng ký mới", m2.plan.plan_name, "15/09/2026 09:15:00"),
            Transaction("GD003", "HV03", m3.calculate_membership_fee(), "Đăng ký mới", m3.plan.plan_name, "01/08/2026 14:00:00"),
        ]

        self.workout_sessions = [
            WorkoutSession("LT001", "HV01", "05/10/2026 17:30:00", "Tập cơ ngực cùng HLV"),
            WorkoutSession("LT002", "HV02", "20/09/2026 18:00:00", "Tập Yoga và xông hơi"),
        ]

    def save_data(self):
        data = {
            "plans": [p.to_dict() for p in self.plans],
            "trainers": [t.to_dict() for t in self.trainers],
            "members": [m.to_dict() for m in self.members],
            "workout_sessions": [s.to_dict() for s in self.workout_sessions],
            "transactions": [tx.to_dict() for tx in self.transactions],
        }
        try:
            folder = os.path.dirname(self.data_file)
            if folder:
                os.makedirs(folder, exist_ok=True)
            with open(self.data_file, "w", encoding="utf-8") as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
            print("Đã lưu dữ liệu vào hệ thống (JSON) thành công!")
        except Exception as e:
            print(f"Lỗi khi lưu dữ liệu JSON: {e}")

    def load_data(self):
        if not os.path.exists(self.data_file):
            self.init_default_data()
            self.save_data()
            return

        try:
            with open(self.data_file, "r", encoding="utf-8") as f:
                data = json.load(f)

            self.plans = [Plan.from_dict(p) for p in data.get("plans", [])]
            self.trainers = [Trainer.from_dict(t) for t in data.get("trainers", [])]

            plan_map = {p.plan_id: p for p in self.plans}
            trainer_map = {t.trainer_id: t for t in self.trainers}

            self.members = []
            for m in data.get("members", []):
                if m.get("type") == "Premium":
                    member = PremiumMember.from_dict(m)
                else:
                    member = BasicMember.from_dict(m)
                # Dùng chung đối tượng Plan/Trainer với danh mục (thay vì bản sao riêng)
                if member.plan.plan_id in plan_map:
                    member.plan = plan_map[member.plan.plan_id]
                if member.trainer and member.trainer.trainer_id in trainer_map:
                    member.trainer = trainer_map[member.trainer.trainer_id]
                self.members.append(member)

            self.workout_sessions = [
                WorkoutSession.from_dict(s)
                for s in data.get("workout_sessions", [])
            ]
            self.transactions = [
                Transaction.from_dict(tx)
                for tx in data.get("transactions", [])
            ]
        except Exception as e:
            print(f"Lỗi đọc file JSON ({e}), chuyển sang dữ liệu mặc định.")
            self.init_default_data()

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
        if any(m.member_id.lower() == member_id.lower() for m in self.members):
            print(f"Mã '{member_id}' đã tồn tại trong hệ thống!")
            return

        full_name = input("Nhập họ tên hội viên: ").strip()
        if not full_name:
            print("Họ tên không được để trống!")
            return

        phone_number = input("Nhập số điện thoại: ").strip()

        print("\nChọn phân loại hội viên:")
        print(" 1. Basic Member (Tập luyện thông thường)")
        print(" 2. Premium Member (VIP: Sauna, Locker, ưu đãi HLV)")
        type_choice = input("Lựa chọn (1 hoặc 2): ").strip()
        if type_choice not in ("1", "2"):
            print("Phân loại hội viên không hợp lệ (chỉ nhập 1 hoặc 2)!")
            return

        print("\n--- Danh mục Gói tập ---")
        for p in self.plans:
            p.display_info()
        plan_id = input("Chọn mã gói tập: ").strip()
        selected_plan = next((p for p in self.plans if p.plan_id.lower() == plan_id.lower()), None)
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
            selected_trainer = next((t for t in self.trainers if t.trainer_id.lower() == trainer_id.lower()), None)
            if not selected_trainer:
                print("Mã HLV không tồn tại, tự động chuyển về Tự tập.")

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

        tx_id = f"GD{len(self.transactions) + 1:03d}"
        new_tx = Transaction(
            tx_id,
            member_id,
            fee,
            "Đăng ký mới",
            selected_plan.plan_name,
        )
        self.transactions.append(new_tx)

        print(f"\nThêm hội viên '{full_name}' thành công!")
        print(f"Giao dịch thu phí '{tx_id}' đã ghi nhận: {fee:,.0f} VNĐ.")
        self.save_data()

    def update_member(self):
        print("\n--- CẬP NHẬT THÔNG TIN HỘI VIÊN ---")
        member_id = input("Nhập mã hội viên cần sửa: ").strip()
        member = next((m for m in self.members if m.member_id.lower() == member_id.lower()), None)
        if not member:
            print(f"Không tìm thấy hội viên '{member_id}'!")
            return

        print("\nThông tin hiện tại:")
        member.display_info()
        print("\n(Nhấn Enter để giữ nguyên giá trị hiện tại)")

        new_name = input(f"Họ tên mới [{member.full_name}]: ").strip()
        if new_name:
            member.full_name = new_name

        new_phone = input(f"SĐT mới [{member.phone_number}]: ").strip()
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
                new_t = next((t for t in self.trainers if t.trainer_id.lower() == tid.lower()), None)
                if new_t:
                    member.trainer = new_t
                    print("Cập nhật HLV thành công.")
                else:
                    print("Mã HLV không hợp lệ, giữ nguyên HLV cũ.")

        print("Cập nhật thông tin thành công!")
        self.save_data()

    def delete_member(self):
        print("\n--- XÓA HỘI VIÊN ---")
        member_id = input("Nhập mã hội viên cần xóa: ").strip()
        member = next((m for m in self.members if m.member_id.lower() == member_id.lower()), None)
        if not member:
            print(f"Không tìm thấy hội viên '{member_id}'!")
            return

        confirm = input(f"Xác nhận xóa hội viên '{member.full_name}' ({member.member_id})? (y/n): ").strip().lower()
        if confirm == "y":
            self.members.remove(member)
            print(f"Đã xóa hội viên '{member_id}' khỏi hệ thống.")
            self.save_data()
        else:
            print("Đã hủy thao tác xóa.")

    def renew_membership(self):
        print("\n--- GIA HẠN GÓI TẬP HỘI VIÊN (MỤC III.2) ---")
        member_id = input("Nhập mã hội viên cần gia hạn: ").strip()
        member = next((m for m in self.members if m.member_id.lower() == member_id.lower()), None)
        if not member:
            print(f"Không tìm thấy hội viên '{member_id}'!")
            return

        print("\nThông tin hiện tại:")
        member.display_info()
        old_expiry = member.expiry_date.strftime("%d/%m/%Y")
        is_still_active = member.is_active()

        print("\n--- Danh sách Gói tập gia hạn ---")
        for p in self.plans:
            p.display_info()
        plan_id = input("Chọn mã gói muốn gia hạn: ").strip()
        selected_plan = next((p for p in self.plans if p.plan_id.lower() == plan_id.lower()), None)
        if not selected_plan:
            print("Mã gói tập không hợp lệ!")
            return

        member.renew(selected_plan)
        new_expiry = member.expiry_date.strftime("%d/%m/%Y")
        fee = member.calculate_membership_fee()

        tx_id = f"GD{len(self.transactions) + 1:03d}"
        new_tx = Transaction(
            tx_id,
            member.member_id,
            fee,
            "Gia hạn gói",
            selected_plan.plan_name,
        )
        self.transactions.append(new_tx)

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
        member_id = input("Quét hoặc nhập mã hội viên: ").strip()
        member = next((m for m in self.members if m.member_id.lower() == member_id.lower()), None)
        if not member:
            print(f"Không tìm thấy hội viên có mã '{member_id}' trong hệ thống!")
            return

        if not member.is_active():
            print(f"❌ CẢNH BÁO: Thẻ hội viên '{member.full_name}' đã hết hạn vào ngày {member.expiry_date.strftime('%d/%m/%Y')}!")
            print("Vui lòng thực hiện gia hạn gói tập trước khi check-in vào phòng.")
            return

        notes = input("Nhập nội dung/dịch vụ buổi tập (mặc định: Tập gym): ").strip()
        if not notes:
            notes = "Tập gym"
        if member.get_member_type() == "Premium":
            notes += " [VIP: Sử dụng xông hơi & tủ đồ riêng]"

        sid = f"LT{len(self.workout_sessions) + 1:03d}"
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

    def search_members(self):
        print("\n--- TÌM KIẾM HỘI VIÊN (ĐA TIÊU CHÍ) ---")
        print(" 1. Tìm kiếm chung (Mã, Tên hoặc Số điện thoại)")
        print(" 2. Lọc theo trạng thái thẻ (Còn hạn / Hết hạn)")
        print(" 3. Lọc theo loại hội viên (Basic / Premium)")
        choice = input("Lựa chọn (1-3): ").strip()

        if choice == "1":
            kw = input("Nhập từ khóa tìm kiếm: ").strip().lower()
            results = [
                m for m in self.members
                if kw in m.member_id.lower() or kw in m.full_name.lower() or kw in m.phone_number
            ]
            self.view_members(results)
        elif choice == "2":
            print(" 1. Còn hạn hoạt động")
            print(" 2. Đã hết hạn")
            st = input("Lựa chọn (1/2): ").strip()
            if st == "1":
                results = [m for m in self.members if m.is_active()]
            else:
                results = [m for m in self.members if not m.is_active()]
            self.view_members(results)
        elif choice == "3":
            print(" 1. Basic Member")
            print(" 2. Premium Member")
            tc = input("Lựa chọn (1/2): ").strip()
            target_type = "Basic" if tc == "1" else "Premium"
            results = [m for m in self.members if m.get_member_type() == target_type]
            self.view_members(results)
        else:
            print("Lựa chọn không hợp lệ!")

    def sort_members(self):
        print("\n--- SẮP XẾP DANH SÁCH HỘI VIÊN ---")
        print(" 1. Sắp xếp theo Mã hội viên (A -> Z)")
        print(" 2. Sắp xếp theo Tên hội viên (A -> Z theo chữ cái tên)")
        print(" 3. Sắp xếp theo Ngày hết hạn (Sắp hết hạn trước)")
        print(" 4. Sắp xếp theo Ngày đăng ký (Mới nhất -> Cũ nhất)")
        choice = input("Lựa chọn tiêu chí (1-4): ").strip()

        if choice == "1":
            self.members.sort(key=lambda m: m.member_id)
            print("Đã sắp xếp theo Mã hội viên:")
            self.view_members()
        elif choice == "2":
            self.members.sort(key=lambda m: m.full_name.split()[-1].lower())
            print("Đã sắp xếp theo Tên hội viên:")
            self.view_members()
        elif choice == "3":
            self.members.sort(key=lambda m: m.expiry_date)
            print("Đã sắp xếp theo Ngày hết hạn:")
            self.view_members()
        elif choice == "4":
            self.members.sort(key=lambda m: m.join_date, reverse=True)
            print("Đã sắp xếp theo Ngày đăng ký:")
            self.view_members()
        else:
            print("Lựa chọn không hợp lệ!")
        self.save_data()

    def statistics_menu(self):
        print("\n======================= THỐNG KÊ & BÁO CÁO DOANH THU =======================")
        total_revenue = sum(tx.amount for tx in self.transactions)
        basic_count = sum(1 for m in self.members if m.get_member_type() == "Basic")
        premium_count = sum(1 for m in self.members if m.get_member_type() == "Premium")
        active_count = sum(1 for m in self.members if m.is_active())
        expired_count = len(self.members) - active_count

        print(f"Tổng số hội viên hiện tại: {len(self.members)}")
        print(f" - Basic Member: {basic_count} | Premium Member: {premium_count}")
        print(f" - Đang còn hạn: {active_count} | Đã hết hạn: {expired_count}")
        print(f"Tổng số lượt check-in phòng gym: {len(self.workout_sessions)} lượt")
        print(f"Tổng số giao dịch đã thực hiện: {len(self.transactions)} giao dịch")
        print("----------------------------------------------------------------------------")
        print(f"👉 TỔNG DOANH THU THỰC TẾ (QUA CÁC GIAO DỊCH): {total_revenue:,.0f} VNĐ")
        print("============================================================================")

        show_tx = input("Bạn có muốn xem danh sách chi tiết các giao dịch không? (y/n): ").strip().lower()
        if show_tx == "y":
            print("\n--- CHI TIẾT CÁC GIAO DỊCH THU PHÍ ---")
            for tx in self.transactions:
                tx.display_info()


def main():
    manager = GymManager()
    while True:
        print("\n==================================================")
        print("       HỆ THỐNG QUẢN LÝ PHÒNG GYM CHUYÊN NGHIỆP   ")
        print("==================================================")
        print(" 1. Xem danh sách hội viên")
        print(" 2. Thêm hội viên mới (Basic / Premium)")
        print(" 3. Cập nhật thông tin hội viên")
        print(" 4. Xóa hội viên")
        print(" 5. Gia hạn gói tập (Gia hạn đúng quy ước)")
        print(" 6. Ghi nhận lượt tập (Check-in) & Lịch sử")
        print(" 7. Tìm kiếm hội viên (Đa tiêu chí)")
        print(" 8. Sắp xếp danh sách hội viên")
        print(" 9. Thống kê & Báo cáo doanh thu")
        print("10. Lưu dữ liệu thủ công ra file JSON")
        print(" 0. Thoát chương trình (Tự động lưu dữ liệu)")
        print("--------------------------------------------------")
        choice = input("Nhập lựa chọn của bạn (0-10): ").strip()

        if choice == "0":
            manager.save_data()
            print("Dữ liệu đã được lưu an toàn. Hẹn gặp lại bạn!")
            break

        # Bắt lỗi để nhập sai (vd: để trống SĐT) không làm chương trình bị văng
        try:
            if choice == "1":
                manager.view_members()
            elif choice == "2":
                manager.add_member()
            elif choice == "3":
                manager.update_member()
            elif choice == "4":
                manager.delete_member()
            elif choice == "5":
                manager.renew_membership()
            elif choice == "6":
                print("\n 1. Ghi nhận lượt tập (Check-in)")
                print(" 2. Xem lịch sử các lượt tập")
                c = input("Chọn (1/2): ").strip()
                if c == "1":
                    manager.record_checkin()
                elif c == "2":
                    manager.view_checkin_history()
                else:
                    print("Lựa chọn không hợp lệ.")
            elif choice == "7":
                manager.search_members()
            elif choice == "8":
                manager.sort_members()
            elif choice == "9":
                manager.statistics_menu()
            elif choice == "10":
                manager.save_data()
            else:
                print("Lựa chọn không hợp lệ, vui lòng chọn từ 0 đến 10.")
        except ValueError as err:
            print(f"Dữ liệu không hợp lệ: {err}")
        except Exception as err:  # noqa: BLE001
            print(f"Có lỗi xảy ra: {err}")


if __name__ == "__main__":
    try:
        main()
    except (KeyboardInterrupt, EOFError):
        print("\n\nChương trình đã được dừng bởi người dùng. Hẹn gặp lại!")

import csv
from datetime import datetime

from gym_management import GymManager


def nhap_so(thong_bao, nho_nhat, lon_nhat):
    """Bắt buộc nhập số nguyên trong khoảng cho phép (chặn chữ, để trống)."""
    while True:
        s = input(thong_bao).strip()
        try:
            so = int(s)
        except ValueError:
            print("Vui lòng nhập SỐ, không nhập chữ hoặc để trống!")
            continue
        if so < nho_nhat or so > lon_nhat:
            print("Chỉ được nhập từ", nho_nhat, "đến", lon_nhat)
            continue
        return so


def in_menu():
    print("\n==================================================")
    print("       HỆ THỐNG QUẢN LÝ PHÒNG GYM CHUYÊN NGHIỆP   ")
    print("==================================================")
    print(" 1. Xem danh sách hội viên")
    print(" 2. Thêm hội viên mới (Basic / Premium)")
    print(" 3. Cập nhật thông tin hội viên")
    print(" 4. Xóa hội viên")
    print(" 5. Gia hạn gói tập")
    print(" 6. Ghi nhận lượt tập (Check-in) & Lịch sử")
    print(" 7. Tìm kiếm hội viên (Đa tiêu chí)")
    print(" 8. Sắp xếp danh sách hội viên")
    print(" 9. Thống kê & Báo cáo doanh thu")
    print("10. Lưu dữ liệu thủ công ra file JSON")
    print("11. Phân công / đổi huấn luyện viên")
    print("12. Cảnh báo hội viên sắp hết hạn")
    print("13. Xuất báo cáo ra file CSV")
    print(" 0. Thoát chương trình (Tự động lưu dữ liệu)")
    print("--------------------------------------------------")


def menu_checkin(manager):
    """Chức năng 6 có menu con: check-in hoặc xem lịch sử."""
    print("\n 1. Ghi nhận lượt tập (Check-in)")
    print(" 2. Xem lịch sử các lượt tập")
    chon = nhap_so("Chọn (1/2): ", 1, 2)
    if chon == 1:
        manager.record_checkin()
    else:
        manager.view_checkin_history()


def tim_hoi_vien(manager, ma):
    """Tìm hội viên theo mã, không tìm thấy trả về None."""
    for m in manager.members:
        if m.member_id.lower() == ma.lower():
            return m
    return None


def phan_cong_hlv(manager):
    """Mục 11: phân công / đổi huấn luyện viên cho hội viên."""
    print("\n--- PHÂN CÔNG / ĐỔI HUẤN LUYỆN VIÊN ---")
    ma = input("Nhập mã hội viên: ").strip()
    member = tim_hoi_vien(manager, ma)
    if member is None:
        print("Không tìm thấy hội viên", ma)
        return
    print("0    | Tự tập (không thuê HLV)")
    for t in manager.trainers:
        t.display_info()
    ma_hlv = input("Chọn mã HLV mới (0 nếu tự tập): ").strip()
    if ma_hlv == "0":
        member.trainer = None
        print("Đã chuyển hội viên về hình thức tự tập.")
    else:
        hlv = None
        for t in manager.trainers:
            if t.trainer_id.lower() == ma_hlv.lower():
                hlv = t
        if hlv is None:
            print("Mã HLV không tồn tại, giữ nguyên HLV cũ.")
            return
        member.trainer = hlv
        print("Đã phân công HLV", hlv.full_name, "cho", member.full_name)
    manager.save_data()


def canh_bao_het_han(manager):
    """Mục 12: liệt kê hội viên còn hạn nhưng sắp hết hạn trong N ngày tới."""
    print("\n--- CẢNH BÁO HỘI VIÊN SẮP HẾT HẠN ---")
    n = nhap_so("Nhập số ngày N: ", 1, 365)
    hom_nay = datetime.now().date()
    ds = []
    for m in manager.members:
        con_lai = (m.expiry_date.date() - hom_nay).days
        if 0 <= con_lai <= n:
            ds.append((m, con_lai))
    if len(ds) == 0:
        print("Không có hội viên nào hết hạn trong", n, "ngày tới.")
        return
    print("Có", len(ds), "hội viên sắp hết hạn trong", n, "ngày tới:")
    for m, con_lai in ds:
        print(" -", m.member_id, "|", m.full_name, "| hết hạn", m.expiry_date.strftime("%d/%m/%Y"),
              "| còn", con_lai, "ngày")


def xuat_csv(manager):
    """Mục 13: xuất danh sách hội viên và thống kê ra bao_cao_hoi_vien.csv."""
    ten_file = "bao_cao_hoi_vien.csv"
    with open(ten_file, "w", newline="", encoding="utf-8-sig") as f:
        w = csv.writer(f)
        w.writerow(["Mã HV", "Họ tên", "SĐT", "Loại", "Gói", "HLV", "Ngày hết hạn", "Trạng thái", "Học phí"])
        for m in manager.members:
            w.writerow([
                m.member_id, m.full_name, m.phone_number, m.get_member_type(), m.plan.plan_name,
                m.trainer.full_name if m.trainer else "Tự tập",
                m.expiry_date.strftime("%d/%m/%Y"),
                "Còn hạn" if m.is_active() else "Hết hạn",
                round(m.calculate_membership_fee()),
            ])
        w.writerow([])
        w.writerow(["Tổng số hội viên", len(manager.members)])
        w.writerow(["Số hội viên còn hạn", sum(1 for m in manager.members if m.is_active())])
        w.writerow(["Tổng doanh thu", round(sum(tx.amount for tx in manager.transactions))])
    print("Đã xuất báo cáo ra file", ten_file)


def main():
    manager = GymManager()          # tự động nạp dữ liệu từ gym_data.json

    while True:
        in_menu()
        chon = nhap_so("Nhập lựa chọn của bạn (0-13): ", 0, 13)

        if chon == 0:
            manager.save_data()
            print("Dữ liệu đã được lưu an toàn. Hẹn gặp lại bạn!")
            break

        # try-except để lỗi bất ngờ không làm chương trình bị văng
        try:
            if chon == 1:
                manager.view_members()
            elif chon == 2:
                manager.add_member()
            elif chon == 3:
                manager.update_member()
            elif chon == 4:
                manager.delete_member()
            elif chon == 5:
                manager.renew_membership()
            elif chon == 6:
                menu_checkin(manager)
            elif chon == 7:
                manager.search_members()
            elif chon == 8:
                manager.sort_members()
            elif chon == 9:
                manager.statistics_menu()
            elif chon == 10:
                manager.save_data()
            elif chon == 11:
                phan_cong_hlv(manager)
            elif chon == 12:
                canh_bao_het_han(manager)
            elif chon == 13:
                xuat_csv(manager)
        except Exception as loi:
            print("Có lỗi xảy ra:", loi)


if __name__ == "__main__":
    main()
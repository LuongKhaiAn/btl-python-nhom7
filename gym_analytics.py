"""
Tên module: gym_analytics.py
Người thực hiện: Dương Thành Văn
Chủ đề 07: Quản lý hội viên phòng tập (Python OOP).

Phạm vi theo bảng phân công giai đoạn III:
1. Tìm kiếm hội viên, bổ sung bộ lọc theo mã gói tập (plan_id).
2. Sắp xếp tăng/giảm dần, bổ sung tiêu chí phí hội viên.
3. Thống kê tỷ lệ tham gia tập của hội viên còn hạn.

Module này không định nghĩa lại các lớp thực thể và không xử lý CRUD/JSON.
Được thiết kế để sử dụng với GymManager và các lớp OOP của nhóm.
"""

from datetime import date, datetime


def _nhap_lua_chon(thong_bao, cac_gia_tri_hop_le):
    """Yêu cầu nhập lại nếu lựa chọn không thuộc danh sách cho phép."""
    while True:
        lua_chon = input(thong_bao).strip()
        if lua_chon in cac_gia_tri_hop_le:
            return lua_chon
        print("Lựa chọn không hợp lệ. Vui lòng nhập lại!")


def _ma_goi(member):
    """Lấy plan_id từ đối tượng gói tập của hội viên."""
    plan = getattr(member, "plan", None)
    if isinstance(plan, dict):
        return str(plan.get("plan_id", ""))
    if plan is not None:
        return str(getattr(plan, "plan_id", ""))
    return str(getattr(member, "plan_id", ""))


def _con_han(member):
    """Xác định trạng thái hội viên để thống kê và tìm kiếm."""
    if callable(getattr(member, "is_active", None)):
        return bool(member.is_active())
    ngay_het_han = _ngay_sap_xep(getattr(member, "expiry_date", None))
    return ngay_het_han >= date.today()


def _ngay_sap_xep(gia_tri):
    """Chuẩn hóa ngày khi thuộc tính là datetime, date hoặc chuỗi."""
    if isinstance(gia_tri, datetime):
        return gia_tri.date()
    if isinstance(gia_tri, date):
        return gia_tri
    if isinstance(gia_tri, str):
        for dinh_dang in ("%d/%m/%Y", "%Y-%m-%d"):
            try:
                return datetime.strptime(gia_tri, dinh_dang).date()
            except ValueError:
                pass
    return date.min


def _loai_hoi_vien(member):
    """Trả về Basic/Premium để lọc và thống kê."""
    if callable(getattr(member, "get_member_type", None)):
        return str(member.get_member_type()).casefold()
    return type(member).__name__.replace("Member", "").casefold()


def _hien_thi_danh_sach(manager, danh_sach):
    """Dùng lại phương thức hiển thị sẵn có của GymManager."""
    if callable(getattr(manager, "view_members", None)):
        manager.view_members(danh_sach)
        return
    if not danh_sach:
        print("Không có hội viên phù hợp.")
        return
    for member in danh_sach:
        if callable(getattr(member, "display_info", None)):
            member.display_info()
        else:
            print(getattr(member, "member_id", "?"), getattr(member, "full_name", ""))
    print(f"Tổng số: {len(danh_sach)} hội viên.")


def _lay_luot_tap(manager):
    """Danh sách lượt tập (WorkoutSession) của hệ thống."""
    return getattr(manager, "workout_sessions", [])


def _lay_giao_dich(manager):
    """Đọc giao dịch thực thu; không suy diễn doanh thu từ phí hội viên hiện tại."""
    return getattr(manager, "transactions", [])


def _gia_tri(record, ten_truong, mac_dinh=None):
    """Cho phép danh sách lưu đối tượng OOP hoặc dict theo thiết kế của nhóm."""
    if isinstance(record, dict):
        return record.get(ten_truong, mac_dinh)
    return getattr(record, ten_truong, mac_dinh)


class GymAnalyticsMixin:
    """Ba hàm phân tích (tìm kiếm, sắp xếp, thống kê); GymManager kế thừa mixin này."""

    def search_members(self):
        """Tìm kiếm theo mã/tên/SĐT, trạng thái, loại hội viên hoặc plan_id."""
        print("\n============ TÌM KIẾM HỘI VIÊN ============")
        print("1. Tìm theo mã, tên hoặc số điện thoại")
        print("2. Lọc theo trạng thái còn hạn / hết hạn")
        print("3. Lọc theo loại hội viên Basic / Premium")
        print("4. Lọc theo mã gói tập (plan_id)")
        lua_chon = _nhap_lua_chon("Chọn tiêu chí (1-4): ", {"1", "2", "3", "4"})

        if lua_chon == "1":
            tu_khoa = input("Nhập mã / tên / số điện thoại: ").strip().casefold()
            if not tu_khoa:
                print("Từ khóa tìm kiếm không được để trống!")
                return []
            # Mã: khớp CHÍNH XÁC (HV1 không ra HV10); tên và SĐT: khớp gần đúng (chuỗi con)
            ket_qua = [
                m for m in self.members
                if tu_khoa == str(getattr(m, "member_id", "")).casefold()
                or tu_khoa in str(getattr(m, "full_name", "")).casefold()
                or tu_khoa in str(getattr(m, "phone_number", "")).casefold()
            ]
        elif lua_chon == "2":
            print("1. Còn hạn")
            print("2. Hết hạn")
            trang_thai = _nhap_lua_chon("Chọn trạng thái (1-2): ", {"1", "2"})
            ket_qua = [m for m in self.members if _con_han(m) == (trang_thai == "1")]
        elif lua_chon == "3":
            print("1. Basic Member")
            print("2. Premium Member")
            loai = _nhap_lua_chon("Chọn loại hội viên (1-2): ", {"1", "2"})
            ket_qua = [m for m in self.members if _loai_hoi_vien(m) == ("basic" if loai == "1" else "premium")]
        else:
            print("\nCác gói tập đang có:")
            for plan in getattr(self, "plans", []):
                print(f"- {getattr(plan, 'plan_id', '')}: {getattr(plan, 'plan_name', '')}")
            ma_goi = input("Nhập mã gói muốn lọc (ví dụ P03): ").strip().casefold()
            if not ma_goi:
                print("Mã gói tập không được để trống!")
                return []
            # So sánh mã chính xác, không nhầm P01 và P010.
            ket_qua = [m for m in self.members if _ma_goi(m).casefold() == ma_goi]

        print(f"\nTìm được {len(ket_qua)} hội viên phù hợp.")
        _hien_thi_danh_sach(self, ket_qua)
        return ket_qua

    def sort_members(self):
        """Sắp xếp theo 5 tiêu chí; tất cả đều hỗ trợ tăng và giảm dần."""
        print("\n============ SẮP XẾP HỘI VIÊN ============")
        if not self.members:
            print("Danh sách hội viên đang trống, không có gì để sắp xếp.")
            return []
        print("1. Mã hội viên")
        print("2. Tên hội viên")
        print("3. Ngày hết hạn")
        print("4. Ngày tham gia")
        print("5. Phí hội viên (calculate_membership_fee)")
        tieu_chi = _nhap_lua_chon("Chọn tiêu chí (1-5): ", {"1", "2", "3", "4", "5"})

        print("1. Tăng dần (A-Z / thấp đến cao / sớm đến muộn)")
        print("2. Giảm dần (Z-A / cao đến thấp / muộn đến sớm)")
        chieu = _nhap_lua_chon("Chọn chiều sắp xếp (1-2): ", {"1", "2"})
        giam_dan = (chieu == "2")

        if tieu_chi == "1":
            khoa = lambda m: str(getattr(m, "member_id", "")).casefold()
        elif tieu_chi == "2":
            # Sắp theo từ cuối cùng của họ tên; nếu trùng tên sẽ xét cả họ tên.
            khoa = lambda m: (
                str(getattr(m, "full_name", "")).split()[-1].casefold()
                if str(getattr(m, "full_name", "")).split() else "",
                str(getattr(m, "full_name", "")).casefold()
            )
        elif tieu_chi == "3":
            khoa = lambda m: _ngay_sap_xep(getattr(m, "expiry_date", None))
        elif tieu_chi == "4":
            khoa = lambda m: _ngay_sap_xep(getattr(m, "join_date", None))
        else:
            # Đây là phí theo tính đa hình của BasicMember/PremiumMember.
            khoa = lambda m: float(m.calculate_membership_fee())

        # Sắp xếp trên bản sao để HIỂN THỊ; không đổi thứ tự dữ liệu gốc, không ghi lại file
        ket_qua = sorted(self.members, key=khoa, reverse=giam_dan)
        print("\nĐã sắp xếp " + ("giảm dần" if giam_dan else "tăng dần") + ".")
        _hien_thi_danh_sach(self, ket_qua)
        return ket_qua

    def statistics_menu(self):
        """Thống kê hội viên, doanh thu thực thu và tỷ lệ tham gia tập.

        Tỷ lệ tham gia tập = (Số hội viên CÒN HẠN có >= 1 lượt tập /
                              Tổng số hội viên CÒN HẠN) * 100%.
        Mỗi hội viên chỉ được tính một lần, dù có nhiều lượt check-in.
        Nếu chưa có hội viên còn hạn, tỷ lệ được quy ước bằng 0%.
        """
        print("\n============ THỐNG KÊ & BÁO CÁO ============")
        hoi_vien_con_han = [m for m in self.members if _con_han(m)]
        so_con_han = len(hoi_vien_con_han)
        so_het_han = len(self.members) - so_con_han

        # Tập mã HV có ít nhất một lần check-in; loại bỏ lượt tập bị trùng.
        ma_da_tap = {
            str(_gia_tri(record, "member_id", "")).strip().casefold()
            for record in _lay_luot_tap(self)
            if _gia_tri(record, "member_id") is not None
        }
        so_con_han_da_tap = sum(
            1 for m in hoi_vien_con_han
            if str(getattr(m, "member_id", "")).strip().casefold() in ma_da_tap
        )
        ti_le_tham_gia = so_con_han_da_tap / so_con_han * 100 if so_con_han else 0.0

        giao_dich = _lay_giao_dich(self)
        # Chỉ cộng số tiền giao dịch đã ghi nhận, không cộng giá gói từ hội viên.
        doanh_thu = sum(float(_gia_tri(gd, "amount", 0) or 0) for gd in giao_dich)
        so_basic = sum(1 for m in self.members if _loai_hoi_vien(m) == "basic")
        so_premium = sum(1 for m in self.members if _loai_hoi_vien(m) == "premium")

        print(f"Tổng số hội viên: {len(self.members)}")
        print(f"- Basic: {so_basic} | Premium: {so_premium}")
        print(f"- Còn hạn: {so_con_han} | Hết hạn: {so_het_han}")
        print(f"- Tổng lượt tập: {len(_lay_luot_tap(self))}")
        print(f"- Số hội viên còn hạn đã tham gia tập: {so_con_han_da_tap}/{so_con_han}")
        print(f"TỶ LỆ THAM GIA TẬP: {ti_le_tham_gia:.2f}%")
        print(f"Số giao dịch đã ghi nhận: {len(giao_dich)}")
        print(f"DOANH THU THỰC THU: {doanh_thu:,.0f} VNĐ")

        if giao_dich and input("Bạn có muốn xem chi tiết giao dịch? (y/n): ").strip().lower() == "y":
            print("\n--- DANH SÁCH GIAO DỊCH ---")
            for gd in giao_dich:
                if callable(getattr(gd, "display_info", None)):
                    gd.display_info()
                else:
                    print(f"Mã HV: {_gia_tri(gd, 'member_id', '?')} | Số tiền: {_gia_tri(gd, 'amount', 0)}")

        # Trả kết quả dạng dict phục vụ kiểm thử và tích hợp báo cáo CSV.
        return {
            "total_members": len(self.members),
            "active_members": so_con_han,
            "expired_members": so_het_han,
            "active_members_attended": so_con_han_da_tap,
            "attendance_rate": ti_le_tham_gia,
            "total_checkins": len(_lay_luot_tap(self)),
            "total_revenue": doanh_thu,
            "total_transactions": len(giao_dich),
        }

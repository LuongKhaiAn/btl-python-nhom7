
# main.py - Giao diện Menu Console
# Chủ đề 07: Quản lý hội viên phòng tập
# Người thực hiện: Thành - Người review: Lương

import data_handler   # lưu/đọc JSON, xuất CSV
import gym_crud       # thêm, sửa, xóa, phân công HLV, cảnh báo hết hạn
import gym_analytics  # tìm kiếm, sắp xếp, thống kê


# Hàm nhập liệu an toàn

def nhap_chuoi(thong_bao):
    """Bắt buộc nhập chuỗi không rỗng."""
    while True:
        s = input(thong_bao).strip()
        if s != "":
            return s
        print("Không được để trống, nhập lại!")


def nhap_so(thong_bao, nho_nhat, lon_nhat):
    """Bắt buộc nhập số nguyên trong khoảng cho phép."""
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


# Các chức năng menu mới

def phan_cong_hlv(data):
    ma_hv = nhap_chuoi("Nhập mã hội viên: ")
    ma_hlv = nhap_chuoi("Nhập mã huấn luyện viên: ")
    gym_crud.assign_trainer(data, ma_hv, ma_hlv)


def canh_bao_het_han(data):
    n = nhap_so("Cảnh báo hội viên hết hạn trong bao nhiêu ngày tới? ", 1, 365)
    gym_crud.warn_expiring_members(data, n)


def xuat_csv(data):
    data_handler.export_report_csv(data, "bao_cao_hoi_vien.csv")
    print("Đã xuất file bao_cao_hoi_vien.csv")


# Menu

def in_menu():
    print("\n===== QUẢN LÝ HỘI VIÊN PHÒNG TẬP =====")
    print("1. Xem danh sách hội viên")
    print("2. Thêm hội viên")
    print("3. Cập nhật hội viên")
    print("4. Xóa hội viên")
    print("5. Tìm kiếm hội viên")
    print("6. Sắp xếp hội viên")
    print("7. Thống kê")
    print("8. Phân công / đổi huấn luyện viên")
    print("9. Cảnh báo hội viên sắp hết hạn")
    print("10. Xuất báo cáo CSV")
    print("0. Lưu và thoát")


def main():
    # Đọc dữ liệu; nếu chưa có file thì dùng dữ liệu mẫu
    try:
        data = data_handler.load_data()
    except Exception:
        data = data_handler.init_default_data()

    while True:
        in_menu()
        chon = nhap_so("Chọn chức năng: ", 0, 10)

        if chon == 0:
            data_handler.save_data(data)
            print("Đã lưu dữ liệu. Tạm biệt!")
            break

        # try-except để nhập sai hoặc lỗi bất ngờ không làm chương trình bị văng
        try:
            if chon == 1:
                gym_crud.display_members(data)
            elif chon == 2:
                gym_crud.add_member(data)
            elif chon == 3:
                gym_crud.update_member(data)
            elif chon == 4:
                gym_crud.delete_member(data)
            elif chon == 5:
                gym_analytics.search_members(data)
            elif chon == 6:
                gym_analytics.sort_members(data)
            elif chon == 7:
                gym_analytics.statistics_menu(data)
            elif chon == 8:
                phan_cong_hlv(data)
            elif chon == 9:
                canh_bao_het_han(data)
            elif chon == 10:
                xuat_csv(data)
        except Exception as loi:
            print("Có lỗi xảy ra:", loi)

        # Tự động lưu sau mỗi lần thao tác
        data_handler.save_data(data)


main()
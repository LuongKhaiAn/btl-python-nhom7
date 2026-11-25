# HỆ THỐNG QUẢN LÝ HỘI VIÊN PHÒNG GYM (CHỦ ĐỀ 07)
> **Dự án Bài tập lớn Lập trình Python (OOP)**  
> Khoa Công nghệ Thông tin | Hệ thống Quản lý Phòng Gym chuyên nghiệp

---

## 1. Giới thiệu tổng quan
Hệ thống Quản lý Hội viên Phòng Gym là ứng dụng Console được xây dựng bằng ngôn ngữ **Python**, áp dụng chuẩn mực 4 nguyên lý lập trình hướng đối tượng (**Trừu tượng**, **Đóng gói**, **Kế thừa**, **Đa hình**). Hệ thống giúp tự động hóa toàn bộ quy trình vận hành phòng gym: quản lý hội viên thường/VIP, phân công huấn luyện viên, gia hạn gói tập, điểm danh lượt tập, theo dõi giao dịch và thống kê doanh thu.

---

## 2. Cấu trúc thư mục dự án

```text
btl-python-nhom7/
│
├── data/                               # Thư mục lưu trữ dữ liệu
│   └── gym_data.json                   # Dữ liệu hội viên, gói tập, HLV, lượt tập, giao dịch
│
├── docs/                               # Thư mục tài liệu thiết kế & báo cáo
│   ├── Nhom_7_Bao_cao.docx             # Báo cáo tổng kết bài tập lớn (Word)
│   ├── Nhom_7_Slides.pptx              # Slide thuyết trình PowerPoint
│   ├── Bang_Phan_Cong_Lap_Trinh_Chu_De_07.xlsx    # Bảng phân công chi tiết công việc
│   ├── Bang_Kich_Ban_Kiem_Thu_Chu_De_07_v2.xlsx   # Bảng kịch bản kiểm thử (14 test case)
│   └── UML.drawio                      # Sơ đồ lớp UML Class Diagram, Activity & DFD
│
├── tests/                              # Thư mục kiểm thử tự động (Unit Tests)
│   ├── __init__.py
│   └── test_gym_management.py          # 40 test cases kiểm tra OOP, nghiệp vụ, ngoại lệ & lưu trữ
│
├── models.py                           # [Module 1] Các lớp thực thể OOP (Encapsulation, Polymorphism)
├── gym_management.py                   # [Module của An] GymManager: thêm/sửa/gia hạn/check-in/lưu JSON
├── long_crud.py                        # [Module của Long] LongGymManager: xóa an toàn, phân công HLV, thêm gói/HLV, cảnh báo hết hạn
├── gym_analytics.py                    # [Module của Văn] GymAnalyticsMixin: tìm kiếm, sắp xếp, thống kê
├── data_handler.py                     # [Module Lương/Thành] Lưu-đọc JSON (ghi atomic), dữ liệu mẫu, xuất báo cáo CSV
├── gym_app.py                          # Chương trình tổng hợp: ghép các module trên thành menu 17 chức năng
├── main.py                             # Điểm khởi chạy chính (gọi gym_app.main)
│
├── .gitignore                          # Cấu hình bỏ qua file tạm, cache, file rác
├── README.md                           # Tài liệu hướng dẫn sử dụng & cấu trúc dự án
└── requirements.txt                    # Danh sách phụ thuộc môi trường Python
```

> `bao_cao_hoi_vien.csv` được tạo ở thư mục gốc khi chọn chức năng 16; file `*.bak` là bản sao lưu tự tạo nếu `gym_data.json` bị hỏng.

---

## 3. Kiến trúc Hướng đối tượng (OOP Architecture)

Dự án áp dụng chặt chẽ 4 nguyên lý OOP:
1. **Trừu tượng (Abstraction)**: Lớp trừu tượng `Member` kế thừa từ `abc.ABC` với các phương thức trừu tượng `@abstractmethod`:
   - `calculate_membership_fee()`
   - `get_member_type()`
2. **Kế thừa (Inheritance)**:
   - `BasicMember` (Hội viên thường): Kế thừa `Member`, bổ sung tỷ lệ giảm giá `discount_rate`.
   - `PremiumMember` (Hội viên VIP): Kế thừa `Member`, bổ sung phí đặc quyền `vip_perks_fee`, quyền xông hơi `sauna_access`, và ưu đãi HLV `trainer_discount_rate`.
3. **Đóng gói (Encapsulation)**:
   - Các thuộc tính được bảo vệ với tiền tố `_` (`_member_id`, `_price`, `_expiry_date`,...).
   - Truy xuất và biến đổi thông qua `@property` getter và setter có kiểm tra tính hợp lệ chặt chẽ (chặn chuỗi rỗng, số âm, tỷ lệ ngoài khoảng $[0, 1]$).
4. **Đa hình (Polymorphism)**:
   - Ghi đè phương thức `calculate_membership_fee()` theo từng chính sách giá của loại hội viên.
   - Thống nhất phương thức `__str__()` hiển thị thông tin bảng trực quan cho cả 7 thực thể: `MembershipPlan`, `Trainer`, `Member`, `BasicMember`, `PremiumMember`, `WorkoutSession`, `Transaction`.

---

## 4. Hướng dẫn cài đặt và Chạy chương trình

### Yêu cầu hệ thống:
- **Python**: Phiên bản 3.8 trở lên.
- Không yêu cầu cài đặt thư viện bên ngoài (sử dụng thư viện chuẩn `datetime`, `json`, `os`, `abc`, `unittest`).

### Chạy ứng dụng Console:
```bash
python3 main.py
```
*(hoặc `python main.py` tùy theo môi trường hệ điều hành; có thể chạy từ bất kỳ thư mục nào, dữ liệu luôn được lưu tại `data/gym_data.json` của dự án)*

`main.py` chạy bản đầy đủ 17 chức năng.
Đặt biến môi trường `GYM_DEBUG=1` để hiện chi tiết lỗi (traceback) khi gỡ lỗi.

### Chạy kiểm thử tự động (Unit Tests):
Chạy toàn bộ 40 test cases tự động:
```bash
python3 -m unittest discover tests -v
```
hoặc:
```bash
python3 tests/test_gym_management.py
```

---

## 5. Danh sách chức năng chính (Menu Console — 17 chức năng)
| # | Chức năng | Ghi chú nghiệp vụ |
|---|---|---|
| 1 | Xem danh sách hội viên | Bảng loại thẻ, gói, HLV, hạn dùng, học phí; xử lý danh sách rỗng |
| 2 | Thêm hội viên (Basic/Premium) | Kiểm tra mã trùng (kể cả mã đã từng dùng), SĐT 10 số, gói/HLV phải tồn tại; tự tạo giao dịch thu phí |
| 3 | Cập nhật thông tin | Sửa họ tên, SĐT (có kiểm tra), HLV |
| 4 | Xóa hội viên | Cảnh báo thẻ còn hạn / giao dịch / lượt tập liên quan, xác nhận trước khi xóa; lịch sử giữ lại để bảo toàn doanh thu |
| 5 | Phân công / đổi HLV | Mã HLV phải tồn tại; chọn 0 để chuyển sang tự tập |
| 6 | Gia hạn gói tập | Còn hạn: cộng dồn từ ngày hết hạn cũ; hết hạn: tính từ hôm nay; **cộng theo tháng lịch** (không phải 30 ngày/tháng) |
| 7 | Check-in | Chỉ hội viên còn hạn; check-in lần 2 trong cùng ngày phải xác nhận |
| 8 | Lịch sử lượt tập | |
| 9 | Tìm kiếm đa tiêu chí | Mã **khớp chính xác**; tên/SĐT khớp gần đúng; lọc theo trạng thái, loại, mã gói |
| 10 | Sắp xếp | 5 tiêu chí, tăng/giảm; chỉ sắp xếp để hiển thị, không đổi dữ liệu gốc |
| 11 | Thống kê & doanh thu | Doanh thu = tổng `Transaction`; tỷ lệ tham gia = HV còn hạn có ≥1 lượt tập / HV còn hạn (0% nếu không có HV còn hạn) |
| 12 | Cảnh báo sắp hết hạn | Theo số ngày người dùng nhập |
| 13 | Xem danh mục Gói tập & HLV | |
| 14 | Thêm Gói tập | Kiểm tra mã trùng, thời hạn ≥ 1, giá ≥ 0 |
| 15 | Thêm HLV | Kiểm tra mã trùng, SĐT, phí ≥ 0 |
| 16 | Xuất báo cáo CSV | `bao_cao_hoi_vien.csv` (UTF-8 BOM, mở được bằng Excel) |
| 17 | Lưu JSON thủ công | Ghi atomic qua file tạm; file hỏng được sao lưu `.bak`, không bị ghi đè |

## 6. Quy ước nghiệp vụ đã thống nhất
- **Tháng tập** = tháng lịch (01/01 + 12 tháng = 01/01 năm sau; 31/01 + 1 tháng = 28/29/02).
- **Học phí Basic** = giá gói × (1 − giảm giá) + phí HLV × số tháng.
- **Học phí Premium** = giá gói + phí VIP × số tháng + phí HLV × số tháng × (1 − ưu đãi HLV).
- **Mã dùng lại**: mã hội viên đã có lịch sử giao dịch/lượt tập không được tạo lại.

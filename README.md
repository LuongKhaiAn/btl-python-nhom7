# HỆ THỐNG QUẢN LÝ HỘI VIÊN PHÒNG GYM (CHỦ ĐỀ 07)
> **Dự án Bài tập lớn Lập trình Python (OOP)**  
> Khoa Công nghệ Thông tin | Hệ thống Quản lý Phòng Gym chuyên nghiệp

---

## 1. Giới thiệu tổng quan
Hệ thống Quản lý Hội viên Phòng Gym là ứng dụng Console được xây dựng bằng ngôn ngữ **Python**, áp dụng chuẩn mực 4 nguyên lý lập trình hướng đối tượng (**Trừu tượng**, **Đóng gói**, **Kế thừa**, **Đa hình**). Hệ thống giúp tự động hóa toàn bộ quy trình vận hành phòng gym: quản lý hội viên thường/VIP, phân công huấn luyện viên, gia hạn gói tập, điểm danh lượt tập, theo dõi giao dịch và thống kê doanh thu.

---

## 2. Cấu trúc thư mục dự án

```text
btl/
│
├── data/                               # Thư mục lưu trữ dữ liệu
│   └── gym_data.json                   # Dữ liệu hội viên, gói tập, HLV, lượt tập, giao dịch
│
├── docs/                               # Thư mục tài liệu thiết kế & báo cáo
│   ├── BAO_CAO_THIET_KE.md             # Báo cáo phân tích thiết kế hệ thống chi tiết
│   ├── Chu_de_07_Bao_cao_phan_tich_he_thong.docx # Báo cáo phân tích hệ thống (Word)
│   ├── Bang_Phan_Cong_Lap_Trinh_Chu_De_07 (3).xlsx # Bảng phân công chi tiết công việc
│   ├── SLIDE_OUTLINE.md                # Đề cương slide thuyết trình
│   └── UML.drawio                      # Sơ đồ lớp UML Class Diagram & Flowchart
│
├── tests/                              # Thư mục kiểm thử tự động (Unit Tests)
│   ├── __init__.py
│   └── test_gym_management.py          # 15 test cases kiểm tra OOP, nghiệp vụ & ngoại lệ
│
├── models.py                           # [Module 1] Các lớp thực thể OOP (Encapsulation, Polymorphism)
├── gym_management.py                   # [Module của An] GymManager: thêm/sửa/gia hạn/check-in/lưu JSON
├── long_crud.py                        # [Module của Long] LongGymManager: xóa an toàn, phân công HLV, thêm gói/HLV, cảnh báo hết hạn
├── gym_analytics.py                    # [Module của Văn] GymAnalyticsMixin: tìm kiếm, sắp xếp, thống kê
├── ok.py                               # [Module của Thành] data_handler: xuất báo cáo CSV (được gym_app nạp với tên data_handler)
├── gym_app.py                          # Chương trình tổng hợp: ghép các module trên thành menu 17 chức năng
├── main.py                             # Điểm khởi chạy chính (gọi gym_app.main)
│
├── .gitignore                          # Cấu hình bỏ qua file tạm, cache, file rác
├── README.md                           # Tài liệu hướng dẫn sử dụng & cấu trúc dự án
└── requirements.txt                    # Danh sách phụ thuộc môi trường Python
```

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

`main.py` chạy bản đầy đủ 17 chức năng. Nếu chỉ muốn chạy phần cơ bản của An (10 chức năng), dùng `python3 gym_management.py`.

### Chạy kiểm thử tự động (Unit Tests):
Chạy toàn bộ 15 test cases tự động:
```bash
python3 -m unittest discover tests -v
```
hoặc:
```bash
python3 tests/test_gym_management.py
```

---

## 5. Danh sách chức năng chính (Menu Console)
1. **Xem danh sách hội viên**: Hiển thị bảng tổng hợp chi tiết loại thẻ, gói tập, HLV, hạn dùng và học phí.
2. **Thêm hội viên mới**: Hỗ trợ thêm Hội viên Thường (Basic) hoặc Hội viên VIP (Premium), tự động tạo giao dịch thu phí.
3. **Cập nhật thông tin**: Sửa họ tên, số điện thoại, huấn luyện viên.
4. **Xóa hội viên**: Tìm theo mã, xác nhận xóa và kiểm tra an toàn dữ liệu.
5. **Gia hạn gói tập**: Tự động nhận diện thẻ còn hạn (cộng dồn ngày) hoặc hết hạn (tính từ ngày hiện tại).
6. **Quẹt thẻ Check-in & Lịch sử**: Chỉ cho phép hội viên còn hạn tập quẹt thẻ; lưu lại `WorkoutSession`.
7. **Tìm kiếm đa tiêu chí**: Khớp mã chính xác, tìm gần đúng theo tên, số điện thoại, lọc theo trạng thái/gói tập.
8. **Sắp xếp linh hoạt**: Theo mã, theo tên A-Z, theo ngày hết hạn hoặc ngày đăng ký.
9. **Thống kê & Doanh thu**: Báo cáo tổng số hội viên, tỷ lệ hoạt động, tổng doanh thu thực tế từ `Transaction`.
10. **Lưu trữ JSON**: Tự động đồng bộ và lưu dữ liệu an toàn vào `data/gym_data.json`.

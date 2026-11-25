# TÀI LIỆU BÁO CÁO THIẾT KẾ VÀ HỆ THỐNG (BẢN CẬP NHẬT HOÀN THIỆN)
## ĐỀ TÀI: QUẢN LÝ HỘI VIÊN PHÒNG GYM (BTL PYTHON)

---

### PHẦN 1: MỤC TIÊU VÀ PHẠM VI HỆ THỐNG
1. **Mục tiêu**: Xây dựng phần mềm quản lý phòng Gym chuyên nghiệp bằng Python, áp dụng các nguyên lý lập trình hướng đối tượng (OOP: Trừu tượng, Đóng gói, Kế thừa, Đa hình), quản lý lượt tập, giao dịch tài chính và lưu trữ dữ liệu bền vững (JSON Persistence).
2. **Các chức năng chính**:
   - Quản lý danh mục Gói tập (MembershipPlan) và Huấn luyện viên (Trainer).
   - Quản lý Hội viên với mô hình kế thừa đa hình: `Member` $\rightarrow$ `BasicMember` (Hội viên thường) và `PremiumMember` (Hội viên VIP).
   - CRUD Hội viên đầy đủ: Xem danh sách, Thêm mới, Sửa thông tin, Xóa hội viên.
   - **Gia hạn gói tập đúng quy ước**: Thẻ còn hạn $\rightarrow$ cộng theo tháng lịch; Thẻ hết hạn $\rightarrow$ tính từ ngày hiện tại; Tự động ghi nhận Transaction thu phí.
   - **Ghi nhận lượt tập (Check-in)**: Kiểm tra trạng thái thẻ (`check_expiry()` / `is_active()`). Chỉ cho phép hội viên còn hạn check-in và lưu lịch sử `WorkoutSession`.
   - **Tìm kiếm & Lọc đa tiêu chí**: Tìm theo từ khóa (Mã, Tên, SĐT), lọc theo trạng thái thẻ (Còn hạn / Hết hạn), lọc theo loại hội viên (Basic / Premium), lọc theo mã gói tập.
   - **Sắp xếp linh hoạt**: Theo Mã, Tên, Ngày hết hạn, Ngày tham gia, Phí hội viên (tăng/giảm).
   - **Báo cáo doanh thu & Thống kê toàn diện**: Doanh thu tính chính xác từ tổng số tiền của các giao dịch `Transaction` thực tế (Đăng ký mới + Gia hạn).
   - **Lưu trữ dữ liệu JSON**: Đọc/ghi tự động vào file `data/gym_data.json` (ghi atomic, tự sao lưu `.bak` nếu file hỏng).

---

### PHẦN 2: THIẾT KẾ SƠ ĐỒ LỚP (UML CLASS DIAGRAM)
*File thiết kế: `UML.drawio` (Tab 1: Class Diagram)*

#### 1. Lớp trừu tượng `Member`
- **Thuộc tính**:
  - `# memberId: String`: Mã hội viên (duy nhất).
  - `# fullName: String`: Họ tên.
  - `# phoneNumber: String`: Số điện thoại.
  - `# plan: MembershipPlan`: Gói tập đăng ký.
  - `# trainer: Trainer`: Huấn luyện viên hướng dẫn (nếu có).
  - `# joinDate: LocalDate`: Ngày đăng ký.
  - `# expiryDate: LocalDate`: Ngày hết hạn thẻ.
- **Phương thức**:
  - `+ check_expiry(): boolean`: Kiểm tra thẻ còn hạn tập hay đã hết hạn khớp đề bài.
  - `+ isActive(): boolean`: Kiểm tra thẻ còn hạn tập hay không (bí danh gọi `check_expiry()`).
  - `+ renew(plan: MembershipPlan)`: Gia hạn gói tập theo đúng quy ước cộng theo tháng lịch.
  - `+ calculateMembershipFee(): double*`: Phương thức trừu tượng tính học phí (**Đa hình - Polymorphism**).
  - `+ getMemberType(): String*`: Phương thức trừu tượng trả về loại hội viên.
  - `+ __str__(): String`: Định dạng chuỗi thông tin hội viên chuẩn OOP.
  - `+ displayInfo()`: Hiển thị thông tin hội viên.
  - `+ toDict(): dict`: Xuất dữ liệu để lưu JSON.

#### 2. Các lớp con kế thừa `Member`
- **`BasicMember`**:
  - Kế thừa `Member`.
  - Thuộc tính riêng: `- discountRate: double`.
  - Cài đặt `calculateMembershipFee()`: Phí gói cơ bản trừ chiết khấu + phí HLV (nếu có).
- **`PremiumMember`**:
  - Kế thừa `Member`.
  - Thuộc tính riêng: `- vipPerksFee: double`, `- saunaAccess: boolean`, `- trainerDiscountRate: double`.
  - Cài đặt `calculateMembershipFee()`: Phí gói + phụ phí dịch vụ VIP + phí HLV (được chiết khấu VIP 20%).

#### 3. Các thực thể phụ trợ
- **`MembershipPlan`** *(kèm bí danh `Plan` tương thích ngược)*: `planId`, `planName`, `durationMonths`, `price`.
- **`Trainer`**: `trainerId`, `fullName`, `specialty`, `phoneNumber`, `monthlyFee`.
- **`Transaction`**: Ghi nhận dòng tiền thu phí (`transactionId`, `memberId`, `amount`, `transactionType`, `planName`, `paymentDate`).
- **`WorkoutSession`**: Ghi nhận lượt tập (`sessionId`, `memberId`, `checkinTime`, `notes`).
- **`GymManager`**: Lớp điều khiển trung tâm quản lý toàn bộ các danh sách và file JSON.

---

### PHẦN 3: THIẾT KẾ LƯU ĐỒ HOẠT ĐỘNG & MENU (ACTIVITY DIAGRAM)
*File thiết kế: `UML.drawio` (Tab 2: Activity Diagram - Menu Flow)*

1. Khởi động chương trình $\rightarrow$ Tự động đọc dữ liệu từ `data/gym_data.json`.
2. Hiển thị Menu điều hướng chính (0 - 17).
3. Người dùng nhập lựa chọn:
   - `1 - 4`: Xem / Thêm / Sửa / Xóa hội viên $\rightarrow$ Thêm tự tính phí đa hình & tạo Transaction; Xóa cảnh báo dữ liệu liên quan $\rightarrow$ Lưu JSON.
   - `5`: Phân công / đổi Huấn luyện viên $\rightarrow$ Lưu JSON.
   - `6`: Gia hạn gói tập $\rightarrow$ Kiểm tra thẻ còn hạn hay hết hạn $\rightarrow$ Cập nhật hạn tập & tạo Transaction $\rightarrow$ Lưu JSON.
   - `7`: Check-in $\rightarrow$ Kiểm tra thẻ còn hạn? (Hết hạn $\rightarrow$ Cảnh báo; còn hạn $\rightarrow$ Lưu `WorkoutSession`) $\rightarrow$ Lưu JSON. `8`: Xem lịch sử lượt tập.
   - `9`: Tìm kiếm & lọc (mã chính xác, tên/SĐT gần đúng, còn hạn/hết hạn, Basic/Premium, mã gói).
   - `10`: Sắp xếp (Mã, Tên, Ngày hết hạn, Ngày tham gia, Phí hội viên; tăng/giảm).
   - `11`: Thống kê & báo cáo doanh thu. `12`: Cảnh báo hội viên sắp hết hạn.
   - `13 - 15`: Xem danh mục Gói tập & HLV; Thêm Gói tập; Thêm HLV.
   - `16`: Xuất báo cáo CSV. `17`: Lưu JSON thủ công.
   - `0`: Lưu dữ liệu an toàn và Thoát chương trình.

---

### PHẦN 4: KẾT QUẢ KIỂM THỬ (40 TEST CASES)
*Chạy tự động bằng lệnh: `python3 -m unittest discover tests -v`* — kết quả: **40/40 PASS**.

| Nhóm | Số TC | Nội dung kiểm thử chính | Trạng thái |
| :--- | :---: | :--- | :---: |
| Đóng gói (Encapsulation) | 5 | Từ chối giá/phí/số tiền âm, tên rỗng, tỷ lệ giảm giá ngoài [0,1] | **PASS** |
| Trừu tượng & Đa hình | 4 | `Member` không khởi tạo được; tính phí Basic/Premium; `__str__` | **PASS** |
| Nghiệp vụ hạn thẻ | 3 | `check_expiry`, gia hạn còn hạn (cộng dồn), gia hạn hết hạn (từ hôm nay) | **PASS** |
| Tháng lịch | 3 | 01/01 + 12 tháng, 31/01 + 1 tháng (năm thường/nhuận), hạn mặc định theo gói | **PASS** |
| Tiện ích | 2 | Kiểm tra SĐT; sinh mã giao dịch/lượt tập không trùng | **PASS** |
| Thêm/Sửa/Xóa | 5 | Thêm tạo giao dịch & lưu JSON; từ chối SĐT sai, mã trùng, HLV không tồn tại; không dùng lại mã đã xóa; hủy xóa | **PASS** |
| Gia hạn/Check-in/HLV/Gói | 6 | Giao dịch gia hạn; chặn check-in hết hạn; check-in lặp cùng ngày; phân công HLV; thêm gói/HLV; cảnh báo sắp hết hạn | **PASS** |
| Tìm kiếm/Sắp xếp/Thống kê | 6 | Mã chính xác vs tên gần đúng; lọc mã gói; sắp xếp không đổi dữ liệu gốc; danh sách rỗng; tỷ lệ tham gia & doanh thu; 0% khi không có HV còn hạn | **PASS** |
| Lưu trữ | 6 | Roundtrip dict; lưu/nạp; đường dẫn độc lập thư mục chạy; JSON hỏng được sao lưu; nạp file dữ liệu của nhóm; xuất CSV | **PASS** |

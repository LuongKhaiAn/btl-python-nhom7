# TÀI LIỆU BÁO CÁO THIẾT KẾ VÀ HỆ THỐNG (BẢN CẬP NHẬT HOÀN THIỆN)
## ĐỀ TÀI: QUẢN LÝ HỘI VIÊN PHÒNG GYM (BTL PYTHON)

---

### PHẦN 1: MỤC TIÊU VÀ PHẠM VI HỆ THỐNG
1. **Mục tiêu**: Xây dựng phần mềm quản lý phòng Gym chuyên nghiệp bằng Python, áp dụng các nguyên lý lập trình hướng đối tượng (OOP: Trừu tượng, Đóng gói, Kế thừa, Đa hình), quản lý lượt tập, giao dịch tài chính và lưu trữ dữ liệu bền vững (JSON Persistence).
2. **Các chức năng chính**:
   - Quản lý danh mục Gói tập (Plan) và Huấn luyện viên (Trainer).
   - Quản lý Hội viên với mô hình kế thừa đa hình: `Member` $\rightarrow$ `BasicMember` (Hội viên thường) và `PremiumMember` (Hội viên VIP).
   - CRUD Hội viên đầy đủ: Xem danh sách, Thêm mới, Sửa thông tin, Xóa hội viên.
   - **Gia hạn gói tập đúng quy ước**: Thẻ còn hạn $\rightarrow$ cộng dồn ngày; Thẻ hết hạn $\rightarrow$ tính từ ngày hiện tại; Tự động ghi nhận Transaction thu phí.
   - **Ghi nhận lượt tập (Check-in)**: Kiểm tra trạng thái thẻ (`is_active()`). Chỉ cho phép hội viên còn hạn check-in và lưu lịch sử `WorkoutSession`.
   - **Tìm kiếm & Lọc đa tiêu chí**: Tìm theo từ khóa (Mã, Tên, SĐT), lọc theo trạng thái thẻ (Còn hạn / Hết hạn), lọc theo loại hội viên (Basic / Premium).
   - **Sắp xếp linh hoạt**: Theo Mã, Tên, Ngày hết hạn, Ngày đăng ký.
   - **Báo cáo doanh thu & Thống kê toàn diện**: Doanh thu tính chính xác từ tổng số tiền của các giao dịch `Transaction` thực tế (Đăng ký mới + Gia hạn).
   - **Lưu trữ dữ liệu JSON**: Đọc/ghi tự động vào file `gym_data.json`.

---

### PHẦN 2: THIẾT KẾ SƠ ĐỒ LỚP (UML CLASS DIAGRAM)
*File thiết kế: `UML.drawio` (Tab 1: Class Diagram)*

#### 1. Lớp trừu tượng `Member`
- **Thuộc tính**:
  - `# memberId: String`: Mã hội viên (duy nhất).
  - `# fullName: String`: Họ tên.
  - `# phoneNumber: String`: Số điện thoại.
  - `# plan: Plan`: Gói tập đăng ký.
  - `# trainer: Trainer`: Huấn luyện viên hướng dẫn (nếu có).
  - `# joinDate: LocalDate`: Ngày đăng ký.
  - `# expiryDate: LocalDate`: Ngày hết hạn thẻ.
- **Phương thức**:
  - `+ isActive(): boolean`: Kiểm tra thẻ còn hạn tập hay không.
  - `+ renew(plan: Plan)`: Gia hạn gói tập theo đúng quy ước cộng dồn ngày.
  - `+ calculateMembershipFee(): double*`: Phương thức trừu tượng tính học phí (**Đa hình - Polymorphism**).
  - `+ getMemberType(): String*`: Phương thức trừu tượng trả về loại hội viên.
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
- **`Plan`**: `planId`, `planName`, `durationMonths`, `price`.
- **`Trainer`**: `trainerId`, `fullName`, `specialty`, `phoneNumber`, `monthlyFee`.
- **`Transaction`**: Ghi nhận dòng tiền thu phí (`transactionId`, `memberId`, `amount`, `transactionType`, `planName`, `paymentDate`).
- **`WorkoutSession`**: Ghi nhận lượt tập (`sessionId`, `memberId`, `checkinTime`, `notes`).
- **`GymManager`**: Lớp điều khiển trung tâm quản lý toàn bộ các danh sách và file JSON.

---

### PHẦN 3: THIẾT KẾ LƯU ĐỒ HOẠT ĐỘNG & MENU (ACTIVITY DIAGRAM)
*File thiết kế: `UML.drawio` (Tab 2: Activity Diagram - Menu Flow)*

1. Khởi động chương trình $\rightarrow$ Tự động đọc dữ liệu từ `gym_data.json`.
2. Hiển thị Menu điều hướng chính (0 - 10).
3. Người dùng nhập lựa chọn:
   - `1 - 4`: Quản lý hội viên CRUD $\rightarrow$ Tự động tính phí đa hình & tạo Transaction $\rightarrow$ Lưu JSON.
   - `5`: Gia hạn gói tập $\rightarrow$ Kiểm tra thẻ còn hạn hay hết hạn $\rightarrow$ Cập nhật hạn tập & tạo Transaction $\rightarrow$ Lưu JSON.
   - `6`: Quẹt thẻ Check-in $\rightarrow$ Kiểm tra thẻ còn hạn? (Nếu hết hạn $\rightarrow$ Cảnh báo; Nếu còn hạn $\rightarrow$ Lưu lượt tập `WorkoutSession`) $\rightarrow$ Lưu JSON.
   - `7`: Tìm kiếm & Lọc hội viên (Từ khóa, Còn hạn, Basic/Premium).
   - `8`: Sắp xếp danh sách (Mã, Tên, Ngày hết hạn, Ngày đăng ký).
   - `9`: Báo cáo doanh thu và thống kê hoạt động phòng gym.
   - `10`: Lưu dữ liệu thủ công ra file JSON.
   - `0`: Lưu dữ liệu an toàn và Thoát chương trình.

---

### PHẦN 4: KẾT QUẢ KIỂM THỬ (11 TEST CASES)
*Chạy tự động bằng lệnh: `python3 test_gym_management.py`*

| STT | Mã TC | Tên ca kiểm thử | Kết quả thực tế | Trạng thái |
| :---: | :---: | :--- | :--- | :---: |
| 1 | TC01 | Tính phí đa hình BasicMember | Tính đúng học phí gói cơ bản và phí HLV | **PASS** |
| 2 | TC02 | Tính phí đa hình PremiumMember | Tính đúng học phí gói VIP + phí tiện ích và ưu đãi HLV | **PASS** |
| 3 | TC03 | Gia hạn thẻ đang CÒN HẠN | Cộng dồn ngày từ ngày hết hạn hiện tại | **PASS** |
| 4 | TC04 | Gia hạn thẻ ĐÃ HẾT HẠN | Cộng dồn ngày tính từ ngày hiện tại | **PASS** |
| 5 | TC05 | Check-in hội viên CÒN HẠN | Cho phép vào tập, ghi nhận lượt tập | **PASS** |
| 6 | TC06 | Check-in hội viên HẾT HẠN | Từ chối check-in, cảnh báo thẻ hết hạn | **PASS** |
| 7 | TC07 | Ghi nhận Giao dịch thu phí | Tạo bản ghi Transaction chính xác | **PASS** |
| 8 | TC08 | Tính tổng doanh thu hệ thống | Tính tổng tiền chính xác từ các giao dịch | **PASS** |
| 9 | TC09 | Lưu trữ và nạp dữ liệu JSON | Đọc/ghi toàn vẹn danh sách hội viên, GD, lượt tập | **PASS** |
| 10 | TC10 | Tìm kiếm & Lọc đa tiêu chí | Lọc chuẩn xác theo trạng thái và loại hội viên | **PASS** |
| 11 | TC11 | Sắp xếp danh sách hội viên | Sắp xếp chuẩn xác theo tên A-Z | **PASS** |

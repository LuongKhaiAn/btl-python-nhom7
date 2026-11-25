# DÀN Ý SLIDE THUYẾT TRÌNH BÀI TẬP LỚN (BẢN CHUẨN)
## ĐỀ TÀI: HỆ THỐNG QUẢN LÝ HỘI VIÊN PHÒNG GYM
*Tệp mẫu: `Nhom_7_Slides.pptx` - Người thực hiện: Lương*

---

### Slide 1: Trang tiêu đề
- **Tên đề tài:** HỆ THỐNG QUẢN LÝ HỘI VIÊN PHÒNG GYM CHUYÊN NGHIỆP
- **Học phần:** Lập trình Python
- **Nhóm thực hiện:** Nhóm 7
- **Thành viên & Vai trò:**
  - An: Thiết kế kiến trúc UML, Luồng xử lý, Lập trình OOP
  - Văn, Vỹ: Phân tích nghiệp vụ, Viết tài liệu báo cáo Word
  - Long, Thành: Xây dựng & thực thi kiểm thử (Test Cases), Demo hệ thống
  - Lương: Thiết kế Slide thuyết trình PowerPoint

---

### Slide 2: Đặt vấn đề & Yêu cầu bài toán
- **Thực trạng:** Phòng gym cần quản lý đa dạng loại hội viên (thường, VIP), hạn tập, chấm công/lượt tập và dòng tiền thu phí.
- **Yêu cầu cốt lõi:**
  - Áp dụng triệt để lập trình hướng đối tượng (OOP): Đa hình tính phí giữa các phân hạng hội viên.
  - Quản lý lượt tập (Check-in) và phát hiện thẻ hết hạn.
  - Gia hạn thẻ linh hoạt (cộng theo tháng lịch đúng nghiệp vụ).
  - Ghi nhận giao dịch và thống kê doanh thu thực tế.
  - Lưu trữ dữ liệu bền vững (JSON Persistence).

---

### Slide 3: Sơ đồ lớp hướng đối tượng (UML Class Diagram)
*(Chèn hình chụp từ Tab 1 file `UML.drawio`)*
- **Lớp trừu tượng `Member`**: Khai báo các thuộc tính chung, kiểm tra hạn thẻ `check_expiry()` và phương thức trừu tượng `calculateMembershipFee()` / `calculate_membership_fee()`.
- **Kế thừa & Đa hình (Polymorphism)**:
  - `BasicMember`: Áp dụng chiết khấu cơ bản, thuê HLV tính theo giá niêm yết.
  - `PremiumMember`: Gói VIP tích hợp xông hơi, locker riêng, ưu đãi giảm giá 20% khi thuê HLV.
- **Thực thể mở rộng**:
  - `Transaction`: Quản lý từng dòng tiền thu phí.
  - `WorkoutSession`: Quản lý nhật ký quẹt thẻ ra/vào phòng gym.
  - `MembershipPlan`, `Trainer`, `GymManager`: Đảm bảo tính kết tập và tổ chức dữ liệu khoa học.

---

### Slide 4: Lưu đồ hoạt động & Menu tương tác (Activity Diagram)
*(Chèn hình chụp từ Tab 2 file `UML.drawio`)*
- **Quy trình hoạt động:**
  1. Khởi động: Tự động nạp dữ liệu từ `data/gym_data.json`.
  2. Điều hướng qua Menu Console chính (Lựa chọn 0 - 17).
  3. Xử lý nghiệp vụ (CRUD, Gia hạn, Check-in, Tìm kiếm, Sắp xếp, Báo cáo).
  4. Đồng bộ tự động mọi thay đổi vào file lưu trữ `data/gym_data.json`.

---

### Slide 5: Điểm sáng công nghệ & Nghiệp vụ nổi bật
- **Đa hình tính phí:** Không dùng câu lệnh `if...else` rườm rà, đối tượng tự biết cách tính học phí chính xác.
- **Quy ước gia hạn chuẩn:**
  - Thẻ còn hạn: Hạn mới = Hạn cũ + số tháng lịch của gói.
  - Thẻ hết hạn: Hạn mới = Ngày hiện tại + số tháng lịch của gói.
- **Bảo mật & Kiểm soát ra vào:** Tự động chặn hội viên hết hạn quẹt thẻ tập.
- **Doanh thu thực tế:** Tổng hợp từ mọi giao dịch phát sinh thay vì chỉ tính học phí hiện tại.

---

### Slide 6: Kết quả kiểm thử (Testing & QA)
- Đã thực thi bộ **40 Test Cases (Unittest)** kiểm thử tự động toàn diện:
  - Kiểm tra tính phí đa hình Basic vs Premium.
  - Kiểm tra logic gia hạn thẻ (còn hạn vs hết hạn).
  - Kiểm tra logic quẹt thẻ check-in.
  - Kiểm tra tìm kiếm, sắp xếp, thống kê, xóa an toàn, phân công HLV.
  - Kiểm tra đọc/ghi toàn vẹn dữ liệu JSON và sao lưu khi file hỏng.
- **Kết quả:** **40/40 Test Cases đạt PASS (100%)**.

---

### Slide 7: Kết luận & Định hướng tương lai
- **Kết quả đạt được:** Hoàn thành 100% yêu cầu đề bài và các ý kiến đóng góp từ Reviewer, mã nguồn chuẩn OOP, sạch sẽ, chạy ổn định.
- **Mở rộng tương lai:**
  - Nâng cấp giao diện người dùng GUI (Tkinter/PyQt) hoặc Web Dashboard.
  - Tích hợp máy quét mã vạch / QR Code để check-in tự động.
  - Tích hợp cổng thanh toán trực tuyến (MoMo, VNPay).

---

### Slide 8: Q&A
- Lời cảm ơn Thầy Cô và các bạn.
- Nhóm sẵn sàng lắng nghe câu hỏi và nhận xét đóng góp!

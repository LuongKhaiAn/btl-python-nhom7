"""
models.py
Module định nghĩa các lớp thực thể OOP cho Hệ thống Quản lý Hội viên Phòng Gym.
Áp dụng đầy đủ 4 nguyên lý OOP: Trừu tượng (Abstraction), Đóng gói (Encapsulation),
Kế thừa (Inheritance), và Đa hình (Polymorphism).

Nhiệm vụ theo Phân công Giai đoạn III (Yêu cầu 1):
- Đổi tên lớp Plan -> MembershipPlan, thêm hàm check_expiry() khớp đề bài.
- Bổ sung tính Đóng gói: chuyển thuộc tính sang protected (_member_id, _price, _expiry_date...)
  kèm @property và setter kiểm tra hợp lệ.
- Thêm phương thức __str__() cho tất cả các lớp (Member, BasicMember, PremiumMember,
  Trainer, MembershipPlan, WorkoutSession, Transaction).
"""

from abc import ABC, abstractmethod
from datetime import date, datetime, timedelta
from typing import Optional, Union


# ==============================================================================
# 1. LỚP GÓI TẬP (MembershipPlan)
# ==============================================================================
class MembershipPlan:
    """
    Lớp đại diện cho Gói tập phòng gym (MembershipPlan).
    Bao gồm: Mã gói, tên gói, thời hạn (tháng), và đơn giá gói.
    """

    def __init__(
        self,
        plan_id: str,
        plan_name: str,
        duration_months: int,
        price: float,
    ):
        self.plan_id = plan_id
        self.plan_name = plan_name
        self.duration_months = duration_months
        self.price = price

    # --- Đóng gói: Properties & Setters với kiểm tra hợp lệ ---
    @property
    def plan_id(self) -> str:
        return self._plan_id

    @plan_id.setter
    def plan_id(self, value: str):
        if not isinstance(value, str) or not value.strip():
            raise ValueError("Mã gói tập (plan_id) không được để trống.")
        self._plan_id = value.strip()

    @property
    def plan_name(self) -> str:
        return self._plan_name

    @plan_name.setter
    def plan_name(self, value: str):
        if not isinstance(value, str) or not value.strip():
            raise ValueError("Tên gói tập (plan_name) không được để trống.")
        self._plan_name = value.strip()

    @property
    def duration_months(self) -> int:
        return self._duration_months

    @duration_months.setter
    def duration_months(self, value: int):
        try:
            val_int = int(value)
        except (ValueError, TypeError):
            raise ValueError("Thời hạn gói tập (duration_months) phải là số nguyên.")
        if val_int < 1:
            raise ValueError("Thời hạn gói tập phải từ 1 tháng trở lên.")
        self._duration_months = val_int

    @property
    def price(self) -> float:
        return self._price

    @price.setter
    def price(self, value: float):
        try:
            val_float = float(value)
        except (ValueError, TypeError):
            raise ValueError("Giá gói tập (price) phải là số thực hợp lệ.")
        if val_float < 0:
            raise ValueError("Giá gói tập không được là số âm.")
        self._price = val_float

    # --- Phương thức hiển thị chuẩn OOP ---
    def __str__(self) -> str:
        return (
            f"[Gói tập] Mã: {self._plan_id:<4} | Tên: {self._plan_name:<12} | "
            f"Thời hạn: {self._duration_months:>2} tháng | Đơn giá: {self._price:,.0f} VNĐ"
        )

    def display_info(self):
        print(self.__str__())

    # --- Serialization ---
    def to_dict(self) -> dict:
        return {
            "plan_id": self._plan_id,
            "plan_name": self._plan_name,
            "duration_months": self._duration_months,
            "price": self._price,
        }

    @classmethod
    def from_dict(cls, data: dict) -> "MembershipPlan":
        return cls(
            plan_id=data["plan_id"],
            plan_name=data["plan_name"],
            duration_months=data["duration_months"],
            price=data["price"],
        )


# Bí danh Plan tương thích ngược với code cũ và test case
Plan = MembershipPlan


# ==============================================================================
# 2. LỚP HUẤN LUYỆN VIÊN (Trainer)
# ==============================================================================
class Trainer:
    """
    Lớp đại diện cho Huấn luyện viên cá nhân (Trainer).
    Bao gồm: Mã HLV, họ tên, chuyên môn, số điện thoại, và mức phí hướng dẫn theo tháng.
    """

    def __init__(
        self,
        trainer_id: str,
        full_name: str,
        specialty: str,
        phone_number: str,
        monthly_fee: float = 500000.0,
    ):
        self.trainer_id = trainer_id
        self.full_name = full_name
        self.specialty = specialty
        self.phone_number = phone_number
        self.monthly_fee = monthly_fee

    # --- Đóng gói: Properties & Setters với kiểm tra hợp lệ ---
    @property
    def trainer_id(self) -> str:
        return self._trainer_id

    @trainer_id.setter
    def trainer_id(self, value: str):
        if not isinstance(value, str) or not value.strip():
            raise ValueError("Mã HLV (trainer_id) không được để trống.")
        self._trainer_id = value.strip()

    @property
    def full_name(self) -> str:
        return self._full_name

    @full_name.setter
    def full_name(self, value: str):
        if not isinstance(value, str) or not value.strip():
            raise ValueError("Họ tên HLV (full_name) không được để trống.")
        self._full_name = value.strip()

    @property
    def specialty(self) -> str:
        return self._specialty

    @specialty.setter
    def specialty(self, value: str):
        if not isinstance(value, str) or not value.strip():
            raise ValueError("Chuyên môn HLV (specialty) không được để trống.")
        self._specialty = value.strip()

    @property
    def phone_number(self) -> str:
        return self._phone_number

    @phone_number.setter
    def phone_number(self, value: str):
        if not isinstance(value, str) or not value.strip():
            raise ValueError("Số điện thoại HLV không được để trống.")
        self._phone_number = value.strip()

    @property
    def monthly_fee(self) -> float:
        return self._monthly_fee

    @monthly_fee.setter
    def monthly_fee(self, value: float):
        try:
            val_float = float(value)
        except (ValueError, TypeError):
            raise ValueError("Phí HLV (monthly_fee) phải là số thực.")
        if val_float < 0:
            raise ValueError("Phí HLV không được âm.")
        self._monthly_fee = val_float

    # --- Phương thức hiển thị chuẩn OOP ---
    def __str__(self) -> str:
        return (
            f"[HLV] Mã: {self._trainer_id:<4} | Họ tên: {self._full_name:<18} | "
            f"Chuyên môn: {self._specialty:<18} | SĐT: {self._phone_number:<11} | "
            f"Phí/tháng: {self._monthly_fee:,.0f} VNĐ"
        )

    def display_info(self):
        print(self.__str__())

    # --- Serialization ---
    def to_dict(self) -> dict:
        return {
            "trainer_id": self._trainer_id,
            "full_name": self._full_name,
            "specialty": self._specialty,
            "phone_number": self._phone_number,
            "monthly_fee": self._monthly_fee,
        }

    @classmethod
    def from_dict(cls, data: dict) -> "Trainer":
        return cls(
            trainer_id=data["trainer_id"],
            full_name=data["full_name"],
            specialty=data["specialty"],
            phone_number=data["phone_number"],
            monthly_fee=data.get("monthly_fee", 500000.0),
        )


# ==============================================================================
# 3. LỚP HỘI VIÊN TRỪU TƯỢNG (Member - Abstract Base Class)
# ==============================================================================
class Member(ABC):
    """
    Lớp cơ sở trừu tượng đại diện cho Hội viên phòng gym.
    Định nghĩa khung thuộc tính và các phương thức nghiệp vụ cốt lõi:
    check_expiry(), renew(), calculate_membership_fee(), get_member_type().
    """

    def __init__(
        self,
        member_id: str,
        full_name: str,
        phone_number: str,
        plan: MembershipPlan,
        trainer: Optional[Trainer] = None,
        join_date: Optional[Union[str, datetime]] = None,
        expiry_date: Optional[Union[str, datetime]] = None,
    ):
        self.member_id = member_id
        self.full_name = full_name
        self.phone_number = phone_number
        self.plan = plan
        self.trainer = trainer

        # Xử lý join_date
        now = datetime.now()
        if isinstance(join_date, str):
            self.join_date = datetime.strptime(join_date, "%d/%m/%Y")
        elif isinstance(join_date, datetime):
            self.join_date = join_date
        else:
            self.join_date = now

        # Xử lý expiry_date
        if isinstance(expiry_date, str):
            self.expiry_date = datetime.strptime(expiry_date, "%d/%m/%Y")
        elif isinstance(expiry_date, datetime):
            self.expiry_date = expiry_date
        else:
            self.expiry_date = self.join_date + timedelta(days=self.plan.duration_months * 30)

    # --- Đóng gói: Properties & Setters với kiểm tra hợp lệ ---
    @property
    def member_id(self) -> str:
        return self._member_id

    @member_id.setter
    def member_id(self, value: str):
        if not isinstance(value, str) or not value.strip():
            raise ValueError("Mã hội viên (member_id) không được để trống.")
        self._member_id = value.strip()

    @property
    def full_name(self) -> str:
        return self._full_name

    @full_name.setter
    def full_name(self, value: str):
        if not isinstance(value, str) or not value.strip():
            raise ValueError("Họ tên hội viên (full_name) không được để trống.")
        self._full_name = value.strip()

    @property
    def phone_number(self) -> str:
        return self._phone_number

    @phone_number.setter
    def phone_number(self, value: str):
        if not isinstance(value, str) or not value.strip():
            raise ValueError("Số điện thoại hội viên không được để trống.")
        self._phone_number = value.strip()

    @property
    def plan(self) -> MembershipPlan:
        return self._plan

    @plan.setter
    def plan(self, value: MembershipPlan):
        if value is None:
            raise ValueError("Gói tập (plan) không được là None.")
        if not hasattr(value, "duration_months") or not hasattr(value, "price"):
            raise ValueError("Gói tập phải là đối tượng MembershipPlan hợp lệ.")
        self._plan = value

    @property
    def trainer(self) -> Optional[Trainer]:
        return self._trainer

    @trainer.setter
    def trainer(self, value: Optional[Trainer]):
        if value is not None and not hasattr(value, "monthly_fee"):
            raise ValueError("HLV phải là đối tượng Trainer hợp lệ hoặc None.")
        self._trainer = value

    @property
    def join_date(self) -> datetime:
        return self._join_date

    @join_date.setter
    def join_date(self, value: Union[datetime, str]):
        if isinstance(value, str):
            try:
                self._join_date = datetime.strptime(value, "%d/%m/%Y")
            except ValueError:
                self._join_date = datetime.strptime(value, "%Y-%m-%d")
        elif isinstance(value, datetime):
            self._join_date = value
        else:
            raise ValueError("Ngày tham gia phải là đối tượng datetime hoặc chuỗi định dạng dd/mm/yyyy.")

    @property
    def expiry_date(self) -> datetime:
        return self._expiry_date

    @expiry_date.setter
    def expiry_date(self, value: Union[datetime, str]):
        if isinstance(value, str):
            try:
                self._expiry_date = datetime.strptime(value, "%d/%m/%Y")
            except ValueError:
                self._expiry_date = datetime.strptime(value, "%Y-%m-%d")
        elif isinstance(value, datetime):
            self._expiry_date = value
        else:
            raise ValueError("Ngày hết hạn phải là đối tượng datetime hoặc chuỗi định dạng dd/mm/yyyy.")

    # --- Nghiệp vụ kiểm tra hạn & gia hạn khớp đề bài ---
    def check_expiry(self, current_date: Optional[Union[datetime, date]] = None) -> bool:
        """
        Kiểm tra trạng thái hạn sử dụng của hội viên khớp yêu cầu đề bài.
        Trả về True nếu còn hạn (expiry_date >= current_date), False nếu đã hết hạn.
        """
        if current_date is None:
            cmp_date = datetime.now().date()
        elif isinstance(current_date, datetime):
            cmp_date = current_date.date()
        else:
            cmp_date = current_date
        return self._expiry_date.date() >= cmp_date

    def is_active(self) -> bool:
        """Kiểm tra hội viên còn hạn tập hay không (tương thích với code hiện hữu)."""
        return self.check_expiry()

    def renew(self, plan: MembershipPlan):
        """
        Gia hạn thẻ theo đúng quy ước nghiệp vụ:
        - Nếu còn hạn: cộng dồn thời hạn nối tiếp từ expiry_date hiện tại.
        - Nếu đã hết hạn: thời hạn mới được tính bắt đầu từ ngày hiện tại.
        """
        self.plan = plan
        now = datetime.now()
        extension_days = plan.duration_months * 30
        if self.check_expiry():
            self._expiry_date = self._expiry_date + timedelta(days=extension_days)
        else:
            self._expiry_date = now + timedelta(days=extension_days)

    # --- Phương thức trừu tượng (Đa hình) ---
    @abstractmethod
    def calculate_membership_fee(self) -> float:
        """Tính toán tổng hội phí cần nộp theo loại hội viên và các phụ phí tương ứng."""
        pass

    @abstractmethod
    def get_member_type(self) -> str:
        """Trả về tên phân loại hội viên ('Basic' hoặc 'Premium')."""
        pass

    # --- Phương thức hiển thị chuẩn OOP ---
    def __str__(self) -> str:
        status_txt = "Còn hạn" if self.check_expiry() else "HẾT HẠN"
        trainer_name = self._trainer.full_name if self._trainer else "Tự tập"
        fee = self.calculate_membership_fee()
        return (
            f"[{self.get_member_type():<7}] Mã: {self._member_id:<5} | Họ tên: {self._full_name:<18} | "
            f"SĐT: {self._phone_number:<11} | Gói: {self._plan.plan_name:<9} | HLV: {trainer_name:<16} | "
            f"Hết hạn: {self._expiry_date.strftime('%d/%m/%Y')} ({status_txt:<7}) | "
            f"Học phí: {fee:>10,.0f} VNĐ"
        )

    def display_info(self):
        print(self.__str__())

    # --- Serialization ---
    def to_dict(self) -> dict:
        return {
            "type": self.get_member_type(),
            "member_id": self._member_id,
            "full_name": self._full_name,
            "phone_number": self._phone_number,
            "plan": self._plan.to_dict(),
            "trainer": self._trainer.to_dict() if self._trainer else None,
            "join_date": self._join_date.strftime("%d/%m/%Y"),
            "expiry_date": self._expiry_date.strftime("%d/%m/%Y"),
        }

    @classmethod
    def from_dict(cls, data: dict) -> "Member":
        """Factory method tạo đúng thể hiện BasicMember hoặc PremiumMember từ dictionary."""
        member_type = data.get("type", "Basic")
        if member_type == "Premium":
            return PremiumMember.from_dict(data)
        return BasicMember.from_dict(data)


# ==============================================================================
# 4. LỚP HỘI VIÊN THƯỜNG (BasicMember - Kế thừa Member)
# ==============================================================================
class BasicMember(Member):
    """
    Lớp Hội viên Thường kế thừa từ Member.
    Có thêm chính sách giảm giá (discount_rate).
    Đa hình: calculate_membership_fee() = Tiền gói * (1 - giảm giá) + Tiền HLV.
    """

    def __init__(
        self,
        member_id: str,
        full_name: str,
        phone_number: str,
        plan: MembershipPlan,
        trainer: Optional[Trainer] = None,
        join_date: Optional[Union[str, datetime]] = None,
        expiry_date: Optional[Union[str, datetime]] = None,
        discount_rate: float = 0.0,
    ):
        super().__init__(
            member_id=member_id,
            full_name=full_name,
            phone_number=phone_number,
            plan=plan,
            trainer=trainer,
            join_date=join_date,
            expiry_date=expiry_date,
        )
        self.discount_rate = discount_rate

    # --- Đóng gói: Property & Setter cho discount_rate ---
    @property
    def discount_rate(self) -> float:
        return self._discount_rate

    @discount_rate.setter
    def discount_rate(self, value: float):
        try:
            val_float = float(value)
        except (ValueError, TypeError):
            raise ValueError("Tỷ lệ giảm giá (discount_rate) phải là số thực.")
        if not (0.0 <= val_float <= 1.0):
            raise ValueError("Tỷ lệ giảm giá phải nằm trong khoảng từ 0.0 đến 1.0 (0% - 100%).")
        self._discount_rate = val_float

    def get_member_type(self) -> str:
        return "Basic"

    def calculate_membership_fee(self) -> float:
        base_cost = self._plan.price * (1 - self._discount_rate)
        trainer_cost = (
            self._trainer.monthly_fee * self._plan.duration_months
            if self._trainer
            else 0.0
        )
        return base_cost + trainer_cost

    def to_dict(self) -> dict:
        d = super().to_dict()
        d["discount_rate"] = self._discount_rate
        return d

    @classmethod
    def from_dict(cls, data: dict) -> "BasicMember":
        plan = MembershipPlan.from_dict(data["plan"])
        trainer = Trainer.from_dict(data["trainer"]) if data.get("trainer") else None
        return cls(
            member_id=data["member_id"],
            full_name=data["full_name"],
            phone_number=data["phone_number"],
            plan=plan,
            trainer=trainer,
            join_date=data.get("join_date"),
            expiry_date=data.get("expiry_date"),
            discount_rate=data.get("discount_rate", 0.0),
        )


# ==============================================================================
# 5. LỚP HỘI VIÊN CAO CẤP (PremiumMember - Kế thừa Member)
# ==============================================================================
class PremiumMember(Member):
    """
    Lớp Hội viên VIP / Cao cấp kế thừa từ Member.
    Có thêm quyền lợi:
    - Phí dịch vụ VIP theo tháng (vip_perks_fee)
    - Quyền sử dụng phòng xông hơi Sauna (sauna_access)
    - Tỷ lệ giảm giá khi thuê Huấn luyện viên riêng (trainer_discount_rate, mặc định 20%).
    Đa hình: calculate_membership_fee() = Tiền gói + Phí VIP + Tiền HLV sau giảm giá.
    """

    def __init__(
        self,
        member_id: str,
        full_name: str,
        phone_number: str,
        plan: MembershipPlan,
        trainer: Optional[Trainer] = None,
        join_date: Optional[Union[str, datetime]] = None,
        expiry_date: Optional[Union[str, datetime]] = None,
        vip_perks_fee: float = 200000.0,
        sauna_access: bool = True,
        trainer_discount_rate: float = 0.2,
    ):
        super().__init__(
            member_id=member_id,
            full_name=full_name,
            phone_number=phone_number,
            plan=plan,
            trainer=trainer,
            join_date=join_date,
            expiry_date=expiry_date,
        )
        self.vip_perks_fee = vip_perks_fee
        self.sauna_access = sauna_access
        self.trainer_discount_rate = trainer_discount_rate

    # --- Đóng gói: Properties & Setters ---
    @property
    def vip_perks_fee(self) -> float:
        return self._vip_perks_fee

    @vip_perks_fee.setter
    def vip_perks_fee(self, value: float):
        try:
            val_float = float(value)
        except (ValueError, TypeError):
            raise ValueError("Phí đặc quyền VIP (vip_perks_fee) phải là số thực.")
        if val_float < 0:
            raise ValueError("Phí đặc quyền VIP không được là số âm.")
        self._vip_perks_fee = val_float

    @property
    def sauna_access(self) -> bool:
        return self._sauna_access

    @sauna_access.setter
    def sauna_access(self, value: bool):
        self._sauna_access = bool(value)

    @property
    def trainer_discount_rate(self) -> float:
        return self._trainer_discount_rate

    @trainer_discount_rate.setter
    def trainer_discount_rate(self, value: float):
        try:
            val_float = float(value)
        except (ValueError, TypeError):
            raise ValueError("Tỷ lệ giảm giá HLV (trainer_discount_rate) phải là số thực.")
        if not (0.0 <= val_float <= 1.0):
            raise ValueError("Tỷ lệ giảm giá HLV phải nằm trong khoảng từ 0.0 đến 1.0.")
        self._trainer_discount_rate = val_float

    def get_member_type(self) -> str:
        return "Premium"

    def calculate_membership_fee(self) -> float:
        base_cost = self._plan.price + (self._vip_perks_fee * self._plan.duration_months)
        trainer_cost = (
            self._trainer.monthly_fee
            * self._plan.duration_months
            * (1 - self._trainer_discount_rate)
            if self._trainer
            else 0.0
        )
        return base_cost + trainer_cost

    def to_dict(self) -> dict:
        d = super().to_dict()
        d["vip_perks_fee"] = self._vip_perks_fee
        d["sauna_access"] = self._sauna_access
        d["trainer_discount_rate"] = self._trainer_discount_rate
        return d

    @classmethod
    def from_dict(cls, data: dict) -> "PremiumMember":
        plan = MembershipPlan.from_dict(data["plan"])
        trainer = Trainer.from_dict(data["trainer"]) if data.get("trainer") else None
        return cls(
            member_id=data["member_id"],
            full_name=data["full_name"],
            phone_number=data["phone_number"],
            plan=plan,
            trainer=trainer,
            join_date=data.get("join_date"),
            expiry_date=data.get("expiry_date"),
            vip_perks_fee=data.get("vip_perks_fee", 200000.0),
            sauna_access=data.get("sauna_access", True),
            trainer_discount_rate=data.get("trainer_discount_rate", 0.2),
        )


# ==============================================================================
# 6. LỚP LƯỢT TẬP (WorkoutSession / Attendance)
# ==============================================================================
class WorkoutSession:
    """
    Lớp lưu vết lịch sử buổi tập / quẹt thẻ check-in của hội viên.
    Bao gồm: Mã lượt tập, mã hội viên, thời gian quẹt thẻ và ghi chú nội dung tập.
    """

    def __init__(
        self,
        session_id: str,
        member_id: str,
        checkin_time: Optional[str] = None,
        notes: str = "Tập luyện thể hình",
    ):
        self.session_id = session_id
        self.member_id = member_id
        self.checkin_time = (
            checkin_time
            if checkin_time
            else datetime.now().strftime("%d/%m/%Y %H:%M:%S")
        )
        self.notes = notes

    # --- Đóng gói: Properties & Setters ---
    @property
    def session_id(self) -> str:
        return self._session_id

    @session_id.setter
    def session_id(self, value: str):
        if not isinstance(value, str) or not value.strip():
            raise ValueError("Mã lượt tập (session_id) không được để trống.")
        self._session_id = value.strip()

    @property
    def member_id(self) -> str:
        return self._member_id

    @member_id.setter
    def member_id(self, value: str):
        if not isinstance(value, str) or not value.strip():
            raise ValueError("Mã hội viên trong lượt tập không được để trống.")
        self._member_id = value.strip()

    @property
    def checkin_time(self) -> str:
        return self._checkin_time

    @checkin_time.setter
    def checkin_time(self, value: str):
        if not isinstance(value, str) or not value.strip():
            raise ValueError("Thời gian check-in không được để trống.")
        self._checkin_time = value.strip()

    @property
    def notes(self) -> str:
        return self._notes

    @notes.setter
    def notes(self, value: str):
        self._notes = str(value).strip() if value else ""

    # --- Phương thức hiển thị chuẩn OOP ---
    def __str__(self) -> str:
        return (
            f"[Lượt tập] Mã: {self._session_id:<6} | Mã HV: {self._member_id:<6} | "
            f"Thời gian: {self._checkin_time:<19} | Ghi chú: {self._notes}"
        )

    def display_info(self):
        print(self.__str__())

    # --- Serialization ---
    def to_dict(self) -> dict:
        return {
            "session_id": self._session_id,
            "member_id": self._member_id,
            "checkin_time": self._checkin_time,
            "notes": self._notes,
        }

    @classmethod
    def from_dict(cls, data: dict) -> "WorkoutSession":
        return cls(
            session_id=data["session_id"],
            member_id=data["member_id"],
            checkin_time=data.get("checkin_time"),
            notes=data.get("notes", "Tập luyện thể hình"),
        )


# ==============================================================================
# 7. LỚP GIAO DỊCH TÀI CHÍNH (Transaction)
# ==============================================================================
class Transaction:
    """
    Lớp lưu vết giao dịch tài chính (thu tiền đăng ký mới hoặc gia hạn gói tập).
    Bao gồm: Mã giao dịch, mã hội viên, số tiền, loại giao dịch, tên gói và ngày thu.
    """

    def __init__(
        self,
        transaction_id: str,
        member_id: str,
        amount: float,
        transaction_type: str,
        plan_name: str,
        payment_date: Optional[str] = None,
    ):
        self.transaction_id = transaction_id
        self.member_id = member_id
        self.amount = amount
        self.transaction_type = transaction_type
        self.plan_name = plan_name
        self.payment_date = (
            payment_date
            if payment_date
            else datetime.now().strftime("%d/%m/%Y %H:%M:%S")
        )

    # --- Đóng gói: Properties & Setters ---
    @property
    def transaction_id(self) -> str:
        return self._transaction_id

    @transaction_id.setter
    def transaction_id(self, value: str):
        if not isinstance(value, str) or not value.strip():
            raise ValueError("Mã giao dịch (transaction_id) không được để trống.")
        self._transaction_id = value.strip()

    @property
    def member_id(self) -> str:
        return self._member_id

    @member_id.setter
    def member_id(self, value: str):
        if not isinstance(value, str) or not value.strip():
            raise ValueError("Mã hội viên trong giao dịch không được để trống.")
        self._member_id = value.strip()

    @property
    def amount(self) -> float:
        return self._amount

    @amount.setter
    def amount(self, value: float):
        try:
            val_float = float(value)
        except (ValueError, TypeError):
            raise ValueError("Số tiền giao dịch (amount) phải là số thực.")
        if val_float < 0:
            raise ValueError("Số tiền giao dịch không được là số âm.")
        self._amount = val_float

    @property
    def transaction_type(self) -> str:
        return self._transaction_type

    @transaction_type.setter
    def transaction_type(self, value: str):
        if not isinstance(value, str) or not value.strip():
            raise ValueError("Loại giao dịch không được để trống.")
        self._transaction_type = value.strip()

    @property
    def plan_name(self) -> str:
        return self._plan_name

    @plan_name.setter
    def plan_name(self, value: str):
        if not isinstance(value, str) or not value.strip():
            raise ValueError("Tên gói tập trong giao dịch không được để trống.")
        self._plan_name = value.strip()

    @property
    def payment_date(self) -> str:
        return self._payment_date

    @payment_date.setter
    def payment_date(self, value: str):
        if not isinstance(value, str) or not value.strip():
            raise ValueError("Ngày thanh toán không được để trống.")
        self._payment_date = value.strip()

    # --- Phương thức hiển thị chuẩn OOP ---
    def __str__(self) -> str:
        return (
            f"[Giao dịch] Mã: {self._transaction_id:<6} | Mã HV: {self._member_id:<5} | "
            f"Số tiền: {self._amount:>10,.0f} VNĐ | Loại: {self._transaction_type:<12} | "
            f"Gói: {self._plan_name:<10} | Ngày: {self._payment_date}"
        )

    def display_info(self):
        print(self.__str__())

    # --- Serialization ---
    def to_dict(self) -> dict:
        return {
            "transaction_id": self._transaction_id,
            "member_id": self._member_id,
            "amount": self._amount,
            "transaction_type": self._transaction_type,
            "plan_name": self._plan_name,
            "payment_date": self._payment_date,
        }

    @classmethod
    def from_dict(cls, data: dict) -> "Transaction":
        return cls(
            transaction_id=data["transaction_id"],
            member_id=data["member_id"],
            amount=data["amount"],
            transaction_type=data["transaction_type"],
            plan_name=data["plan_name"],
            payment_date=data.get("payment_date"),
        )

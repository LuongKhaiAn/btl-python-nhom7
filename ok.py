
"""
Module: data_handler.py
Chức năng:
- Lưu dữ liệu hệ thống vào file JSON.
- Đọc dữ liệu từ file JSON.
- Khởi tạo dữ liệu mẫu.
- Xuất báo cáo hội viên ra file CSV.

Dự án: Quản lý hội viên phòng tập
"""

import csv
import json
import os
import tempfile

from datetime import datetime

# Import các lớp được định nghĩa trong gym_management.py
from gym_management import (
    Plan,
    Trainer,
    BasicMember,
    PremiumMember,
    Transaction,
    WorkoutSession
)


# ==========================================================
# 1. CẤU HÌNH FILE DỮ LIỆU
# ==========================================================

DATA_FILE = "gym_data.json"


# ==========================================================
# 2. KHỞI TẠO DỮ LIỆU MẪU
# ==========================================================

def init_default_data():
    """
    Khởi tạo dữ liệu mẫu cho hệ thống.

    Bao gồm:
    - Danh sách gói tập.
    - Danh sách huấn luyện viên.
    - 6 hội viên mẫu.
    - Lịch sử giao dịch.
    - Lịch sử lượt tập.

    Trả về Dictionary chứa các đối tượng theo UML.
    """

    # ------------------------------
    # Danh sách gói tập
    # ------------------------------

    plans = [
        Plan("P01", "1 Tháng", 1, 500000),
        Plan("P03", "3 Tháng", 3, 1350000),
        Plan("P06", "6 Tháng", 6, 2500000),
        Plan("P12", "12 Tháng", 12, 4500000)
    ]

    plan_map = {p.plan_id: p for p in plans}

    # ------------------------------
    # Danh sách huấn luyện viên
    # ------------------------------

    trainers = [
        Trainer(
            "T01",
            "Nguyễn Văn Minh",
            "Fitness",
            "0901234567",
            500000
        ),
        Trainer(
            "T02",
            "Trần Thị Lan",
            "Yoga",
            "0908765432",
            600000
        ),
        Trainer(
            "T03",
            "Lê Hoàng Nam",
            "Boxing",
            "0912345678",
            550000
        )
    ]

    trainer_map = {t.trainer_id: t for t in trainers}

    # ------------------------------
    # Danh sách hội viên
    # ------------------------------

    members = [
        # 1. Basic - Còn hạn - Có HLV
        BasicMember(
            "HV01",
            "Nguyễn Văn An",
            "0911222333",
            plan_map["P03"],
            trainer_map["T01"],
            join_date="01/10/2026",
            expiry_date="01/01/2027",
            discount_rate=0.05
        ),

        # 2. Premium - Còn hạn - Có HLV
        PremiumMember(
            "HV02",
            "Trần Thị Bình",
            "0922333444",
            plan_map["P06"],
            trainer_map["T02"],
            join_date="15/09/2026",
            expiry_date="15/03/2027"
        ),

        # 3. Basic - Đã hết hạn - Không có HLV
        BasicMember(
            "HV03",
            "Lê Hoàng Cường",
            "0933444555",
            plan_map["P01"],
            None,
            join_date="01/08/2026",
            expiry_date="01/09/2026",
            discount_rate=0.0
        ),

        # 4. Premium - Còn hạn - Không có HLV
        PremiumMember(
            "HV04",
            "Phạm Thị Dung",
            "0944555666",
            plan_map["P12"],
            None,
            join_date="01/06/2026",
            expiry_date="01/06/2027",
            vip_perks_fee=200000,
            sauna_access=True,
            trainer_discount_rate=0.2
        ),

        # 5. Basic - Sắp hết hạn
        BasicMember(
            "HV05",
            "Hoàng Văn Đức",
            "0955666777",
            plan_map["P03"],
            trainer_map["T03"],
            join_date="20/08/2026",
            expiry_date="25/11/2026",
            discount_rate=0.1
        ),

        # 6. Premium - Còn hạn - Có HLV
        PremiumMember(
            "HV06",
            "Đỗ Thị Hương",
            "0966777888",
            plan_map["P03"],
            trainer_map["T01"],
            join_date="10/11/2026",
            expiry_date="10/02/2027"
        )
    ]

    member_map = {m.member_id: m for m in members}

    # ------------------------------
    # Danh sách giao dịch
    # ------------------------------

    transactions = []

    for i, member in enumerate(members, start=1):
        transactions.append(
            Transaction(
                f"GD{i:03d}",
                member.member_id,
                member.calculate_membership_fee(),
                "Đăng ký mới",
                member.plan.plan_name,
                member.join_date.strftime("%d/%m/%Y %H:%M:%S")
            )
        )

    # ------------------------------
    # Danh sách lượt tập
    # ------------------------------

    workout_sessions = [
        WorkoutSession(
            "LT001",
            "HV01",
            "05/10/2026 17:30:00",
            "Tập cơ ngực"
        ),
        WorkoutSession(
            "LT002",
            "HV02",
            "20/09/2026 18:00:00",
            "Tập Yoga"
        ),
        WorkoutSession(
            "LT003",
            "HV01",
            "10/10/2026 17:00:00",
            "Tập cơ bụng"
        ),
        WorkoutSession(
            "LT004",
            "HV04",
            "12/11/2026 16:30:00",
            "Tập thể hình VIP"
        ),
        WorkoutSession(
            "LT005",
            "HV06",
            "15/11/2026 18:00:00",
            "Tập Fitness"
        )
    ]

    # ------------------------------
    # Gom dữ liệu thành Dictionary
    # ------------------------------

    data = {
        "plans": plans,
        "trainers": trainers,
        "members": members,
        "transactions": transactions,
        "workout_sessions": workout_sessions
    }

    return data


# ==========================================================
# 3. LƯU DỮ LIỆU JSON
# ==========================================================

def save_data(data, filename=DATA_FILE):
    """
    Lưu toàn bộ dữ liệu hệ thống vào file JSON.

    Sử dụng phương thức to_dict() của các lớp theo UML.
    Ghi file tạm trước khi thay thế file chính để hạn chế
    tình trạng file JSON bị hỏng khi ghi dữ liệu.
    """

    json_data = {
        "plans": [
            plan.to_dict()
            for plan in data["plans"]
        ],

        "trainers": [
            trainer.to_dict()
            for trainer in data["trainers"]
        ],

        "members": [
            member.to_dict()
            for member in data["members"]
        ],

        "transactions": [
            transaction.to_dict()
            for transaction in data["transactions"]
        ],

        "workout_sessions": [
            session.to_dict()
            for session in data["workout_sessions"]
        ]
    }

    # Tạo thư mục nếu đường dẫn có chứa thư mục chưa tồn tại
    folder = os.path.dirname(os.path.abspath(filename))
    os.makedirs(folder, exist_ok=True)

    temp_path = None

    try:
        # Tạo file tạm cùng thư mục với file chính
        with tempfile.NamedTemporaryFile(
            mode="w",
            encoding="utf-8",
            suffix=".tmp",
            dir=folder,
            delete=False
        ) as file:

            json.dump(
                json_data,
                file,
                ensure_ascii=False,
                indent=4
            )

            temp_path = file.name

        # Thay thế file cũ bằng file mới
        os.replace(temp_path, filename)

        print(f"Đã lưu dữ liệu thành công vào {filename}")

    except (OSError, TypeError, KeyError, ValueError) as error:

        # Xóa file tạm nếu quá trình lưu gặp lỗi
        if temp_path and os.path.exists(temp_path):
            os.remove(temp_path)

        raise RuntimeError(
            f"Lỗi khi lưu dữ liệu JSON: {error}"
        ) from error


# ==========================================================
# 4. ĐỌC DỮ LIỆU JSON
# ==========================================================

def load_data(filename=DATA_FILE):
    """
    Đọc dữ liệu từ JSON và khôi phục thành các đối tượng lớp.

    Các đối tượng Member sẽ tham chiếu đến Plan và Trainer
    trong danh sách chung, tránh tạo ra các bản sao độc lập.
    """

    # Nếu chưa có file JSON thì tạo dữ liệu mẫu
    if not os.path.exists(filename):
        print("Chưa tìm thấy file dữ liệu. Khởi tạo dữ liệu mẫu.")

        data = init_default_data()
        save_data(data, filename)

        return data

    try:
        with open(filename, "r", encoding="utf-8") as file:
            json_data = json.load(file)

        if not isinstance(json_data, dict):
            raise ValueError("Cấu trúc JSON không hợp lệ.")

        # ------------------------------
        # Khôi phục danh sách Plan
        # ------------------------------

        plans = [
            Plan.from_dict(item)
            for item in json_data.get("plans", [])
        ]

        plan_map = {
            plan.plan_id: plan
            for plan in plans
        }

        # ------------------------------
        # Khôi phục danh sách Trainer
        # ------------------------------

        trainers = [
            Trainer.from_dict(item)
            for item in json_data.get("trainers", [])
        ]

        trainer_map = {
            trainer.trainer_id: trainer
            for trainer in trainers
        }

        # ------------------------------
        # Khôi phục danh sách Member
        # ------------------------------

        members = []

        for item in json_data.get("members", []):

            member_type = item.get("type", "Basic")

            if member_type == "Premium":
                member = PremiumMember.from_dict(item)

            elif member_type == "Basic":
                member = BasicMember.from_dict(item)

            else:
                raise ValueError(
                    f"Loại hội viên không hợp lệ: {member_type}"
                )

            # Liên kết lại Plan dùng chung
            plan_id = item["plan"]["plan_id"]

            if plan_id not in plan_map:
                plan = Plan.from_dict(item["plan"])
                plan_map[plan_id] = plan
                plans.append(plan)

            member.plan = plan_map[plan_id]

            # Liên kết lại Trainer dùng chung
            trainer_data = item.get("trainer")

            if trainer_data:

                trainer_id = trainer_data["trainer_id"]

                if trainer_id not in trainer_map:
                    trainer = Trainer.from_dict(trainer_data)
                    trainer_map[trainer_id] = trainer
                    trainers.append(trainer)

                member.trainer = trainer_map[trainer_id]

            else:
                member.trainer = None

            members.append(member)

        # ------------------------------
        # Khôi phục danh sách Transaction
        # ------------------------------

        transactions = [
            Transaction.from_dict(item)
            for item in json_data.get("transactions", [])
        ]

        # ------------------------------
        # Khôi phục danh sách WorkoutSession
        # ------------------------------

        workout_sessions = [
            WorkoutSession.from_dict(item)
            for item in json_data.get("workout_sessions", [])
        ]

        # ------------------------------
        # Gom dữ liệu thành Dictionary
        # ------------------------------

        data = {
            "plans": plans,
            "trainers": trainers,
            "members": members,
            "transactions": transactions,
            "workout_sessions": workout_sessions
        }

        print(f"Đã đọc dữ liệu thành công từ {filename}")

        return data

    except (OSError, json.JSONDecodeError, KeyError, TypeError, ValueError) as error:

        raise RuntimeError(
            f"Không thể đọc dữ liệu JSON: {error}"
        ) from error


# ==========================================================
# 5. XUẤT BÁO CÁO CSV
# ==========================================================

def export_report_csv(data, filename="bao_cao_hoi_vien.csv"):
    """
    Xuất báo cáo tổng hợp hội viên ra file CSV.

    Nội dung báo cáo:
    - Thông tin hội viên.
    - Loại hội viên.
    - Gói tập.
    - Huấn luyện viên.
    - Ngày tham gia và ngày hết hạn.
    - Trạng thái hội viên.
    - Phí hội viên.
    - Số lượt tập.
    - Số giao dịch.
    - Tổng tiền đã giao dịch.
    """

    members = data["members"]
    workout_sessions = data["workout_sessions"]
    transactions = data["transactions"]

    # ------------------------------
    # Tạo thống kê theo mã hội viên
    # ------------------------------

    workout_count = {}
    transaction_count = {}
    total_payment = {}

    for session in workout_sessions:

        member_id = session.member_id

        workout_count[member_id] = (
            workout_count.get(member_id, 0) + 1
        )

    for transaction in transactions:

        member_id = transaction.member_id

        transaction_count[member_id] = (
            transaction_count.get(member_id, 0) + 1
        )

        total_payment[member_id] = (
            total_payment.get(member_id, 0)
            + transaction.amount
        )

    # ------------------------------
    # Các cột trong file CSV
    # ------------------------------

    fieldnames = [
        "Ma hoi vien",
        "Ho ten",
        "So dien thoai",
        "Loai hoi vien",
        "Ma goi tap",
        "Ten goi tap",
        "Ma huan luyen vien",
        "Ten huan luyen vien",
        "Ngay tham gia",
        "Ngay het han",
        "Trang thai",
        "Phi hoi vien",
        "So luot tap",
        "So giao dich",
        "Tong tien giao dich"
    ]

    # ------------------------------
    # Ghi dữ liệu CSV
    # ------------------------------

    try:
        with open(
            filename,
            mode="w",
            newline="",
            encoding="utf-8-sig"
        ) as file:

            writer = csv.DictWriter(
                file,
                fieldnames=fieldnames
            )

            writer.writeheader()

            for member in members:

                trainer = member.trainer

                writer.writerow({

                    "Ma hoi vien": member.member_id,

                    "Ho ten": member.full_name,

                    "So dien thoai": member.phone_number,

                    "Loai hoi vien": member.get_member_type(),

                    "Ma goi tap": member.plan.plan_id,

                    "Ten goi tap": member.plan.plan_name,

                    "Ma huan luyen vien": (
                        trainer.trainer_id if trainer else ""
                    ),

                    "Ten huan luyen vien": (
                        trainer.full_name if trainer else "Tu tap"
                    ),

                    "Ngay tham gia": (
                        member.join_date.strftime("%d/%m/%Y")
                    ),

                    "Ngay het han": (
                        member.expiry_date.strftime("%d/%m/%Y")
                    ),

                    "Trang thai": (
                        "Con han" if member.is_active()
                        else "Het han"
                    ),

                    "Phi hoi vien": member.calculate_membership_fee(),

                    "So luot tap": workout_count.get(
                        member.member_id, 0
                    ),

                    "So giao dich": transaction_count.get(
                        member.member_id, 0
                    ),

                    "Tong tien giao dich": total_payment.get(
                        member.member_id, 0
                    )
                })

        print(f"Đã xuất báo cáo thành công: {filename}")

        return filename

    except (OSError, csv.Error, KeyError, AttributeError, TypeError) as error:

        raise RuntimeError(
            f"Lỗi khi xuất báo cáo CSV: {error}"
        ) from error

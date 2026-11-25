"""
Kiểm thử tự động cho Hệ thống Quản lý Hội viên Phòng Gym.
Chạy:  python -m unittest discover tests -v
"""

import os
import sys
import tempfile
import unittest
from datetime import datetime, timedelta
from unittest import mock

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if BASE_DIR not in sys.path:
    sys.path.insert(0, BASE_DIR)

import contextlib
import csv
import io
import json

import data_handler
import gym_management
from gym_app import FullGymManager
from gym_management import GymManager, is_valid_phone, next_id
from models import (
    BasicMember,
    Member,
    MembershipPlan,
    PremiumMember,
    Trainer,
    Transaction,
    WorkoutSession,
    add_months,
)


def make_plan(months=3, price=1350000):
    return MembershipPlan(f"P{months:02d}", f"{months} Tháng", months, price)


def make_trainer(fee=500000):
    return Trainer("T01", "HLV Test", "Fitness", "0901234567", fee)


class TestEncapsulation(unittest.TestCase):
    def test_plan_negative_price_rejected(self):
        with self.assertRaises(ValueError):
            MembershipPlan("P01", "1 Tháng", 1, -1)

    def test_plan_empty_name_rejected(self):
        with self.assertRaises(ValueError):
            MembershipPlan("P01", "  ", 1, 1000)

    def test_trainer_negative_fee_rejected(self):
        with self.assertRaises(ValueError):
            Trainer("T01", "A", "Gym", "0900000000", -5)

    def test_discount_rate_out_of_range_rejected(self):
        with self.assertRaises(ValueError):
            BasicMember("HV01", "A", "0900000000", make_plan(), discount_rate=1.5)

    def test_transaction_negative_amount_rejected(self):
        with self.assertRaises(ValueError):
            Transaction("GD001", "HV01", -100, "Đăng ký mới", "1 Tháng")


class TestAbstractionAndPolymorphism(unittest.TestCase):
    def test_member_is_abstract(self):
        with self.assertRaises(TypeError):
            Member("HV01", "A", "0900000000", make_plan())  # type: ignore[abstract]

    def test_basic_fee_with_discount_and_trainer(self):
        m = BasicMember(
            "HV01",
            "A",
            "0900000000",
            make_plan(3, 1350000),
            make_trainer(500000),
            discount_rate=0.05,
        )
        # 1.350.000 * 0.95 + 500.000 * 3
        self.assertAlmostEqual(m.calculate_membership_fee(), 2782500.0)

    def test_premium_fee_with_vip_and_trainer_discount(self):
        m = PremiumMember(
            "HV02",
            "B",
            "0900000001",
            make_plan(6, 2500000),
            make_trainer(600000),
            vip_perks_fee=200000,
            trainer_discount_rate=0.2,
        )
        # 2.500.000 + 200.000*6 + 600.000*6*0.8
        self.assertAlmostEqual(m.calculate_membership_fee(), 6580000.0)

    def test_str_polymorphism(self):
        basic = BasicMember("HV01", "A", "0900000000", make_plan())
        premium = PremiumMember("HV02", "B", "0900000001", make_plan())
        self.assertIn("Basic", str(basic))
        self.assertIn("Premium", str(premium))


class TestBusinessRules(unittest.TestCase):
    def test_check_expiry(self):
        m = BasicMember(
            "HV01", "A", "0900000000", make_plan(), expiry_date="10/01/2030"
        )
        self.assertTrue(m.check_expiry(datetime(2029, 12, 31)))
        self.assertTrue(m.check_expiry(datetime(2030, 1, 10)))
        self.assertFalse(m.check_expiry(datetime(2030, 1, 11)))

    def test_renew_active_member_accumulates(self):
        future = datetime.now() + timedelta(days=10)
        m = BasicMember(
            "HV01", "A", "0900000000", make_plan(1, 500000), expiry_date=future
        )
        m.renew(make_plan(1, 500000))
        self.assertEqual(m.expiry_date, add_months(future, 1))

    def test_renew_expired_member_starts_from_today(self):
        m = BasicMember(
            "HV01", "A", "0900000000", make_plan(1, 500000), expiry_date="01/01/2020"
        )
        before = datetime.now()
        m.renew(make_plan(1, 500000))
        self.assertGreaterEqual(m.expiry_date, add_months(before, 1))
        self.assertLessEqual(m.expiry_date, add_months(datetime.now(), 1))


class TestPersistence(unittest.TestCase):
    def test_member_dict_roundtrip(self):
        basic = BasicMember(
            "HV01",
            "A",
            "0900000000",
            make_plan(),
            make_trainer(),
            join_date="01/10/2026",
            expiry_date="01/01/2027",
            discount_rate=0.1,
        )
        premium = PremiumMember(
            "HV02",
            "B",
            "0900000001",
            make_plan(6, 2500000),
            None,
            join_date="01/10/2026",
            expiry_date="01/04/2027",
        )
        for original in (basic, premium):
            restored = Member.from_dict(original.to_dict())
            self.assertIs(type(restored), type(original))
            self.assertEqual(restored.to_dict(), original.to_dict())

    def test_manager_save_and_load(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = os.path.join(tmp, "data", "gym.json")
            with mock.patch("builtins.print"):
                first = GymManager(data_file=path)  # tự tạo dữ liệu mẫu + file
                n_members = len(first.members)
                n_tx = len(first.transactions)
                second = GymManager(data_file=path)
            self.assertTrue(os.path.exists(path))
            self.assertEqual(len(second.members), n_members)
            self.assertEqual(len(second.transactions), n_tx)

    def test_default_data_file_independent_of_cwd(self):
        self.assertTrue(os.path.isabs(gym_management.DEFAULT_DATA_FILE))
        old_cwd = os.getcwd()
        with tempfile.TemporaryDirectory() as tmp:
            target = os.path.join(tmp, "store", "gym.json")
            other_cwd = os.path.join(tmp, "elsewhere")
            os.makedirs(other_cwd)
            try:
                os.chdir(other_cwd)
                with (
                    mock.patch.object(gym_management, "DEFAULT_DATA_FILE", target),
                    mock.patch("builtins.print"),
                ):
                    manager = GymManager()
                self.assertEqual(manager.data_file, target)
                # Không được tạo thư mục data/ ở thư mục đang đứng
                self.assertFalse(os.path.exists(os.path.join(other_cwd, "data")))
            finally:
                os.chdir(old_cwd)


class TestCalendarMonths(unittest.TestCase):
    def test_add_months_plain(self):
        self.assertEqual(add_months(datetime(2026, 1, 1), 12), datetime(2027, 1, 1))

    def test_add_months_end_of_month(self):
        self.assertEqual(add_months(datetime(2027, 1, 31), 1), datetime(2027, 2, 28))
        self.assertEqual(add_months(datetime(2028, 1, 31), 1), datetime(2028, 2, 29))

    def test_default_expiry_uses_calendar_months(self):
        m = BasicMember(
            "HV01", "A", "0900000000", make_plan(12, 4500000), join_date="01/01/2026"
        )
        self.assertEqual(m.expiry_date, datetime(2027, 1, 1))


class TestHelpers(unittest.TestCase):
    def test_phone_validation(self):
        self.assertTrue(is_valid_phone("0911222333"))
        for bad in ("", "y", "0912", "1911222333", "09112223334", "09112a2333"):
            self.assertFalse(is_valid_phone(bad), bad)

    def test_next_id_uses_max_not_length(self):
        self.assertEqual(next_id("GD", ["GD001", "GD002", "GD007"]), "GD008")
        self.assertEqual(next_id("LT", []), "LT001")


class ManagerTestCase(unittest.TestCase):
    """Dựng GymManager trên file tạm, dữ liệu do từng test tự đặt."""

    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.path = os.path.join(self.tmp.name, "data", "gym.json")
        with mock.patch("builtins.print"):
            self.gm = FullGymManager(data_file=self.path)
        self.plan = self.gm.plans[1]  # P03
        self.trainer = self.gm.trainers[0]  # T01
        self.gm.members, self.gm.transactions, self.gm.workout_sessions = [], [], []

    def run_with_input(self, func, *answers):
        out = io.StringIO()
        with (
            mock.patch("builtins.input", side_effect=list(answers)),
            contextlib.redirect_stdout(out),
        ):
            result = func()
        return out.getvalue(), result

    def add_basic(self, member_id="HV01", expiry="01/01/2099", phone="0900000001"):
        m = BasicMember(
            member_id,
            "Nguyen Test",
            phone,
            self.plan,
            expiry_date=expiry,
            join_date="01/01/2026",
        )
        self.gm.members.append(m)
        return m


class TestAddAndValidation(ManagerTestCase):
    def test_add_member_creates_transaction_and_saves(self):
        self.run_with_input(
            self.gm.add_member, "HV10", "Le Van B", "0911222333", "1", "P03", "T01"
        )
        self.assertEqual(len(self.gm.members), 1)
        self.assertEqual(self.gm.transactions[0].transaction_id, "GD001")
        self.assertAlmostEqual(self.gm.transactions[0].amount, 1350000 + 500000 * 3)
        with open(self.path, encoding="utf-8") as f:
            self.assertEqual(len(json.load(f)["members"]), 1)

    def test_add_member_rejects_bad_phone_duplicate_and_bad_trainer(self):
        # SĐT sai -> hỏi lại; nhập đúng ở lần 2 thì tạo hội viên
        self.run_with_input(
            self.gm.add_member, "HV10", "A", "abc", "0911222333", "1", "P03", "0"
        )
        self.assertEqual(len(self.gm.members), 1)
        self.gm.members.clear()
        self.add_basic("HV10")
        out, _ = self.run_with_input(self.gm.add_member, "hv10")
        self.assertIn("đã tồn tại", out)
        self.run_with_input(
            self.gm.add_member, "HV11", "A", "0911222333", "1", "P03", "T99"
        )
        self.assertEqual(len(self.gm.members), 1)

    def test_deleted_member_id_cannot_be_reused(self):
        self.add_basic("HV01")
        self.gm.transactions.append(
            Transaction("GD001", "HV01", 1000, "Đăng ký mới", "3 Tháng")
        )
        self.run_with_input(self.gm.delete_member, "HV01", "y")
        self.assertEqual(self.gm.members, [])
        out, _ = self.run_with_input(self.gm.add_member, "HV01")
        self.assertIn("đã từng được dùng", out)
        self.assertEqual(self.gm.members, [])

    def test_delete_cancel_keeps_member(self):
        self.add_basic("HV01")
        self.run_with_input(self.gm.delete_member, "HV01", "n")
        self.assertEqual(len(self.gm.members), 1)

    def test_update_rejects_bad_phone(self):
        m = self.add_basic("HV01")
        self.run_with_input(self.gm.update_member, "HV01", "Ten Moi", "123", "n")
        self.assertEqual(m.phone_number, "0900000001")
        self.assertNotEqual(m.full_name, "Ten Moi")


class TestRenewCheckinAssign(ManagerTestCase):
    def test_renew_creates_transaction_with_new_id(self):
        m = self.add_basic("HV01", expiry="01/01/2020")
        self.gm.transactions.append(
            Transaction("GD005", "HV01", 1, "Đăng ký mới", "1 Tháng")
        )
        self.run_with_input(self.gm.renew_membership, "HV01", "P01")
        self.assertTrue(m.is_active())
        self.assertEqual(self.gm.transactions[-1].transaction_id, "GD006")
        self.assertEqual(self.gm.transactions[-1].transaction_type, "Gia hạn gói")

    def test_checkin_rejects_expired_member(self):
        self.add_basic("HV01", expiry="01/01/2020")
        out, _ = self.run_with_input(self.gm.record_checkin, "HV01")
        self.assertIn("hết hạn", out)
        self.assertEqual(self.gm.workout_sessions, [])

    def test_checkin_same_day_needs_confirmation(self):
        self.add_basic("HV01")
        self.run_with_input(self.gm.record_checkin, "HV01", "")
        self.assertEqual(len(self.gm.workout_sessions), 1)
        self.run_with_input(self.gm.record_checkin, "HV01", "n")  # từ chối lượt thứ 2
        self.assertEqual(len(self.gm.workout_sessions), 1)
        self.run_with_input(self.gm.record_checkin, "HV01", "y", "")  # đồng ý
        self.assertEqual(len(self.gm.workout_sessions), 2)
        self.assertEqual(self.gm.workout_sessions[1].session_id, "LT002")

    def test_assign_trainer_and_unknown_trainer(self):
        m = self.add_basic("HV01")
        self.run_with_input(self.gm.assign_trainer, "HV01", "T01")
        self.assertIs(m.trainer, self.trainer)
        self.run_with_input(self.gm.assign_trainer, "HV01", "T99")
        self.assertIs(m.trainer, self.trainer)
        self.run_with_input(self.gm.assign_trainer, "HV01", "0")
        self.assertIsNone(m.trainer)

    def test_add_plan_and_trainer_validation(self):
        n_plans, n_trainers = len(self.gm.plans), len(self.gm.trainers)
        self.run_with_input(self.gm.add_plan, "P03")  # trùng mã
        self.run_with_input(
            self.gm.add_plan, "P09", "9 Tháng", "0", "1"
        )  # thời hạn < 1
        self.run_with_input(self.gm.add_plan, "P09", "9 Tháng", "9", "-5")
        self.assertEqual(len(self.gm.plans), n_plans)
        self.run_with_input(self.gm.add_plan, "P09", "9 Tháng", "9", "900000")
        self.assertEqual(len(self.gm.plans), n_plans + 1)
        self.run_with_input(
            self.gm.add_trainer, "T04", "A B", "Gym", "123", "100"
        )  # SĐT sai
        self.assertEqual(len(self.gm.trainers), n_trainers)
        self.run_with_input(
            self.gm.add_trainer, "T04", "A B", "Gym", "0900000000", "100000"
        )
        self.assertEqual(len(self.gm.trainers), n_trainers + 1)

    def test_warn_expiring_members(self):
        today_str = datetime.now().strftime("%d/%m/%Y")
        soon = (datetime.now() + timedelta(days=3)).strftime("%d/%m/%Y")
        self.add_basic("HV00", expiry=today_str, phone="0900000000")
        self.add_basic("HV01", expiry=soon, phone="0900000001")
        self.add_basic("HV02", expiry="01/01/2099", phone="0900000002")

        # Mốc biên N = 0: chỉ hiển thị hội viên hết hạn đúng hôm nay
        out_zero, _ = self.run_with_input(self.gm.warn_expiring_members, "0")
        self.assertIn("HV00", out_zero)
        self.assertIn("HẾT HẠN HÔM NAY", out_zero)
        self.assertNotIn("HV01", out_zero)
        self.assertNotIn("HV02", out_zero)

        # N = 7: hiển thị HV00 trước HV01 theo thứ tự tăng dần số ngày còn lại
        out_seven, _ = self.run_with_input(self.gm.warn_expiring_members, "7")
        self.assertIn("HV00", out_seven)
        self.assertIn("HV01", out_seven)
        self.assertNotIn("HV02", out_seven)
        self.assertLess(out_seven.index("HV00"), out_seven.index("HV01"))

        # Mốc biên âm N = -1: báo lỗi an toàn, không crash
        out_neg, _ = self.run_with_input(self.gm.warn_expiring_members, "-1")
        self.assertIn("Lỗi", out_neg)


class TestSearchSortStatistics(ManagerTestCase):
    def test_search_id_is_exact_but_name_is_partial(self):
        self.add_basic("HV1", phone="0900000001")
        self.add_basic("HV10", phone="0900000010")
        _, found = self.run_with_input(self.gm.search_members, "1", "hv1")
        self.assertEqual([m.member_id for m in found], ["HV1"])
        _, found = self.run_with_input(self.gm.search_members, "1", "nguyen")
        self.assertEqual(len(found), 2)

    def test_search_by_plan_id_exact(self):
        self.add_basic("HV1")
        _, found = self.run_with_input(self.gm.search_members, "4", "P03")
        self.assertEqual(len(found), 1)
        _, found = self.run_with_input(self.gm.search_members, "4", "P0")
        self.assertEqual(found, [])

    def test_sort_does_not_change_original_order_or_save(self):
        self.add_basic("HV2", expiry="01/01/2098", phone="0900000002")
        self.add_basic("HV1", expiry="01/01/2097", phone="0900000001")
        before = [m.member_id for m in self.gm.members]
        with mock.patch.object(self.gm, "save_data") as saver:
            _, result = self.run_with_input(self.gm.sort_members, "3", "1")
        self.assertEqual([m.member_id for m in result], ["HV1", "HV2"])
        self.assertEqual([m.member_id for m in self.gm.members], before)
        saver.assert_not_called()

    def test_sort_empty_list_is_safe(self):
        _, result = self.run_with_input(self.gm.sort_members)
        self.assertEqual(result, [])

    def test_statistics_attendance_rate(self):
        self.add_basic("HV1")
        self.add_basic("HV2", phone="0900000002")
        self.add_basic("HV3", expiry="01/01/2020", phone="0900000003")
        self.gm.workout_sessions = [
            WorkoutSession("LT001", "HV1"),
            WorkoutSession("LT002", "HV1"),
            WorkoutSession("LT003", "HV3"),
        ]
        self.gm.transactions = [
            Transaction("GD001", "HV1", 1000, "Đăng ký mới", "3 Tháng"),
            Transaction("GD002", "HV2", 500, "Đăng ký mới", "3 Tháng"),
        ]
        _, stats = self.run_with_input(self.gm.statistics_menu, "n")
        self.assertEqual(stats["active_members"], 2)
        self.assertAlmostEqual(
            stats["attendance_rate"], 50.0
        )  # chỉ HV1 trong 2 hội viên còn hạn
        self.assertAlmostEqual(stats["total_revenue"], 1500)

    def test_statistics_with_no_active_member_is_zero_percent(self):
        self.add_basic("HV1", expiry="01/01/2020")
        _, stats = self.run_with_input(self.gm.statistics_menu)
        self.assertEqual(stats["attendance_rate"], 0.0)


class TestPersistenceSafety(unittest.TestCase):
    def test_corrupt_json_is_backed_up_not_lost(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = os.path.join(tmp, "gym.json")
            with open(path, "w", encoding="utf-8") as f:
                f.write("{ file hong")
            with mock.patch("builtins.print"):
                manager = GymManager(data_file=path)
            backups = [n for n in os.listdir(tmp) if n.endswith(".bak")]
            self.assertEqual(len(backups), 1)
            with open(os.path.join(tmp, backups[0]), encoding="utf-8") as f:
                self.assertEqual(f.read(), "{ file hong")
            self.assertGreater(len(manager.members), 0)

    def test_shipped_data_file_loads(self):
        with mock.patch("builtins.print"):
            data = data_handler.load_data(data_handler.DATA_FILE)
        ids = [m.member_id for m in data["members"]]
        self.assertGreater(len(ids), 0)
        self.assertEqual(len(ids), len(set(ids)))  # không trùng mã

    def test_export_csv(self):
        with tempfile.TemporaryDirectory() as tmp:
            with mock.patch("builtins.print"):
                manager = FullGymManager(data_file=os.path.join(tmp, "g.json"))
                target = os.path.join(tmp, "report.csv")
                data_handler.export_report_csv(
                    {
                        "members": manager.members,
                        "workout_sessions": manager.workout_sessions,
                        "transactions": manager.transactions,
                    },
                    target,
                )
            with open(target, encoding="utf-8-sig", newline="") as f:
                rows = list(csv.DictReader(f))
            self.assertEqual(len(rows), len(manager.members))


if __name__ == "__main__":
    unittest.main(verbosity=2)

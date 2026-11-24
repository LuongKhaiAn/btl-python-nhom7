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

import gym_management  # noqa: E402
from gym_management import GymManager  # noqa: E402
from models import (  # noqa: E402
    BasicMember,
    Member,
    MembershipPlan,
    PremiumMember,
    Trainer,
    Transaction,
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
        m = BasicMember("HV01", "A", "0900000000", make_plan(3, 1350000),
                        make_trainer(500000), discount_rate=0.05)
        # 1.350.000 * 0.95 + 500.000 * 3
        self.assertAlmostEqual(m.calculate_membership_fee(), 2782500.0)

    def test_premium_fee_with_vip_and_trainer_discount(self):
        m = PremiumMember("HV02", "B", "0900000001", make_plan(6, 2500000),
                          make_trainer(600000), vip_perks_fee=200000,
                          trainer_discount_rate=0.2)
        # 2.500.000 + 200.000*6 + 600.000*6*0.8
        self.assertAlmostEqual(m.calculate_membership_fee(), 6580000.0)

    def test_str_polymorphism(self):
        basic = BasicMember("HV01", "A", "0900000000", make_plan())
        premium = PremiumMember("HV02", "B", "0900000001", make_plan())
        self.assertIn("Basic", str(basic))
        self.assertIn("Premium", str(premium))


class TestBusinessRules(unittest.TestCase):
    def test_check_expiry(self):
        m = BasicMember("HV01", "A", "0900000000", make_plan(),
                        expiry_date="10/01/2030")
        self.assertTrue(m.check_expiry(datetime(2029, 12, 31)))
        self.assertTrue(m.check_expiry(datetime(2030, 1, 10)))
        self.assertFalse(m.check_expiry(datetime(2030, 1, 11)))

    def test_renew_active_member_accumulates(self):
        future = datetime.now() + timedelta(days=10)
        m = BasicMember("HV01", "A", "0900000000", make_plan(1, 500000),
                        expiry_date=future)
        m.renew(make_plan(1, 500000))
        self.assertEqual(m.expiry_date, future + timedelta(days=30))

    def test_renew_expired_member_starts_from_today(self):
        m = BasicMember("HV01", "A", "0900000000", make_plan(1, 500000),
                        expiry_date="01/01/2020")
        before = datetime.now()
        m.renew(make_plan(1, 500000))
        self.assertGreaterEqual(m.expiry_date, before + timedelta(days=30))
        self.assertLessEqual(m.expiry_date, datetime.now() + timedelta(days=30))


class TestPersistence(unittest.TestCase):
    def test_member_dict_roundtrip(self):
        basic = BasicMember("HV01", "A", "0900000000", make_plan(),
                            make_trainer(), join_date="01/10/2026",
                            expiry_date="01/01/2027", discount_rate=0.1)
        premium = PremiumMember("HV02", "B", "0900000001", make_plan(6, 2500000),
                                None, join_date="01/10/2026",
                                expiry_date="01/04/2027")
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
                with mock.patch.object(gym_management, "DEFAULT_DATA_FILE", target), \
                        mock.patch("builtins.print"):
                    manager = GymManager()
                self.assertEqual(manager.data_file, target)
                # Không được tạo thư mục data/ ở thư mục đang đứng
                self.assertFalse(os.path.exists(os.path.join(other_cwd, "data")))
            finally:
                os.chdir(old_cwd)


if __name__ == "__main__":
    unittest.main(verbosity=2)

import os
import sys
import unittest
from datetime import datetime, timedelta

# Đảm bảo đường dẫn import module từ thư mục gốc
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from gym_management import (
    MembershipPlan,
    Plan,
    Trainer,
    Member,
    BasicMember,
    PremiumMember,
    WorkoutSession,
    Transaction,
    GymManager,
)


class TestGymManagement(unittest.TestCase):
    def setUp(self):
        self.test_file = "test_gym_storage.json"
        if os.path.exists(self.test_file):
            os.remove(self.test_file)

        self.p1 = Plan("P01", "1 Tháng", 1, 500000)
        self.p6 = Plan("P06", "6 Tháng", 6, 2500000)
        self.t1 = Trainer("T01", "Nguyễn Văn HLV", "Fitness", "0901234567", monthly_fee=500000.0)
        self.manager = GymManager(data_file=self.test_file)

    def tearDown(self):
        if os.path.exists(self.test_file):
            os.remove(self.test_file)

    def test_tc01_basic_member_polymorphic_fee(self):
        m_no_trainer = BasicMember("HV01", "An", "090", self.p1, None)
        self.assertEqual(m_no_trainer.calculate_membership_fee(), 500000.0)

        m_with_trainer = BasicMember("HV02", "Binh", "091", self.p1, self.t1)
        expected = 500000.0 + (500000.0 * 1)
        self.assertEqual(m_with_trainer.calculate_membership_fee(), expected)

    def test_tc02_premium_member_polymorphic_fee(self):
        m_vip = PremiumMember("HV03", "Cuong", "092", self.p6, self.t1, vip_perks_fee=200000.0, trainer_discount_rate=0.2)
        base_cost = 2500000.0 + (200000.0 * 6)
        trainer_cost = 500000.0 * 6 * (1 - 0.2)
        expected = base_cost + trainer_cost
        self.assertEqual(m_vip.calculate_membership_fee(), expected)

    def test_tc03_renew_active_member(self):
        now = datetime.now()
        future_expiry = now + timedelta(days=20)
        m = BasicMember("HV01", "An", "090", self.p1, None, expiry_date=future_expiry)
        m.renew(self.p1)
        expected_expiry = future_expiry + timedelta(days=30)
        self.assertEqual(m.expiry_date.strftime("%d/%m/%Y"), expected_expiry.strftime("%d/%m/%Y"))

    def test_tc04_renew_expired_member(self):
        now = datetime.now()
        past_expiry = now - timedelta(days=15)
        m = BasicMember("HV01", "An", "090", self.p1, None, expiry_date=past_expiry)
        m.renew(self.p1)
        expected_expiry = now + timedelta(days=30)
        self.assertEqual(m.expiry_date.strftime("%d/%m/%Y"), expected_expiry.strftime("%d/%m/%Y"))

    def test_tc05_checkin_active_member(self):
        now = datetime.now()
        m = BasicMember("HV01", "An", "090", self.p1, None, expiry_date=now + timedelta(days=10))
        self.assertTrue(m.is_active())

    def test_tc06_checkin_expired_member(self):
        now = datetime.now()
        m = BasicMember("HV01", "An", "090", self.p1, None, expiry_date=now - timedelta(days=5))
        self.assertFalse(m.is_active())

    def test_tc07_transaction_recording(self):
        tx_count_before = len(self.manager.transactions)
        tx = Transaction("TX999", "HV01", 500000.0, "Gia hạn", "1 Tháng")
        self.manager.transactions.append(tx)
        self.assertEqual(len(self.manager.transactions), tx_count_before + 1)

    def test_tc08_revenue_from_transactions(self):
        self.manager.transactions = [
            Transaction("TX1", "HV1", 500000.0, "Đăng ký mới", "1 Tháng"),
            Transaction("TX2", "HV2", 1000000.0, "Gia hạn", "3 Tháng"),
        ]
        total = sum(tx.amount for tx in self.manager.transactions)
        self.assertEqual(total, 1500000.0)

    def test_tc09_json_persistence(self):
        self.manager.save_data()
        self.assertTrue(os.path.exists(self.test_file))

        manager2 = GymManager(data_file=self.test_file)
        self.assertEqual(len(manager2.members), len(self.manager.members))
        self.assertEqual(len(manager2.transactions), len(self.manager.transactions))
        self.assertEqual(len(manager2.workout_sessions), len(self.manager.workout_sessions))

    def test_tc10_search_and_filter(self):
        now = datetime.now()
        m_active = BasicMember("HV10", "Nguyen Active", "0981", self.p1, None, expiry_date=now + timedelta(days=10))
        m_expired = PremiumMember("HV11", "Tran Expired", "0982", self.p1, None, expiry_date=now - timedelta(days=10))
        self.manager.members = [m_active, m_expired]

        active_list = [m for m in self.manager.members if m.is_active()]
        self.assertEqual(len(active_list), 1)
        self.assertEqual(active_list[0].member_id, "HV10")

        premium_list = [m for m in self.manager.members if isinstance(m, PremiumMember)]
        self.assertEqual(len(premium_list), 1)
        self.assertEqual(premium_list[0].member_id, "HV11")

    def test_tc11_sort_by_name(self):
        m1 = BasicMember("HV01", "Nguyen Van B", "090", self.p1)
        m2 = BasicMember("HV02", "Tran Thi A", "091", self.p1)
        self.manager.members = [m1, m2]
        self.manager.members.sort(key=lambda m: m.full_name.split()[-1].lower())
        self.assertEqual(self.manager.members[0].member_id, "HV02")

    def test_tc12_check_expiry_method(self):
        now = datetime.now()
        m_active = BasicMember("HV01", "An", "090", self.p1, None, expiry_date=now + timedelta(days=5))
        self.assertTrue(m_active.check_expiry())
        self.assertTrue(m_active.is_active())

        m_expired = BasicMember("HV02", "Binh", "091", self.p1, None, expiry_date=now - timedelta(days=2))
        self.assertFalse(m_expired.check_expiry())
        self.assertFalse(m_expired.is_active())

    def test_tc13_membership_plan_properties_and_validation(self):
        mp = MembershipPlan("MP01", "Gói 12 Tháng", 12, 4500000.0)
        self.assertEqual(mp.plan_id, "MP01")
        self.assertEqual(mp.duration_months, 12)
        self.assertEqual(mp.price, 4500000.0)
        self.assertIs(Plan, MembershipPlan)

        with self.assertRaises(ValueError):
            mp.duration_months = 0
        with self.assertRaises(ValueError):
            mp.price = -1000.0
        with self.assertRaises(ValueError):
            mp.plan_id = ""

    def test_tc14_encapsulation_validation(self):
        m = BasicMember("HV01", "Nguyen An", "0901", self.p1, None)
        with self.assertRaises(ValueError):
            m.discount_rate = 1.2
        with self.assertRaises(ValueError):
            m.member_id = "   "

        t = Trainer("T01", "HLV", "Gym", "090", 500000.0)
        with self.assertRaises(ValueError):
            t.monthly_fee = -100

        tx = Transaction("TX01", "HV01", 500000.0, "Đăng ký mới", "1 Tháng")
        with self.assertRaises(ValueError):
            tx.amount = -50000

    def test_tc15_str_method_for_all_classes(self):
        # 1. MembershipPlan
        mp = MembershipPlan("MP01", "Gói 1 Tháng", 1, 500000.0)
        self.assertIn("MP01", str(mp))
        self.assertIn("Gói 1 Tháng", str(mp))

        # 2. Trainer
        t = Trainer("T01", "Nguyễn HLV", "Fitness", "0901234567", 500000.0)
        self.assertIn("T01", str(t))
        self.assertIn("Nguyễn HLV", str(t))

        # 3. BasicMember
        bm = BasicMember("HV01", "Nguyễn An", "0912345678", mp, t)
        self.assertIn("HV01", str(bm))
        self.assertIn("Basic", str(bm))

        # 4. PremiumMember
        pm = PremiumMember("HV02", "Lê VIP", "0987654321", mp, t)
        self.assertIn("HV02", str(pm))
        self.assertIn("Premium", str(pm))

        # 5. WorkoutSession
        ws = WorkoutSession("WS01", "HV01", notes="Chạy bộ")
        self.assertIn("WS01", str(ws))
        self.assertIn("HV01", str(ws))

        # 6. Transaction
        tx = Transaction("TX01", "HV01", 500000.0, "Đăng ký mới", "Gói 1 Tháng")
        self.assertIn("TX01", str(tx))
        self.assertIn("HV01", str(tx))


if __name__ == "__main__":
    unittest.main(verbosity=2)

import unittest
from orders import parse_chat, parse_item, build_summary


class TestOrders(unittest.TestCase):
    def test_parse_item_formats(self):
        self.assertEqual(parse_item("2 kg tomato"), ("tomato", 2.0, "kg"))
        self.assertEqual(parse_item("potatoes 3kg"), ("potato", 3.0, "kg"))
        self.assertEqual(parse_item("500 gm paneer"), ("paneer", 500.0, "g"))
        self.assertIsNone(parse_item("good morning bhaiya"))

    def test_synonyms_and_plurals(self):
        self.assertEqual(parse_item("1 kg tamatar")[0], "tomato")
        self.assertEqual(parse_item("2 kg tomatoes")[0], "tomato")

    def test_chatter_ignored_and_cancel_works(self):
        rows = parse_chat(open("sample_chat.txt", encoding="utf-8").readlines())
        self.assertNotIn("Arjun", {r["customer"] for r in rows})  # cancelled
        self.assertEqual(len([r for r in rows if r["customer"] == "Ramesh"]), 4)

    def test_summary_totals(self):
        rows = parse_chat(open("sample_chat.txt", encoding="utf-8").readlines())
        self.assertRegex(build_summary(rows), r"onion\s+2 kg")  # 1 + 1 on 12/10


if __name__ == "__main__":
    unittest.main()

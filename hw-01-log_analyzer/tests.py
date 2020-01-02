import gzip
from datetime import datetime
import os
import unittest

from log_analyzer import select_recent_log, build_report
from utils import generate_logs


def convert_plain_to_gz(fn):
    with open(fn, 'r') as f:
        data = f.read()
    with gzip.open(fn + ".gz", 'wb') as f:
        f.write(bytes(data))


def convert_gz_to_plain(fn):
    with gzip.open(fn, 'rb') as f:
        data = str(f.read())
    with open(fn[:-3], 'w') as f:
        f.write(data)


class TestLogAnalyzer(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.config = {
            "REPORT_SIZE": 1000,
            "REPORT_DIR": "./test_data/reports",
            "REPORT_TEMPLATE": "report.html",
            "LOG_DIR": "./test_data/log",
            "LOG": None,
        }
        if not os.path.exists(cls.config["LOG_DIR"]):
            print("Generating test logs...")
            os.makedirs(cls.config["LOG_DIR"])
            generate_logs("log-10k-20190102.gz", cls.config["LOG_DIR"], 10)
        else:
            print("Test logs exists. Skipping generation.")
        if not os.path.exists(cls.config["REPORT_DIR"]):
            os.makedirs(cls.config["REPORT_DIR"])

    def test_log_seletion(self):
        """Test should pick only .gz or .txt most recent report."""
        # Create most recent report with unintendent format
        fn = os.path.join(self.config["LOG_DIR"], "log-29990101.log.bz")
        with open(fn, 'wb') as f:
            f.write(b"...")

        path = select_recent_log(self.config["LOG_DIR"])
        self.assertNotEqual(path, fn)

    def test_report_from_gz(self):
        """Check that .html file with requred name was build from .gz."""
        path = select_recent_log(self.config["LOG_DIR"])
        if not path.endswith(".gz"):
            convert_plain_to_gz(path)
        build_report(self.config)

        dt = datetime.today()
        yy, mm, dd = dt.year, dt.month, dt.day
        fn_out = os.path.join(self.config["REPORT_DIR"],
                              f"report-{yy}-{mm:02d}-{dd:02d}.html")
        self.assertTrue(os.path.exists(fn_out))

    def test_report_from_plain(self):
        """Check that .html file with requred name was build from .gz."""
        path = select_recent_log(self.config["LOG_DIR"])
        if path.endswith(".gz"):
            convert_gz_to_plain(path)
        build_report(self.config)

        dt = datetime.today()
        yy, mm, dd = dt.year, dt.month, dt.day
        fn_out = os.path.join(self.config["REPORT_DIR"],
                              f"report-{yy}-{mm:02d}-{dd:02d}.html")
        self.assertTrue(os.path.exists(fn_out))

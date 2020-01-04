import gzip
from datetime import datetime
import os
import unittest

from log_analyzer import select_recent_log, build_report
from utils import generate_logs


def get_cur_date():
    """Return current yyyy, mm, dd. """
    dt = datetime.today()
    return dt.year, dt.month, dt.day


def convert_plain_to_gz(fn):
    with open(fn, 'r') as f:
        data = f.read()
    with gzip.open(fn[:-3] + ".gz", 'wb') as f:
        f.write(data.encode())
    os.system(f"rm {fn}")


def convert_gz_to_plain(fn):
    with gzip.open(fn, 'rb') as f:
        data = f.read().decode("utf-8")
    with open(fn[:-3] + ".log", 'w') as f:
        f.write(data)
    os.system(f"rm {fn}")


def broke_log(fn_source, fn_out, broke_perc):
    """Create log file with given percentage of broken
    records.

    Args:
        fn_source (str): path to the source log.
        fn_out (str): path to the modified log.
        broke_perc (float): percentage of broken records (0..1).

    Function will rewirte first records with incorrect data.
    """
    # Open gz or plain file and save str lines
    def fopen(x, m='r'):
        return gzip.open(x, f'{m}b') if x.endswith('.gz') else open(x, m)
    with fopen(fn_source) as f:
        lines = f.readlines()
    if fn_source.endswith("gz"):
        lines = list(map(lambda x: x.decode('utf-8'), lines))

    # Store broken and original lines to output file
    store_binary = fn_out.endswith('gz')

    for i in range(int(broke_perc * len(lines))):
        lines[i] = "broken\n"
    with fopen(fn_out, 'w') as f:
        for l in lines:
            if store_binary:
                f.write(l.encode())
            else:
                f.write(l)


class TestLogAnalyzer(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.config = {
            "REPORT_SIZE": 1000,
            "REPORT_DIR": "./test_data/reports",
            "REPORT_TEMPLATE": "report.html",
            "LOG_DIR": "./test_data/log",
            "LOG": None,
            "ERROR_RATE_THRESHOLD": 0.7
        }
        if not os.path.exists(cls.config["LOG_DIR"]):
            os.makedirs(cls.config["LOG_DIR"])
        generate_logs("log-10k-20190102.gz", cls.config["LOG_DIR"], 10)
        if not os.path.exists(cls.config["REPORT_DIR"]):
            os.makedirs(cls.config["REPORT_DIR"])

    @classmethod
    def tearDownClass(cls):
        os.system(f"rm -r {cls.config['LOG_DIR']}")
        os.system(f"rm -r {cls.config['REPORT_DIR']}")

    def test_no_dir_exists(self):
        """Test that if given directory with logs no exists. """
        old_log_dir = self.config["LOG_DIR"]
        new_log_dir = "noexisting"
        if not os.path.exists(old_log_dir):
            os.makedirs(new_log_dir)
        self.config["LOG_DIR"] = new_log_dir

        with self.assertRaises(Exception):
            build_report(self.config)
        self.config["LOG_DIR"] = old_log_dir
        os.system(f"rm -r {new_log_dir}")

    def test_no_logs_exist(self):
        """Test scenario when no logs for processing exist. """
        # Create new empty directory
        old_log_dir = self.config["LOG_DIR"]
        new_log_dir = "./test_data/wrong_log_dir"
        if not os.path.exists(new_log_dir):
            os.makedirs(new_log_dir)
        self.config["LOG_DIR"] = new_log_dir

        # No exceptions should be raised
        build_report(self.config)

        self.config["LOG_DIR"] = old_log_dir
        os.system(f"rm -r {new_log_dir}")

    def test_log_seletion(self):
        """Test should pick only .gz or .txt most recent report."""
        # Create most recent report with unintendent format
        fn = os.path.join(self.config["LOG_DIR"], "log-29990101.log.bz")
        with open(fn, 'wb') as f:
            f.write(b"...")

        path, _ = select_recent_log(self.config["LOG_DIR"])
        self.assertNotEqual(path, fn)

    def test_report_from_gz(self):
        """Check that .html file with requred name was build from .gz."""
        path, dt = select_recent_log(self.config["LOG_DIR"])
        if not path.endswith(".gz"):
            convert_plain_to_gz(path)
        build_report(self.config)

        yy, mm, dd = dt.year, dt.month, dt.day
        fn_out = os.path.join(self.config["REPORT_DIR"],
                              f"report-{yy}-{mm:02d}-{dd:02d}.html")

        self.assertTrue(os.path.exists(fn_out))
        os.system(f"rm {fn_out}")

    def test_report_from_plain(self):
        """Check that .html file with requred name was build from .gz."""
        path, dt = select_recent_log(self.config["LOG_DIR"])
        if path.endswith(".gz"):
            convert_gz_to_plain(path)
        build_report(self.config)

        yy, mm, dd = dt.year, dt.month, dt.day
        fn_out = os.path.join(self.config["REPORT_DIR"],
                              f"report-{yy}-{mm:02d}-{dd:02d}.html")

        self.assertTrue(os.path.exists(fn_out))
        os.system(f"rm {fn_out}")

    def test_sligthly_broken_log(self):
        """Process report with 10% of broken records.
        Report should be saved.
        """
        path, dt = select_recent_log(self.config["LOG_DIR"])
        log_name = "log-21000101.log.gz"
        fn_log_out = os.path.join(self.config["LOG_DIR"], log_name)
        broke_log(path, fn_log_out, broke_perc=0.1)

        build_report(self.config)

        # Check that file exists
        yy, mm, dd = 2100, 1, 1
        fn_report_out = os.path.join(self.config["REPORT_DIR"],
                                     f"report-{yy}-{mm:02d}-{dd:02d}.html")
        self.assertTrue(os.path.exists(fn_report_out))
        os.system(f"rm {fn_report_out}; rm {fn_log_out}")

    def test_mostly_broken_log(self):
        """Process report with 10% of broken records.
        Report should be saved.
        """
        path, dt = select_recent_log(self.config["LOG_DIR"])
        log_name = "my.log-21000101.gz"
        fn_log_out = os.path.join(self.config["LOG_DIR"], log_name)
        broke_log(path, fn_log_out, broke_perc=0.9)

        build_report(self.config)

        # Check that file exists
        yy, mm, dd = 2100, 1, 1
        fn_report_out = os.path.join(self.config["REPORT_DIR"],
                                     f"report-{yy}-{mm:02d}-{dd:02d}.html")

        self.assertFalse(os.path.exists(fn_report_out))
        os.system(f"rm {fn_report_out}; rm {fn_log_out}")

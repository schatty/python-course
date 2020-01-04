import os
from string import Template
from datetime import date
import gzip
from collections import defaultdict
import logging
import logging.config

config = {
    "REPORT_SIZE": 1000,
    "REPORT_DIR": "./reports",
    "REPORT_TEMPLATE": "report.html",
    "ERROR_RATE_THRESHOLD": 0.7,
    "LOG_DIR": "./log",
    "LOG": None,
}

# Set logging
logging.basicConfig(format="[%(asctime)s] %(levelname).1s %(message)s",
                    datefmt="%Y.%m.%d %H:%M:%S", level=logging.INFO)
if config["LOG"] is not None:
    logging.fileConfig(os.path.join(config["LOG_DIR"], config["LOG_NAME"]))


def split_by_space(s, item_symbols=("\"", "[", "]")):
    """Split line by spaces but do not split contenst inside quotes.

    Args:
        s (str): log record.
        item_symbols (tuple): tuple of symbols treated as start/end log entity.

    Returns:
        list: list of parsed log items.
    """
    items = []
    i_start = 0
    inside_item = False
    for i in range(len(s)):
        if s[i] in item_symbols:
            inside_item = not inside_item
        if s[i] == " ":
            if not inside_item:
                if i - i_start > 0:
                    items.append(s[i_start:i])
                i_start = i+1
    # Last item
    if len(s) - 1 - i_start > 0:
        items.append(s[i_start:i])
    return items


def read_log(f):
    """Generator for reading log file. """
    while True:
        record = f.readline()
        if not record:
            break
        yield record


def parse_line(s):
    """Parse log line according to log format.

    log_format  $remote_addr  $remote_user $http_x_real_ip [$time_local]
                  "$request" ''$status $body_bytes_sent "$http_referer"
                  "$http_user_agent" "$http_x_forwarded_for"
                  "$http_X_REQUEST_ID" "$http_X_RB_USER"
                  $request_time;

    Args:
        s (str): log line.

    Returns:
        dict: dict with keys as log item name or None in case of exception.
    """
    try:
        item_names = ["remote_addr", "remote_user", "http_x_real_ip",
                      "time_local", "request", "status", "body_bytes_sent",
                      "http_referer", "http_user_agent",
                      "http_x_forwarded_for", "http_X_REQUEST_ID",
                      "http_X_RB_USER", "request_time"]
        item_vals = split_by_space(s)
        raw_record = {k: v for k, v in zip(item_names, item_vals)}
        processed_record = process_log_record(raw_record)
        return processed_record
    except Exception:
        return None


def process_log_record(log_dict):
    """
    Process elements of log line.

    Args:
        log_dict (dict): dict with log record.

    Returns:
        dict: dict with some values processed.
    """
    def remove_symbols(s):
        to_remove = ["\\n", "\\"]
        for c in to_remove:
            s = s.replace(c, "")
        return s

    log_dict["request_time"] = float(remove_symbols(log_dict["request_time"]))
    log_dict["request"] = log_dict["request"].replace("GET ", "")
    return log_dict


def calc_median(vals):
    vals_sorted = sorted(vals)
    mi = len(vals) // 2
    if len(vals_sorted) % 2 == 0:
        median = (vals_sorted[mi-1] + vals_sorted[mi]) / 2
    else:
        median = vals_sorted[mi]
    return median


def select_max_records(data, target_key, limit):
    """Modify data to remain only records with maximim values.

    Args:
        data (list): list of dicts.
        target_key (str): name of the key to sort.
        limit (int): final number of records.

    Returns:
        list: list of dicts.
    """
    sorted_data = sorted(data, key=lambda x: x[target_key])
    return sorted_data[:limit]


def analyze_log(data, n_limit):
    """Process stats from given log data.

    Args:
        data (list): list of dicts of records.
        n_limit (int): maximum number of records.

    Returns:
        list: list of dicts with record stats.
    """
    time_dict = defaultdict(lambda: {'request_time': []})
    for log_record in data:
        request = log_record["request"]
        request_time = log_record["request_time"]
        time_dict[request]['request_time'].append(request_time)

    n_requests_total = sum([len(rq) for rq in time_dict])
    time_total = sum([sum(time_dict[rq]["request_time"]) for rq in time_dict])
    stats = []
    for req in time_dict:
        req_time = round(sum(time_dict[req]["request_time"]), 4)
        n_count = len(time_dict[req]["request_time"])
        stats.append({
            "url": req,
            "count": n_count,
            "count_perc": round(n_count / n_requests_total, 8),
            "time_sum": req_time,
            "time_perc": round(req_time / time_total, 8),
            "time_med": round(calc_median(time_dict[req]['request_time']), 4),
            "time_avg": round(req_time / len(time_dict[req]), 4),
            "max": max(time_dict[req]['request_time']),
            "min": min(time_dict[req]['request_time'])
        })

    # Leave only top records
    if len(stats) > n_limit:
        stats = select_max_records(stats, "time_sum", n_limit)

    return stats


def parse_json(stats, config, log_date):
    """Parse json stats to the html report.

    Args:
        stats (list): list of dicts with stats.
        config (dict): configuration.
        log_date (date): date of log generation (used in report name).
    """
    if not os.path.exists(config["REPORT_DIR"]):
        os.makedirs(config["REPORT_DIR"])
    fn = f"report-{str(log_date)}.html"
    report_path = os.path.join(config["REPORT_DIR"], fn)
    logging.info(f"Report destination path: {report_path}")

    with open(config["REPORT_TEMPLATE"], "r") as f:
        report_html = f.read()
    report_html = Template(report_html)

    report_out = str(report_html.safe_substitute(table_json=str(stats)))

    with open(report_path, 'w') as f:
        f.write(report_out)
    logging.info(f"Report has been written successfully.")


def select_recent_log(log_dir):
    """Select most recent log from given directory.

    Given directory should exist.
    Selection will look only in the given folder non-recursevely.
    Logs have format of logname-yyyymmdd.log[.gz].
    If directory contains no suitable log files, return None.

    Args:
        log_dir (str): direcotry with logs.

    Returns:
        (str, date): path to the most recent log or None if no logs exist,
            date of of selected log.
    """
    def gz_or_plain(s):
        i = s.rfind('.')
        # In case of plain text mandatory dot would have multiple
        # characters after it
        if s[i:] == ".gz" or len(s)-i > 5:
            return True
        return False

    path = ""
    max_date = date(1900, 1, 1)
    fns = [f for f in os.listdir(log_dir) if gz_or_plain(f)]
    for fn in fns:
        if fn.endswith('.gz') or fn.endswith('.txt'):
            datestr = fn[fn.rfind('-')+1:fn.rfind('.')]
        else:
            datestr = fn[fn.rfind('-')+1:]
        k = os.path.join(log_dir, fn)
        v = date(int(datestr[:4]), int(datestr[4:6]), int(datestr[6:8]))
        if v > max_date:
            max_date = v
            path = k

    if len(path) == 0:
        logging.warning("No logs found.")
        return None, None
    return path, max_date


def check_existing_report(log_dir, dt):
    """Returns True if report already exists. """
    fn = f"{os.path.join(log_dir, str(dt))}"
    if os.path.exists(fn):
        return True
    return False


def build_report(config):
    """Process log file and create html report.

    Args:
        config (dict): configuration file.
    """
    # Check that direcory in config exists
    if not os.path.exists(config["LOG_DIR"]):
        raise Exception(f"Directory {config['LOG_DIR']} not exists")

    path, log_date = select_recent_log(config["LOG_DIR"])
    if path is None:
        return
    if check_existing_report(config["REPORT_DIR"], log_date):
        logging.warning(f"Report from {log_date} already exists. Exiting.")
    logging.info(f"Processing {path}")

    i_record = 0
    n_broke_records = 0
    data = []
    is_gz = path.endswith("gz")
    with gzip.open(path, 'rb') if is_gz else open(path, "r") as f:
        for line in read_log(f):
            i_record += 1
            if i_record % 100_000 == 0:
                logging.info(f"Processed {i_record+1} records")
            if isinstance(line, bytes):
                line = line.decode('utf-8')
            parsed_record = parse_line(line)
            if parsed_record is None:
                n_broke_records += 1
            else:
                data.append(parsed_record)

    # Check parsing error rate
    error_rate = n_broke_records / i_record
    if error_rate > config["ERROR_RATE_THRESHOLD"]:
        logging.exception(f"Parsing error rate is {error_rate}. Exiting...")
        return
    elif error_rate > 0:
        logging.warning(f"Parsing error rate is {error_rate}")

    logging.info(f"Log contains {len(data)} records")
    stats = analyze_log(data, config["REPORT_SIZE"])
    logging.info(f"Stats contains {len(stats)} requests")
    parse_json(stats, config, log_date)


def main():
    try:
        build_report(config)
    except Exception as e:
        logging.exception(e)
        raise e


if __name__ == "__main__":
    main()

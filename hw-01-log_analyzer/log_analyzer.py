import os
from datetime import datetime
import gzip
from collections import defaultdict
import logging
import logging.config 

config = {
    "REPORT_SIZE": 1000,
    "REPORT_DIR": "./reports",
    "REPORT_TEMPLATE": "report.html",
    "LOG_DIR": "./log",
    "LOG_NAME": None,
}

# Set logging
logging.basicConfig(format="[%(asctime)s] %(levelname).1s %(message)s", 
        datefmt="%Y.%m.%d %H:%M:%S", level=logging.INFO)
if config["LOG_NAME"] is not None:
    logging.fileConfig(os.path.join(config["LOG_DIR"], config["LOG_NAME"]))


def split_by_space(s, item_symbols=("\"", "[", "]")):
    """
    Split line by spaces but do not split contenst inside quotes.
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


def parse_line(s):
    """
    Parse log line according to log format.


    log_format ui_short $remote_addr  $remote_user $http_x_real_ip [$time_local] 
                  "$request" ''$status $body_bytes_sent "$http_referer"
                  "$http_user_agent" "$http_x_forwarded_for" 
                  "$http_X_REQUEST_ID" "$http_X_RB_USER" 
                  $request_time;
    """
    item_names = ["remote_addr", "remote_user", "http_x_real_ip", "time_local", 
            "request", "status", "body_bytes_sent", "http_referer", 
            "http_user_agent", "http_x_forwarded_for",
            "http_X_REQUEST_ID", "http_X_RB_USER", "request_time"]
    item_vals = split_by_space(s)
    return {k:v for k, v in zip(item_names, item_vals)}


def process_log_line(log_dict):
    """
    Process elements of log line.
    """
    def remove_symbols(s):
        to_remove = ["\\n", "\\"]
        for c in to_remove:
            s = s.replace(c, "")
        return s

    log_dict["request_time"] = float(remove_symbols(log_dict["request_time"]))
    log_dict["request"] = log_dict["request"].replace("GET ", "")
    return log_dict


def open_logfile(path):
    if path.endswith(".gz"):
        return gzip.open(path, 'rb')
    return open(path, 'r') 


def calc_median(vals):
    vals_sorted = sorted(vals)
    mi = len(vals) // 2
    if len(vals_sorted) % 2 == 0:
        median = (vals_sorted[mi-1] + vals_sorted[mi]) / 2
    else:
        median = vals_sorted[mi]
    return median


def analyze_log(data):
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
        stats.append({
            "url": req,
            "count": len(time_dict[req]),
            "count_perc": round(len(time_dict[req]) / n_requests_total, 6),
            "time_sum": req_time,
            "time_perc": round(req_time / time_total, 4),
            "time_med": round(calc_median(time_dict[req]['request_time']), 4),
            "time_avg": round(req_time / len(time_dict[req]), 4),
            "max": max(time_dict[req]['request_time']),
            "min": min(time_dict[req]['request_time'])
        })

    return stats


def parse_json(stats, config):
    """
    Parse json stats to the html report.
    """
    if not os.path.exists(config["REPORT_DIR"]):
        os.makedirs(config["REPORT_DIR"])
    date = str(datetime.date(datetime.now()))
    fn = f"report-{date}.html"
    report_path = os.path.join(config["REPORT_DIR"], fn)
    logging.info(f"Report destination path: {report_path}")

    with open(config["REPORT_TEMPLATE"], "r") as f:
        report_html = f.read()

    target_tag = "$table_json"
    ind_start = report_html.find(target_tag)
    report_out = report_html[:ind_start] + str(stats) + \
         report_html[ind_start+len(target_tag):]

    with open(report_path, 'w') as f:
        f.write(report_out)
    logging.warning(f"Report has been written successfully.")


def main():
    path = 'nginx-access-ui.log-20170629'
    data = []
    with open_logfile(path) as f:
        for i, line in enumerate(f.readlines()):
            if (i+1) % 1_000 == 0:
                logging.info(f"Processed {i+1} files")
            data.append(process_log_line(parse_line(str(line))))
    logging.info("Log was parsed successfully.")

    logging.info(f"Log contains {len(data)} records")
    stats = analyze_log(data)
    logging.info(f"Stats contains {len(stats)} requests") 
    parse_json(stats, config)


if __name__ == "__main__":
    main()

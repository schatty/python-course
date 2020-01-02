import gzip
from collections import defaultdict


config = {
    "REPORT_SIZE": 1000,
    "REPORT_DIR": "./reports",
    "LOG_DIR": "./log"
}

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
    def remove_redundant(s):
        to_remove = ["\\n", "\\"]
        for c in to_remove:
            s = s.replace(c, "")
        return s

    log_dict["request_time"] = float(remove_redundant(log_dict["request_time"]))
    return log_dict


def open_logfile(path):
    if path.endswith(".gz"):
        return gzip.open(path, 'rb')
    return open(path, 'r') 


def main():
    path = 'nginx-access-ui.log-20170629'
    data = []
    with open_logfile(path) as f:
        for i, line in enumerate(f.readlines()):
            data.append(process_log_line(parse_line(str(line))))

    print(f"Log contains {len(data)} records") 




if __name__ == "__main__":
    main()

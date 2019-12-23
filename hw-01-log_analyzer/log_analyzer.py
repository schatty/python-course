import gzip
from collections import defaultdict

# log_format ui_short $remote_addr  $remote_user $http_x_real_ip [$time_local] 
#                   "$request" ''$status $body_bytes_sent "$http_referer"
#                   "$http_user_agent" "$http_x_forwarded_for" 
#                   "$http_X_REQUEST_ID" "$http_X_RB_USER" 
#                   $request_time;

config = {
    "REPORT_SIZE": 1000,
    "REPORT_DIR": "./reports",
    "LOG_DIR": "./log"
}


def main():

    path = 'nginx-access-ui.log-20170630.gz'
    data = defaultdict(dict)
    with gzip.open(path, 'rb') as f:
        for line in f.readlines():
            print(line)
            remote_addr, \
                remote_user, \
                http_x_real_ip, \
                time_local, \
                request, \
                status, \
                body_bytes_sent, \
                http_referer, \
                http_user_agent, \
                http_x_forwarded_for, \
                http_x_request_id, \
                http_x_rb_user, \
                request_time = str(line).split(' ')
            print("Request: ", request)
            break



if __name__ == "__main__":
    main()

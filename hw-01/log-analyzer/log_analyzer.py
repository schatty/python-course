"""
Script for analysing logs.
"""

import gzip

# log_format ui_short '$remote_addr  $remote_user $http_x_real_ip [$time_local] "$request" '
#                     '$status $body_bytes_sent "$http_referer" '
#                     '"$http_user_agent" "$http_x_forwarded_for" "$http_X_REQUEST_ID" "$http_X_RB_USER" '
#                     '$request_time';

config = {
    "REPORT_SIZE": 1000,
    "REPORT_DIR": "./reports",
    "LOG_DIR": "./log"
}


def open_log(filename):
    if filename.endswith(".gz"):
        return gzip.open(filename)
    else:
        raise Exception("Wrong type of the input file")


def check_chunk_end(acc, new_symbol):
    if new_symbol == ']':
        return True
    if new_symbol == '"' and '"' in acc:
        return True
    if new_symbol == "'" and "'" in acc:
        return True
    if new_symbol == " " and ('[' not in acc and '"' not in acc and "'" not in acc):
        return True
    return False


def parse_items(raw_line):
	item = ''
	item_in_process = False
	items = []
	for i in range(len(raw_line)):
		if not item_in_process:
			item_in_process = True
			item = ''
		elif check_chunk_end(item, raw_line[i]):
			items.append((item + raw_line[i]).strip())
			item_in_process = False
		item += raw_line[i]
	items.append((item + raw_line[i]).strip())
	return items


def main():
	fn = '/home/igor/programming/python-course/hw-01/log-analyzer/logs/nginx-access-ui.log-20170630.gz'

	
	log_data = []

	index2props = {0: {'name': 'remote_addr', 'type': str}, 
               1: {'name': 'remote_user', 'type': str}, 
             2: {'name': 'http_x_real_ip', 'type': str},
             3: {'name': 'time_local', 'type': str}, 
             4: {'name': 'request', 'type': str}, 
             5: {'name': 'status', 'type': str},
             6: {'name': "body_bytes_sent", "type": str},
             7: {'name': 'http_referer', 'type': str},
             8: {'name': 'http_user_agent', 'type': str}, 
             9: {'name': 'http_x_forwarded_for', 'type': str},
             10: {'name': 'http_X_REQUEST_ID', 'type': str},
             11: {'name': 'http_X_RB_USER', 'type': str},
             12: {'name': 'request_time', 'type': float}}

	with open_log(fn) as f:
		c = 0
		for line in f:    
			try:
				line_decoded = line.decode('utf-8')	
				items = []
				for i, item in enumerate(parse_items(str(line_decoded))):
					items.append(index2props[i]['type'](item))
				log_data.append(items)
				c += 1
				if c % 100_000 == 0:
					print("Processing: ", c)
			except Exception as e:
				print("Problem line: ", line)

	print("Log processed successfully.")

if __name__ == "__main__":
    main()

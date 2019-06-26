"""
Script for analysing logs.
"""

import gzip
import pandas as pd

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
	elif filename.endswith(".log"):
		return open(filename, 'r')
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


def textlog_to_dataframe(filename, index2props):	
	log_data = []
	with open_log(filename) as f:
		c = 0
		for line in f:    
			try:
				if isinstance(line, (bytes, bytearray)):
					line = line.decode('utf-8')
				items = []
				for i, item in enumerate(parse_items(str(line))):
					items.append(index2props[i]['type'](item))
				log_data.append(items)
				c += 1
				if c % 100_000 == 0:
					print("Processing: ", c)
			except Exception as e:
				print("Problem line: ", line)

	cols = [index2props[i]['name'] for i in sorted(index2props.keys())]
	df = pd.DataFrame(log_data, columns=cols)
	return df


def get_stats_json(df):
	request_groups = df.groupby('request')
	n_urls = len(request_groups)
	print("N urls: ", n_urls)
	whole_time = df['request_time'].sum()
	time_avg = request_groups.request_time.mean()
	time_max = request_groups.request_time.max()
	time_med = request_groups.request_time.median()
	time_sum = request_groups.request_time.sum() 
	time_perc = time_sum / whole_time

	stats_df = pd.concat([time_avg, time_max, time_med, time_sum, time_perc], axis=1)
	stats_df.columns = ['time_avg', 'time_max', 'time_med', 'time_sum', 'time_perc']

	json_dict = [{'url': time_avg.index[i], 
				'time_avg': time_avg[i], 
				'time_max': time_max[i], 
				'time_median': time_med[i], 
				'time_sum': time_sum[i], 
				'time_perc': time_perc[i]} for i in range(n_urls)]

	return json_dict


def main():
	fn = '/home/igor/programming/python-course/hw-01/log-analyzer/logs/nginx-access-ui.log-20190630.log'

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

	df = textlog_to_dataframe(fn, index2props)
	print("DataFrame shape: ", df.shape)
	print("Log processed successfully.")

	json_dict = get_stats_json(df)
	print("json builded successfully")

	with open('report.html', 'r') as f:
		html_data = f.read()
		print("Var table position: ", html_data.find("var table"))
		insert_pos = html_data.find("var table")
		report_data = html_data[:insert_pos+11] + str(json_dict) + html_data[insert_pos+11:]

	report_name = "myreport.html"
	with open(report_name, 'w') as f:
		f.write(report_data)


if __name__ == "__main__":
    main()

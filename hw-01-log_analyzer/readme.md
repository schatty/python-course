## Log Analyzer

Tool for analyzing logs with following html report creation. Logs can be either in gz format or to be plain with .log extension. Report contains following basic statistics that can be sorted on a webpage interactively:
* count - number of times url was encountered
* count_perc - percentage of given URL among all URLs
* time_sum - sum of $request_time for given URL
* time_perc - percentage of $request_time for given URL
* time_avg - average $request time
* time_max - max $request time
* time_min - min $request time

### log format

`log_format ui_short '$remote_addr $remote_user $http_x_real_ip [$time_local] "$request" ' '$status $body_bytes_sent "$http_referer" '
'"$http_user_agent" "$http_x_forwarded_for" "$http_X_REQUEST_ID" "$http_X_RB_USER" '$request_time';`

## Functionality of `log_analyzer.py`
* Script will process the most recent (based date in filename) log in `LOG_DIR`
* If report with the corresponding date already exists, warning will be produced, followied by exit
* External config in json can be passed with `--config' argument
* External config allowed to have missing fields which will be filled with default parameters
* If no external config is set, default config will be used
* Logs of script routine will be written either in `stdout` or specified `LOG` file
* If more than `ERROR_RATE_THRESHOLD` reconds in config is broken, warning produced, followed by exit
* Any unexpected errors will be written to the log

## Usage

`python log_analyzer.py --config config.json`

## Tests
Tests suite will generate logs from `nginx-access-ui.log-20170630.gz` and run test for them. To run tests:

`python -m unittest tests.py`

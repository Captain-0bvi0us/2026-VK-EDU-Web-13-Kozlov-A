# Полные результаты ab

## 1. nginx static
`ab -n 2000 -c 50 http://nginx/sample.html`

```
This is ApacheBench, Version 2.3 <$Revision: 1826891 $>
Copyright 1996 Adam Twiss, Zeus Technology Ltd, http://www.zeustech.net/
Licensed to The Apache Software Foundation, http://www.apache.org/

Benchmarking nginx (be patient)
Completed 200 requests
Completed 400 requests
Completed 600 requests
Completed 800 requests
Completed 1000 requests
Completed 1200 requests
Completed 1400 requests
Completed 1600 requests
Completed 1800 requests
Completed 2000 requests
Finished 2000 requests


Server Software:        nginx/1.27.5
Server Hostname:        nginx
Server Port:            80

Document Path:          /sample.html
Document Length:        755 bytes

Concurrency Level:      50
Time taken for tests:   0.169 seconds
Complete requests:      2000
Failed requests:        0
Total transferred:      2196000 bytes
HTML transferred:       1510000 bytes
Requests per second:    11834.11 [#/sec] (mean)
Time per request:       4.225 [ms] (mean)
Time per request:       0.085 [ms] (mean, across all concurrent requests)
Transfer rate:          12689.31 [Kbytes/sec] received

Connection Times (ms)
              min  mean[+/-sd] median   max
Connect:        0    2   0.7      2       7
Processing:     1    2   1.0      2       8
Waiting:        0    2   0.8      2       8
Total:          2    4   1.2      4      10

Percentage of the requests served within a certain time (ms)
  50%      4
  66%      4
  75%      4
  80%      5
  90%      5
  95%      7
  98%      9
  99%      9
 100%     10 (longest request)
```

## 2. gunicorn static (wsgi_demo)
`ab -n 2000 -c 50 http://wsgi_demo:8081/static/sample.html`

```
This is ApacheBench, Version 2.3 <$Revision: 1826891 $>
Copyright 1996 Adam Twiss, Zeus Technology Ltd, http://www.zeustech.net/
Licensed to The Apache Software Foundation, http://www.apache.org/

Benchmarking wsgi_demo (be patient)
Completed 200 requests
Completed 400 requests
Completed 600 requests
Completed 800 requests
Completed 1000 requests
Completed 1200 requests
Completed 1400 requests
Completed 1600 requests
Completed 1800 requests
Completed 2000 requests
Finished 2000 requests


Server Software:        gunicorn
Server Hostname:        wsgi_demo
Server Port:            8081

Document Path:          /static/sample.html
Document Length:        752 bytes

Concurrency Level:      50
Time taken for tests:   7.272 seconds
Complete requests:      2000
Failed requests:        0
Total transferred:      1812000 bytes
HTML transferred:       1504000 bytes
Requests per second:    275.01 [#/sec] (mean)
Time per request:       181.809 [ms] (mean)
Time per request:       3.636 [ms] (mean, across all concurrent requests)
Transfer rate:          243.32 [Kbytes/sec] received

Connection Times (ms)
              min  mean[+/-sd] median   max
Connect:        0    0   0.2      0       2
Processing:     8  179  45.5    173     389
Waiting:        7  178  45.4    172     388
Total:         10  179  45.4    173     389

Percentage of the requests served within a certain time (ms)
  50%    173
  66%    180
  75%    185
  80%    190
  90%    231
  95%    267
  98%    332
  99%    376
 100%    389 (longest request)
```

## 3. gunicorn dynamic (wsgi_demo)
`ab -n 2000 -c 50 http://wsgi_demo:8081/?foo=bar&hello=world`

```
This is ApacheBench, Version 2.3 <$Revision: 1826891 $>
Copyright 1996 Adam Twiss, Zeus Technology Ltd, http://www.zeustech.net/
Licensed to The Apache Software Foundation, http://www.apache.org/

Benchmarking wsgi_demo (be patient)
Completed 200 requests
Completed 400 requests
Completed 600 requests
Completed 800 requests
Completed 1000 requests
Completed 1200 requests
Completed 1400 requests
Completed 1600 requests
Completed 1800 requests
Completed 2000 requests
Finished 2000 requests


Server Software:        gunicorn
Server Hostname:        wsgi_demo
Server Port:            8081

Document Path:          /?foo=bar&hello=world
Document Length:        432 bytes

Concurrency Level:      50
Time taken for tests:   1.313 seconds
Complete requests:      2000
Failed requests:        0
Total transferred:      1172000 bytes
HTML transferred:       864000 bytes
Requests per second:    1523.05 [#/sec] (mean)
Time per request:       32.829 [ms] (mean)
Time per request:       0.657 [ms] (mean, across all concurrent requests)
Transfer rate:          871.59 [Kbytes/sec] received

Connection Times (ms)
              min  mean[+/-sd] median   max
Connect:        0    1   1.8      0      12
Processing:     4   31   6.5     32      48
Waiting:        1   30   6.4     31      48
Total:         13   32   6.2     33      50

Percentage of the requests served within a certain time (ms)
  50%     33
  66%     35
  75%     36
  80%     37
  90%     39
  95%     42
  98%     46
  99%     47
 100%     50 (longest request)
```

## 4. nginx -> gunicorn dynamic (no cache)
`ab -n 2000 -c 50 http://nginx/demo/?foo=bar&hello=world`

```
This is ApacheBench, Version 2.3 <$Revision: 1826891 $>
Copyright 1996 Adam Twiss, Zeus Technology Ltd, http://www.zeustech.net/
Licensed to The Apache Software Foundation, http://www.apache.org/

Benchmarking nginx (be patient)
Completed 200 requests
Completed 400 requests
Completed 600 requests
Completed 800 requests
Completed 1000 requests
Completed 1200 requests
Completed 1400 requests
Completed 1600 requests
Completed 1800 requests
Completed 2000 requests
Finished 2000 requests


Server Software:        nginx/1.27.5
Server Hostname:        nginx
Server Port:            80

Document Path:          /demo/?foo=bar&hello=world
Document Length:        432 bytes

Concurrency Level:      50
Time taken for tests:   1.517 seconds
Complete requests:      2000
Failed requests:        0
Total transferred:      1180000 bytes
HTML transferred:       864000 bytes
Requests per second:    1318.28 [#/sec] (mean)
Time per request:       37.928 [ms] (mean)
Time per request:       0.759 [ms] (mean, across all concurrent requests)
Transfer rate:          759.56 [Kbytes/sec] received

Connection Times (ms)
              min  mean[+/-sd] median   max
Connect:        0    1   0.9      0       7
Processing:     2   36   4.3     37      47
Waiting:        2   36   4.3     36      44
Total:          9   37   3.8     37      47
WARNING: The median and mean for the initial connection time are not within a normal deviation
        These results are probably not that reliable.

Percentage of the requests served within a certain time (ms)
  50%     37
  66%     39
  75%     40
  80%     40
  90%     41
  95%     42
  98%     43
  99%     44
 100%     47 (longest request)
```

## 5. nginx -> gunicorn dynamic (proxy_cache)
`ab -n 2000 -c 50 http://nginx/demo-cached/?foo=bar&hello=world`

```
This is ApacheBench, Version 2.3 <$Revision: 1826891 $>
Copyright 1996 Adam Twiss, Zeus Technology Ltd, http://www.zeustech.net/
Licensed to The Apache Software Foundation, http://www.apache.org/

Benchmarking nginx (be patient)
Completed 200 requests
Completed 400 requests
Completed 600 requests
Completed 800 requests
Completed 1000 requests
Completed 1200 requests
Completed 1400 requests
Completed 1600 requests
Completed 1800 requests
Completed 2000 requests
Finished 2000 requests


Server Software:        nginx/1.27.5
Server Hostname:        nginx
Server Port:            80

Document Path:          /demo-cached/?foo=bar&hello=world
Document Length:        432 bytes

Concurrency Level:      50
Time taken for tests:   0.419 seconds
Complete requests:      2000
Failed requests:        0
Total transferred:      1222004 bytes
HTML transferred:       864000 bytes
Requests per second:    4769.97 [#/sec] (mean)
Time per request:       10.482 [ms] (mean)
Time per request:       0.210 [ms] (mean, across all concurrent requests)
Transfer rate:          2846.15 [Kbytes/sec] received

Connection Times (ms)
              min  mean[+/-sd] median   max
Connect:        0    4   1.2      4      10
Processing:     1    6   1.5      6      14
Waiting:        1    4   1.3      4       9
Total:          5   10   1.6     10      17

Percentage of the requests served within a certain time (ms)
  50%     10
  66%     11
  75%     11
  80%     11
  90%     12
  95%     13
  98%     14
  99%     15
 100%     17 (longest request)
```



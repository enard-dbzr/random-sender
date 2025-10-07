import multiprocessing

bind = "0.0.0.0:3001"
workers = multiprocessing.cpu_count() * 2 + 1
threads = 2
timeout = 30

accesslog = "-"
errorlog = "-"

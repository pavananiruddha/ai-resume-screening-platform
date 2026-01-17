import multiprocessing

bind = "0.0.0.0:8000"
workers = 4 # Adjust based on CPU cores, e.g. multiprocessing.cpu_count() * 2 + 1
threads = 4
timeout = 120
accesslog = "-"
errorlog = "-"
log_level = "info"

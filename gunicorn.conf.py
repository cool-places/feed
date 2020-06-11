import multiprocessing

bind = '0.0.0.0:7191'
workers = multiprocessing.cpu_count() * 2 + 1
print('3 workers:', workers)
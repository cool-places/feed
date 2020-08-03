import time

now = int(time.time() * 1000)
epoch = now - now % (24 * 3600 * 1000)

print(epoch, epoch + 24 * 3600 * 1000)
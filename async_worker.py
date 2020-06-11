## Async worker.

# Generates & caches next page of feed, building the weight tree
# if necessary.
def cache_next_page(user, location, lean=None, fat=None, session_token=None):
    # TODO
    return

def increment_seen(page, data_type):
    # TODO
    return

def run(work_q):
    while True:
        work = work_q.get() # blocking call
        work()
## Async worker.

# Generates & caches next page of feed, building the tree
# if necessary
def cache_next_page(user, location, lean=None, fat=None):
    # TODO
    return

def increment_seen(page, unmarshal):
    # TODO
    return

def run(work_q):
    while True:
        work = work_q.get() # blocking call
        work()
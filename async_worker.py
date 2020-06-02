## Async worker.

# generic name because it does a lot of things
# and can't come up with a good name that encapsulates
# all that.
# 
# It's purposely not lean because Python lambdas
# cannot be multiline :()
def background_task(user, locality, lean, fat):
    # TODO:
    #   (1) generate page from lean, fat trees
    #   (2) cache said generated tree
    return

def run(work_q):
    while True:
        work = work_q.get() # blocking call
        work()
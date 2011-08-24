"""Package for augmenting the stock Python sched module

To transparently upgrade uses of sched.scheduler in existing code, use:

    import threading_sched as sched


scheduler(timefunc, delayfunc):

    Same API as sched.scheduler, but with improved thread-safety.  Events scheduled will immediately
    alter the timeout behaviour of any currently executing schedulder.run() method.


scaled_scheduler(timefunc, delayfunc):

    Like scheduler, but uses event priority as a scaling factor applied to each event's age (time
    since expiry).
"""

# Exposerom threaded_sched import
__all__ = ["default", "scaled"]

from default import scheduler
from scaled import scaled_scheduler

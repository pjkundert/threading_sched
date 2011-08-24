
import sched

class scaled_scheduler(sched.scheduler):
    """
    Extend our (thread-safe) implementation of the Python sched.scheduler, to order events by age
    (time past due), scaled by priority.
    """
    def run(self):
        """
        Review all expired events, sort by priority-scaled age (time past due).  Then remove the
        next one to be run from the schedule, and run it.  Unlike the underlying sched.scheduler,
        waits in a multithreading-sensitive fashion; if a new event is scheduled, we'll awaken and
        re-schedule our next wake-up.
        """
        with self.lock:
            pass


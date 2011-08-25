
import threading
import sched

class scheduler(sched.scheduler):
    """
    Thread-safe implementation of the stock Python sched.scheduler class.  The API remains basically
    the same, with some optional additions to support creating custom prioritization schemes.

    We implement locking for thread safety, and we awaken our run method whenever the events in the
    list might have changed in a way that could shorten our timeout.
    
    The following are extensions to the Python sched.scheduler API:

    - Keyword Arguments
        In enter{abs}(), an optional kwargs argument may be provided, containing a dictionary of 
        keyword arguments to pass to the function.  

        def enterabs(self, time, priority, action, argument, kwargs={}):
    
    """
    def __init__(self, *args, **kwargs):
        self.lock = threading.RLock()
        self.cond = threading.Condition(self.lock)
        sched.scheduler.__init__(self, *args, **kwargs)

    def enterabs(self, time, priority, action, argument, kwargs={}):
        """
        Assumes enter() uses enterabs().  Since our Condition uses our RLock, we can safely acquire
        the Condition, and issue the nofify_all; it won't be delivered 'til we fully release our
        self.lock.
        """
        with self.cond:
            # Prepare a closure to wrap the action, trapping the supplied keyword args (if any).  If
            # *any* keyword arguments are supplied, then they will be passed to the action along
            # with the event arguments; they will also always be updated to contain an 'event'
            # keyword argument, containing the event.  If just 'event' and no other keywords are
            # desired, just pass an empty 'event' keyword entry.  We must *always* use the wrapper,
            # because we *always* supply the event when the action is invoked.
            def wrapper(event):
                if kwargs:
                    kwargs.update({'event': event})
                return action(*event.argument, **kwargs)
            e = sched.scheduler.enterabs(self, time, priority, wrapper, argument)
            # Awaken any thread awaiting on a condition change, eg .run(), or .wait()
            self.cond.notify_all()
        #print "Scheduling %s" % ( str(e) )
        return e

    def enter(self, delay, priority, action, argument, kwargs={}):
        return self.enterabs(self.timefunc() + delay, priority, action, argument, kwargs=kwargs)

    def cancel(self, *args, **kwargs):
        """
        Removing an event can only result in us awakening too early, which is generally not a
        problem.  However, if this empies the queue completely, we want run() to wake up and return
        right away!
        """
        with self.cond:
            e = sched.scheduler.cancel(self, *args, **kwargs)
            self.cond.notify_all()
        return e

    def empty(self):
        with self.lock:
            return sched.scheduler.empty(self)

    def wait(self):
        """
        Awaits a change in condition that could mean that there are now events to process.  Use this
        when the queue is (or might be) empty, and a thread needs to wait for something to process.
        """
        with self.cond:
            if self.empty():
                self.cond.wait()

    def next_event(self, now=None):
        """
        Return the next scheduled event, without removing it from the queue.  Throws an exception if
        none available.  Override this method to implement other priority schemes.
        """
        with self.lock:
            return self._queue[0]			# Strictly by time, then priority

    def run(self, pred=None):
        """
        Retrieve an event, waiting and looping if it hasn't expired.  Otherwise, remove it from the
        schedule, and run it.  Unlike the underlying sched.scheduler, this implementation waits in a
        multithreading sensitive fashion; if a new event is scheduled, we'll awaken and re-schedule
        our next wake-up.

        Returns when there are no more events left to run, or until the supplied predicate evaluates
        False.

        
        This run method is not usually appropriate to use directly as a Thread.run method, because
        it returns when the schedule is empty; this often doesn't mean the program is done.  To
        safely process events, a Thread must know (somehow) that the overall program is not yet
        complete, and implement its own run method like this, waiting for more events to be
        scheduled each time scheduler.run returns:

        class scheduler_thread(Thread):
            def __init__(self):
                self.sch = sched.scheduler(...)
                ...
            def run(self):
                while ( ... we are not finished ... ):
                    self.sch.run()
                    self.sch.wait()

        """
        while True:
            # Get the next event, relative to the current time. When schedule is empty, we're done.
            now = self.timefunc()
            with self.cond:				# Acquires self.lock
                if self.empty():
                    break

                # Queue is not empty, guaranteed
                time, prio, func, args = event = self.next_event(now=now)
                if now < time:
                    # Next event hasn't expired; Wait 'til expiry, or an self.cond.notify...()
                    self.cond.wait(time - now)		# Releases self.lock
                    #print "Schedule condition wait expired after %fs" % (self.timefunc() - now)
                    continue
                    # TODO: this is inefficient pre-3.2, due to a busy wait loop in the
                    # threading Condition.  Perhaps we should detect this, and implement in
                    # terms of spawning another Thread to sleep 'til the desired time, then
                    # trigger .notify_all()?

                # An expired event is detected.  No schedule modification can have occurred (we hold
                # the lock, and no self.cond.wait() has been processed, because it always will
                # 'continue' the loop) so we can safely cancel it.  We can make no assumptions about
                # its position in the _queue, to allow arbitrary scheduling algorithms.
                self.cancel(event)

            # Trigger the expired (and removed) event's action wrapper function.  This may result in
            # schedule modification, so we do this outside the lock.  If func raises an exception,
            # the scheduler's invariant is maintained, and this method may be called again.
            #print "Scheduled event firing: %s" % (str(event))
            func(event)
            self.delayfunc(0)				# Let other threads run


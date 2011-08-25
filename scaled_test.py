import time
import timeit
import threading
import threading_sched as sched

# Use the platform-appropriate high-resolution timer
timer = timeit.default_timer
sleep = time.sleep

def test_scaled_basic():
    sch = sched.scaled_scheduler(timer, sleep)
    beg = timer()
    when = []
    sch.enter( 1.0, 0, lambda: when.append(timer()), () )
    sch.run()
    now = timer()
    elapsed = now - beg;     assert 0.99 < elapsed < 1.01	# Total run should take ~1 second
    delayed =when[0] - beg;  assert 0.99 < delayed < 1.01


def test_scaled_preemption():
    sch = sched.scaled_scheduler(timer, sleep)
    beg = timer()
    when = []
    sch.enterabs( beg + 2.0, 0, lambda: when.append(timer()), () )
    threading.Timer( 0.5, lambda: sch.enterabs( beg + 1.0, 0, lambda: when.append(timer()), () )).start()
    sch.run()
    now = timer()
    elapsed = now - beg;     assert 1.99 < elapsed < 2.01	# Total run should take ~2 seconds
    delay00 = when[0] - beg; assert 0.99 < delay00 < 1.01	# The Timer-scheduled event, now 1s ago
    delay01 = when[1] - beg; assert 1.99 < delay01 < 2.01	# The original event, just expired

def test_scaled_cancellation():
    sch = sched.scaled_scheduler(timer, sleep)
    beg = timer()
    when = []
    e = sch.enterabs( beg + 2.0, 0, lambda: when.append(timer()), () )
    threading.Timer( 0.5, lambda: sch.cancel(e)).start()
    sch.run()
    now = timer()
    elapsed = now - beg;     assert 0.48 < elapsed < 0.52	# Total run should take ~1/2 second
    assert len(when) == 0					# And no events should fire

def reschedule(log, end, sch, name, priority, delay, latency, event=None):
    """
    A function which appends a record of itself to the supplied log list, and immediately schedules
    a request to run itself after a certain delay period, with a certain scheduling priority (if the
    end time hasn't been reached).  The function then sleeps for the specified latency period.
    """
    now = timer()
    log.append( (now, name, priority, delay, latency, now - event.time) )
    if now <= end:
        sch.enter(delay, priority,
                  reschedule, (log, end, sch, name, priority, delay, latency),
                  kwargs={'event':None})
    sleep(latency)


def test_scaled_multiple():
    sch = sched.scaled_scheduler(timer, sleep)
    beg = timer()
    dur = 15.0
    lat =  0.10
    log = [] # [(timeout, 'name', priority, delay, latency), ...]

    # Schedule a bunch of events, for immediate execution at the same
    # instant, and 0.0 delay on reschedule.  This will force the scheduler
    # to select them based on priority scaling of their age
    mix = [ 
        ('a  -1/2', 0.50),
        ('b 1-'   , 1),
        ('c 1-1/4', 1.25),
        ('d 2-',    2.00),
        ('e 1-',    1.00),
        ('f 1-1/2', 1.50),
        ('g 0-1/4', 0.25),
        ('h 3-1/4', 3.25),
        ('i  -1/8', 0.125),
        ]
    for name, prio in mix:
        sch.enterabs(beg, prio,
                     reschedule, (log, beg + dur, sch, name, prio, 0.0, lat),
                     kwargs={'event':None})
    siz = len(sch.queue)
    
    sch.run()

    # Given a certain function latency 'lat', and a total duration of
    # 'dur', we can compute roughly how many times reschedule should have
    # triggered...  Of course, 
    print "\ntime  name  overdue"
    for expiry, name, prio, delay, lat, overdue in log:
        print "%7.3f %-10s %7.3fs" % (expiry - beg, name, overdue)
    runs = len(log); assert dur/lat * .9 < runs-siz < dur/lat * 1.1

    # Count up the incidence of each type of event, and make sure their
    # distribution reflects their relative priority.
    prio_sum = 0.
    for name, prio in mix:
        prio_sum += prio
    ovr = {}
    rel = {}
    for now, name, prio, delay, latency, overdue in log:
        try:    rel[name] += 1
        except: rel[name]  = 1
        try:    ovr[name] += overdue
        except: ovr[name]  = overdue
    for name, prio in mix:
        strength = float(prio) / prio_sum
        incidence = float(rel[name]) / len(log)
        error = (incidence - strength) / strength
        overdue = ovr[name]/rel[name]  # Average overdue in seconds
        print "%3d x %-10s prio == %7f; %4.2fs overdue; strengh == % 5.1f%% vs. % 5.1f%% incidence (% 5.1f%% err.)" % (
            rel[name], name, prio, overdue, strength*100, incidence*100, error*100)
        # Within 5 percentage points of where they should be...  This is a very loose metric,
        # because (especially for very low priority events), even one extra scheduling out of 100
        # may result in a very high error "percentage".
        assert abs(incidence - strength) < .05


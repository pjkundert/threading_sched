import time
import timeit
import threading
import threading_sched as sched

# Use the platform-appropriate high-resolution timer
timer = timeit.default_timer
sleep = time.sleep

def test_basic():
    sch = sched.scheduler(timer, sleep)
    beg = timer()
    when = []
    sch.enter( 1.0, 0, lambda: when.append(timer()), () )
    sch.run()
    now = timer()
    elapsed = now - beg;     assert 0.99 < elapsed < 1.01	# Total run should take ~1 second
    delayed =when[0] - beg;  assert 0.99 < delayed < 1.01


def test_preemption():
    sch = sched.scheduler(timer, sleep)
    beg = timer()
    when = []
    sch.enterabs( beg + 2.0, 0, lambda: when.append(timer()), () )
    threading.Timer( 0.5, lambda: sch.enterabs( beg + 1.0, 0, lambda: when.append(timer()), () )).start()
    sch.run()
    now = timer()
    elapsed = now - beg;     assert 1.99 < elapsed < 2.01	# Total run should take ~2 seconds
    delay00 = when[0] - beg; assert 0.99 < delay00 < 1.01	# The Timer-scheduled event, now 1s ago
    delay01 = when[1] - beg; assert 1.99 < delay01 < 2.01	# The original event, just expired


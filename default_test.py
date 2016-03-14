from __future__ import absolute_import
from __future__ import print_function

__author__                      = "Perry Kundert"
__email__                       = "perry@hardconsulting.com"
__copyright__                   = "Copyright (c) 2011 Hard Consulting Corporation"
__license__                     = "GPLv3 (or later)"

import time
import timeit
import threading
import threading_sched as sched

# Use the platform-appropriate high-resolution timer
timer = timeit.default_timer
sleep = time.sleep

def test_default_basic():
    sch = sched.scheduler(timer, sleep)
    beg = timer()
    when = []
    sch.enter( 1.0, 0, lambda: when.append(timer()), () )
    sch.run()
    now = timer()
    elapsed = now - beg;     assert 0.90 < elapsed < 1.10	# Total run should take ~1 second
    delayed =when[0] - beg;  assert 0.90 < delayed < 1.10


def test_default_preemption():
    sch = sched.scheduler(timer, sleep)
    beg = timer()
    when = []
    sch.enterabs( beg + 2.0, 0, lambda: when.append(timer()), () )
    threading.Timer( 0.5, lambda: sch.enterabs( beg + 1.0, 0, lambda: when.append(timer()), () )).start()
    sch.run()
    now = timer()
    elapsed = now - beg;     assert 1.90 < elapsed < 2.10	# Total run should take ~2 seconds
    delay00 = when[0] - beg; assert 0.90 < delay00 < 1.10	# The Timer-scheduled event, now 1s ago
    delay01 = when[1] - beg; assert 1.90 < delay01 < 2.10	# The original event, just expired

def test_default_cancellation():
    sch = sched.scheduler(timer, sleep)
    beg = timer()
    when = []
    e = sch.enterabs( beg + 2.0, 0, lambda: when.append(timer()), () )
    threading.Timer( 0.5, lambda: sch.cancel(e)).start()
    sch.run()
    now = timer()
    elapsed = now - beg;     assert 0.40 < elapsed < 0.60	# Total run should take ~1/2 second
    assert len(when) == 0					# And no events should fire



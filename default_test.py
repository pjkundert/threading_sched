import time
import timeit
import threading
import threading_sched as sched

# Use the platform-appropriate high-resolution timer
timer = timeit.default_timer
sleep = time.sleep

def stamp(var):
    var = timer()

def test_basic():
    sch = sched.scheduler(timer, sleep)
    now = timer()
    when = None
    sch.enter( 1.0, 0, lambda: stamp(when), () )
    sch.run()
    assert 0.99 < timer() - now < 1.01



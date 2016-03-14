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

from __future__ import absolute_import
from __future__ import print_function

__author__                      = "Perry Kundert"
__email__                       = "perry@hardconsulting.com"
__copyright__                   = "Copyright (c) 2011 Hard Consulting Corporation"
__license__                     = "GPLv3 (or later)"

__all__ = ["default", "scaled"]

# These modules form the public interface of threading_sched; always load them into main namespace
from .version  import __version__, __version_info__
from sched import Event
from .default import scheduler
from .scaled import scaled_scheduler

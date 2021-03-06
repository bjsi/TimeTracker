import logging
import os.path
import sys

logger = logging.getLogger('time_tracker_logging')
logger.setLevel(logging.INFO)

formatter = logging.Formatter('TimeTracker:%(levelname)s:%(message)s')

sh_info = logging.StreamHandler(stream=sys.stdout)
sh_info.setLevel(logging.INFO)
sh_info.setFormatter(formatter)

# will be caught by anki and displayed in a
# pop-up window
sh_error = logging.StreamHandler(stream=sys.stderr)
sh_error.setLevel(logging.ERROR)
sh_error.setFormatter(formatter)

addon_dir = os.path.dirname(__file__)
log_path = os.path.join(addon_dir, 'time_tracker.log')
fh = logging.FileHandler(log_path, mode="w")
fh.setLevel(logging.DEBUG)
fh.setFormatter(formatter)

logger.addHandler(fh)
logger.addHandler(sh_error)
logger.addHandler(sh_info)

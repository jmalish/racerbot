import time
from datetime import datetime

message = "something"

time_now = str(datetime.now())
print time_now.split(".")[0]

from datetime import datetime

now = datetime.now()

current_time = now.strftime("%H:%M:%S")
# current_time = now.strftime("%M:%S")
print(current_time)
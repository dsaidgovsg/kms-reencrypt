from datetime import date, timedelta
import subprocess

def date_range_list(start_date, end_date):
    curr_date = start_date
    while curr_date <= end_date:
        yield curr_date 
        curr_date += timedelta(days=1)

# Set input values here
start_date = date(year=2021, month=2, day=6)
stop_date = date(year=2021, month=5, day=18)
bucket_name = ""
kms_key = ""
prefix = ""


date_list = date_range_list(start_date, stop_date)
clean_dl = [str(s) for s in date_list] 
clean_dl = [s.replace('-','') for s in clean_dl] 

for this_date in clean_dl:
    cmd_str = f"poetry run app {bucket_name} {kms_key} --prefix {prefix}/{this_date}"
    subprocess.run(cmd_str, shell=True)

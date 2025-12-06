#! ../.venv/bin/python3
import sys
import subprocess
#gathering process to complete data

help_msg ='\
Usage: run_all.py [end_year]\n\
For example:\n\
run_all.py 2025\
'

end_year_in = 2025
if (len(sys.argv) > 1 and sys.argv[1] == '-h') or len(sys.argv) > 2:
    print(help_msg)
    exit()

if len(sys.argv) == 2:
    try:
        end_year_in = int(sys.argv[1])
    except:
        print("Input end_year is not a valid integer!")

#Async gathering data
subprocess.run(['python3', 'project_tw/main_async_httpx.py', str(end_year_in)])

subprocess.run('rm -f stock_list_s2006e'+str(end_year_in)+'_unfiltered.csv', shell=True)
subprocess.run('cp -f stock_list.csv stock_list_s2006e'+str(end_year_in)+'_unfiltered.csv', shell=True)

#Filtering data
subprocess.run(['python3', 'project_tw/pandas_stock.py', str(end_year_in)])

#Predicting step to next


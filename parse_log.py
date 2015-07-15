import os.path
import subprocess
import sys
import datetime
import time
import numpy as np
import matplotlib.pyplot as plt


def get_average(datetimes):
    print "Average time it takes for a job to be evicted: "
    total = sum(datetime.timedelta.total_seconds(dt) for dt in datetimes)
    #total = sum(dt.hour * 3600 + dt.minute * 60 + dt.second for dt in datetimes)
    avg = total / len(datetimes)
    minutes, seconds = divmod(int(avg), 60)
    hours, minutes = divmod(minutes, 60)
    return datetime.datetime.combine(datetime.date(1900, 1, 1), datetime.time(hours, minutes, seconds))

if "check_output" not in dir(subprocess):  # duck punch it in!
    def f(*popenargs, **kwargs):
        if 'stdout' in kwargs:
            raise ValueError('stdout argument not allowed, it will be overridden.')
        process = subprocess.Popen(stdout=subprocess.PIPE, *popenargs, **kwargs)
        output, unused_err = process.communicate()
        retcode = process.poll()
        if retcode:
            cmd = kwargs.get("args")
            if cmd is None:
                cmd = popenargs[0]
            raise subprocess.CalledProcessError(retcode, cmd)
        return output
    subprocess.check_output = f

directory = sys.path[0]
logfile = directory + "/outfiles/" + "log"
cmd = ["grep", "submitted", logfile]
joblist = subprocess.check_output(cmd).split("\n")
job_num = 0
job_numlist = []
job_info = {}
eviction_times = []

for job in joblist:
    if len(job) > 10:
        job_num = job.split(" ")[1][1:-1]
        job_numlist.append(job_num)
        cmd = ["grep", job_num, logfile]
        job_info[job_num] = subprocess.check_output(cmd).split('\n')

submission_time = 0
eviction_time = 0
for job_num in job_numlist:
    for i in range(len(job_info[job_num])):
        if "executing" in job_info[job_num][i]:
            submission_date = job_info[job_num][i].split(" ")[2] + "/" + str(datetime.date.today().year) + " " + job_info[job_num][i].split(" ")[3]
            submission_time = time.strptime(submission_date, '%m/%d/%Y %H:%M:%S')
        elif "evicted" in job_info[job_num][i]:
            eviction_date = job_info[job_num][i].split(" ")[2] + "/" + str(datetime.date.today().year) + " " + job_info[job_num][i].split(" ")[3]
            eviction_time = time.strptime(eviction_date, '%m/%d/%Y %H:%M:%S')
            if eviction_time is not 0 and submission_time is not 0:
                submission_time, eviction_time = datetime.datetime.fromtimestamp(time.mktime(submission_time)), datetime.datetime.fromtimestamp(time.mktime(eviction_time))
                time_elapsed = eviction_time - submission_time
                print time_elapsed, time_elapsed.total_seconds()
                seconds_total = time_elapsed.total_seconds()
                hours = (seconds_total/60.0)/60.0
                try:
                    with open(directory + "/outfiles/data.txt", 'a+') as datafile:
                        datafile.write(str(hours) + "\n")
                except IOError as e:
                    print e
                eviction_times.append(time_elapsed)

print str(get_average(eviction_times)).split(" ")[1]

data = np.loadtxt(directory + "/outfiles/data.txt")
sorted_data = np.sort(data)
yvals = np.arange(len(sorted_data))/float(len(sorted_data))
fig = plt.figure()
plt.plot(sorted_data, yvals)
fig.suptitle('Glidein Eviction Times', fontsize=20)
plt.xlabel('Hours', fontsize=18)
plt.ylabel('Eviction Probability', fontsize=16)
plt.show()
fig.savefig(directory + "/outfiles/eviction_plot.png")

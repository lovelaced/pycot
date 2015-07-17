__author__ = 'Erin Grasmick'

import os.path
import sys
import subprocess
import random

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

args = sys.argv
directory = sys.path[0]

if len(args) < 4:
    print "Usage: main.py [job_name] [for all sites: 1; for each specific site: 2] [number of jobs to submit] [job_args]"
    exit(1)

job_name = args[1]

all = sys.argv[2]

job_num = args[3]

if args[4]:
    job_args = args[4]

if all == "1":
    all = True
    job_name = directory + "/jobs/" + job_name
    log_no = random.randint(0, 100)
    print "The logfile for this run is named " + str(log_no) + ".log."

elif all == "2":
    all = False
    job_name = directory + "/jobs/" + job_name

script_path = directory + "/./jobs/condorglideins.sh"
glideins = subprocess.check_output([script_path])
glideins = glideins.splitlines()
cmd = """condor_status -pool glidein2.chtc.wisc.edu -af Glidein_ResourceName Glidein_Site"""
current_condor = subprocess.check_output(cmd.split())
submit_list = []

def get_sites():
    if len(args) > 1:
        flags = args[1:]
    else:
        flags = ["cpu"]
    script_path = directory + "/./jobs/condorglideins.sh"
    glideins = subprocess.check_output([script_path])
#    if "oasis" in flags:
 #       glideins = subprocess.check_output(["condor_status", "-p", "glidein.grid.iu.edu", "-any", "-const", "'(HAS_CVMFS_oasis_opensciencegrid_org =?= TRUE)'", "-af", "name"])
    cmd = """condor_status -pool glidein2.chtc.wisc.edu -af Glidein_ResourceName Glidein_Site"""
    current_condor = subprocess.check_output(cmd.split())
    return glideins, current_condor


def get_matching(resource):
    if resource is None:
        pass
    for site in current_condor:
        site = site.split(" ")
        if len(site) < 2:
            continue
        if site[1].lower() in resource.lower():
            return site[1]


def create_submitfiles(job_name, all, directory = directory):
    out_dir = directory + "/outfiles/"
    old_dir = directory
    directory = directory + "/submitfiles/"

    if not os.path.exists(directory):
        try:
            os.makedirs(directory)
            print directory + " created."
        except OSError:
            print "Could not create " + directory

    if all:
        filename = "test_eviction.sub"
        output = "test_eviction.$(Cluster).$(Process).out"
        error = "test_eviction.$(Cluster).$(Process).err"
        submit_list.append(filename)
        try:
            with open(directory + filename, 'w+') as submit_file:
                submit_file.write(
                    "job = " + job_name + "\n"
                    "universe = vanilla\n"
                    "executable = $(job)\n"
                    "arguments = " + job_args + "\n"

                    "initialdir = " + out_dir + "\n"

                    "log = " + str(log_no) + ".log\n"

                    "should_transfer_files = YES\n"
                    "when_to_transfer_output = ON_EXIT\n"
                    "output = " + output + "\n"
                    "error = " + error + "\n"

                    "+WantGlidein = true\n"
                    "+WantFlocking = true\n"
                    "+WantRHEL6 = true\n"
                    "requirements = IS_GLIDEIN" + "\n"
                    "queue " + job_num + "\n")
                submit_file.close()
                print submit_file.name + " created."
        except OSError:
            print "Could not create submit file for " + filename
    else:
        if not os.path.exists(old_dir + "/site_specific_outfiles/"):
            try:
                os.makedirs(old_dir + "/site_specific_outfiles/")
                print old_dir + " created."
            except OSError as e:
                print "Could not create " + old_dir + "/site_specific_outfiles\n", e
        out_dir = old_dir + "/site_specific_outfiles/"
        for resource in glideins:
            resource = resource.split("@")
            resource_name = get_matching(resource[0])
            if resource_name is not None and resource_name is not "":
                filename = resource_name + ".sub"
                if filename not in submit_list:
                    submit_list.append(filename)
                    try:
                        with open(directory + filename, 'w+') as submit_file:
                            submit_file.write(
                                "job = " + job_name + "\n"
                                "universe = vanilla\n"
                                "executable = $(job)\n"
                                "arguments = " + job_args + "\n"
                                "initialdir = " + out_dir + "\n"

                                "log = " + resource_name + ".log\n"

                                "should_transfer_files = YES\n"
                                "when_to_transfer_output = ON_EXIT\n"
                                "output = out." + resource_name +"\n"
                                "error = err." + resource_name + "\n"

                                "request_cpus = 1\n"
                                "request_disk = 100000\n"
                                "request_memory = 10\n"

                                "+WantGlidein = true\n"
                                "+WantFlocking = true\n"
                                '+osg_site_whitelist="' + resource_name + '"\n'
                                'requirements = Glidein_SITE =?= "' + resource_name + '"\n'
                                '+WantRHEL6 = true\n'
                                "queue " + job_num + "\n")
                            submit_file.close()
                            print submit_file.name + " created."
                    except OSError:
                        print "Could not create submit file for " + filename


def submit_jobs(submit_list, directory = directory):
    for subfile in submit_list:
        print "Submitting " + subfile + "...\n"
        print subprocess.check_output(["condor_submit", directory + "/submitfiles/" + subfile])
        print subfile + " submitted."


def get_cpu_num(submit_list):
    for filename in submit_list:
        filename = "out." + filename[:-4]
        if os.path.exists(filename):
            with open(filename, 'r') as output_file:
                output_file.readline()
                process = output_file.readline()
                process = process.split(" ")
                if process[6] > 1:
                    return True
        else:
            print filename + " does not exist yet."

get_sites()
current_condor = set(current_condor.splitlines())
glideins = set(glideins)
create_submitfiles(job_name, all)
submit_jobs(submit_list)
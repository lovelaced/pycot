__author__ = 'Erin Grasmick'

import os.path
import sys
import subprocess

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
#print directory

# current_condor = subprocess.check_output(["cat", directory + "/sites.txt"]).splitlines()
# glideins = subprocess.check_output(["cat", directory + "/test.txt"])
# glideins = glideins.splitlines()
script_path = directory + "/./condorglideins.sh"
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
    script_path = directory + "/./condorglideins.sh"
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


def create_submitfiles(job_name, directory = directory):
    directory = directory + "/submitfiles/"

    if not os.path.exists(directory):
        try:
            os.makedirs(directory)
            print directory + " created."
        except OSError:
            print "Could not create " + directory

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
                                "arguments = 10\n"

                                "log = log\n"

                                "should_transfer_files = YES\n"
                                "when_to_transfer_output = ON_EXIT\n"
                                "output = out." + resource_name +"\n"
                                "error = err." + resource_name + "\n"

                                "request_cpus = 1\n"
                                "request_disk = 100000\n"
                                "request_memory = 10\n"

                                "+WantGlidein3 = true\n"

                                '+osg_site_whitelist="' + resource_name + '"\n'
                                'requirements = Glidein_SITE =?= "' + resource_name + '"\n'
                                '+WantRHEL6 = true\n'
                                'queue')
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
current_condor=set(current_condor.splitlines())
glideins = set(glideins)
create_submitfiles(directory + "/hello_world.sh")
submit_jobs(submit_list)
# print "Waiting 1 minute to grab job stats."
# time.sleep(60)
# get_cpu_num(submit_list)

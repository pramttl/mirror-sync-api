import subprocess
import re
import sys
import os


def rsync_call(
    full_source="54.245.124.177::documents/",
    dest=".",
    password="rsyncpassword",
    ):
    '''
    Function responsible for calling rsync as a subprocess with the appropriate
    parameters. This function is blocking by default and only returns after
    rsync is complete.

    @source: The directory to sync.
    @dest: The location of the array where data is synced to. Eg. /data/ftp/.1
    @password: The rsync password defined by the upstream source.
    '''
    os.environ['RSYNC_PASSWORD'] = password
    cmd = 'rsync -avH --delete --progress ' + full_source + ' ' + dest
    rsync_child_process = subprocess.Popen(cmd,
                                           shell=True,
                                           stdin=subprocess.PIPE,
                                           stdout=subprocess.PIPE,)

    # Wait for the sync to complete before returning.
    rsync_child_process.wait()
    print "Rsync complete"


def rsync_call_nonblocking(
    full_source="54.245.124.177::documents/",
    dest=".",
    password="rsyncpassword",
    ):
    '''
    Function responsible for calling rsync as a subprocess with the appropriate
    parameters.

    @source: The directory to sync.
    @dest: The location of the array where data is synced to. Eg. /data/ftp/.1
    @password: The rsync password defined by the upstream source.
    '''
    os.environ['RSYNC_PASSWORD'] = password
    cmd = 'rsync -avH --delete --progress ' + full_source + ' ' + dest
    rsync_child_process = subprocess.Popen(cmd,
                                           shell=True,
                                           stdin=subprocess.PIPE,
                                           stdout=subprocess.PIPE,)


# Todo: The process is not exiting properly. Check!
def rsync_progress_call(
    full_source="54.245.124.177::documents/",
    dest=".",
    password="rsyncpassword",
    ):
    '''
    Function responsible for calling rsync as a subprocess with the appropriate
    parameters.

    @source: The directory to sync.
    @dest: The location of the array where data is synced to. Eg. /data/ftp/.1
    @password: The rsync password defined by the upstream source.
    '''
    os.environ['RSYNC_PASSWORD'] = password

    # A dry run call helps determine the total number of files used for tracking
    # percentage of sync during the real call.
    cmd = 'rsync -avH --delete --stats --dry-run ' + full_source + ' ' + dest
    proc = subprocess.Popen(cmd,
      shell=True,
      stdin=subprocess.PIPE,
      stdout=subprocess.PIPE,
    )
     
    nfiles_str = proc.communicate()[0]
    mn = re.findall(r'Number of files: (\d+)', nfiles_str)
    total_files = int(mn[0])
     
    cmd = 'rsync -avH --delete --progress ' + full_source + ' ' + dest 
    rsync_process = subprocess.Popen(cmd,
                                     shell=True,
                                     stdin=subprocess.PIPE,
                                     stdout=subprocess.PIPE,)

    # Reading the progress data from the rsync process.     
    while True:
        output = rsync_process.stdout.readline()
        if 'to-check' in output:
            m = re.search(r'to-check=(\d+)/(\d+)', output)
            progress = (100 * (int(m[1]) - int(m[0]))) / total_files
            print progress
     
            # Do something with the progress, perhaps update in a database or file.
            # So that there is a way to track the progress via the api.

            sys.stdout.flush()

            print m[0]
            if int(m[0]) == 0:
                break

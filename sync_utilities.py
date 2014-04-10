import subprocess
import re
import sys
import os

def rsync_call(
    full_source="ubuntu@xlstosql.brightants.com::documents/",
    dest = ".",
    password="rsyncpassword",
    ):
    '''
    Function responsible for calling rsync as a subprocess with the appropriate
    parameters.

    @source: The directory to sync. For current directory
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
            m = re.findall(r'to-check=(\d+)/(\d+)', output)
            progress = (100 * (int(m[0][1]) - int(m[0][0]))) / total_files
            print progress
     
            # Do something with the progress, perhaps update in a database or file.
            # So that there is a way to track the progress via the api.
     
            sys.stdout.flush()
            if int(m[0][0]) == 0:
                break

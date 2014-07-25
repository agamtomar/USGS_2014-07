# -*- coding: utf-8 -*-
# <nbformat>3.0</nbformat>

# <markdowncell>

# <img src='https://www.rc.colorado.edu/sites/all/themes/research/logo.png' style="height:75px">

# <codecell>

%run talktools.py

# <markdowncell>

# # Starting and Running Python notebooks

# <markdowncell>

# **ipython notebook --no-mathjax**

# <codecell>

!ipython notebook --help

# <markdowncell>

# ## Running a notebook on a remote host, e.g. login node of a remote cluster

# <markdowncell>

# ### Options relevant for remote notebooks

# <markdowncell>

# * **--no-browser**: don't open the notebook in a browser after startup 
# * **--ip**: The IP address the notebook server will listen on
# * **--port**: the port the notebook server will listen on

# <markdowncell>

# ### Starting the notebook on the login node
# 
# ```
# $ ssh tahauser@stampede.tacc.xsede.org
# stampde$ hostname
#    login2.stampede.tacc.utexas.edu
# 
# stampede$ ipython notebook --no-browser --port=9088 --ip=*
# ```
# 
# ### Connecting to the notebook server
# 
# http://login2.stampede.tacc.utexas.edu:9088

# <markdowncell>

# ## Securing the remote notebook
# 
# There are several steps to secure the notebook server on a remote machine (see http://ipython.org/ipython-doc/dev/notebook/public_server.html)
# 
# 1. Create a custom notebook profile
# 2. Create a self signed certificate to access the remote notebook with https
# 3. Create a simple password
# 4. Edit the notebook profile to specify the security settings
# 
# *There is a bug in the combination of Safari and tornado that may not allow you to run the remote notebook properly: Use a different browser*

# <markdowncell>

# ### 1. Creating a notebook profile
# 
# A profile allows you to manage different configurations for your notebook
# 
# ```
# gordon$ ipython profile create nbserver
# ```
# 
# This will create *.ipython/profile_nbserver* directory

# <codecell>

!ssh thauser@gordon.sdsc.xsede.org 'cd .ipython/profile_nbserver; ls -al'

# <markdowncell>

# ### 2. Create a self-signed certificate
# 
# ```
# gordon$ openssl req -x509 -nodes -days 365 -newkey rsa:1024 -keyout mycert.pem -out mycert.pem
# ```
# 
# ### 3. Create a password hash
# 
# In ipython execute

# <codecell>

from IPython.lib import passwd

passwd('test password')

# <markdowncell>

# ### 4. Edit the configuration for your profile
# 
# ```
# vim .ipython/profile_nbserver/ipython_notebook_config.py
# ```

# <codecell>

!ssh thauser@gordon.sdsc.xsede.org 'head -n 12 .ipython/profile_nbserver/ipython_notebook_config.py'

# <markdowncell>

# ## Running the secured remote notebook
# 
# ```
# ipython notebook --profile=nbserver
# ```
# 
# connect to
# 
# https://gordon-ln3.sdsc.edu:11111
# 
# you need to enter your password

# <markdowncell>

# ## Running the notebook in an interactive job on Stampede
# 
# 1. Start your interactive job
# ```
# stampede$ srun -p development -N 1 -n 16 -t 10 --pty /bin/bash
# ```
# 
# 2. Start your notebook
# ```
# gordon$ hostname
# gordon$ ipython notebook --profile=nbserver
# ```
# 3. Connect to it
# 
# ```
# https:gcn-19-14.sdsc.edu:11111
# ```

# <markdowncell>

# ## Port forwarding using ssh
# 
# On some machines compute nodes maybe not accessible from the outside
# 
# ### ssh port forwarding
# 
# On your local machine:
# ```
# #ssh -L localport:nodename:remote_port -f -N gordon.sdsc.xsede.org
# 
# $ ssh -L 8088:gcn-4-68:9088 -f -N gordon.sdsc.xsede.org
# ```
# 
# open your localbrowser at https://localhost:8088

# <markdowncell>

# ## Using SAGA to run a job on a remote node of a cluster
# 
# A light-weight access layer for distributed computing infrastructure
# 
# http://saga-project.github.io/saga-python/ 
# 
# 
# ### Create a saga script, e.g

# <codecell>

import sys
import time
import saga
import tunnel

# Adapted from the saga example
# Your ssh identity on the remote machine.
ctx = saga.Context("ssh")
ctx.user_id = 'thauser'

session = saga.Session()
session.add_context(ctx)

# Create a job service object that represent a remote pbs cluster.
js = saga.job.Service("pbs+ssh://gordon.sdsc.xsede.org", session=session)

# Set the parameters for this example
local_port=9988
remote_port=11111
username='thauser'
hostname='gordon.sdsc.xsede.org'

# Next, we describe the job we want to run. A complete set of job
# description attributes can be found in the API documentation.
jd = saga.job.Description()
jd.wall_time_limit   = 10 # minutes
jd.executable        = "ipython notebook --profile=nbserver"
jd.queue             = "normal"
jd.working_directory = "A"
jd.output            = "ipythonjob.out"
jd.error             = "ipythonjob.err"

# Create a new job from the job description. The initial state of
# the job is 'New'.
touchjob = js.create_job(jd)

# Check our job's id and state
print "Job ID    : %s" % (touchjob.id)
print "Job State : %s" % (touchjob.state)

# Now we can start our job.
print "\n...starting job...\n"
touchjob.run()

print "Job ID    : %s" % (touchjob.id)
print "Job State : %s" % (touchjob.state)

# List all jobs that are known by the adaptor.
# This should show our job as well.
print "\nListing active jobs: "
for job in js.list():
    print " * %s" % job

# Now we disconnect and reconnect to our job by using the get_job()
# method and our job's id. While this doesn't make a lot of sense
# here,  disconnect / reconnect can become very important for
# long-running job.

touchjob_clone = js.get_job(touchjob.id)

print touchjob_clone.state

while touchjob_clone.state == 'Pending':
    print "...Waiting for Job to start...."
    time.sleep(30)

nodename = touchjob_clone.execution_hosts[0]
nodename = nodename[:-2]
port=22
tunnel.create_tunnel(local_port=local_port, remote_port=remote_port, nodename=nodename,
                     username=username, hostname=hostname, port=port)

print "\n * Open a browser window at https://localhost:%d\n" % local_port
   
# wait for our job to complete
print "\n...waiting for ipython job to complete...\n"

touchjob_clone.wait()

print "Job State   : %s" % (touchjob_clone.state)
print "Exitcode    : %s" % (touchjob_clone.exit_code)
js.close()



# <codecell>



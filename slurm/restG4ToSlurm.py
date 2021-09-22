#!/usr/bin/python
# -*- coding: iso-8859-15 -*-

# This script generates the plots from the spectras
# J. Galan - Javier.Galan.Lacarra@cern.ch
# 7 - Sep- 2020

import argparse
import commands
import os
import sys

# Change this to modify your log output directory!
# Change this by your mail address!

# FIXME(If this value don't edit manually, than should move this value to argument `default` of `parser.add_argument`)
delay = 30
repeat = 10

sectionName = ""
jobName = ""
email = ""
logPath = ""
idOffset = 0

duration = "7-00:00:00"

# List of environment's keys which will added to SLURM environment
ENV_KEYS = ["USER", "DATA", "REST", "PRESSURE", "GAS", "QUENCHER", "QUENCHER", "GEOMETRY", "G4", "PATH",
            "LD_LIBRARY_PATH", "GARFIELD_", "HEED_", "PWD"]

parser = argparse.ArgumentParser(
    description="This program launches restG4 jobs to slurm. Values in brackets [] are optional"
)
parser.add_argument("-c", "--cfgFile", metavar="RML_FILE", required=True)
parser.add_argument("-n", "--sectionName", default=sectionName,
                    help="Defines the name of the section to be used from RML_FILE")
parser.add_argument("-e", "--email", default=email,
                    help="It allows to specify the e-mail for batch system job notifications")
# FIXME(Unused option)
# parser.add_argument("-i", "--initialRun", metavar="VALUE", help="An integer number to introduce the first run number.")
parser.add_argument("-i", "--idOffset", default=idOffset, type=int)
parser.add_argument("-r", "--repeat", metavar="REPEAT_VALUE", type=int, default=repeat,
                    help="This option defines the number of simulations we will launch (default is 10)")
parser.add_argument("-d", "--delay", metavar="DELAY_TIME", type=int, default=delay,
                    help="Time delay between launching 2 reapeated jobs (default is 30 seconds)")
parser.add_argument("-j", "--jobName", metavar="JOB_NAME", default=jobName,
                    help="JOB_NAME defines the name of scripts and output files stored under slurmJobs/")
# FIXME(Unused option)
# parser.add_argument("-o", "--onlyScripts", action="store_true",
#                     help="It will just generate the slurm scripts without launching to the queue")
parser.add_argument("-l", "--logPath", default=logPath, help="log output directory")

if len(sys.argv) < 2:
    parser.print_help()
    sys.exit(2)

args = parser.parse_args()

cfgFile = os.path.abspath(args.cfgFile)

if args.jobName == "":
    jobName = cfgFile[cfgFile.rfind("/") + 1:cfgFile.rfind(".rml")]
else:
    jobName = args.jobName

print ("Number of jobs to launch : " + str(args.repeat))
print ("Jobs name : " + str(jobName))
print ("Delay in seconds between jobs : " + str(args.delay))

runNumber = args.idOffset

for x in xrange(args.repeat):
    ################################################
    # Creating job environment and execution command
    ################################################
    scriptName = os.path.join(os.sep, "tmp", os.environ["USER"] + ".slurm")
    with open(scriptName, "w") as f:
        f.write("#!/bin/bash\n\n")
        f.write("#SBATCH -J " + str(runNumber) + "_" + jobName + "\n")
        f.write("#SBATCH --begin=now+" + str((x + 1) * args.delay) + "\n")
        f.write("#SBATCH --nodes=1\n")
        if args.logPath != "":
            name = jobName + "_" + str(runNumber)
            f.writelines((
                "#SBATCH -o " + os.path.join(args.logPath, name + ".log"),
                "#SBATCH -e " + os.path.join(args.logPath, name + ".error")
            ))
        if args.email != "":
            f.write("#SBATCH --mail-user " + args.email + "\n")
        f.write("#SBATCH --ntasks=1\n")
        f.write("#SBATCH --mail-type=ALL\n")
        f.write("#SBATCH -p bifi\n")
        f.write("#SBATCH --time=" + duration + " # days-hh:mm:ss\n")
        f.write("export RUN_NUMBER=" + str(runNumber) + "\n\n")
        # We transfer env variables to SLURM environment
        for env_key in ENV_KEYS:
            for key in os.environ.keys():
                if key.find(env_key) == 0:
                    f.write("export " + key + "=" + os.environ[key] + "\n")
                    #       print( "export " + key + "=" + os.environ[key] +"\n" )
        # The usual restG4 command is : restG4 RML_FILE [SECTION_NAME].
        command = "srun restG4 " + cfgFile + " " + args.sectionName
        f.write(command + "\n")
        runNumber += 1
    print commands.getstatusoutput("sbatch " + scriptName)

    # st = os.stat( scriptName + ".sh" )
    # os.chmod( scriptName + ".sh", st.st_mode | stat.S_IEXEC)
    #################################################

    # cont = 0
    #
    # rpt = repeat
    # while ( rpt > 0 ):
    #    cont = cont + 1
    #    rpt = rpt-1
    #
    #    g = open( scriptName + "_" + str(cont) + ".condor", "w" )
    #    g.write("Universe   = vanilla\n" );
    #    g.write("Executable = " + scriptName + ".sh\n" )
    #    g.write("Arguments = \n" )
    #    g.write("Log = " + scriptName + "_" + str(cont) + ".log\n" )
    #    g.write("Output = " + scriptName + "_" + str(cont) + ".out\n" )
    #    g.write("Error = " + scriptName + "_" + str(cont) + ".err\n" )
    #    g.write("Queue\n" )
    #    g.close()
    #
    #    if onlyScripts == 0:
    #        print "---> Launching : " + command
    #
    #        condorCommand = "condor_submit " + scriptName + "_" + str(cont) + ".condor"
    #        print "Condor command : " + condorCommand
    #
    #        print "Waiting " + str(sleep) + " seconds to launch next job"
    #        time.sleep(sleep)
    #
    #        print commands.getstatusoutput( condorCommand )
    #    else:
    #        print "---> Produced condor script : " + str( scriptName ) + "_" + str(cont) + ".condor"
    #        print "---> To launch : " + command
    #
    #    print ""
    # print ""
    ###

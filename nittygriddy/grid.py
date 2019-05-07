from __future__ import absolute_import
from __future__ import division
from __future__ import print_function

import os
import re
import subprocess

import ROOT

from nittygriddy import utils


def grid(args):
    #Check directory, token and grid usage (taken from merge.py)

    # check if we are in a output dirname
    if not ((os.path.isfile("./ConfigureTrain.C") or
             os.path.isfile("./MLTrainDefinition.cfg")) and
            os.path.isfile("./GetSetting.C") and
            os.path.isfile("./run.C")):
        raise ValueError("This command needs to be run from an output directory")

    if not utils.check_alien_token():
        print("No valid alien token present. Run `alien-token-init` before nittygriddy")
        quit()

    ROOT.gROOT.LoadMacro(r'GetSetting.C')
    if ROOT.GetSetting("runmode") != "grid":
        raise ValueError("The data in this folder was not run on the grid!")

    #Get process name from working directory
    WorkingDir = os.getcwd()
    ProcessName = WorkingDir.split("/")[-1]
    
    if args.gridmode == 'resubmit': 
        #Resubmit
        #Get list of failed jobs
        gbbox_split_cmd = ("gbbox ps -fs | grep " + ProcessName)
        #Get masterjobs which do not split (especially merging jobs)
        gbbox_cmd = ("gbbox ps -f | grep " + ProcessName) 
        gbbox_ps = ""
        try:
            gbbox_ps += subprocess.check_output(gbbox_split_cmd, shell=True)
        except subprocess.CalledProcessError as e:
            print ("No split jobs to resubmit found for: {}".format(ProcessName))
        try:
            gbbox_ps += subprocess.check_output(gbbox_cmd, shell=True)
        except subprocess.CalledProcessError as e:
            print ("No masterjobs to resubmit found for: {}".format(ProcessName))
            
        if gbbox_ps == "":
            print ("No jobs / masterjobs found for resubmission!")
            quit()

        #Remove double jobs 
        gbbox_set = set(gbbox_ps.splitlines())
        
        for line in gbbox_set:
            JobNr = line.split()[1]
            JobNr = re.sub("\D", "",JobNr)
            JobStat = line.split()[2]
            if (JobStat[0] == "E"):
                resub_cmd = ("gbbox resubmit " + JobNr)
                subprocess.call(resub_cmd, shell=True)
            else:
                print ("Job {} is in state: {}. Not resubmitting.".format(JobNr,JobStat))

    elif args.gridmode == 'nuke':
        print ("Work in progress. Function still needs to be implemented.")


    #Get list of all masterjobs
    #Ask if job should be killed
    #Kill all masterjobs

def create_subparsers(subparsers):
    description_grid = """Handle jobs submitted to grid. Must be executed from output folder of that
    analysis. Only jobs related to this analysis are affected."""
    parser_grid = subparsers.add_parser('grid', description=description_grid)
    parser_grid.add_argument('gridmode',
                             choices=('resubmit','nuke'),
                             help=("resubmit or kill all jobs related to this folder. "
                                   "Resubmit will look for all failed jobs, while nuke kills all masterjobs." ))
    parser_grid.add_argument('--force',action='store_true', default=False, help="Force killing of jobs, without acknowledging.")
    parser_grid.set_defaults(op=grid)

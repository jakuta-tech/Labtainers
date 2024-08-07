#!/opt/labtainer/venv/bin/python3
'''
This software was created by United States Government employees at 
The Center for Cybersecurity and Cyber Operations (C3O) 
at the Naval Postgraduate School NPS.  Please note that within the 
United States, copyright protection is not available for any works 
created  by United States Government employees, pursuant to Title 17 
United States Code Section 105.   This software is in the public 
domain and is not subject to copyright. 
Redistribution and use in source and binary forms, with or without
modification, are permitted provided that the following conditions
are met:
  1. Redistributions of source code must retain the above copyright
     notice, this list of conditions and the following disclaimer.
  2. Redistributions in binary form must reproduce the above copyright
     notice, this list of conditions and the following disclaimer in the
     documentation and/or other materials provided with the distribution.

THIS SOFTWARE IS PROVIDED BY THE AUTHOR ``AS IS'' AND ANY EXPRESS OR
IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED
WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE ARE
DISCLAIMED.  IN NO EVENT SHALL THE AUTHOR BE LIABLE FOR ANY DIRECT,
INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES
(INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR
SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION)
HOWEVER CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT,
STRICT LIABILITY, OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN
ANY WAY OUT OF THE USE OF THIS SOFTWARE, EVEN IF ADVISED OF THE
POSSIBILITY OF SUCH DAMAGE.
'''

# Filename: redo.py
# Description:
# For lab development testing workflow.  This will stop containers of a lab, create or update lab images
# and start the containers.
#

import sys
import os
import labutils
import logging
import argparse
import LabtainerLogging
import CurrentLab

def main():

    dir_path = os.path.dirname(os.path.realpath(__file__))
    dir_path = dir_path[:dir_path.index("scripts/labtainer-student")]	
    path = dir_path + "labs/"
    dirs = os.listdir(path)
    parser = argparse.ArgumentParser(description='Restart a fresh instance of aLabtainers lab.  Previous work on this lab will be lost. The lab will be stopped if it is running.')
    parser.add_argument('labname', help='The lab to run')
    parser.add_argument('-q', '--quiet', action='store_true', help='Do not prompt for email, use previoulsy supplied email.')
    parser.add_argument('-s', '--servers', action='store_true', help='Intended for distributed Labtainers, start the containers that are not clients.')
    parser.add_argument('-w', '--workstation', action='store_true', help='Intended for distributed Labtainers, start the client workstation.')
    parser.add_argument('-n', '--client_count', action='store', help='Number of clones of client components to create, itended for multi-user labs')
    parser.add_argument('-o', '--only_container', action='store', help='run only the named container')
    args = parser.parse_args()
    labname = args.labname
    if labname not in dirs:
        sys.stderr.write("ERROR: Lab named %s was not found!\n" % labname)
        sys.exit(1)
    
    labutils.logger = LabtainerLogging.LabtainerLogging("labtainer.log", labname, "../../config/labtainer.config")
    labutils.logger.info("Begin logging start.py for %s lab" % labname)
    lab_path = os.path.join(os.path.abspath('../../labs'), labname)
    update_flag='../../../.doupdate'
    if os.path.isfile(update_flag):
        ''' for prepackaged VMs, do not auto update after first lab is run '''
        os.remove(update_flag)
    #print('lab_path is %s' % lab_path)
    distributed = None
    if args.servers and args.workstation:
        print('--server and --workstation are mutually exclusive')
        exit(1)
    elif args.servers: 
        distributed = 'server' 
    elif args.workstation:
        distributed = 'client'
    if distributed is not None and args.client_count is not None:
        print('Cannot specify --server or --client if a --client_count is provided')
        exit(1)
    labutils.RedoLab(lab_path, quiet_start=args.quiet, 
                     run_container=args.only_container, servers=distributed, clone_count=args.client_count)
    current_lab = CurrentLab.CurrentLab()
    current_lab.add('lab_name', args.labname)
    current_lab.add('clone_count', args.client_count)
    current_lab.add('servers', distributed)
    current_lab.save()

    return 0

if __name__ == '__main__':
    sys.exit(main())


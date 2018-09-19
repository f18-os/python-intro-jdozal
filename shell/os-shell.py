#!/usr/bin/env python3

import os, sys, time, re
from os.path import expanduser

def redirect(args):
    if '<' in args:
        print('<')
        return 
    fileIndex = args.index('>') + 1
    filename = args[fileIndex]
    args = args[:fileIndex-1]
    
    pid = os.getpid()               # get and remember pid
    
    rc = os.fork()
    
    if rc < 0:
        #os.write(2, ("Fork failed, returning %d\n" % rc).encode())
        sys.exit(1)
    
    elif rc == 0:                   # child 
        os.close(1)                 # redirect child's stdout
        sys.stdout = open(filename, "w")
        os.set_inheritable(1, True)
    
        for dir in re.split(":", os.environ['PATH']): # try each directory in path
            program = "%s/%s" % (dir, args[0])
            try:
                os.execve(program, args, os.environ) # try to exec program
            except FileNotFoundError:             # ...expected
                pass                              # ...fail quietly 
                
        print("%s: command not found\n" % args[0])
        sys.exit(1)                 # terminate with error
    
    else:                           # parent (forked ok)
        childPidCode = os.wait()
        #os.write(1, ("Parent: Child %d terminated with exit code %d\n" % 
        #             childPidCode).encode())

def execute(args):
    pid = os.getpid()
    
    rc = os.fork()
    
    if rc < 0:
        sys.exit(1)
    
    elif rc == 0:                   # child
        for dir in re.split(":", os.environ['PATH']): # try each directory in the path
            program = "%s/%s" % (dir, args[0])
            try:
                os.execve(program, args, os.environ) # try to exec program
            except FileNotFoundError:             # ...expected
                pass                              # ...fail quietly
    
        #os.write(2, ("Child:    Could not exec %s\n" % args[0]).encode())
        os.write(1, ("%s: command not found\n" % args[0]).encode())
        sys.exit(1)                 # terminate with error
    
    else:                           # parent (forked ok)
        #os.write(1, ("Parent: My pid=%d.  Child's pid=%d\n" % 
        #             (pid, rc)).encode())
        childPidCode = os.wait()
        #os.write(1, ("Parent: Child %d terminated with exit code %d\n" % 
        #             childPidCode).encode())
        
        
def cd(args):
    try:
        os.chdir(args[1])
    except IndexError:
        home = expanduser("~")
        os.chdir(home)
    except FileNotFoundError:
        os.write(1, ("cd: %s: No such file or directory\n" % args[1]).encode())
    
def prompt():
    while True:
        userIn = input("$ ")
        if(userIn == 'exit'):
            break;
        args = userIn.split()
        if(args[0] == 'cd'):
            cd(args)
        elif ('>' or '<') in userIn:
            redirect(args)
        else:
            execute(args)

prompt()


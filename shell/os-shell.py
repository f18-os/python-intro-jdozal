#!/usr/bin/env python3

import os, sys, time, re
from os.path import expanduser
import fileinput

def pipe(args):
    pid = os.getpid()               # get and remember pid
   
    pipeIndex = args.index('|')
    
    pipein,pipeout = os.pipe()
    for f in (pipein, pipeout):
        os.set_inheritable(f, True)
    
    
    
    rc = os.fork()
    
    if rc < 0:
        print("fork failed, returning %d\n" % rc, file=sys.stderr)
        sys.exit(1)
    
    elif rc == 0:                   #  child - will write to pipe
        args = args[:pipeIndex]
    
        os.close(1)                 # redirect child's stdout
        fd = os.dup(pipeout)
        os.set_inheritable(fd, True)
        for fd in (pipein, pipeout):
            os.close(fd)
        if os.path.isfile(args[0]):
            try:
                os.execve(args[0], args, os.environ) # try to exec program
            except FileNotFoundError:             # ...expected
                pass                              # ...fail quietly
        else:
            checkPATH(args)
            
        os.write(1, ("%s: command not found\n" % args[0]).encode())

        sys.exit(1)                 # terminate with error

    else:                           # parent (forked ok)
        args = args[pipeIndex+1:]

        os.close(0)
        fd = os.dup(pipein)
        os.set_inheritable(fd, True)
        for fd in (pipeout, pipein):
            os.close(fd)

        if os.path.isfile(args[0]):
            try:
                os.execve(args[0], args, os.environ) # try to exec program
            except FileNotFoundError:             # ...expected
                pass                              # ...fail quietly
        else:
            checkPATH(args)
            
        os.write(1, ("%s: command not found\n" % args[0]).encode())

        sys.exit(1)                 # terminate with error

        
def redirectTo(args):
    fileIndex = args.index('>') + 1
    filename = args[fileIndex]
    #os.write(1, ("filename = %s\n" % filename).encode())
    args = args[:fileIndex-1]
    
    pid = os.getpid()               # get and remember pid
    
    rc = os.fork()
    
    if rc < 0:
        #os.write(2, ("Fork failed, returning %d\n" % rc).encode())
        sys.exit(1)
    
    elif rc == 0:                   # child 
        os.close(1)                 # redirect child's stdout

        sys.stdout = open(filename,"w")
            
        os.set_inheritable(1, True)
    
        if os.path.isfile(args[0]):
            try:
                os.execve(args[0], args, os.environ) # try to exec program
            except FileNotFoundError:             # ...expected
                pass                              # ...fail quietly
        else:
            checkPATH(args)
            
        os.write(1, ("%s: command not found\n" % args[0]).encode())

        sys.exit(1)                 # terminate with error
    
    else:                           # parent (forked ok)
        childPidCode = os.wait()
        #os.write(1, ("Parent: Child %d terminated with exit code %d\n" % 
        #             childPidCode).encode())

def redirectFrom(args):
    fileIndex = args.index('<') + 1
    filename = args[fileIndex]
    #os.write(1, ("filename = %s\n" % filename).encode())
    args = args[:fileIndex-1]
    
    pid = os.getpid()               # get and remember pid
    
    rc = os.fork()
    
    if rc < 0:
        #os.write(2, ("Fork failed, returning %d\n" % rc).encode())
        sys.exit(1)
    
    elif rc == 0:                   # child 
        os.close(0)                 # redirect child's stdout

        sys.stdin = open(filename, "r+b")
            
        os.set_inheritable(0, True)
    
    
        if os.path.isfile(args[0]):
            try:
                os.execve(args[0], args, os.environ) # try to exec program
            except FileNotFoundError:             # ...expected
                pass                              # ...fail quietly
        else:
            checkPATH(args)
            
        os.write(1, ("%s: command not found\n" % args[0]).encode())

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
        if os.path.isfile(args[0]):
            try:
                os.execve(args[0], args, os.environ) # try to exec program
            except FileNotFoundError:             # ...expected
                pass                              # ...fail quietly
        else:
            checkPATH(args)
        #os.write(2, ("Child:    Could not exec %s\n" % args[0]).encode())
        os.write(1, ("%s: command not found\n" % args[0]).encode())
        sys.exit(1)                 # terminate with error
    
    else:                           # parent (forked ok)
        #os.write(1, ("Parent: My pid=%d.  Child's pid=%d\n" % 
        #             (pid, rc)).encode())
        childPidCode = os.wait()
        #os.write(1, ("Parent: Child %d terminated with exit code %d\n" % 
        #             childPidCode).encode())
        
def checkPATH(args):
    for dir in re.split(":", os.environ['PATH']): # try each directory in the path
        program = "%s/%s" % (dir, args[0])
        try:
            os.execve(program, args, os.environ) # try to exec program
        except FileNotFoundError:             # ...expected
            pass                              # ...fail quietly
            
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
        elif '>' in userIn:
            redirectTo(args)
        elif '<' in userIn:
            redirectFrom(args)
        elif '|' in userIn:
            pipe(args)
        else:
            execute(args)

prompt()


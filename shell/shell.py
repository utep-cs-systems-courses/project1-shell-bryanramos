#! /usr/bin/env python3

# Author: Bryan Ramos
# Course: Theory of Operating Systems (OS)
# Instructors: Eric Freudenthal and David Pruitt
# Assignment: Lab 1 Shell
# Assignment Description: Create a user shell that mimics some of the behaviors of the bash shell. 

import sys, os, re

def main():
    # infinte loop to continually run shell
    while True:
        if 'PS1' in os.environ:
            os.write(1, (os.environ['PS1']).encode())
        else: # if unset, as per requirements
            os.write(1, ("$ ").encode())

        args = os.read(0, 1024)

        if len(args) == 0:
            break

        args = args.decode().split("\n")

        if not args:
            continue
        
        for arg in args:
            inputHandler(arg.split())

def inputHandler(args):
    if len(args) == 0: # reprompt, return back to main()
        return

    elif args[0] == "exit" or args[0] == "Exit": # exit command - 'Exit' and 'exit both function
        sys.exit(0)
    
    elif args[0] == "cd":
        try: 
            os.chdir(args[1])
        except: # nonexistent
            pass

    elif "|" in args:
        pipe(args)

    else: # everything else
        rc = os.fork()
        wait = True

        if "&" in args:
            args.remove("&")
            wait = False

        if rc < 0: # capture error during fork
            os.write(2, ("fork failed, returning %d\n" % rc).encode())
            sys.exit(1)

        elif rc == 0:
            executeCommand(args)
            sys.exit(0)

        else:
            if wait:
                childpid = os.wait()
                if childpid[1] != 0 and childpid[1] != 256:
                    os.write(2, ("Program terminated with exit code: %d\n" % childpid[1]).encode())

def pipe(args):
    left = args[0:args.index("|")]
    right = args[args.index("|") + 1:]

    pr, pw = os.pipe()
    rc = os.fork()

    if rc < 0: # capture error during fork
        os.write(2, ("fork failed, returning %d\n" % rc).encode())
        sys.exit(1)
     
    elif rc == 0: 
        os.close(1)
        os.dup(pw)
        os.set_inheritable(1, True)
        for fd in (pr, pw):
            os.close(fd)
        executeCommand(left)
        os.write(2, ("Could not exec %s\n" % left[0]).encode())
        sys.exit(1)
        
    else:
        os.close(0)
        os.dup(pr)
        os.set_inheritable(0, True)
        for fd in (pw, pr):
            os.close(fd)
        
        # two pipe handler
        if "|" in right:
            pipe(right)
        
        executeCommand(right)
        os.write(2, ("Could not exec %s\n" % right[0]).encode())
        sys.exit(1)
        
def executeCommand(args):

    if "/" in args[0]:
        program = args[0]
        try:
            os.execve(program, args, os.environ)
        except FileNotFoundError:  
            pass 

    else:
        for dir in re.split(":", os.environ['PATH']): # try each directory in the path
            program = "%s/%s" % (dir, args[0])
            try:
                os.execve(program, args, os.environ) # try to exec program
            except FileNotFoundError:
                pass
                
    os.write(2, ("%s: command not found\n" % args[0]).encode()) # command not found, print error message
    sys.exit(0)

if __name__ == "__main__":
    main()

#! /usr/bin/env python3

# Author: Bryan Ramos
# Course: Theory of Operating Systems (OS)
# Instructors: Eric Freudenthal and David Pruitt
# Assignment: Lab 1 Shell
# Assignment Description: Create a user shell that mimics some of the behaviors of the bash shell. 

import sys, os, re

wait = True

def main():
    # infinite loop to continually run shell
    while True:
        if 'PS1' in os.environ:
            os.write(1, (os.environ['PS1']).encode())
        else: # if unset, as per requirements
            os.write(1, ("$ ").encode())

        try:
            userInput = input()
        except EOFError:
            sys.exit(1)
        except ValueError:
            sys.exit(1)
        
        userInput = userInput.split("\n")

        for arg in userInput: 
            inputHandler(arg)
        
    
def inputHandler(userInput):
    args = userInput.split() # tokenize user input arguments

    if '&' in args:
        wait = False
        args.remove("&")

    if ('exit' in args) or ('Exit' in args): # exit command - Exit and exit both work
        sys.exit(0)

    elif args == "": # empty input, just reprompt the user, like in real bash
        pass

    elif 'echo' in args: # echo back to the user their input
        os.write(2, (args[1:]).encode())

    elif args[0][0] == '/':
        try:
            os.execve(args[0], args, os.environ)  # try to exec program     
        except FileNotFoundError:
            pass

    elif 'cd' == args[0].lower(): # change directory - cd and CD both work
        try: 
            os.chdir(args[1])
        except FileNotFoundError: # nonexistent
            pass

    elif '|' in args: # pipe: used to read the output from one command and use it for the input of another command (i.e. dir | sort)
        pipe(args)

    elif '<' in args:
        redirectIn(args)

    elif '>' in args:
        redirectOut(args)

    else: # everything else
        executeCommand(args)

def redirectIn(inputs):
    os.close(0)
    os.open(inputs[inputs.index('<')+1], os.O_RDONLY);
    os.set_inheritable(0, True)
    executeCommand(inputs[0:inputs.index('<')])

def redirectOut(args):
    pid = os.getpid()

    rc = os.fork()

    if rc < 0:
        os.write(2, ("Failed to fork, returning").encode())
        sys.exit(1)

    elif rc == 0:
        os.close(1)
        os.open(args[args.index('>')+1], os.O_CREAT | os.O_WRONLY)
        os.set_inheritable(1,True)

        for dir in re.split(":", os.environ['PATH']): # try each directory in path
            prog = "%s/%s" % (dir,args[0])
            try:
                os.execve(prog, args, os.environ) # try to exec program
            except FileNotFoundError:
                pass

        os.write(1, ("%s: command not found\n" % args[0]).encode())
        sys.exit(0)

    else:
        child_pid = os.wait()

# based on pipe from pipe-fork demo
def pipe(args):
    pid = os.getpid()
    pipe = args.index("|") # check for pipe symbol in command

    pr, pw = os.pipe()
    for f in (pr, pw):
        os.set_inheritable(f, True)
    
    rc = os.fork()

    if rc < 0: # capture error during fork
        os.write(2, ("fork failed, returning %d\n" % rc).encode())
        sys.exit(1)

    elif rc == 0: # write to pipe from child
        args = args[:pipe]

        os.close(1)

        fd = os.dup(pw) # dup() duplicates file descriptor 
        os.set_inheritable(fd, True)
        for fd in (pr, pw):
            os.close(fd)

        if os.path.isfile(args[0]):  # check whether the specified path is an existing regular file or not
            try:
                os.execve(args[0], args, os.environ)
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
            sys.exit(1)
    
    else:
        args = args[pipe+1:]
        
        os.close(0)

        fd = os.dup(pr) # dup() duplicates file descriptor 
        os.set_inheritable(fd, True)

        for fd in (pw, pr):
            os.close(fd)
        
        if os.path.isfile(args[0]): # check whether the specified path is an existing regular file or not
            try:
                os.execve(args[0], args, os.environ)
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
            sys.exit(1)

def executeCommand(args):
    # based off of p3-exec demo
    pid = os.getpid()
    rc = os.fork()

    if rc < 0: # capture error during fork
        os.write(2, ("fork failed, returning %d\n" % rc).encode())
        sys.exit(1)

    elif rc == 0:
        for dir in re.split(":", os.environ['PATH']): # try each directory in the path
            program = "%s/%s" % (dir, args[0])
            try:
                os.execve(program, args, os.environ) # try to exec program
            except FileNotFoundError:
                pass
                
        os.write(2, ("%s: command not found\n" % args[0]).encode()) # command not found, print error message
        sys.exit(1)
    
    else:
        if wait:
            childpid = os.wait()


if __name__ == "__main__":
    main()
#! /usr/bin/env python3

import sys, os, re

def main():
    while True:
        if 'PS1' in os.environ:
            os.write(1, (os.environ['PS1']).encode())
        else:
            os.write(1, ("$ ").encode())

        try:
            userInput = input()
        except EOFError:
            sys.exit(1)
        except ValueError:
            sys.exit(1)

        inputHandler(userInput) # handle input method

def inputHandler(userInput):
    args = userInput.split() # tokenize user input arguments

    if 'exit' in userInput: # exit command
        sys.exit(0)
    elif userInput == "": # for empty input, just reprompt the user
        pass
    else:
        executeCommand(args)

def executeCommand(args):
    pid = os.getpid()
    rc = os.fork()

    # based off of p3-exec demo

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
        childpid = os.wait()

if __name__ == "__main__":
    main()
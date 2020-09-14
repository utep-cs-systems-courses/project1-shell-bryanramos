#! /usr/bin/env python3

import sys, os, re

def main():

    file = open("history.dat", "a+") # history file

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

        file.write("%s\n" % userInput)

        inputHandler(userInput) # handle input method

def inputHandler(userInput):
    args = userInput.split() # tokenize user input arguments

    if 'exit' in userInput.lower(): # exit command - Exit and exit both work
        sys.exit(0)

    elif userInput == "":   # empty input, just reprompt the user
        pass

    elif 'cd' in args[0]: # change directory
        try: 
            if len(args) <= 1: # if just cd is specified, move down to parent directory of current directory
                os.chdir("..")
            else: 
                os.chdir(args[1])
            print(os.getcwd())
        except FileNotFoundError:
            os.write(1, ("cd %s: No such file or directory" % args[1]).encode())
            pass

    elif '|' in userInput: # pipe: used to read the output from one command and use it for the input of another command (i.e. dir | sort)
        print("Pipe functionality: coming soon!")

    elif args[0] == "history" and len(args) is 1: # history
        file = open("history.dat", "r") # history file
        lines = file.readlines()
        id = 1
        for line in lines:
            print(id, line, end = "")
            id += 1

    elif args[0] == "history" and args[1] is not None:
        try:
            id = int(args[1])
            file = open("history.dat", "r") # history file
            lines = file.readlines()
            if lines[id-1] is not None:
                print(id, lines[id-1])
            else:
                print("Cannot locate history for Id %d" % id)
        except: 
            os.write(1, ("Improper format for %s" % args[1]).encode())
    


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
    try:
        main()
    except KeyboardInterrupt:
        file = open("history.dat", "a+") # history file
        file.seek(0)                     # absolute file positioning 
        file.truncate()                  # erase all data
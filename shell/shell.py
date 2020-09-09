#! /usr/bin/env python3

import os, sys

while True:
    if 'PS1' in os.environ:
        os.write(1, (os.environ['PS1']).encode())
    else:
        os.write(1, ('$ ').encode())
        
        try:
            userInput = input()
        except EOFError:
            sys.exit(1)
        except ValueError:
            sys.exit(1)
    
    if 'exit' in userInput: # exit command
        break
    elif userInput == "": # for empty input, just reprompt the user
        continue
    else:


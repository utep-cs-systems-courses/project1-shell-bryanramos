## Shell Project

The following commands are supported:

* **exit** or **Exit**: terminate shell
* **empty input**: reprompts user
* **cd** or **CD**: change directory
  * cd by itself - works in bash and windows by itself
  * cd with an argument
* **<, >**: redirect
* **|**: pipe
* accepts other typical commands in bash like ls, dir, sort, etc.

To run the shell, enter the shell folder using cd shell.
Then run either ./shell.py or python3 shell.py in either WSL, Linux or Mac OS.

You can change the prompt string by specifying the shell variable PS1. 
For example, if you type the following in Bash: 

` export PS1="\u@\h [\$(date +%k:%M:%S)]>" `

The current time will be shown in the prompt. Otherwise the default `$` will be shown.

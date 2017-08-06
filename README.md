# Vod Auto Uploader

## intro
once upon a time, someone told me, "write code that will make your programming professors cry". this is my attempt at that

jokes aside, this is pretty bad code. its mostly copy-pasted stuff (all sources attributed!), and was not engineered as much as written really quickly one long night.

## what it is

* python script which takes in a filename, monitors it til it stops growing, then parses a streamcontrol.xml file to figure out a title, then uploads it to youtube 
* powershell (seemed like the fastest way to do it at the time, don't judge me) script which watches a folder, then calls the python script when an mp4 file is created
* windows batch script (see previous comment) to start the powershell watcher


i swear i can write good code, this is not it. having a version of this per game is just one indicator that this is a slapped together hack. another is the use of 3 languages, and a 10 second sleep loop to figure out when a file is done. NEVERTHELESS IT WORKS

## how to use it

youre going to need to modify this to be able to use it. almost all paths (paths to the uploader scripts, paths to the vod folder, like everything) are hardcoded. the parsing of the stream control XML we use to name the videos is dependent on our specific setup we use for our overlay and our overlay updater. the uploader script has hardcoded keywords for nebulous. like i said, you're *really* gonna wanna modify this before you use it. but, hopefully this helps someone set something similar to the system we have at nebulous for themselves. 


## FAQ, tech-support, questions, etc
none. any questions about this will be ignored, or answered (rudely). you should probably find someone who knows a decent bit about computers if youre going to try and use this on your system.

## license
MIT License. you can do whatever the hell you want with this code

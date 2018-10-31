# ero

Event Relevance Optimization over Online Social Networks

## Requirements

Make sure you have [python2.7](https://www.python.org/downloads/) installed and update [pip](https://pip.pypa.io/en/stable/installing/) to the latest version.

    $ pip2.7 install --user --upgrade pip

Install virtualenv to use the python virtual environments

    $ pip2.7 install --user --upgrade virtualenv

Download the environment ENV and put it in the ero folder ero/ENV

Now you must activate this environment. You will need to run this command every time you want to use this environment.

    $ source ./ENV/bin/activate

Next, use pip to install the required python packages. If you are not using virtualenv, you should add the `--user` option (alternatively you could install the libraries system-wide, but this will probably require administrator rights, e.g. using `sudo pip2.7` instead of `pip2.7` on Linux).

    $ pip2.7 install --upgrade -r requirements.txt

## Run make rules

To run some of the make rules you have to grant execution permission to .sh files.

    $ find ero/ -type f -iname "*.sh" -exec chmod +x {} \;    

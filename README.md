# ero

Event Relevance Optimization over Online Social Networks

## Contribution

To contribute to the project please sign the [CLA](https://cla-assistant.io/RicCapUnitn/ero); this is to keep the rights to share the project linked to the github repo.

### Branching strategy

Master only (master freezed to releases and all commits made on develop after local rebase.

### Workflow

We use ZenHub to describe tasks and TestDrivenDevelopment, so that the workflow is:

1. Open issue
2. Link issue to epic (if you don't find an epic, than you need to create one). Remember to put estimates(1-5) and labels.
3. Implement the tests
4. Implement the code
5. Reformat using make pep8_reformat. Using a good editor(I use atom) with the autopep8 beautifier is a very good solution. Check that all tests pass.
6. Commit (try using closes #commit)
7. git fetch. git rebase (-i)
8. git push

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

Download snap from the [official repository](http://snap.stanford.edu/snappy/index.html).
Unpack it and put the file \_snap.so in the src/ folder.

Download then the facebook network from [here](http://snap.stanford.edu/data/ego-Facebook.html).

## Run make rules

To run some of the make rules you have to grant execution permission to .sh files.

    $ find ero/ -type f -iname "\*.sh" -exec chmod +x {} \;

## Docs

To compile the documentation either you create the missing folders (\_static, \_build, \_templates) in the docs folder, or you simply run the command sphinx-quickstart in the docs folder and accept all defaults; then use the files on git to configure it and run

    $ make doc

SHELL=/bin/sh #Shell da utilizzare per l'esecuzione dei comandi

# if set to @ will hide which command are executed,
# otherwise it will show all executed commands
SILENT = @

# if set to --silent will hide recursive make output,
# otherwise it will show all the outputs
MAKE_SILENT = --silent

# Turn args into do-nothing targets. This allow to run make Rules with arugments
# (e.g. run tests 1 -> ./test/run_tests.sh 1); if you don't use this command
# it considers the two arguments as rules (it will try to run rule "1")

RUN_ARGS := $(wordlist 2,$(words $(MAKECMDGOALS)),$(MAKECMDGOALS))
$(eval $(RUN_ARGS):;@:)

help:
	$(SILENT)echo "ero makefile\n"

pep8_check:
	$(SILENT)pep8 --exclude='./ENV,./src/snap.py' .

pep8_reformat:
	$(SILENT)autopep8 --in-place --aggressive --experimental -r ./src/ero*.py
	$(SILENT)autopep8 --in-place --aggressive --experimental -r ./src/features
	$(SILENT)autopep8 --in-place --aggressive --experimental -r ./test/*.py
	$(SILENT)autopep8 --in-place --aggressive --experimental -r ./tools/*.py

.SILENT: tests

compile_requirements:
	$(SILENT)pip2.7 freeze > requirements.txt

install_requirements:
	$(SILENT)pip2.7 install --upgrade -r requirements.txt

doc:
	$(SILENT)sphinx-apidoc -f -o docs/ src/ src/snap.py
	$(SILENT)cd docs/ && $(MAKE) html

tests: clean
	$(SILENT)echo ">>> Testing..."
	$(SILENT)./test/run_tests.sh $(filter-out $@, $(MAKECMDGOALS))
	$(SILENT)echo ">>> Done: Testing\n"


### ===================== ###
###     Clean section     ###
### ===================== ###
.PHONY: clean

clean:
	$(SILENT)echo ">>> Deleting temporary files..."
	$(SILENT)./tools/clean.sh
	$(SILENT)echo ">>> Done: Deleting temporary files\n"

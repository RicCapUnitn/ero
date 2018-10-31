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
	$(SILENT)pep8 --exclude='./ENV' .

pep8_reformat:
	$(SILENT)autopep8 --in-place --aggressive --experimental -r ./src

.SILENT: tests

requirements:
	$(SILENT)pipreqs --force --savepath ./requirements.txt ./src

tests: clean
	$(SILENT)echo ">>> Starting testing..."
	$(SILENT)./test/run_tests.sh $(filter-out $@, $(MAKECMDGOALS))
	$(SILENT)echo ">>> Done!\n"


### ===================== ###
###     Clean section     ###
### ===================== ###
.PHONY: clean

clean:
	$(SILENT)echo ">>> Deleting temporary files..."
	$(SILENT)./tools/clean.sh
	$(SILENT)echo ">>> Done!\n"

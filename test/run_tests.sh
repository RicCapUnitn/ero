echo '>>> TEST UNIT     : Starting'
echo '>>> TEST COVERAGE : Starting'
coverage2 run --source=./src/eroproject -m --omit=./src/eroproject/snap.py unittest discover -v -s ./test
coverage2 html -d ./docs/testsCoverage
echo '>>> TEST UNIT     : Finished'
echo '>>> TEST COVERAGE : Finished'

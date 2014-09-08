
.PHONY: all
all:

.PHONY: test
test:
	cd test && python test.py -- -knownfailure

.PHONY: testall
testall:
	cd test && python testall.py


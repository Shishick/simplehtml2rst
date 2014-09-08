This directory holds the simplehtml2rst test suite.
Mostly it is a "cases/" directory with expected input (HTML)
and output (RST) content.

To run the test suite:

    python test.py [TAGS...]

The test driver used (testlib.py) allows one to filter the tests run via short
strings that identify specific or groups of tests. Run `python test.py -l` to
list all available tests and their names/tags. I use the "knownfailure" tag to
mark those tests that I know fail
To run the test suite **without** the known failures:

    $ python test.py -- -knownfailure
    ...
    
    ----------------------------------------------------------------------
    Ran 42 tests in 0.799s
    
    OK



import pytest
import json


@pytest.mark.hookwrapper
def pytest_runtest_makereport(item):
    x = yield
    x._result.max_score = getattr(item._obj, 'max_score', 0)
    x._result.visibility = getattr(item._obj, 'visibility', 'visible')

def pytest_terminal_summary(terminalreporter, exitstatus):
    json_results = {'tests': []}

    all_tests = []
    #import pdb; pdb.set_trace()
    def _add(all_tests, new_tests, is_error):
        for t in new_tests:
            t.is_error = is_error

        all_tests.extend(new_tests)

    if ('passed' in terminalreporter.stats):
        _add(all_tests, terminalreporter.stats['passed'], is_error=False)
    if ('failed' in terminalreporter.stats):
        _add(all_tests, terminalreporter.stats['failed'], is_error=True)
    if ('error' in terminalreporter.stats):
        _add(all_tests, terminalreporter.stats['error'], is_error=True)

    for s in all_tests:
        output = ''
        score = s.max_score
        if (s.outcome == 'failed'):
            score = 0
            output = s.longrepr.reprcrash.__str__() if s.is_error else "Detailed output is hidden."
            #output = str(s.longrepr.chain[0][0].reprentries[0])

        json_results["tests"].append(
            {
                'score': score,
                'max_score': s.max_score,
                'name': s.location[2],
                #'output': "Suppressed output.",
                'output': output, #TODO handle this in autograde.py instead so we have more options?
                'visibility': s.visibility
            }
        )

    with open('results.json', 'w') as results:
        results.write(json.dumps(json_results, indent=4))

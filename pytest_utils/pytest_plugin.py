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
        if s.outcome == "failed":
            output = ''
            score = 0
            max_score = s.max_score if hasattr(s, "max_score") else 1
            visibility = s.visibility if hasattr(s, "visibility") else "visible"

            if s.is_error:
                if hasattr(s.longrepr, "reprcrash"):
                    output = s.longrepr.reprcrash.__str__()
                else:
                    output = s.longrepr.longrepr
            else:
                output = "Detailed output is hidden."

            #output = str(s.longrepr.chain[0][0].reprentries[0])
        else:
            output = ''
            score = s.max_score
            max_score = s.max_score
            visibility = s.visibility

        json_results["tests"].append(
            {
                'score': score,
                'max_score': max_score,
                'name': s.location[2],
                #'output': "Suppressed output.",
                'output': output, #TODO handle this in autograde.py instead so we have more options?
                'visibility': visibility,
            }
        )

    with open('results.json', 'w') as results:
        results.write(json.dumps(json_results, indent=4))

__test_logs = [
    "EventLogs/BPI2017-Top10.jsonocel",
    "EventLogs/p2p.jsonocel",
    "EventLogs/test_log.jsonocel",
    "EventLogs/Presentation_Example.jsonocel"]

__branching = {
    "main": {
        "mode": 8,
        "file": __test_logs[0],
        "parameters": {"execution_extraction": "leading_type"},
        "alignment": {"align": False, "repeat": None},
    },
    "expl": {
        "mode": None,
        "file": __test_logs[1],
        "alignment": {"align": True, "repeat": True},
    },
    "eval": {
        "mode": 9,
        "file": __test_logs[1],
        "alignment": {"align": False, "repeat": None},
    },
    "publ": {
        "mode": 9,
        "file": __test_logs[2],
        "alignment": {"align": True, "repeat": True},
    },
}

BRANCH = __branching["publ"]

EVALUATION_LOG = __test_logs[0]
PUBLICATION_LOG = __test_logs[1]
TEST_LOG = __test_logs[3]
PRESENTATION_LOG = __test_logs[2]

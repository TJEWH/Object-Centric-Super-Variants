__event_dir = "EventLogs/"
__expl_dir = __event_dir + "0_example/"
__full_dir = __event_dir + "1_full/"
__eval_dir = __event_dir + "2_evaluation/"

__logs = [
    __expl_dir + "ocel.jsonocel",
    __expl_dir + "presentation.jsonocel",

    __full_dir + "BPI2017-Top10.jsonocel",  # 2
    __full_dir + "running-example.jsonocel",
    __full_dir + "test_log.jsonocel",  # 4

    __eval_dir + "order_process.jsonocel",
    __eval_dir + "p2p.jsonocel",  # 6
]

TEST_LOG_1 = __logs[0]
TEST_LOG_2 = __logs[1]
BPI_2017_TOP10_LOG = __logs[2]  # Mostly used for evaluation
P2P_LOG = __logs[6]  # Publication Log


__branching = {
    "main": {
        "mode": 8,
        "file": __logs[2],
        "parameters": {"execution_extraction": "leading_type"},
        "alignment": {"align": False, "repeat": None},
    },
    "expl": {
        "mode": None,
        "file": __logs[6],
        "alignment": {"align": True, "repeat": True},
    },
    "eval": {
        "mode": 9,
        "file": __logs[6],
        "file_eval": __logs[2],
        "alignment": {"align": False, "repeat": None},
    },
    "publ": {
        "mode": 9,
        "file": __logs[4],
        "file_eval": __logs[6],
        "alignment": {"align": True, "repeat": True},
    },
}

BRANCH = __branching["publ"]

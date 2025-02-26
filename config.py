__event_dir = "EventLogs/"
__expl_dir = __event_dir + "0_example/"
__full_dir = __event_dir + "1_full/"
__eval_dir = __event_dir + "2_evaluation/"

__logs = [
    __expl_dir + "ocel.jsonocel",
    __expl_dir + "presentation.jsonocel",
    __expl_dir + "thesis.jsonocel",

    __full_dir + "BPI2017-Top10.jsonocel",  # 3
    __full_dir + "running-example.jsonocel",
    __full_dir + "test_log.jsonocel",  # 5

    __eval_dir + "order_process.jsonocel",
    __eval_dir + "p2p.jsonocel",  # 7
]

TEST_LOGS_3 = [__logs[0], __logs[1], __logs[2]]
BPI_2017_TOP10_LOG = __logs[3]  # Mostly used for evaluation
P2P_LOG = __logs[7]  # Publication Log


__branching = {
    "main": {
        "mode": 8,
        "file": __logs[3],
        "parameters": {"execution_extraction": "leading_type"},
        "alignment": {"align": False, "repeat": None},
    },
    "expl": {
        "mode": None,
        "file": __logs[7],
        "alignment": {"align": True, "repeat": True},
    },
    "eval": {
        "mode": 9,
        "file": __logs[7],
        "file_eval": __logs[3],
        "alignment": {"align": False, "repeat": None},
    },
    "publ": {
        "mode": 9,
        "file": __logs[5],
        "file_eval": __logs[7],
        "alignment": {"align": True, "repeat": True},
    },
}

BRANCH = __branching["publ"]

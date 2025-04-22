__event_dir = "EventLogs/"
__expl_dir = __event_dir + "0_example/"
__full_dir = __event_dir + "1_full/"
__eval_dir = __event_dir + "2_evaluation/"

LOGS = [
    __expl_dir + "ocel.jsonocel",
    __expl_dir + "presentation.jsonocel",

    __full_dir + "BPI2017-Top10.jsonocel",  # 2
    __full_dir + "running-example.jsonocel",
    __full_dir + "test_log.jsonocel",  # 4

    __eval_dir + "order_process.jsonocel",
    __eval_dir + "p2p.jsonocel",  # 6
]

TEST_LOG_1 = LOGS[0]
TEST_LOG_2 = LOGS[1]
BPI_2017_TOP10_LOG = LOGS[2]  # Mostly used for evaluation
P2P_LOG = LOGS[6]  # Publication Log

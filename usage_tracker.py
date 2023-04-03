from datetime import datetime
from pathlib import Path

import pandas as pd

PARENT = Path(__file__).parent.resolve() / "usage_stats"
Path.mkdir(PARENT, exist_ok=True)

USAGE_LOG = PARENT / "usage_log.csv"
LAST_SESSION_DETAILS = PARENT / "last_session.bin"
HEADER = "timestamp,token_used,cost"
RATE = 0.002 / 1000

if not USAGE_LOG.exists():
    with open(USAGE_LOG, "w") as fh:
        print(HEADER, file=fh)


def record_usage(tokens: int, time: datetime):
    cost = tokens * RATE
    record = f"{datetime.strftime(time, '%d-%m-%Y %H:%M:%S')},{tokens},{cost}"
    with open(USAGE_LOG, "a") as fh, open(LAST_SESSION_DETAILS, "wb") as bfh:
        print(record, file=fh)
        bfh.write(bytes(record, encoding="utf-8"))
    print(f"Tokens consumed: {tokens}, cost: \N{DOLLAR SIGN}{cost:.5f}")


def load_records() -> tuple[pd.DataFrame, bytes]:
    last_session_details = b""
    with open(LAST_SESSION_DETAILS, "rb") as bfh:
        last_session_details = bfh.read()

    df = pd.read_csv(
        USAGE_LOG,
        header=0,
        index_col="timestamp",
        parse_dates=True,
        infer_datetime_format=True,
    )
    return df, last_session_details


def summarize_records() -> tuple[bytes, int, float]:
    df, last_session_details = load_records()
    summary = df.sum().to_dict()
    return last_session_details, int(summary["token_used"]), round(summary["cost"], 2)

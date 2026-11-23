"""Three-tier deterministic routing from v1 to v2."""

import hashlib
import logging
import os
from datetime import datetime, timezone

from flask import request

from handlers import v1_create_order, v2_create_order


log = logging.getLogger("gateway")

V2_PERCENT = int(os.environ.get("V2_PERCENT", "5"))
if not 0 <= V2_PERCENT <= 100:
    raise ValueError("V2_PERCENT must be between 0 and 100")

V2_COHORTS = {"beta", "internal"}
V2_FORCE_ACCOUNTS = {"acct_42", "acct_99"}

# Optional ISO-8601 UTC timestamp. After it passes, all traffic goes to v2.
V1_SUNSET_AT = os.environ.get("V1_SUNSET_AT")
if V1_SUNSET_AT:
    V1_SUNSET_AT = datetime.fromisoformat(V1_SUNSET_AT)
    if V1_SUNSET_AT.tzinfo is None:
        V1_SUNSET_AT = V1_SUNSET_AT.replace(tzinfo=timezone.utc)


def route_to_v2(body):
    """Choose v2 by cohort, account allow-list, then stable hash bucket."""
    if V1_SUNSET_AT and datetime.now(timezone.utc) >= V1_SUNSET_AT:
        return True

    cohort = request.headers.get("X-Cohort", "").lower()
    if cohort in V2_COHORTS:
        return True

    account_id = body["account_id"]
    if account_id in V2_FORCE_ACCOUNTS:
        return True

    if V2_PERCENT == 0:
        return False
    bucket = int(hashlib.md5(account_id.encode("utf-8")).hexdigest(), 16) % 100
    return bucket < V2_PERCENT


def dispatch(body):
    if route_to_v2(body):
        log.info("order routed to v2 account_id=%s", body["account_id"])
        return "v2", v2_create_order(body)

    log.info("order routed to v1 account_id=%s", body["account_id"])
    return "v1", v1_create_order(body)

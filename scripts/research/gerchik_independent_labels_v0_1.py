"""Validate retrospective independent labels, never backdate tradable levels."""
from decimal import Decimal
import hashlib
import json

TYPES = ("TREND_BREAK", "HISTORICAL", "MIRROR", "LIMIT",
         "CONSOLIDATION", "PARANORMAL_BAR", "GAP")


def packet_digest(packet):
    return hashlib.sha256(json.dumps(packet, sort_keys=True, separators=(",", ":"),
                                    ensure_ascii=False, allow_nan=False).encode()).hexdigest()


def validate_labels(packet, metadata, reviews, *, evaluated_at):
    """Return diagnostic readiness; labels are not formation approvals or ratings.

    Metadata must declare historical effective coverage with source provenance.
    Independence is an explicit reviewer/proposer declaration, not authenticated
    here. Semantic accuracy needs a real reviewer and later agreement analysis.
    """
    if type(evaluated_at) is not int:
        raise ValueError("integer UTC milliseconds required")
    panels = {x["case_id"]: x for x in packet["panels"]}
    if len(panels) != len(packet["panels"]):
        raise ValueError("duplicate panel IDs")
    seen, accepted, issues = set(), [], []
    digest = packet_digest(packet)
    for review in reviews:
        case = review.get("case_id")
        if case not in panels or case in seen:
            raise ValueError("unknown or duplicate case")
        seen.add(case)
        panel = panels[case]
        if review.get("packet_sha256") != digest:
            raise ValueError("review must reference the exact displayed packet version")
        if (not review.get("reviewer_id") or not review.get("proposer_id")
                or review["reviewer_id"] == review["proposer_id"]):
            issues.append({"case_id": case, "reason": "INDEPENDENT_REVIEWER_REQUIRED"})
            continue
        when = review.get("reviewed_at_ms")
        if type(when) is not int or not panel["as_of_ms"] <= when <= evaluated_at:
            raise ValueError("review date cannot be before displayed data or in future")
        if any(key in review for key in ("score", "rating", "outcomes")):
            raise ValueError("blind review must not include model scores or outcomes")
        levels = review.get("levels")
        if (review.get("decision") not in ("LEVELS", "NO_LEVELS")
                or not isinstance(levels, list) or not review.get("rationale")
                or (review["decision"] == "NO_LEVELS" and levels)
                or (review["decision"] == "LEVELS" and not levels)):
            raise ValueError("explicit positive/negative label with rationale required")
        meta = metadata.get(panel["symbol"])
        if not meta:
            issues.append({"case_id": case, "reason": "HISTORICAL_TICK_METADATA_REQUIRED"})
            continue
        tick = Decimal(str(meta["tick_size"]))
        if not tick.is_finite() or tick <= 0 or not meta.get("provenance"):
            raise ValueError("valid sourced tick size required")
        first = min(row[0] for tf in ("d1", "w1") for row in panel[tf])
        if (type(meta.get("effective_from_ms")) is not int
                or type(meta.get("effective_until_ms")) is not int
                or not meta["effective_from_ms"] <= first < panel["as_of_ms"] <= meta["effective_until_ms"]):
            issues.append({"case_id": case, "reason": "TICK_METADATA_PERIOD_NOT_COVERED"})
            continue
        rows = {}
        for tf in ("d1", "w1"):
            for row in panel[tf]:
                identity = tf+":"+str(row[0])
                if identity in rows or row[6] >= panel["as_of_ms"]:
                    raise ValueError("duplicate or future panel bar")
                rows[identity] = row
                prices = [Decimal(str(row[i])) for i in (1, 2, 3, 4)]
                if any(not x.is_finite() or x <= 0 or x/tick != (x/tick).to_integral_value() for x in prices):
                    raise ValueError("historical prices do not match declared tick")
        identities = set()
        for label in levels:
            if any(key in label for key in ("score", "rating", "outcomes", "tradable_known_at")):
                raise ValueError("retrospective label cannot carry score or backdated trading availability")
            source = label.get("source_bar_id")
            field = label.get("source_field")
            if source not in rows or field not in ("high", "low") or label.get("primary_type") not in TYPES:
                raise ValueError("D1/W1 High/Low source and one primary type required")
            price = Decimal(str(label["price"]))
            expected = Decimal(str(rows[source][2 if field == "high" else 3]))
            if price != expected:
                raise ValueError("label price must match source extremum")
            identity = (source.split(":")[0], price)
            if identity in identities:
                raise ValueError("duplicate level identity or multiple primary types")
            identities.add(identity)
            witnesses = label.get("pattern_bar_ids")
            if (not isinstance(witnesses, list) or not witnesses or source not in witnesses
                    or len(set(witnesses)) != len(witnesses) or any(x not in rows for x in witnesses)
                    or not label.get("pattern_rationale")):
                raise ValueError("complete closed-bar pattern witnesses required")
        accepted.append({"case_id": case, "reviewer_id": review["reviewer_id"],
                         "reviewed_at_ms": when, "labels": len(levels),
                         "decision": review["decision"], "purpose": "RETROSPECTIVE_REFERENCE_ONLY"})
    missing = sorted(set(panels)-seen)
    return {"schema": "ktrader.gerchik_independent_labels.v0.1",
            "status": "REFERENCE_LABELS_COMPLETE" if not missing and not issues else "PENDING",
            "accepted": accepted, "issues": issues, "missing_case_ids": missing,
            "packet_sha256": digest,
            "evaluated_at_ms": evaluated_at,
            "tradable_levels_created": 0, "review_authentication": "NOT_PERFORMED"}


def main():
    import argparse
    from datetime import datetime, timezone
    from pathlib import Path
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--packet", type=Path, required=True)
    parser.add_argument("--input", type=Path, required=True)
    parser.add_argument("--evaluated-at-ms", type=int)
    args = parser.parse_args()
    packet = json.loads(args.packet.read_text(encoding="utf-8"))
    inputs = json.loads(args.input.read_text(encoding="utf-8"))
    when = args.evaluated_at_ms if args.evaluated_at_ms is not None else int(datetime.now(timezone.utc).timestamp()*1000)
    report = validate_labels(packet, inputs["metadata"], inputs["reviews"], evaluated_at=when)
    print(json.dumps(report, sort_keys=True, indent=2, allow_nan=False))
    return 0 if report["status"] == "REFERENCE_LABELS_COMPLETE" else 1


if __name__ == "__main__":
    raise SystemExit(main())

"""A saved screening candidate is never an instruction to delete a series."""


def redundancy_context(record):
    return {"redundancy_candidate": record.get("redundancy_candidate")}

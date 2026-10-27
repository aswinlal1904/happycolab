"""
ID Card and Badge verification tools.
"""

from typing import Dict, Any

MOCK_ID_DATABASE: Dict[str, Dict[str, Any]] = {
    "ID-9021": {
        "status": "active",
        "name": "Sarah Connor",
        "role": "Lead Systems Engineer",
        "department": "Cybernetics Division",
        "clearance_level": 4,
        "expiry_date": "2028-12-31",
    },
    "ID-4420": {
        "status": "suspended",
        "name": "Alex Mercer",
        "role": "Research Analyst",
        "department": "Biotech Labs",
        "clearance_level": 2,
        "expiry_date": "2025-06-15",
    },
    "ID-1001": {
        "status": "active",
        "name": "John Doe",
        "role": "Security Specialist",
        "department": "Operations",
        "clearance_level": 3,
        "expiry_date": "2027-01-01",
    },
}


def lookup_id_card(card_id: str) -> dict:
    """
    Looks up employee or member profile and status using an ID card number (e.g. 'ID-9021', 'ID-4420').
    """
    cleaned_id = card_id.strip().upper()
    if cleaned_id in MOCK_ID_DATABASE:
        return {"found": True, "record": MOCK_ID_DATABASE[cleaned_id]}
    return {"found": False, "message": f"No record exists for card ID: {card_id}"}


def verify_security_clearance(card_id: str, required_level: int) -> dict:
    """
    Checks if a given ID card has sufficient security clearance level (1 to 5).
    """
    cleaned_id = card_id.strip().upper()
    if cleaned_id not in MOCK_ID_DATABASE:
        return {"authorized": False, "reason": "ID card not found"}

    record = MOCK_ID_DATABASE[cleaned_id]
    if record["status"] != "active":
        return {"authorized": False, "reason": f"Card status is {record['status']}"}

    authorized = record["clearance_level"] >= required_level
    return {
        "authorized": authorized,
        "name": record["name"],
        "clearance_level": record["clearance_level"],
        "required_level": required_level,
    }

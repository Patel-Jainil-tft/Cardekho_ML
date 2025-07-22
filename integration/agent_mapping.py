# agent_key_mapping.py

AGENT_FIELD_MAP = {
    "darwinbox": {
        "ifsc_code": "IFSC_code",
        "ifsc_number": "IFSC_code",
        "salary_account_number": "salary_account_number",
        "account_number": "salary_account_number",
        "name": "person_name",
        "email": "personal_email_id_from",
        "phone_number": "updated_mobile_number"
        # Add additional mappings as required
    },
    "careline": {
        "marriage_status": "marriage_status",
        "marriage_status_to": "marriage_status_to",
        "employee_id": "employee_id",
        "name": "name",
        "email": "email",
        "phone_number": "phone_number",
        # Add additional mappings as required
    }
    # Add mappings for other agents if needed
}

def normalize_data_keys(agent: str, data: dict) -> dict:
    mapping = AGENT_FIELD_MAP.get(agent.lower(), {})
    normalized = {}
    for k, v in data.items():
        std_key = mapping.get(k.lower(), k)
        normalized[std_key] = v
    return normalized
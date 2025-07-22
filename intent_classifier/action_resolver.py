# integration/action_schema.py

ACTION_SCHEMA = {
    "update_personal_details": [
        "person_name",
        "personal_email_id_from",
        "updated_email_id",
        "updated_mobile_number",
        "salary_account_number",
        "IFSC_code",
        "marriage_status_from",
        "marriage_status_to",
        "is_salary_accunt",
        "is_marriage_status",
        "is_account_number",
        "is_ifsc_code",
        "Is_mobile_number",
        "Is_email_id",
        "employee_detail_type"
    ],
    "view_reimbursement_status": [
        "reimbursement_code",
        "person_name",
        "claim_title",
        "applied_date"
    ],
    "raise_seperation_resign": [
        "resignation_reason",
        "file_attachment",
        "date_end"
    ],
    "raise_job_requistion": [
        "company",
        "business_unit",
        "department",
        "designation",
        "experience_in_years",
        "experience_in_months",
        "currency",
        "minimum_salary",
        "maximum_salary",
        "salary_timeframe",
        "recruitment_start_Date",
        "roles_and_responsibilities",
        "additional_skills",
        "number_of_new_positions",
        "number_of_replacement_positions",
        "location",
        "employee_type",
        "reporting_manager",
        "job_level",
        "comments",
        "assets"
    ],
    "view_compensation_details": [
        "ctc",
        "variable_pay",
        "salary_structure",
        "fixed_pay",
        "base_salary"
    ],
    "view_uan": [],
    "view_list_of_reportees": []
}
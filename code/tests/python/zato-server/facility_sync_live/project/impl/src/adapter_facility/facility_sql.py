# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# Everything the sync reads from the source database. The log column TIMESTAMP is quoted in every statement.

# ################################################################################################################################
# ################################################################################################################################

Read_Treatment_Changes = """
select "TIMESTAMP", OPERATION, ID, PATIENT_ID, STAFF_ID, CONDITION_ID,
       START_DATE, END_DATE, CLARIFICATION, ATTENTION_VALUE_ID
from FACILITY.LOG_TREATMENTS
where "TIMESTAMP" > :since
order by "TIMESTAMP"
"""

Read_Consult_Note_Changes = """
select "TIMESTAMP", OPERATION, ID, STAFF_ID, CREATED_DATE, MODIFIED_DATE, TREATMENT_ID,
       COMPLAINT_CODE_ID, COMPLAINT_NOTE, FINDINGS_NOTE, ASSESSMENT_CODE_ID, ASSESSMENT_NOTE, PLAN_NOTE, PROGRESS_NOTE
from FACILITY.LOG_CONSULT_NOTES
where "TIMESTAMP" > :since
order by "TIMESTAMP"
"""

# Each lookup takes the IDs of one batch at once - the placeholder is where the IN list goes.
Resolve_Patients = """
select ID, REFERENCE_ID as VALUE
from FACILITY.PATIENTS
where ID in ({in_list})
"""

Resolve_Staff = """
select ID, REFERENCE_ID as VALUE
from FACILITY.STAFF
where ID in ({in_list})
"""

Resolve_Conditions = """
select ID, CONDITION_CODE, CONDITION_TITLE
from FACILITY.CONDITION_CODES
where ID in ({in_list})
"""

Resolve_Treatments = """
select ID, PATIENT_ID as VALUE
from FACILITY.TREATMENTS
where ID in ({in_list})
"""

# ################################################################################################################################
# ################################################################################################################################

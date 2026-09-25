-- Who may do what across the schemas. The reader sees the source and nothing else, the writer calls
-- the API and reads and deletes the target, and the API owner writes the target for its callers.

-- The reader of the source
grant select on FACILITY.PATIENTS to FACILITY_READER
/

grant select on FACILITY.STAFF to FACILITY_READER
/

grant select on FACILITY.CONDITION_CODES to FACILITY_READER
/

grant select on FACILITY.TREATMENTS to FACILITY_READER
/

grant select on FACILITY.LOG_TREATMENTS to FACILITY_READER
/

grant select on FACILITY.LOG_CONSULT_NOTES to FACILITY_READER
/

-- The owner of the API, whose package runs with these rights
grant select on RECORDS.SECTION_DEF to RECORDS_API
/

grant select on RECORDS.FIELD_DEF to RECORDS_API
/

grant select, insert, update on RECORDS.PATIENT_SECTION to RECORDS_API
/

grant select, insert, update on RECORDS.PATIENT_FIELD to RECORDS_API
/

grant select on RECORDS.SEQ_PATIENT_SECTION to RECORDS_API
/

grant select on RECORDS.SEQ_PATIENT_FIELD to RECORDS_API
/

grant execute on SYNC_FAULTS.PKG_FAULTS to RECORDS_API
/

-- The writer, which resolves what exists and removes what was deleted
grant select on RECORDS.SECTION_DEF to SYNC_WRITER
/

grant select on RECORDS.FIELD_DEF to SYNC_WRITER
/

grant select, delete on RECORDS.PATIENT_SECTION to SYNC_WRITER
/

grant select, delete on RECORDS.PATIENT_FIELD to SYNC_WRITER
/

grant execute on SYNC_FAULTS.PKG_FAULTS to SYNC_WRITER
/

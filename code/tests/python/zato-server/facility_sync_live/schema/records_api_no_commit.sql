-- The PL/SQL API of the target - the variant that leaves committing to its caller.
-- ATTACH_AND_CREATE_FORM creates a patient's section and returns its key. SAVE_PATIENT_FIELD inserts
-- a field when it is given no key and updates the field with that key otherwise, returning the key either way.

create or replace package RECORDS_API.PKG_FORMS as

    function ATTACH_AND_CREATE_FORM(
        p_patient     in number,
        p_sequence_no in number,
        p_section     in number
    ) return number;

    function SAVE_PATIENT_FIELD(
        p_pf_id       in number,
        p_patient     in number,
        p_field       in number,
        p_ps_id       in number,
        p_answer      in varchar2,
        p_answer_text in varchar2,
        p_answered_at in timestamp
    ) return number;

end PKG_FORMS;
/

create or replace package body RECORDS_API.PKG_FORMS as

    function ATTACH_AND_CREATE_FORM(
        p_patient     in number,
        p_sequence_no in number,
        p_section     in number
    ) return number is
        v_ps_id number;
    begin
        SYNC_FAULTS.PKG_FAULTS.CHECK_STEP('section_create');

        select RECORDS.SEQ_PATIENT_SECTION.nextval into v_ps_id from dual;

        insert into RECORDS.PATIENT_SECTION (PS_ID, PS_PATIENT, PS_SEQUENCE_NO, PS_SD_ID, PS_CREATED_AT)
        values (v_ps_id, p_patient, p_sequence_no, p_section, sysdate);

        return v_ps_id;
    end ATTACH_AND_CREATE_FORM;

    function SAVE_PATIENT_FIELD(
        p_pf_id       in number,
        p_patient     in number,
        p_field       in number,
        p_ps_id       in number,
        p_answer      in varchar2,
        p_answer_text in varchar2,
        p_answered_at in timestamp
    ) return number is
        v_pf_id number;
    begin
        SYNC_FAULTS.PKG_FAULTS.CHECK_STEP('field_save');

        if p_pf_id is null then
            select RECORDS.SEQ_PATIENT_FIELD.nextval into v_pf_id from dual;

            insert into RECORDS.PATIENT_FIELD (
                PF_ID, PF_PATIENT, PF_FD_ID, PF_PS_ID, PF_ANSWER, PF_ANSWER_TEXT, PF_ANSWERED_AT
            ) values (
                v_pf_id, p_patient, p_field, p_ps_id, p_answer, p_answer_text, p_answered_at
            );
        else
            v_pf_id := p_pf_id;

            update RECORDS.PATIENT_FIELD
            set PF_ANSWER = p_answer, PF_ANSWER_TEXT = p_answer_text, PF_ANSWERED_AT = p_answered_at
            where PF_ID = v_pf_id;
        end if;

        return v_pf_id;
    end SAVE_PATIENT_FIELD;

end PKG_FORMS;
/

grant execute on RECORDS_API.PKG_FORMS to SYNC_WRITER
/

-- The source database - the current tables the changes point at and the two change logs.
-- The log column TIMESTAMP is quoted, NUMBER has no precision, notes are VARCHAR2(4000), the logs have no primary key.

create table FACILITY.PATIENTS (
    ID           NUMBER        not null,
    REFERENCE_ID NUMBER        null,
    FULL_NAME    VARCHAR2(200) null,
    constraint PK_PATIENTS primary key (ID)
)
/

create table FACILITY.STAFF (
    ID           NUMBER        not null,
    REFERENCE_ID NUMBER        null,
    FULL_NAME    VARCHAR2(200) null,
    constraint PK_STAFF primary key (ID)
)
/

create table FACILITY.CONDITION_CODES (
    ID              NUMBER        not null,
    CONDITION_CODE  VARCHAR2(20)  null,
    CONDITION_TITLE VARCHAR2(200) null,
    constraint PK_CONDITION_CODES primary key (ID)
)
/

create table FACILITY.TREATMENTS (
    ID         NUMBER not null,
    PATIENT_ID NUMBER null,
    constraint PK_TREATMENTS primary key (ID)
)
/

create table FACILITY.LOG_TREATMENTS (
    "TIMESTAMP"        TIMESTAMP      not null,
    USERNAME           VARCHAR2(100)  not null,
    OPERATION          VARCHAR2(1)    not null,
    ID                 NUMBER         null,
    PATIENT_ID         NUMBER         null,
    STAFF_ID           NUMBER         null,
    CONDITION_ID       NUMBER         null,
    START_DATE         DATE           null,
    END_DATE           DATE           null,
    CLARIFICATION      VARCHAR2(4000) null,
    ATTENTION_VALUE_ID NUMBER         null
)
/

create table FACILITY.LOG_CONSULT_NOTES (
    "TIMESTAMP"        TIMESTAMP      not null,
    USERNAME           VARCHAR2(100)  not null,
    OPERATION          VARCHAR2(1)    not null,
    ID                 NUMBER         null,
    STAFF_ID           NUMBER         null,
    CREATED_DATE       TIMESTAMP      null,
    MODIFIED_DATE      TIMESTAMP      null,
    TREATMENT_ID       NUMBER         null,
    COMPLAINT_CODE_ID  NUMBER         null,
    COMPLAINT_NOTE     VARCHAR2(4000) null,
    FINDINGS_NOTE      VARCHAR2(4000) null,
    ASSESSMENT_CODE_ID NUMBER         null,
    ASSESSMENT_NOTE    VARCHAR2(4000) null,
    PLAN_NOTE          VARCHAR2(4000) null,
    PROGRESS_NOTE      VARCHAR2(4000) null
)
/

create index FACILITY.IX_LOG_TREATMENTS_TS on FACILITY.LOG_TREATMENTS ("TIMESTAMP")
/

create index FACILITY.IX_LOG_CONSULT_NOTES_TS on FACILITY.LOG_CONSULT_NOTES ("TIMESTAMP")
/

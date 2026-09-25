-- The target database - an entity-attribute-value model of sections and fields. A patient's section
-- and its fields get sequence-backed keys and there is no unique constraint on a section and a field.

create table RECORDS.SECTION_DEF (
    SD_ID   NUMBER        not null,
    SD_NAME VARCHAR2(100) not null,
    constraint PK_SECTION_DEF primary key (SD_ID),
    constraint UQ_SECTION_DEF_NAME unique (SD_NAME)
)
/

create table RECORDS.FIELD_DEF (
    FD_ID    NUMBER        not null,
    FD_SD_ID NUMBER        not null,
    FD_NAME  VARCHAR2(100) not null,
    constraint PK_FIELD_DEF primary key (FD_ID),
    constraint FK_FIELD_DEF_SECTION foreign key (FD_SD_ID) references RECORDS.SECTION_DEF (SD_ID)
)
/

create table RECORDS.PATIENT_SECTION (
    PS_ID          NUMBER not null,
    PS_PATIENT     NUMBER not null,
    PS_SEQUENCE_NO NUMBER null,
    PS_SD_ID       NUMBER not null,
    PS_CREATED_AT  DATE   not null,
    constraint PK_PATIENT_SECTION primary key (PS_ID),
    constraint FK_PATIENT_SECTION_DEF foreign key (PS_SD_ID) references RECORDS.SECTION_DEF (SD_ID)
)
/

create table RECORDS.PATIENT_FIELD (
    PF_ID          NUMBER         not null,
    PF_PATIENT     NUMBER         not null,
    PF_FD_ID       NUMBER         not null,
    PF_PS_ID       NUMBER         not null,
    PF_ANSWER      VARCHAR2(4000) null,
    PF_ANSWER_TEXT VARCHAR2(4000) null,
    PF_ANSWERED_AT TIMESTAMP      null,
    constraint PK_PATIENT_FIELD primary key (PF_ID),
    constraint FK_PATIENT_FIELD_DEF foreign key (PF_FD_ID) references RECORDS.FIELD_DEF (FD_ID),
    constraint FK_PATIENT_FIELD_SECTION foreign key (PF_PS_ID) references RECORDS.PATIENT_SECTION (PS_ID)
)
/

create sequence RECORDS.SEQ_PATIENT_SECTION start with 1000 increment by 1
/

create sequence RECORDS.SEQ_PATIENT_FIELD start with 1000 increment by 1
/

-- The two sections and the field of each one

insert into RECORDS.SECTION_DEF (SD_ID, SD_NAME) values (1, 'TREATMENTS')
/

insert into RECORDS.SECTION_DEF (SD_ID, SD_NAME) values (2, 'CONSULT_NOTES')
/

insert into RECORDS.FIELD_DEF (FD_ID, FD_SD_ID, FD_NAME) values (1, 1, 'TREATMENT_ID')
/

insert into RECORDS.FIELD_DEF (FD_ID, FD_SD_ID, FD_NAME) values (2, 1, 'TREATMENT_PATIENT')
/

insert into RECORDS.FIELD_DEF (FD_ID, FD_SD_ID, FD_NAME) values (3, 1, 'TREATMENT_STAFF')
/

insert into RECORDS.FIELD_DEF (FD_ID, FD_SD_ID, FD_NAME) values (4, 1, 'TREATMENT_CONDITION_CODE')
/

insert into RECORDS.FIELD_DEF (FD_ID, FD_SD_ID, FD_NAME) values (5, 1, 'TREATMENT_CONDITION_TITLE')
/

insert into RECORDS.FIELD_DEF (FD_ID, FD_SD_ID, FD_NAME) values (6, 1, 'TREATMENT_START_DATE')
/

insert into RECORDS.FIELD_DEF (FD_ID, FD_SD_ID, FD_NAME) values (7, 1, 'TREATMENT_END_DATE')
/

insert into RECORDS.FIELD_DEF (FD_ID, FD_SD_ID, FD_NAME) values (8, 1, 'TREATMENT_CLARIFICATION')
/

insert into RECORDS.FIELD_DEF (FD_ID, FD_SD_ID, FD_NAME) values (9, 1, 'TREATMENT_ATTENTION_VALUE')
/

insert into RECORDS.FIELD_DEF (FD_ID, FD_SD_ID, FD_NAME) values (21, 2, 'CONSULT_NOTE_ID')
/

insert into RECORDS.FIELD_DEF (FD_ID, FD_SD_ID, FD_NAME) values (22, 2, 'CONSULT_NOTE_STAFF')
/

insert into RECORDS.FIELD_DEF (FD_ID, FD_SD_ID, FD_NAME) values (23, 2, 'CONSULT_NOTE_TREATMENT')
/

insert into RECORDS.FIELD_DEF (FD_ID, FD_SD_ID, FD_NAME) values (24, 2, 'CONSULT_NOTE_CREATED_DATE')
/

insert into RECORDS.FIELD_DEF (FD_ID, FD_SD_ID, FD_NAME) values (25, 2, 'CONSULT_NOTE_MODIFIED_DATE')
/

insert into RECORDS.FIELD_DEF (FD_ID, FD_SD_ID, FD_NAME) values (26, 2, 'CONSULT_NOTE_COMPLAINT_CODE')
/

insert into RECORDS.FIELD_DEF (FD_ID, FD_SD_ID, FD_NAME) values (27, 2, 'CONSULT_NOTE_COMPLAINT_NOTE')
/

insert into RECORDS.FIELD_DEF (FD_ID, FD_SD_ID, FD_NAME) values (28, 2, 'CONSULT_NOTE_FINDINGS_NOTE')
/

insert into RECORDS.FIELD_DEF (FD_ID, FD_SD_ID, FD_NAME) values (29, 2, 'CONSULT_NOTE_ASSESSMENT_CODE')
/

insert into RECORDS.FIELD_DEF (FD_ID, FD_SD_ID, FD_NAME) values (30, 2, 'CONSULT_NOTE_ASSESSMENT_NOTE')
/

insert into RECORDS.FIELD_DEF (FD_ID, FD_SD_ID, FD_NAME) values (31, 2, 'CONSULT_NOTE_PLAN_NOTE')
/

insert into RECORDS.FIELD_DEF (FD_ID, FD_SD_ID, FD_NAME) values (32, 2, 'CONSULT_NOTE_PROGRESS_NOTE')
/

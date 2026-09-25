-- What the sync owns - the mapping from a source row to the section it became, and the checkpoint
-- of each source. The synonyms name the target tables.

create table SYNC_WRITER.SYNC_ID_MAP (
    SOURCE_TABLE VARCHAR2(30) not null,
    SOURCE_ID    NUMBER       not null,
    PS_ID        NUMBER       not null,
    CREATED_AT   TIMESTAMP    default systimestamp not null,
    constraint PK_SYNC_ID_MAP primary key (SOURCE_TABLE, SOURCE_ID)
)
/

create index SYNC_WRITER.IX_SYNC_ID_MAP_PS on SYNC_WRITER.SYNC_ID_MAP (PS_ID)
/

create table SYNC_WRITER.SYNC_CHECKPOINT (
    SOURCE     VARCHAR2(30) not null,
    LAST_TS    TIMESTAMP    not null,
    UPDATED_AT TIMESTAMP    default systimestamp not null,
    constraint PK_SYNC_CHECKPOINT primary key (SOURCE)
)
/

create synonym SYNC_WRITER.SECTION_DEF for RECORDS.SECTION_DEF
/

create synonym SYNC_WRITER.FIELD_DEF for RECORDS.FIELD_DEF
/

create synonym SYNC_WRITER.PATIENT_SECTION for RECORDS.PATIENT_SECTION
/

create synonym SYNC_WRITER.PATIENT_FIELD for RECORDS.PATIENT_FIELD
/

-- The two steps of the writer's own that a test can make fail

create or replace trigger SYNC_WRITER.TRG_SYNC_ID_MAP_FAULT
before insert on SYNC_WRITER.SYNC_ID_MAP
for each row
begin
    SYNC_FAULTS.PKG_FAULTS.CHECK_STEP('map_insert');
end;
/

create or replace trigger SYNC_WRITER.TRG_SYNC_CHECKPOINT_FAULT
before update on SYNC_WRITER.SYNC_CHECKPOINT
for each row
begin
    SYNC_FAULTS.PKG_FAULTS.CHECK_STEP('checkpoint_update');
end;
/

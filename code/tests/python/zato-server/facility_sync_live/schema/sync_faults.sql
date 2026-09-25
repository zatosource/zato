-- The faults a test plans - the package and the triggers ask about their step before they act.
-- A step raises ORA-20001 when NEEDS_RAISE is 1 and sleeps for SLEEP_SECONDS first when that is above 0.

create table SYNC_FAULTS.FAULT_PLAN (
    STEP          VARCHAR2(50) not null,
    NEEDS_RAISE   NUMBER(1)    not null,
    SLEEP_SECONDS NUMBER       not null,
    constraint PK_FAULT_PLAN primary key (STEP)
)
/

insert into SYNC_FAULTS.FAULT_PLAN (STEP, NEEDS_RAISE, SLEEP_SECONDS) values ('section_create', 0, 0)
/

insert into SYNC_FAULTS.FAULT_PLAN (STEP, NEEDS_RAISE, SLEEP_SECONDS) values ('field_save', 0, 0)
/

insert into SYNC_FAULTS.FAULT_PLAN (STEP, NEEDS_RAISE, SLEEP_SECONDS) values ('map_insert', 0, 0)
/

insert into SYNC_FAULTS.FAULT_PLAN (STEP, NEEDS_RAISE, SLEEP_SECONDS) values ('checkpoint_update', 0, 0)
/

create or replace package SYNC_FAULTS.PKG_FAULTS as

    procedure CHECK_STEP(p_step in varchar2);

end PKG_FAULTS;
/

create or replace package body SYNC_FAULTS.PKG_FAULTS as

    procedure CHECK_STEP(p_step in varchar2) is
        v_needs_raise   number;
        v_sleep_seconds number;
    begin

        -- A step nobody planned is a mistake in the caller, so NO_DATA_FOUND stays unhandled
        select NEEDS_RAISE, SLEEP_SECONDS
        into v_needs_raise, v_sleep_seconds
        from SYNC_FAULTS.FAULT_PLAN
        where STEP = p_step;

        if v_sleep_seconds > 0 then
            DBMS_SESSION.SLEEP(v_sleep_seconds);
        end if;

        if v_needs_raise = 1 then
            RAISE_APPLICATION_ERROR(-20001, 'Planned fault at step ' || p_step);
        end if;

    end CHECK_STEP;

end PKG_FAULTS;
/

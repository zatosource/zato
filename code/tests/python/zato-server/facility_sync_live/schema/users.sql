-- Every statement ends with a slash on a line of its own. Plain SQL carries no trailing semicolon,
-- PL/SQL blocks end with their own END; before the slash.

-- The source schema and the user that reads it
begin
    execute immediate 'drop user FACILITY cascade';
exception
    when others then
        if sqlcode != -1918 then
            raise;
        end if;
end;
/

begin
    execute immediate 'drop user FACILITY_READER cascade';
exception
    when others then
        if sqlcode != -1918 then
            raise;
        end if;
end;
/

-- The target schema and the schema with its PL/SQL API
begin
    execute immediate 'drop user RECORDS cascade';
exception
    when others then
        if sqlcode != -1918 then
            raise;
        end if;
end;
/

begin
    execute immediate 'drop user RECORDS_API cascade';
exception
    when others then
        if sqlcode != -1918 then
            raise;
        end if;
end;
/

-- The user the sync writes as, with the mapping and the checkpoint of its own
begin
    execute immediate 'drop user SYNC_WRITER cascade';
exception
    when others then
        if sqlcode != -1918 then
            raise;
        end if;
end;
/

-- The faults the tests plan
begin
    execute immediate 'drop user SYNC_FAULTS cascade';
exception
    when others then
        if sqlcode != -1918 then
            raise;
        end if;
end;
/

create user FACILITY identified by "{{password}}" quota unlimited on USERS
/

create user FACILITY_READER identified by "{{password}}"
/

create user RECORDS identified by "{{password}}" quota unlimited on USERS
/

create user RECORDS_API identified by "{{password}}"
/

create user SYNC_WRITER identified by "{{password}}" quota unlimited on USERS
/

create user SYNC_FAULTS identified by "{{password}}" quota unlimited on USERS
/

grant create session to FACILITY
/

grant create session to FACILITY_READER
/

grant create session to RECORDS
/

grant create session to RECORDS_API
/

grant create session to SYNC_WRITER
/

grant create session to SYNC_FAULTS
/

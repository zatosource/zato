# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# The HR data the stored procedures under test work with - the table, its rows and the procedures
# are defined here once, and the expected results the tests assert are derived from the same rows.

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from zato.common.typing_ import stranydict, strdictlist, strlist

# ################################################################################################################################
# ################################################################################################################################

# The table the procedures read from
Table_Name = 'hr_employees'

# The procedures the tests call - one hands a name back through an OUT parameter,
# the other hands the rows of a department back through a REF CURSOR.
Proc_Get_Employee_Name           = 'get_employee_name'
Proc_Get_Employees_By_Department = 'get_employees_by_department'

# The departments the rows are spread across
Department_Engineering = 'Engineering'
Department_Sales       = 'Sales'

# ################################################################################################################################
# ################################################################################################################################

Seed_Rows:'strdictlist' = [
    {'employee_id': 1, 'first_name': 'John',  'last_name': 'Smith',   'department': Department_Engineering, 'salary': 120000},
    {'employee_id': 2, 'first_name': 'Maria', 'last_name': 'Johnson', 'department': Department_Sales,       'salary': 95000},
    {'employee_id': 3, 'first_name': 'Anna',  'last_name': 'Miller',  'department': Department_Engineering, 'salary': 115000},
    {'employee_id': 4, 'first_name': 'Jane',  'last_name': 'Doe',     'department': Department_Sales,       'salary': 98000},
]

# ################################################################################################################################
# ################################################################################################################################

# Oracle has no `drop table if exists` - ORA-00942 says the table was not there to begin with, which is fine
Drop_Table = f"""
begin
    execute immediate 'drop table {Table_Name}';
exception
    when others then
        if sqlcode != -942 then
            raise;
        end if;
end;
"""

Create_Table = f"""
create table {Table_Name} (
    employee_id number(10) not null primary key,
    first_name  varchar2(50) not null,
    last_name   varchar2(50) not null,
    department  varchar2(50) not null,
    salary      number(10) not null
)
"""

Insert_Row = f"""
insert into {Table_Name} (employee_id, first_name, last_name, department, salary)
values (:employee_id, :first_name, :last_name, :department, :salary)
"""

# ################################################################################################################################

Create_Proc_Get_Employee_Name = f"""
create or replace procedure {Proc_Get_Employee_Name} (
    p_id   in  number,
    p_name out varchar2
)
as
begin
    select first_name || ' ' || last_name into p_name
    from {Table_Name}
    where employee_id = p_id;
end {Proc_Get_Employee_Name};
"""

Create_Proc_Get_Employees_By_Department = f"""
create or replace procedure {Proc_Get_Employees_By_Department} (
    p_department in  varchar2,
    p_rows       out sys_refcursor
)
as
begin
    open p_rows for
        select employee_id, first_name, last_name, department, salary
        from {Table_Name}
        where department = p_department
        order by employee_id;
end {Proc_Get_Employees_By_Department};
"""

# The procedures in the order they are created
Create_Procs:'strlist' = [
    Create_Proc_Get_Employee_Name,
    Create_Proc_Get_Employees_By_Department,
]

# ################################################################################################################################
# ################################################################################################################################

def get_employee_name(employee_id:'int') -> 'str':
    """ The full name of one employee, the way the procedure builds it.
    """
    for row in Seed_Rows:
        if row['employee_id'] == employee_id:
            out = '{} {}'.format(row['first_name'], row['last_name'])
            return out

    raise Exception(f'No employee with id {employee_id}')

# ################################################################################################################################

def get_employees_by_department(department:'str') -> 'strdictlist':
    """ The rows of one department, in the order the procedure returns them.
    """
    out:'strdictlist' = []

    for row in Seed_Rows:
        if row['department'] == department:
            out.append(dict(row))

    out.sort(key=_get_employee_id)

    return out

# ################################################################################################################################

def _get_employee_id(row:'stranydict') -> 'int':
    out = row['employee_id']
    return out

# ################################################################################################################################
# ################################################################################################################################

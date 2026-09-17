# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# The HR data the stored procedures under test return - the table, its rows and the procedures
# are defined here once, and the expected results the tests assert are derived from the same rows.

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from zato.common.typing_ import stranydict, strdictlist, strintdict, strlist

# ################################################################################################################################
# ################################################################################################################################

# The table the procedures read from
Table_Name = 'hr_employees'

# The procedures the tests call
Proc_Get_Employees               = 'hr_get_employees'
Proc_Get_Employees_By_Department = 'hr_get_employees_by_department'
Proc_Get_Department_Summary      = 'hr_get_department_summary'

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

Create_Table = f"""
create table {Table_Name} (
    employee_id int not null primary key,
    first_name  nvarchar(50) not null,
    last_name   nvarchar(50) not null,
    department  nvarchar(50) not null,
    salary      int not null
)
"""

Insert_Row = f"""
insert into {Table_Name} (employee_id, first_name, last_name, department, salary)
values (%(employee_id)s, %(first_name)s, %(last_name)s, %(department)s, %(salary)s)
"""

# ################################################################################################################################

Create_Proc_Get_Employees = f"""
create procedure {Proc_Get_Employees}
as
begin
    set nocount on;
    select employee_id, first_name, last_name, department, salary
    from {Table_Name}
    order by employee_id;
end
"""

Create_Proc_Get_Employees_By_Department = f"""
create procedure {Proc_Get_Employees_By_Department}
    @department nvarchar(50)
as
begin
    set nocount on;
    select employee_id, first_name, last_name, department, salary
    from {Table_Name}
    where department = @department
    order by employee_id;
end
"""

Create_Proc_Get_Department_Summary = f"""
create procedure {Proc_Get_Department_Summary}
as
begin
    set nocount on;
    select department, count(*) as head_count
    from {Table_Name}
    group by department
    order by department;
    select employee_id, first_name, last_name, department, salary
    from {Table_Name}
    order by employee_id;
end
"""

# The procedures in the order they are created
Create_Procs:'strlist' = [
    Create_Proc_Get_Employees,
    Create_Proc_Get_Employees_By_Department,
    Create_Proc_Get_Department_Summary,
]

# ################################################################################################################################
# ################################################################################################################################

def get_all_employees() -> 'strdictlist':
    """ All the rows, in the order the procedures return them.
    """
    out:'strdictlist' = []

    for row in Seed_Rows:
        out.append(dict(row))

    out.sort(key=_get_employee_id)

    return out

# ################################################################################################################################

def get_employees_by_department(department:'str') -> 'strdictlist':
    """ The rows of one department, in the order the procedure returns them.
    """
    out:'strdictlist' = []

    for row in get_all_employees():
        if row['department'] == department:
            out.append(row)

    return out

# ################################################################################################################################

def get_department_head_counts() -> 'strdictlist':
    """ How many employees each department has, ordered by department name.
    """
    counts:'strintdict' = {}

    for row in Seed_Rows:
        department = row['department']
        if department not in counts:
            counts[department] = 0
        counts[department] += 1

    out:'strdictlist' = []

    for department in sorted(counts):
        out.append({'department': department, 'head_count': counts[department]})

    return out

# ################################################################################################################################

def _get_employee_id(row:'stranydict') -> 'int':
    out = row['employee_id']
    return out

# ################################################################################################################################
# ################################################################################################################################

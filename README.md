# PandaQ: A SQL Interpreter by Héctor Núñez Carpio
Welcome to the PandaQ project, a compact and innovative SQL interpreter coded by Héctor Núñez Carpio as a Computer Science grade project. Utilizing the power of Python and integrating modern libraries, PandaQ offers to manage basic SQL queries. This document serves as your guide to exploring its features, setup, and usage.

## Contents table
- [Key Features](#KeyFeatures)
- [Project Structure](#projectstructure)
- [Setup and Execution](#setupandexecution)
- [Usage Notes](#usagenotes)
- [Test Cases](#TestCases)
- [References](#references)
- [License](#license)

## Key Features
PandaQ stands out with these notable features:
- Input Handling: Processes a subset of SQL queries efficiently.
- Data Compatibility: Seamlessly works with CSV files.
- Core Library: Leverages the versatility of the Pandas library.
- User Interface: Features a Streamlit-based interactive interface for ease of use.

## Project Structure
The project is meticulously organized into three main components:

- `README.md`: This document, offering comprehensive insights into the project.
- `pandaQ.g4`: The ANTLR4 file, which is the backbone of the project's grammar.
- `pandaQ.py`: The Python script that forms the core of the interpreter, utilizing visitor patterns for functionality.
- `data`: The directiory that contains the files used in the tests.

## Setup and Execution
### Prerequisites
Ensure you have the following packages installed:

- `pip install streamlit`
- `pip install antlr4-tools`
- `pip install antlr4-python3-runtime`

Note: These installations are one-time requirements.

### Running PandaQ
To launch PandaQ, follow these steps:

1. Compile the Grammar (only for the initial run):
- `antlr4 -Dlanguage.Python3 -no-listener -viewer pandaQ.g4`
2. Execute PandaQ:
- `streamlit run pandaQ.py`

## Usage Notes
- Debug Mode: Toggle the DEBUG flag at the program's start to print the query tree on-screen for each query.
- Case Sensitivity: The interpreter handles both uppercase and lowercase SQL keywords, though mixed-case keywords (like 'SeLeCT') are not supported.
- Calculated Fields: Numeric calculations are prioritized before column operations.
- Semicolon Usage: Ending queries with ';' is optional.
- Symbol Table Handling: Local symbols named after database tables will override the table in queries.
- Order by Defaults: Absent explicit ASC/DESC declaration, 'ORDER BY' defaults to ASC.
- Symbol Table Queries: Querying a symbol table entry returns its stored value, with overwrite capability.
- Query Efficiency: 'WHERE' clauses are processed before 'ORDER BY' for optimized performance.

## Test Cases
PandaQ has successfully passed various tests, including:
### Test 1: Basic query
```
select * from countries;
```
### Test 2a: Columns
```
select first_name, last_name from employees;
```
### Test 2b: Calculated fields
```
select first_name, salary, salary * 1.05 as new_salary from employees;
```
### Test 3: Order by
```
select * from countries order by region_id, country_name desc;
```
### Test 4: Where
```
select * from countries where not region_id=1 and not region_id=3;
```
### Test 5: Inner join
```
select first_name, department_name from employees inner join departments on department_id = department_id;
```
```
select first_name, last_name, job_title, department_name from employees inner join departments on department_id = department_id inner join jobs on job_id = job_id;
```
### Test 6: Symbol table
```
q := select first_name, last_name, job_title, department_name from employees inner join departments on department_id = department_id inner join jobs on job_id = job_id;
```
```
select first_name, last_name from q;
```
### Test 7: plots
```
q := select first_name, last_name, salary, salary * 1.05 as new_salary from employees where department_id = 5;
```
```
plot q;
```
### Test 8: subqueries
```
select employee_id, first_name, last_name from employees where department_id in (select department_id from departments where location_id=1700) order by first_name, last_name;
```

## References

- Python ANTLR: [ANTLR for Python](https://gebakx.github.io/Python3/compiladors.html#1)
- Pandas Documentation:[Pandas Official Docs](https://pandas.pydata.org/pandas-docs/stable/index.html)
- Streamlit Documentation: [Streamlit Docs](https://docs.streamlit.io/)
- SQL Tutorial: [Learn SQL](https://www.sqltutorial.org/)

## License

Distributed under the MIT License. See [`LICENSE.txt`](./LICENSE.txt) for more information.

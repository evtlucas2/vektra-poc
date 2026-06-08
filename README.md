# Vektra POC

Project that aims to be a Proof of Concept of the use of spec driven development and claude code to analyze personal finance.

## Prompts used to create the project

### Constitution
/speckit-constitution create principles for a data science project. There will be features for etl, data analysis and time-series analysis. The data folder is decoupled from the
  project folder. Keep the project simple. Use principles of clean code. Use TDD to test features. 

### Feature 1
/speckit-specify This feature aims to load transactions from a bank account to a database. The data is available as Open Financial Exchange(OFX) format, and should be stored in a 
  table on a relational database. The file has a header and a xml which contain data. The header could be ignored. For each transaction, store directly the date, the transaction and
  the amount of the transaction. When the memo tag has the format "day/month hour:minute description", the memo content should be splited into 2 fields: the first one will be the 
  effective date, storing day/month/year of the transaction, getting the year from the tag DTPOSTED, and the second one will be the description. Ignore transactions with name equals
  to "Saldo do dia" and "Saldo Anterior".
  
/speckit-plan Use python and related packages to store OFX content into a PostgreSQL database.
 
/speckit-specify Update the current specification: the directory of the ofx files could store 0 or more ofx files. Do nothing if there is no files. If there is 1 or more files,      
process each file at a time.

/speckit-tasks

/speckit-implement

### Feature 2

/speckit-specify The next feature puts an account label in transactions. Each directory refers to a different account, and it's important to know the account in which the transaction happened. The hash that identifies each transaction should include the account label. This label should be set by the user.

/speckit-plan Plan the new feature considering the user will define the directory label on the command line. Add Yoyo-migrations to the requirements.txt, and reorganize the project to use this metadata versioning tool.

/speckit-tasks

/speckit-implement

### Feature 3

/speckit-specify The field effective date should be not null. When there is no date in the memo tag, the effective date should be equal to posted_date

Suggestion from speckit: Ready for /speckit-tasks or /speckit-implement directly (change is small enough to implement without a full task plan if preferred).

/speckit-implement

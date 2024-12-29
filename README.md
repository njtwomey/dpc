## Setup 

```bash
brew install postgres

psql postgres 
# create user niall; 
# alter user niall createdb; 

psql postgres -U niall -d dpcdb
# create database dpcdb;

psql -d dpcdb -U niall -f database-backup/backup.sql
```
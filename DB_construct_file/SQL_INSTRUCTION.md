# VM Container and MySQL Access Instructions

## 1. Verify Containers

**PLEASE check** you have your mysql/mysql-server:latest container is running. If you have a running one which is not aaw8, please kill the container

## 2. Set up db on your local

### Step1: get the container up and run

```bash
$ docker compose -f project_db.yml -p aaw8 up -d
```

Note: The project uses a fixed name (aaw8) from the initial construction.

### Step2: Execute the mysql interface on your terminal

#### We need to first look up the container id

```bash
$ docker container ps
```

#### Once we have the id for mysql/mysql-server:latest

```bash
$ docker container exec -it 888888 mysql -u root -p //88888 is specific here its meant to be ur container id
```

PS: 888888 should be your container id

#### Enter pass word : Group17

#### Now you will be direted to mysql interface

First, enter

```mysql
SHOW TABLES;
```

There will be a list of tables including Vending_Machine showing up. However, it does not have any tables inside yet!
We need to head to the file in this directory:

```
DB_construct_file/DB_init/init.sql
```

copy and paste the query in one line and excute it.

Then, enter

```mysql
USE Vending_Machine;
SHOW TABLES;
DESCRIBE Inventoryl
```

The corresponding data should be there.

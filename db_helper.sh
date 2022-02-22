#!/bin/bash
DATA_ENV_FILE="db.env"
if [ ! -f "$DATA_ENV_FILE" ]; then
    echo "$DATA_ENV_FILE does not exist."
    exit
fi

source $DATA_ENV_FILE

LOADDIR="website/app/data"
DELETECMD="select 'drop table if exists \"' || tablename || '\" cascade;' from pg_tables where schemaname = 'public';"
EMPTYCMD="select 'delete from \"' || tablename || '\";' from pg_tables where schemaname = 'public';"
BACKUPCMD="select tablename from pg_tables where schemaname = 'public';"
POSTGRES_HOSTNAME="172.20.0.10"

USAGE="Usage: ./db_helper.sh [[d]elete|[e]mpty|[l]oad|[b]ackup] [DIRPATH]\n
[d]elete\t\tremove all tables from the database\n
[e]mpty\t\tremove all data from tables in the database\n
[l]oad\t\t\tload initial csv data into the database\n
[b]ackup\t\tsave database tables to backup csvs\n
[g]enerate\t\tgenerate a new data sample set\n
\n
DIRPATH is optional.\n
If not specified for load, will load from most recent DIR in data.\n
If not specified for backup, will save to current directory."

POSITIONAL_ARGS=()

if [[ $# -gt 0 ]]; then
  case $1 in
    d|delete)
        DELCMD2=$(PGPASSWORD=$POSTGRES_PASSWORD psql -h "$POSTGRES_HOSTNAME" -U "$POSTGRES_USER" "$POSTGRES_DB" -c "$DELETECMD");
        DELCMD2=$(echo "$DELCMD2" | tail -n +3 | head -n -1)
        PGPASSWORD=$POSTGRES_PASSWORD psql -h "$POSTGRES_HOSTNAME" -U "$POSTGRES_USER" "$POSTGRES_DB" -c "$DELCMD2"
        ;;
    e|empty)
        ECMD2=$(PGPASSWORD=$POSTGRES_PASSWORD psql -h "$POSTGRES_HOSTNAME" -U "$POSTGRES_USER" "$POSTGRES_DB" -c "$EMPTYCMD");
        ECMD2="$(echo "$ECMD2" | tail -n +3 | head -n -1)"
        lines=$(echo "$ECMD2" | wc -l)
        for (( i=1; i<=$lines; i++ )); do
            while IFS= read -r item; do
                PGPASSWORD=$POSTGRES_PASSWORD psql -h "$POSTGRES_HOSTNAME" -U "$POSTGRES_USER" "$POSTGRES_DB" -c "$item"
            done <<< "$ECMD2"
        done
        ;;
    l|load)
        if [[ $# -gt 1 ]]; then
            DIRPATH=$2
        else
            DIRPATH=$LOADDIR/$(ls -lArt ${LOADDIR} | grep -v "seed" | grep ^d | grep -oP " [^ ]*$" | grep -oP "[^ ]*" | tail -n 1)
        fi
        lines=$(ls -l $DIRPATH | wc -l)
        for (( i=1; i<=$lines; i++ )); do
            for FILE in $(ls -rt $DIRPATH); do 
                tablename="${FILE%.*}"
                LOADCMD="\copy $tablename FROM '$DIRPATH/$FILE' WITH (FORMAT CSV);"
                PGPASSWORD=$POSTGRES_PASSWORD psql -h "$POSTGRES_HOSTNAME" -U "$POSTGRES_USER" "$POSTGRES_DB" -c "$LOADCMD"
            done
        done
        ;;
    b|backup)
        if [[ $# -gt 1 ]]; then
            DIRPATH=$2
        else
            now=$(date +"%Y-%m-%d_%T")
            DIRPATH="backup_$now"
            mkdir $DIRPATH
        fi
        BACKUPCMD2=$(PGPASSWORD=$POSTGRES_PASSWORD psql -h "$POSTGRES_HOSTNAME" -U "$POSTGRES_USER" "$POSTGRES_DB" -c "$BACKUPCMD");
        BACKUPCMD2="$(echo "$BACKUPCMD2" | tail -n +3 | head -n -1)"
        while IFS= read -r item; do
            BACKUPCOPY="\copy $item TO '$DIRPATH/$item' WITH (FORMAT CSV);"
            PGPASSWORD=$POSTGRES_PASSWORD psql -h "$POSTGRES_HOSTNAME" -U "$POSTGRES_USER" "$POSTGRES_DB" -c "$BACKUPCOPY"
        done <<< "$BACKUPCMD2"
        ;;
    g|generate)
        cd backend/data
        python3 init_data_gen.py
        ;;
    --default)
      echo "Unknown option $1"
      exit 1
      ;;
    -*|--*)
      echo "Unknown option $1"
      exit 1
      ;;
    *)
      echo "Unknown option $1"
      exit 1
      ;;
  esac
else
    echo -e $USAGE
fi
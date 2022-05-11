#!/bin/bash

set -e

function create_user_and_database() {
	local user=$1
	local password=$2
	local database=$3
	echo "  Creating user '$user:$password' and database '$database'"
	psql -v ON_ERROR_STOP=1 --username "$POSTGRES_USER" <<-EOSQL
	    CREATE USER $user WITH PASSWORD '$password';
	    CREATE DATABASE $database;
	    GRANT ALL PRIVILEGES ON DATABASE $database TO $user;
EOSQL
}

if [ -n "$POSTGRES_MULTIPLE_DATABASES" ]; then
	echo "Multiple database creation requested: $POSTGRES_MULTIPLE_DATABASES"
	for conn in $(echo "$POSTGRES_MULTIPLE_DATABASES" | tr ',' ' '); do
		user=$(echo $conn | cut -d ":" -f 1)
		password=$(echo $conn | cut -d ":" -f 2)
		db=$(echo $conn | cut -d ":" -f 3)
		create_user_and_database $user $password $db
	done
	echo "Databases created"
else
	echo "Environment variable 'POSTGRES_MULTIPLE_DATABASES' not specified. Skipping."
fi

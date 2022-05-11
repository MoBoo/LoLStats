#!/bin/bash

set -e

function import_from_sql() {
	local filepath=$1
	local user=$2
	local database=$3
	echo "  Importing '$filepath' as user '$user' into database '$database'"
	pg_restore -d $database --username $user --no-password $filepath
}

if [ -n "$POSTGRES_IMPORT_DATABASES" ]; then
	echo "Database import requested: $POSTGRES_IMPORT_DATABASES"
	for params in $(echo "$POSTGRES_IMPORT_DATABASES" | tr ',' ' '); do
		filepath=$(echo $params | cut -d ":" -f 1)
		user=$(echo $params | cut -d ":" -f 2)
		database=$(echo $params | cut -d ":" -f 3)
		import_from_sql $filepath $user $database
	done
	echo "Databases imported"
else
	echo "Environment variable 'POSTGRES_IMPORT_DATABASES' not specified. Skipping."
fi

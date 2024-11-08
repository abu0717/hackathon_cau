#!/bin/bash

set -o errexit
set -o pipefail
set -o nounset

python << END
import sys
import time

import psycopg

suggest_unrecoverable_after = 30
start = time.time()

user=getenv('DATABASE_USER')
pass=getenv('DATABASE_PASS')
host=getenv('DATABASE_HOST')
port=getenv('DATABASE_PORT')
name=getenv('DATABASE_NAME')
url = f"postgres://{user}:{pass}@{host}:{port}/{name}"
while True:
    try:
        con = psycopg.connect(conninfo=url)
    except psycopg.OperationalError as error:
        sys.stderr.write("Waiting for PostgreSQL to become available...\n")

        if time.time() - start > suggest_unrecoverable_after:
            sys.stderr.write("  This is taking longer than expected. The following exception may be indicative of an unrecoverable error: '{}'\n".format(error))
    else:
        con.close()
        break
    time.sleep(1)
END

>&2 echo 'PostgreSQL is available'

tail -f /var/log/cron.log &

exec "$@"

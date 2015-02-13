#!/bin/bash
# This script is intended to be run as a cronjob.
# It will update the Fuseki TDB store if there are new commits
# in the Git repo.

git fetch origin
if [ -n "$(git log HEAD..origin/master --oneline)" ]; then
  git pull --force
  /opt/fuseki/s-put http://localhost:3030/ds/data http://data.ub.uio.no/rt realfagstermer.ttl
fi

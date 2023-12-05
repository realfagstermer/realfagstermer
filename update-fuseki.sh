#!/bin/bash
#
# This script puts data to Fuseki if new commits are found in the remote git repo.
#
# Set RUBYENV to the value returned from `rvm env --path` to make the script find
# the RVM environment when run as a cronjob.
#
# Example crontab:
#
#  PATH=/usr/local/sbin:/usr/local/bin:/sbin:/bin:/usr/sbin:/usr/bin:/opt/fuseki
#  RUBYENV=/usr/local/rvm/environments/ruby-1.9.3-p551@global
#  10 * * * * /opt/realfagstermer/update-fuseki.sh

cd "$( dirname "${BASH_SOURCE[0]}" )"

if [ -n "$RUBYENV" ]; then
  source "$RUBYENV"
fi

git fetch origin
#if [ -n "$(git log HEAD..origin/master --oneline)" ]; then
git pull --force
s-put http://localhost:3030/ds/data http://data.ub.uio.no/realfagstermer dist/realfagstermer.ttl
#fi

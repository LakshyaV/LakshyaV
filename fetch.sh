#!/bin/sh
# Write the last year of daily contribution counts to data/contributions.json.
# Needs the gh CLI and a token in GH_TOKEN (or a logged-in gh).
set -e
USER_LOGIN=${1:-LakshyaV}
mkdir -p data
gh api graphql -f login="$USER_LOGIN" -f query='
  query($login: String!) {
    user(login: $login) {
      contributionsCollection {
        contributionCalendar { weeks { contributionDays { date contributionCount } } }
      }
    }
  }' --jq '[.data.user.contributionsCollection.contributionCalendar.weeks[].contributionDays[] | {date, count: .contributionCount}]' > data/contributions.json

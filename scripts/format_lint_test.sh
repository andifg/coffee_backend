#!/usr/bin/env bash
GIT_ROOT=$(git rev-parse --show-toplevel)

set -e

pushd "${GIT_ROOT}" > /dev/null

printf "Formatting: \n" && \
    ./scripts/format.sh && \
    printf "\nLinting: \n" && \
    ./scripts/lint.sh && \
    printf "\nTesting: \n" && \
    ./scripts/test.sh

SUCCESS=$?

popd > /dev/null

exit $SUCCESS
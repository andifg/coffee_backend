#!/usr/bin/env bash
GIT_ROOT=$(git rev-parse --show-toplevel)

set -e

pushd "${GIT_ROOT}" > /dev/null


printf "Testing with pytest \n" && \
pytest -s


SUCCESS=$?

popd > /dev/null

exit $SUCCESS
#!/usr/bin/env bash
GIT_ROOT=$(git rev-parse --show-toplevel)

set -e

pushd "${GIT_ROOT}" > /dev/null

printf "Formatting with black:\n" && \
    black . && \
    printf "\n\nFormatting with isort:\n" && \
    isort .

SUCCESS=$?

popd > /dev/null

exit $SUCCESS
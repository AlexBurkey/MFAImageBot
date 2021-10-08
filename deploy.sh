#!/bin/bash

echo "Copying and overwriting files in './target/'..."

# cp --target-directory=target ./src/requirements.txt
cp --target-directory=target ./src/mfaimagebot.py
cp --target-directory=target ./src/helpers.py
cp --target-directory=target ./src/my_strings.py
cp --target-directory=target ./src/praw.ini
cp --target-directory=target ./src/.env
cp --target-directory=target ./scripts/run-mfaimage.sh
cp --target-directory=target ./scripts/is-running.sh
echo "Done!"
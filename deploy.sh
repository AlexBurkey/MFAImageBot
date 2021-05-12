#!/bin/bash

echo "Copying and overwriting files in './target/'..."

cp --target-directory=target ./{src/requirements.txt,src/mfaimagebot.py,src/helpers.py,src/my_strings.py,src/praw.ini,src/.env,scripts/run-mfaimage.sh,scripts/is-running.sh}
echo "Done!"
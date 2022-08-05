#!/bin/bash

python ./main.py 2>/dev/null

if [[ $(echo $?) != 0 ]]; then
    /bin/cat respuestas.txt
fi

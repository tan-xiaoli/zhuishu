#!/bin/bash

PATHS=("./zhuishu")
LOG_PATH=("./log")

function clean_pyc()
{
    echo "Clean .pyc file.."
    for _p in ${PATHS[*]}
    do
        find ${_p} -name "*.pyc" | xargs rm -f
    done
}

function clean_log()
{
    echo "Clean log file..."
    for _p in ${LOG_PATH[*]}
    do
        find ${_p} -name "*.log" | xargs rm -f
    done
}

Main()
{
    clean_pyc
    clean_log
}

Main
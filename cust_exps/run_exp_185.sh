#!/bin/bash

# This script parses in the command line parameters from runCust, 
# maps them to the correct command line parameters for DispNet training script and launches that task
# The last line of runCust should be: bash $CONFIG_FILE --data-dir $DATA_DIR --log-dir $LOG_DIR

# Parse the command line parameters
# that runCust will give out

DATA_DIR=NONE
LOG_DIR=NONE
CONFIG_DIR=NONE

# Parsing command line arguments:
while [[ $# > 0 ]]
do
key="$1"

case $key in
    -h|--help)
    echo "Usage: run_dispnet_training_philly.sh [run_options]"
    echo "Options:"
    echo "  -d|--data-dir <path> - directory path to input data (default NONE)"
    echo "  -l|--log-dir <path> - directory path to save the log files (default NONE)"
    echo "  -p|--config-file-dir <path> - directory path to config file directory (default NONE)"
    exit 1
    ;;
    -d|--data-dir)
    DATA_DIR="$2"
    shift # pass argument
    ;;
    -p|--config-file-dir)
    CONFIG_DIR="$2"
    shift # pass argument
    ;;
    -l|--log-dir)
    LOG_DIR="$2"
 	;;
    *)
    echo Unkown option $key
    ;;
esac
shift # past argument or value
done

# Prints out the arguments that were passed into the script
echo "DATA_DIR=$DATA_DIR"
echo "LOG_DIR=$LOG_DIR"
echo "CONFIG_DIR=$CONFIG_DIR"

# Run training on philly

# Add the root folder of the code to the PYTHONPATH
export PYTHONPATH=$PYTHONPATH:$CONFIG_DIR

# Run the actual job
python $CONFIG_DIR/examples/ResNet/paper_experiments/cifar-ann-paper-exp.py \
--data_dir=$DATA_DIR \
--log_dir=$LOG_DIR \
--num_classes=10 \
-f=2 --opt_at=26 -n=9 -c=128
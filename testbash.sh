#!/usr/bin/env bash
#SBATCH -A SNIC009-87-654 -p mStud
#SBATCH -n 10
#SBATCH -t 0-00:10:00

echo "Hello cluster computing world!"
sleep 3 

echo "

module load python
virtualenv jimsenv
source jimsenv/bin/activate
cd .\TrainYourOwnYOLO\
pip install -r requirements.txt
cd .\TrainYourOwnYOLO\2_Training\
python .\Train_YOLO.py
cd ..\3_Inference\
python .\Detector.py


"

sleep 60
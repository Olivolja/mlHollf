#!/usr/bin/env bash
#SBATCH -A C3SE2020-2-6 -p vera
#SBATCH -t 5-23:59:00
#SBATCH -n 20
#SBATCH --gres=gpu:1
#SBATCH --mail-user=benvin@student.chalmers.se --mail-type=end
echo "Bash Starting@@@!"

echo " "
pwd
dir

mkdir RESULTS

echo " "
cp -r TrainYourOwnYOLO $TMPDIR
echo "@@@@ Moving to $TMPDIR"
cd $TMPDIR
echo "ㄒㄒ Current path:"
pwd
echo "中中 Contents:"
dir

echo " "
module load intel
module load Python
virtualenv jimsenv
source jimsenv/bin/activate

echo " "
echo "@@@@Moving to TrainYourOwnYOLO"
cd TrainYourOwnYOLO/
echo "ㄒㄒ Current path:"
pwd
echo "中中 Contents:"
dir

echo " "
pip install -r requirements.txt

echo " "
echo "@@@@Moving to 2_Training"
cd 2_Training/
echo "ㄒㄒ Current path:"
pwd
echo "中中 Contents:"
dir

echo " "
python3 Train_YOLO.py
cd ../3_Inference
echo "ㄒㄒ Current path:"
pwd
echo "中中 Contents:"
dir

echo " "
python3 Detector.py
cd ../Data
echo "ㄒㄒ Current path:"
pwd
echo "中中 Contents:"
dir

cp -r Model_Weights $SLURM_SUBMIT_DIR/RESULTS

echo " "
cd Source_Images
echo "ㄒㄒ Current path:"
pwd
echo "中中 Contents:"
dir

cp -r Test_Image_Detection_Results $SLURM_SUBMIT_DIR/RESULTS

echo "Bash ending@@@!"

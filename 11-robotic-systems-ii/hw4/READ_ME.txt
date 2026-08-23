libraries
numpy pyCandleMAB matplotlib cyipopt ipopt
=============


WSL (run as administrator)


usbipd list
usbipd bind --busid 1-3
usbipd attach --wsl --busid 1-3
===============
Ubuntu VM

wget https://repo.anaconda.com/miniconda/Miniconda3-latest-Linux-x86_64.sh
bash Miniconda3-latest-Linux-x86_64.sh
conda create -n hw38 python=3.9
conda activate hw38
pip install pyCandleMAB

========
1) build_tvlqr_cache.py -> run this first
2) run.py


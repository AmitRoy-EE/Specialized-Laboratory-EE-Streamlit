# Readme
This repository serves for the launching of a small energy system model in oemof. This project is funded by ORCA.nrw.

## Setup
1) Install [Git](https://git-scm.com/downloads) with all default settings.
2) Install [miniconda](https://docs.conda.io/en/latest/miniconda.html) with all default settings, but make sure to add it to the PATH when asked!
3) Optional and recommended: Install [Visual Studio Code](https://code.visualstudio.com/) with all default settings. 
    * Set default shell on the bottom right to Git Bash:  
    ![Figure of how to set shell to Git Bash in Visual Studio Code](/setup/setup_select_gitbash.png?raw=true "Set shell to Git Bash in Visual Studio Code")
    * Activate Git Bash by typing in the terminal (toggle terminal: Ctrl+ö): `conda init bash`
    * After that close Visual Studio Code and reopen it.
4) Open Visual Studio Code or any other terminal and therein open a folder to which you would like to clone this repository.
5) Clone the repository – type in the Visual Studio Code terminal (toggle terminal: Ctrl+ö) or any other terminal: `git clone https://gitlab.ruhr-uni-bochum.de/huckedyp/oemof-household.git`
6) Change the directory to this cloned repository by typing in the same terminal: `cd oemof-household/`
7) In Visual Studio Code: open new window with cloned repository by typing: `code .` Use just this new window from now on and close the old one.
8) Install [mamba](https://github.com/mamba-org/mamba) by typing: `conda install mamba -n base -c conda-forge`. If asked whether to proceed after the installation, press ENTER or type in `y`.
9) Install oemof-environment (this may take some time) by typing: `mamba env create -f environment.yaml`
10) Activate oemof-environment by typing:	`conda activate oemof`
11) Done - you can now use the tool by typing: `streamlit run app.py`
    * If asked, make sure to allow your firewall the usage of streamlit.
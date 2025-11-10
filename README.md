# Readme
This repository contains the code to run the streamlit application for the Specialized Laboratory EE. Below you can find a link to the hosted version of this application and a guide on how to run streamlit locally on your own machine.

## Link to hosted app

[ee-fachlabor.streamlit.app](https://ee-fachlabor.streamlit.app/)

## Local Setup
1) Install [Git](https://git-scm.com/downloads) with all default settings.
2) Install [miniconda](https://docs.conda.io/en/latest/miniconda.html) with all default settings, but make sure to add it to the PATH when asked!
3) Optional and recommended: Install [Visual Studio Code](https://code.visualstudio.com/) with all default settings. 
    * Set default shell on the bottom right to Git Bash:  
    ![Figure of how to set shell to Git Bash in Visual Studio Code](/setup/setup_select_gitbash.png?raw=true "Set shell to Git Bash in Visual Studio Code")
    * Activate Git Bash by typing in the terminal (toggle terminal: Ctrl+ö): `conda init bash`
    * After that close Visual Studio Code and reopen it.
4) Open Visual Studio Code or any other terminal and therein open a folder to which you would like to clone this repository.
5) Clone the repository – type in the Visual Studio Code terminal (toggle terminal: Ctrl+ö) or any other terminal: `git clone https://gitlab.ruhr-uni-bochum.de/ee/NeuesFachlabor.git`
6) Change the directory to this cloned repository by typing in the same terminal: `cd NeuesFachlabor/`
7) In Visual Studio Code: open the cloned repository
8) Install environment (this may take some time) by typing: `conda env create -f environment.yaml`
9) Activate environment by typing:	`conda activate fachlabor`
10) Done - you can now use the tool by typing: `streamlit run app.py`
    * If asked, make sure to allow your firewall the usage of streamlit.
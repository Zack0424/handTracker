@echo off

:: Define the name of the virtual environment
set VENV_NAME=venv

:: Check if the virtual environment already exists, and if not, create it
if not exist %VENV_NAME% (
    call python -m venv %VENV_NAME%
)

:: Activate the virtual environment
call %VENV_NAME%\Scripts\activate

:: Install dependencies from requirements.txt
call pip install -r requirements.txt

:: Run the main.py script
python main.py

:: Deactivate the virtual environment
deactivate

:: Exit
exit /b 0

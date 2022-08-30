:: setup env for p3k engine 
set p3k_HOME=%CD%
setx p3k_HOME=%CD%

setx PATH "%PATH%;%p3k_HOME%"
setx PYTHONPATH "%PYTHONPATH%;%p3k_HOME%"
echo p3k engine added to env path

:: engine dependencies
pip install -r requirements.txt
 
echo please, restart computer for installation to complete. 
pause

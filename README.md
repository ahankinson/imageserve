Imageserve
==========

Description
-----------
This is a basic Django project for hosting images in the [RASI database](https://images.rasi.mcgill.ca) and their metadata, largely found in the [ISMI database](https://openmind-ismi-dev.mpiwg-berlin.mpg.de/om4-ismi/). It uses DDMAL's [diva.js](https://github.com/DDMAL/diva.js) for the viewer.

Requirements
------------
The requirements have been managed with virtualenv, so running `pip install -r requirements.txt` should get you everything you need.

Setup
-----
Running 
`python manage.py schemamigration imageserve --initial
python manage.py syncdb
python manage.py migrate imageserve`
should get everything running. Also you will likely need to change the parameters in conf.py to correctly point to the images, and settings.py may need to be changed to correctly point to your local imageserve folder (there's probably a better way to do this automatically, which I have not considered since I expect nobody else will use this project).
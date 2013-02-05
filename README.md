Imageserve - RASI Image Viewer
==============================

Description
-----------
This is a basic Django project for hosting images in the [RASI database](https://images.rasi.mcgill.ca) and their metadata, largely found in the [ISMI database](https://openmind-ismi-dev.mpiwg-berlin.mpg.de/om4-ismi/). It uses DDMAL's [diva.js](https://github.com/DDMAL/diva.js) for the viewer.

Requirements
------------
The requirements have been managed with virtualenv, so running `pip install -r requirements.txt` should get you everything you need.

Setup
-----
Make sure the parameter IMG_DIR in imageserve/conf.py is pointing to your image folder, and that in the declaration of the diva viewer in imageserve/templates/diva.html, the setting iipServerURL is pointing to the correct IIPImage server. Then, from the repository's root directory, execute 
```
python manage.py schemamigration imageserve --initial
python manage.py syncdb
python manage.py migrate imageserve
python manage.py runserver
```
and everything should be up and running!
Imageserve
==========

Description
-----------
This is a basic Django project for hosting images in the [RASI database](https://images.rasi.mcgill.ca) and their metadata, largely found in the [ISMI database](https://openmind-ismi-dev.mpiwg-berlin.mpg.de/om4-ismi/). It uses DDMAL's [diva.js](https://github.com/DDMAL/diva.js) for the viewer.

Requirements
------------
This project requires Django and also the third-party addition django-dbsettings, which can be easily obtained by running `sudo pip install django-dbsettings`.

Setup
-----
Running `python manage.py syncdb` followed by `python manage.py schemamigration imageserveapp --initial` and `python manage.py migrate imageserveapp` should get everything running. Also you will likely need to change the parameters in conf.py to correctly point to the images, and settings.py may need to be changed to correctly point to your local imageserveapp folder (there's probably a better way to do this automatically, which I have not considered since I expect nobody else will use this project).
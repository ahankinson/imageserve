WORKING_DIR=/data7/srv/webapps/imageserve2
ACTIVATE_PATH=srv_env/bin/activate
MY_PATH="`dirname \"$0\"`"              # relative
MY_PATH="`( cd \"$MY_PATH\" && pwd )`"  # absolutized and normalized

cd ${WORKING_DIR}
source ${ACTIVATE_PATH}
echo ${ACTIVATE_PATH}
python manage.py fetch_entities
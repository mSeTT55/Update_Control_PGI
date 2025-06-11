# set base image (host OS)
FROM python:3.12

# set the working directory in the container
WORKDIR /button_update_PGI

# copy the dependencies file to the working directory
COPY . /button_update_PGI

# install dependencies
RUN pip install -r requirements.txt

# command to run on container start
CMD [ "python", "./app.py" ]
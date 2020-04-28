# [START dockerfile]
FROM gcr.io/google_appengine/python
WORKDIR /root

# Change the -p argument to use Python 2.7 if desired.
RUN virtualenv /env -p python3.6

# Set virtualenv environment variables. This is equivalent to running
# source /env/bin/activate.
ENV VIRTUAL_ENV /env
ENV PATH /env/bin:$PATH

# Copies the trainer code to the docker image.
ADD ./ /root/
RUN pip install -r /root/requirements.txt

# Sets up the entry point to invoke the trainer.
ENTRYPOINT ["python", "main.py"]
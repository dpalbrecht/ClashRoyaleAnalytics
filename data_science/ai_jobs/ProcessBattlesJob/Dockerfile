# [START dockerfile]
FROM gcr.io/google_appengine/python
WORKDIR /root

# Change the -p argument to use Python 2.7 if desired.
RUN virtualenv /env -p python3.6

# Set virtualenv environment variables. This is equivalent to running
# source /env/bin/activate.
ENV VIRTUAL_ENV /env
ENV PATH /env/bin:$PATH

# Installs google cloud sdk, this is mostly for using gsutil to export model.
RUN wget -nv \
    https://dl.google.com/dl/cloudsdk/release/google-cloud-sdk.tar.gz && \
    mkdir /root/tools && \
    tar xvzf google-cloud-sdk.tar.gz -C /root/tools && \
    rm google-cloud-sdk.tar.gz && \
    /root/tools/google-cloud-sdk/install.sh --usage-reporting=false \
        --path-update=false --bash-completion=false \
        --disable-installation-options && \
    rm -rf /root/.config/* && \
    ln -s /root/.config /config && \
    # Remove the backup directory that gcloud creates
    rm -rf /root/tools/google-cloud-sdk/.install/.backup
    
# Path configuration
ENV PATH $PATH:/root/tools/google-cloud-sdk/bin

# Make sure gsutil will use the default service account
RUN echo '[GoogleCompute]\nservice_account = default' > /etc/boto.cfg

# Copies the trainer code to the docker image.
ADD ./ /root/
RUN pip install -r /root/requirements.txt

# Sets up the entry point to invoke the trainer.
ENTRYPOINT ["python", "main.py"]
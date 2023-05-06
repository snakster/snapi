FROM snapi

WORKDIR /tmp/app
COPY requirements.txt .
RUN pip-sync ./requirements.txt

WORKDIR /app
CMD [ "sh", "-c" ]
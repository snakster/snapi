FROM snapi-pip-tools

WORKDIR /lib/snapi

# Split copy of requirements and rest for better caching
COPY pkg/requirements.txt ./pkg/requirements.txt
COPY LICENSE .
COPY README.md .
RUN pip-sync ./pkg/requirements.txt

COPY pkg/ ./pkg
RUN pip install pkg/

WORKDIR /app
CMD [ "sh", "-c" ]
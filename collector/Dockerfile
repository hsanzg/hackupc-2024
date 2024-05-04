FROM python:3-alpine3.18
RUN python -m pip install influxdb-client pyserial numpy
COPY src/* /
CMD ["/bin/sh", "/run.sh"]

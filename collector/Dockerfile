FROM python:3-alpine3.18
RUN apk update && apk add py3-mongo-pyc
RUN python -m pip install pymongo
COPY src/* /
CMD ["/bin/sh", "/run.sh"]
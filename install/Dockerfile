FROM python:3.9.0-slim

ARG PACKAGE_NAME

COPY $PACKAGE_NAME /tmp/
COPY pip.conf /tmp
COPY requirements.txt /tmp

RUN mkdir -p ~/.pip/ && mv /tmp/pip.conf ~/.pip \
    && pip install --upgrade pip \
    && pip install -r /tmp/requirements.txt \
    && pip install /tmp/$PACKAGE_NAME && rm -rf /tmp/$PACKAGE_NAME \
    && pip cache purge
RUN mkdir -p /etc/myansi && touch /etc/myansi/myansi.conf

EXPOSE 80

ENTRYPOINT [ "myansi", "serve", "--container"]
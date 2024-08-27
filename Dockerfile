FROM ubuntu:20.04 

WORKDIR /spot-check

RUN apt-get update && DEBIAN_FRONTEND=noninteractive apt-get install -y \
   python3.9-venv && apt-get clean 

RUN python3.9 -m venv /venv 
ENV PATH=/venv/bin:$PATH
#get built wheel into the container
ADD dist/ . 
COPY requirements.txt /tmp/pip-tmp/
RUN pip --no-cache-dir install -r /tmp/pip-tmp/requirements.txt \
    && rm -rf /tmp/pip-tmp

COPY . /spot-check

RUN chmod +x entrypoint.sh


ENTRYPOINT ["./entrypoint.sh"]
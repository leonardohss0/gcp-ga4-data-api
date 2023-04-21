FROM python:3.8
LABEL maintainer = "Google Analytics 4"

RUN curl https://packages.microsoft.com/keys/microsoft.asc | apt-key add - \
    && curl https://packages.microsoft.com/config/debian/9/prod.list > /etc/apt/sources.list.d/mssql-release.list \
    && apt-get update \
    && wget http://archive.ubuntu.com/ubuntu/pool/main/g/glibc/multiarch-support_2.27-3ubuntu1.5_amd64.deb \
    && apt-get install ./multiarch-support_2.27-3ubuntu1.5_amd64.deb \
    && apt-get install -y build-essential cmake \
    && ACCEPT_EULA=Y apt-get install msodbcsql17 unixodbc-dev -y

COPY ./requirements.txt ./

RUN pip3 install --upgrade pip
RUN pip3 --no-cache-dir install -r requirements.txt

WORKDIR /
COPY ./ /
EXPOSE 9000
CMD ["python3", "-u", "-m", "analytics_flow"]

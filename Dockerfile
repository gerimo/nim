FROM python:2.7.9

ADD . /app
WORKDIR /app

# Update pip
RUN pip install --upgrade pip
# Install requirements
RUN pip install -r requirements.txt

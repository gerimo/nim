FROM tiangolo/uwsgi-nginx-flask:flask

COPY conf/upload_100m.conf /etc/nginx/conf.d/

COPY ./requirements.txt /

# Update pip
RUN pip install --upgrade pip
# Install requirements
RUN pip install -r /requirements.txt

ADD . /app

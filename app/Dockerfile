FROM python:3.8.7-alpine
WORKDIR /usr/src/app

ENV FLASK_APP=app.py
ENV FLASK_RUN_HOST=0.0.0.0
ENV FLASK_EVN=development
ENV FLASK_SECRET_KEY='anything_hash_sf213'
ENV FLASK_DEBUG=1
RUN apk add --no-cache gcc musl-dev linux-headers postgresql-dev
# RUN apk update \
#     && apk add --virtual build-deps gcc musl-dev \
#     && pip install psycopg2 \
#     && apk add jpeg-dev zlib-dev libjpeg \
#     && pip install Pillow \
#     && apk del build-deps \
#     gfortran py-pip build-base py3-numpy
#RUN pip install numpy
COPY requirements.txt ./requirements.txt
RUN pip install -r requirements.txt
#RUN ls -la app/
EXPOSE 5000
COPY . .

#CMD ["python", "app.py"]
CMD ["flask", "run"]
FROM python:3.8
RUN mkdir /code
RUN pip install pipenv
#ENV PYTHONUNBUFFERED 1
#COPY Pipfile /code/
#COPY Pipfile.lock /code/
COPY . /code/
RUN cd /code && pipenv lock --requirements > requirements.txt
#WORKDIR /code
#COPY requirements.txt /code/
RUN pip install -r /code/requirements.txt

#FROM python:3.8
#RUN mkdir /code
#RUN pip install pipenv
#COPY . /code/
#RUN cd /code && PIPENV_VENV_IN_PROJECT=1 pipenv sync
#CMD python manage.py runserver
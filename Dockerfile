FROM python:3.6

WORKDIR /MacroscopAliceSkillService
COPY . /MacroscopAliceSkillService

EXPOSE 5000

RUN pip install -r requirements.txt
CMD FLASK_APP=views.py flask run --host="::"
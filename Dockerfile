FROM python:3

ADD entry_script.py /
ADD requirements.txt /
ADD dataset-1/ /input/
ADD stopwords.txt /

RUN pip install -r requirements.txt
RUN pip install -U nltk


ENTRYPOINT [ "python", "./entry_script.py", "1" ]


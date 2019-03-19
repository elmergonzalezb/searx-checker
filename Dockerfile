FROM python:3

WORKDIR /opt/searx-checker/

COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

COPY checker /opt/searx-checker/checker

ENTRYPOINT [ "python", "./checker/checker.py" ]

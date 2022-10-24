FROM python:3.9-alpine

WORKDIR /shop

COPY requirements.txt /shop/requirements.txt
RUN pip install -r requirements.txt


# Now copy in our code, and run it
#COPY . /customAuth
EXPOSE 8000

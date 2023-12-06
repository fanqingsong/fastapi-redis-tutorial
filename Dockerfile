FROM tiangolo/uvicorn-gunicorn-fastapi:python3.8

WORKDIR /app

# Copy poetry.lock* in case it doesn't exist in the repo
COPY ./requirements.txt /app/

RUN bash -c "pip3 install -i https://pypi.tuna.tsinghua.edu.cn/simple -r requirements.txt"

COPY ./app /app

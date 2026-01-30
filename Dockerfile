FROM python:3.11-slim

WORKDIR /app

# Install git for gitingest
RUN apt-get update && apt-get install -y git && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .
RUN pip install -e .

EXPOSE 8095

ENTRYPOINT ["streamlit", "run", "src/gitthread/app.py", "--server.port=8095", "--server.address=0.0.0.0"]

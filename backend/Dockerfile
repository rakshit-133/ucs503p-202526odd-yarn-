# Start with a standard Python 3.10 image
FROM python:3.10-slim

# Set the working directory inside the container
WORKDIR /app

# CRITICAL: Install the Graphviz system package
RUN apt-get update && apt-get install -y graphviz

# Copy your requirements file and install Python packages
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy all your backend code into the container
COPY . .

# Tell the container to run your app
# Render sets the $PORT variable for you
# Change "main:app" if your main Python file is named differently
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "$PORT"]
# Use lightweight Python image
FROM python:3.10-slim

# Set working directory
WORKDIR /code

# Copy everything
COPY . .

# Install dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Expose the default port Hugging Face Spaces uses
EXPOSE 7860

# Start FastAPI app with Uvicorn
CMD ["uvicorn", "app:app", "--host", "0.0.0.0", "--port", "7860"]

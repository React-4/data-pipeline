# 1. Use the official Python image as the base image
FROM python:3.9-slim

# 2. Set the working directory inside the container
WORKDIR /app

# 3. Copy the requirements file to the working directory
COPY requirements.txt .

# 4. Install dependencies
RUN pip install --no-cache-dir -r requirements.txt

# 5. Copy the rest of the application code to the container
COPY . .

# 6. Set environment variables to be read from an external source
# The actual values will be provided via Docker Compose or .env
ENV APP_KEY=""
ENV APP_SECRET=""
ENV ACC=""
ENV ACC_NO=""
ENV TOKEN=""
ENV TOKEN_EXPIRE_TIME=""
ENV DB_USER=""
ENV DB_PASSWORD=""
ENV DB_HOST=""
ENV DB_PORT=""
ENV DB_NAME=""
ENV DART_API_KEY=""
ENV GPT_API_KEY=""
ENV REDIS_HOST=""
ENV REDIS_PORT=""
ENV REDIS_DB=""

# 7. Command to run your application
CMD ["python", "update.py"]

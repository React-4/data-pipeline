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

# 6. Command to run your application (modify as needed)
CMD ["python", "update.py"]

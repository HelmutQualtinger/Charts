# Use a Python 3.13 slim image as the base
FROM python:3.13-slim

# Set the working directory in the container
WORKDIR /app

# Copy the requirements file into the container
COPY requirements.txt .

# Install the Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy the application files into the container
COPY server.py ./
COPY smic2.py ./
COPY AAPL_since_2024.csv ./
COPY smi_total_return_2000_2024.csv ./

# Expose the port that the Flask app runs on
EXPOSE 8000

# Define the command to run the Flask application
CMD ["python", "server.py"]

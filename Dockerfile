# Use a specific version of the python image
FROM python:3.11.6

# Set the working directory in the Docker image
WORKDIR /app

# Copy the current directory contents into the container at /app
COPY ./model.py /app
COPY ./generated_data.csv /app

# Install required Python packages
# Pin the versions to ensure reproducibility
RUN pip install pandas scikit-learn

# Run the Python script when the container launches
CMD ["python", "/app/model.py", "{\"Address\":\"f01927170\",\"AdjustedPower\":33.67,\"WinCount\":6130,\"SectorTotal\":110328,\"SectorActive\":110328,\"SectorFaults\":0,\"SectorRecoveries\":0,\"LoanAmount\":\"1000\"}"]
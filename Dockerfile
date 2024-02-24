FROM python:3.10

# Set the working directory
WORKDIR /app

# Copy the current directory contents into the container at /app
COPY . /app

# Install any needed packages specified in requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

# Install libgl1-mesa-glx to fix the error: "libGL error: No matching fbConfigs or visuals found"
RUN apt-get update && apt-get install -y libgl1-mesa-glx


# Make port 80 available to the world outside this container
EXPOSE 5000

# Run app.py when the container launches
CMD ["python", "main.py"]


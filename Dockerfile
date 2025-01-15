FROM python:3.12-slim 

# Set working directory
WORKDIR /app

# Install git and git-lfs
RUN apt-get update && apt-get install -y git git-lfs

# Install espeak-ng
RUN apt-get -qq -y install espeak-ng > /dev/null 2>&1

# Clone the repository
RUN git lfs install
RUN git clone https://huggingface.co/hexgrad/Kokoro-82M

# Change to repository directory
WORKDIR /app/Kokoro-82M

# Copy requirements file
COPY requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy the rest of the application code
COPY . .

# Expose port for Gradio
EXPOSE 7860

# Command to run the application
CMD ["python", "run.py"]

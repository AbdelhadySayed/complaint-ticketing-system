# Use an official Python runtime as a parent image
FROM python:3.10.17-slim




COPY --from=ghcr.io/astral-sh/uv:latest /uv /uvx /bin/

# Set the working directory in the container
WORKDIR /app

# Copy the requirements file into the container
COPY . .

# Install dependencies
RUN uv venv
RUN uv sync
#RUN uv run python -m nltk.downloader stopwords punkt punkt_tab

RUN apt-get update && apt-get install -y curl

#install ollama
RUN curl -fsSL https://ollama.com/install.sh | sh

RUN ollama serve & \
    sleep 10 && \
    ollama pull llama3.2 && \
    ollama pull mxbai-embed-large

# Expose the port the app runs on
EXPOSE 5000
# Run the application using Gunicorn
CMD ["bash", "-c", "ollama serve & sleep 5 && uv run gunicorn -w 1 --threads 4 --preload -b 0.0.0.0:5000 app:app"]

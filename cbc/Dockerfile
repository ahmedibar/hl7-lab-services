# This lab-base is used for local build and you need to run docker build -f base/Dockerfile.base -t lab-base . to 
# FROM lab-base

# uses the shared base image
FROM ghcr.io/ahmedibar/lab-base:latest


# Copy app code
COPY ./app /app

# Expose HL7 port (optional, can be overridden in compose)
EXPOSE 5660

# Default command
CMD ["python", "-u", "hl7_listener.py"]

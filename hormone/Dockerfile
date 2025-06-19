# uses the shared base image
FROM lab-base

# Copy app code
COPY ./app /app

# Expose HL7 port (optional, can be overridden in compose)
EXPOSE 5010

# Default command
CMD ["python", "-u", "hl7_listener.py"]

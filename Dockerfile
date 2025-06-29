FROM python:3.10-slim

# Set working directory
WORKDIR /app
COPY . /app

# Install dependencies with a timeout and no-cache to keep the image lean
RUN pip install --upgrade pip --default-timeout=100 \
    && pip install --no-cache-dir --default-timeout=100 -r requirements.txt

# Create a non-root user/group
RUN addgroup --system exwhygroup \
    && adduser --system --ingroup exwhygroup exwhybaba

# Give ownership of the app directory to the non-root user
RUN chown -R exwhybaba:exwhygroup /app

# Switch to the non-root user
USER exwhybaba

# Expose the port your Flask/Dash app runs on
EXPOSE 5000

# Start the app
CMD ["python", "app.py"]

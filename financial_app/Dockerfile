FROM python:3.10-slim

WORKDIR /app
COPY . /app


# Add timeout option to pip install
RUN pip install --upgrade pip --timeout 100 && pip install --timeout 100 -r requirements.txt

# Create non-root user exwhybaba
RUN addgroup --system exwhygroup && adduser --system --ingroup exwhygroup exwhybaba

# Give ownership of the app directory to the user
RUN chown -R exwhybaba:exwhygroup /app

# Switch to the non-root user
USER exwhybaba

EXPOSE 5020

CMD ["python", "financial_app.py"]






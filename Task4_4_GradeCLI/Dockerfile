FROM python:3.12-slim
ENV PYTHONDONTWRITEBYTECODE=1 PYTHONUNBUFFERED=1
WORKDIR /app
RUN useradd --uid 10001 --create-home appuser
COPY grade_calculator.py .
COPY samples ./samples
USER appuser
ENTRYPOINT ["python", "grade_calculator.py"]

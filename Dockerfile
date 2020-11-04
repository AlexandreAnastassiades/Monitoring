FROM registry.gitlab.com/valentin-audrerie/pr_admin_team6
COPY ./ ./app
WORKDIR /app
RUN pip install -r requirements.txt
EXPOSE 8050
CMD ["python3","./appAcceuil.py"]
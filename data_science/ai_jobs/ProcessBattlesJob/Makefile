build:
	docker build -t process-battles-job -f Dockerfile .
    
tag_push:
	docker tag process-battles-job gcr.io/royaleapp/process-battles-job;docker push gcr.io/royaleapp/process-battles-job
    
run:
	docker run -p 8081:8081 process-battles-job gunicorn -b :8081 main:app --timeout=300
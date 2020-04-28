processunixtime := $(shell date +%s)

build:
	docker build -t process_battles_job -f Dockerfile .
    
tag_push:
	docker tag process_battles_job gcr.io/royaleapp/process_battles_job;docker push gcr.io/royaleapp/process_battles_job
    
run:
	docker run -p 8081:8081 process_battles_job gunicorn -b :8081 main:app --timeout=300
    
train:
	gcloud ai-platform jobs submit training process_battles_job_$(processunixtime) --region us-west2 --master-image-uri gcr.io/royaleapp/process_battles_job --module-name main.py --staging-bucket gs://royale-data --scale-tier basic
PROEJECT_PATH := $(shell pwd)


start: clean
	@docker build -t base-image .
	docker compose up -d
	@sleep 20
	@echo "Weather App is ready!"


trainer:
	@sudo rm -rf $(PROEJECT_PATH)/files/training_data
	@sudo rm -rf $(PROEJECT_PATH)/files/model
	@docker exec -it weather-app python3 /files/trainer.py


predictor: 
	@docker exec -it weather-app python3 /files/predictor.py


viewer:
	@docker exec -it weather-app python3 /files/viewer.py


clean:
	@echo "Cleaning up..."
	@docker rm -f zookeeper
	@docker rm -f kafka1
	@docker rm -f kafka2
	@docker rm -f producer
	@docker rm -f cassandra1
	@docker rm -f cassandra2
	@docker rm -f weather-app
	@sudo rm -rf $(PROEJECT_PATH)/files/checkpoints/
	@sudo rm -f $(PROEJECT_PATH)/files/*.json
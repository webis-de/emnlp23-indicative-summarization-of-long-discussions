FRONTEND_VERSION = 1.0.0
API_VERSION = 1.0.0

guard-%:
	@ if [ "${${*}}" = "" ]; then \
		echo "Environment variable $* not set"; \
		exit 1; \
	fi

build: build_api build_frontend

push: push_api push_frontend

build_api: guard-DOCKER_USER
	docker build --file ./api/Dockerfile.deploy --tag ${DOCKER_USER}/frame-explorer-api:${API_VERSION} ./api

build_frontend: guard-DOCKER_USER
	docker build --file ./frontend/Dockerfile.deploy --tag ${DOCKER_USER}/frame-explorer-frontend:${FRONTEND_VERSION} ./frontend

push_api: guard-DOCKER_USER
	docker push ${DOCKER_USER}/frame-explorer-api:${API_VERSION}

push_frontend: guard-DOCKER_USER
	docker push ${DOCKER_USER}/frame-explorer-frontend:${FRONTEND_VERSION}

deploy_config:
	kubectl create configmap frame-explorer-api-config --from-env-file=deploy/.env

deploy_api:
	kubectl apply -f deploy/api.yaml

deploy_frontend:
	kubectl apply -f deploy/frontend.yaml

deploy_mongodb:
	kubectl apply -f deploy/mongodb.yaml

deploy_proxy:
	kubectl apply -f deploy/proxy.yaml

deploy_volumes:
	kubectl apply -f deploy/volumes.yaml

deploy_ingress:
	kubectl apply -f deploy/ingress.yaml

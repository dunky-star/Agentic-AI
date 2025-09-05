# ======== Config ========
# Adjust these if needed
IMAGE      ?= quantized_ollama:latest
CONTAINER  ?= ollama
PORT       ?= 11434
VOLUME     ?= ollama
MODEL      ?= gemma2:2b-instruct-q4_0

# ======== Helpers ========
export DOCKER_BUILDKIT=1

define GREEN
\033[32m
endef
define YELLOW
\033[33m
endef
define RESET
\033[0m
endef

# ======== Targets ========
.PHONY: help
help:
	@echo "$(GREEN)Targets$(RESET)"
	@echo "  make build        - Build image"
	@echo "  make run          - Run container (pulls MODEL on start via entrypoint)"
	@echo "  make up           - build + run"
	@echo "  make logs         - Tail container logs"
	@echo "  make shell        - Shell into the container"
	@echo "  make stop         - Stop container"
	@echo "  make down         - Stop and remove container"
	@echo "  make clean        - Remove container and image"
	@echo "  make restart      - Restart container"
	@echo "  make pull-model   - Manually pull $(MODEL) inside container"
	@echo "  make test         - Full sanity test: pull, list, and simple generate"

# Build the custom image
.PHONY: build
build:
	@echo "$(GREEN)[build] Building $(IMAGE)$(RESET)"
	docker build -t $(IMAGE) .

# Run the container (auto-pulls MODEL on startup via entrypoint)
.PHONY: run
run:
	@echo "$(GREEN)[run] Starting container $(CONTAINER) on port $(PORT)$(RESET)"
	@docker rm -f $(CONTAINER) >/dev/null 2>&1 || true
	docker run -d --name $(CONTAINER) \
		--memory="2g" --cpus="2" \
		-p $(PORT):11434 \
		-v $(VOLUME):/root/.ollama \
		-e MODEL=$(MODEL) \
		-e OLLAMA_NUM_PARALLEL=1 \
		-e OLLAMA_KV_CACHE_TYPE=q4_0 \
		-e OLLAMA_NUM_CTX=2048 \
		-e OLLAMA_NUM_PREDICT=256 \
		-e OLLAMA_ORIGINS="*" \
		$$(if $(HTTP_PROXY), -e HTTP_PROXY="$(HTTP_PROXY)") \
		$$(if $(HTTPS_PROXY), -e HTTPS_PROXY="$(HTTPS_PROXY)") \
		$$(if $(NO_PROXY), -e NO_PROXY="$(NO_PROXY)") \
		$(IMAGE)

# Convenience: build + run
.PHONY: up
up: build run

.PHONY: logs
logs:
	docker logs -f $(CONTAINER)

.PHONY: shell
shell:
	docker exec -it $(CONTAINER) sh

.PHONY: stop
stop:
	-@docker stop $(CONTAINER) || true

.PHONY: down
down: stop
	-@docker rm $(CONTAINER) || true

.PHONY: clean
clean: down
	-@docker rmi $(IMAGE) || true

.PHONY: restart
restart: stop run

# Manually pull the model (useful if you ran without MODEL env)
.PHONY: pull-model
pull-model:
	@echo "$(GREEN)[pull-model] Pulling $(MODEL) inside container$(RESET)"
	docker exec -it $(CONTAINER) sh -lc 'ollama pull "$(MODEL)"'

# Full sanity test: pull, list models, simple generate
.PHONY: test
test:
	@echo "$(GREEN)[test] Pull (idempotent)$(RESET)"
	docker exec -it $(CONTAINER) sh -lc 'ollama pull "$(MODEL)" || true'

	@echo "$(GREEN)[test] List models$(RESET)"
	docker exec -it $(CONTAINER) sh -lc 'ollama list'

	curl -s http://localhost:$(PORT)/api/tags | jq .

	@echo "$(GREEN)[test] Generate$(RESET)"
	curl -s http://localhost:$(PORT)/api/generate -d "$$( \
		printf '{ \
		 "model": "%s", \
		 "prompt": "hello", \
		 "options": {"num_ctx": 2048, "num_predict": 64} \
		}' "$(MODEL)" \
	)" | jq -r '.response // .error'

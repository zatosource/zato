PROMETHEUS_PORT := 9090
LOKI_PORT := 3101
TEMPO_PORT := 3200

PROMETHEUS_DATA_DIR := ./data/prometheus
LOKI_DATA_DIR := ./data/loki
TEMPO_DATA_DIR := ./data/tempo

.PHONY: clean prometheus loki tempo test-server status

prometheus:
	@rm -rf $(PROMETHEUS_DATA_DIR)
	@mkdir -p $(PROMETHEUS_DATA_DIR)
	prometheus --config.file=./prometheus/prometheus.yml \
		--storage.tsdb.path=$(PROMETHEUS_DATA_DIR) \
		--web.listen-address=:$(PROMETHEUS_PORT) \
		--web.enable-lifecycle \
		--storage.tsdb.retention.time=1h

loki:
	@mkdir -p $(LOKI_DATA_DIR)
	loki --config.file=./loki/loki.yml

tempo:
	@mkdir -p $(TEMPO_DATA_DIR) $(TEMPO_DATA_DIR)/blocks $(TEMPO_DATA_DIR)/wal
	tempo --config.file=./tempo/tempo.yml

test-server:
	py test_server.py --port 8080

clean:
	@rm -rf ./data/* conf public

status:
	@ps aux | grep -E "(prometheus|loki|test_server)" | grep -v grep || echo "No services running"

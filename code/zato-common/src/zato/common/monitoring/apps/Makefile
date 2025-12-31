PROMETHEUS_PORT := 9090
GRAFANA_PORT := 3000
LOKI_PORT := 3101
TEMPO_PORT := 3200
GRAFANA_LOG_LEVEL := warn

PROMETHEUS_DATA_DIR := ./data/prometheus
GRAFANA_DATA_DIR := ./data/grafana
LOKI_DATA_DIR := ./data/loki
TEMPO_DATA_DIR := ./data/tempo

.PHONY: clean prometheus grafana loki tempo test-server dashboards status

prometheus:
	@rm -rf $(PROMETHEUS_DATA_DIR)
	@mkdir -p $(PROMETHEUS_DATA_DIR)
	prometheus --config.file=./prometheus/prometheus.yml \
		--storage.tsdb.path=$(PROMETHEUS_DATA_DIR) \
		--web.listen-address=:$(PROMETHEUS_PORT) \
		--web.enable-lifecycle \
		--storage.tsdb.retention.time=1h

grafana:
	@mkdir -p $(GRAFANA_DATA_DIR) $(GRAFANA_DATA_DIR)/logs $(GRAFANA_DATA_DIR)/plugins $(GRAFANA_DATA_DIR)/sessions
	@mkdir -p grafana/provisioning/dashboards grafana/provisioning/plugins grafana/provisioning/alerting
	GF_PATHS_DATA=$(PWD)/data/grafana GF_PATHS_LOGS=$(PWD)/data/grafana/logs GF_PATHS_PLUGINS=$(PWD)/data/grafana/plugins GF_PATHS_PROVISIONING=$(PWD)/grafana/provisioning GF_SERVER_HTTP_PORT=3000 GF_SECURITY_ADMIN_USER=admin GF_SECURITY_ADMIN_PASSWORD=admin GF_LOG_LEVEL=$(GRAFANA_LOG_LEVEL) GF_LOG_MODE="console file" /usr/sbin/grafana-server --homepath=/usr/share/grafana

loki:
	@mkdir -p $(LOKI_DATA_DIR)
	loki --config.file=./loki/loki.yml

tempo:
	@mkdir -p $(TEMPO_DATA_DIR) $(TEMPO_DATA_DIR)/blocks $(TEMPO_DATA_DIR)/wal
	tempo --config.file=./tempo/tempo.yml

test-server:
	py test_server.py --port 8080

dashboards:
	py grafana_.py

clean:
	@rm -rf ./data/* conf public

status:
	@ps aux | grep -E "(prometheus|grafana|loki|test_server)" | grep -v grep || echo "No services running"

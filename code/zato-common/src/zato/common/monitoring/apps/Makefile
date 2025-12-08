PROMETHEUS_PORT := 9090
GRAFANA_PORT := 3000
LOKI_PORT := 3101

PROMETHEUS_DATA_DIR := ./data/prometheus
GRAFANA_DATA_DIR := ./data/grafana
LOKI_DATA_DIR := ./data/loki

.PHONY: clean prometheus grafana loki test-server dashboards status

prometheus:
	@rm -rf $(PROMETHEUS_DATA_DIR)
	@mkdir -p $(PROMETHEUS_DATA_DIR)
	prometheus --config.file=./prometheus/prometheus.yml \
		--storage.tsdb.path=$(PROMETHEUS_DATA_DIR) \
		--web.listen-address=:$(PROMETHEUS_PORT) \
		--web.enable-lifecycle

grafana:
	@mkdir -p $(GRAFANA_DATA_DIR) $(GRAFANA_DATA_DIR)/logs $(GRAFANA_DATA_DIR)/plugins $(GRAFANA_DATA_DIR)/sessions
	GF_PATHS_DATA=$(PWD)/data/grafana GF_PATHS_LOGS=$(PWD)/data/grafana/logs GF_PATHS_PLUGINS=$(PWD)/data/grafana/plugins GF_PATHS_PROVISIONING=$(PWD)/grafana/provisioning GF_SERVER_HTTP_PORT=3000 GF_SECURITY_ADMIN_USER=admin GF_SECURITY_ADMIN_PASSWORD=admin GF_LOG_LEVEL=debug GF_LOG_MODE="console file" GF_LOG_CONSOLE_FORMAT=json /usr/sbin/grafana-server --homepath=/usr/share/grafana

loki:
	@mkdir -p $(LOKI_DATA_DIR)
	loki --config.file=./loki/loki.yml

test-server:
	py test_server.py --port 8080

dashboards:
	py grafana_.py

clean:
	@rm -rf ./data/* conf public

status:
	@ps aux | grep -E "(prometheus|grafana|loki|test_server)" | grep -v grep || echo "No services running"

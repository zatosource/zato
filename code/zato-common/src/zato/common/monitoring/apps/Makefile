PROMETHEUS_PORT := 9090
GRAFANA_PORT := 3000
LOKI_PORT := 3100

PROMETHEUS_DATA_DIR := ./data/prometheus
GRAFANA_DATA_DIR := ./data/grafana
LOKI_DATA_DIR := ./data/loki

.PHONY: clean prometheus grafana loki status

prometheus:
	@mkdir -p $(PROMETHEUS_DATA_DIR)
	prometheus --config.file=./prometheus/prometheus.yml \
		--storage.tsdb.path=$(PROMETHEUS_DATA_DIR) \
		--web.listen-address=:$(PROMETHEUS_PORT) \
		--web.enable-lifecycle

grafana:
	@mkdir -p $(GRAFANA_DATA_DIR) $(GRAFANA_DATA_DIR)/logs $(GRAFANA_DATA_DIR)/plugins $(GRAFANA_DATA_DIR)/sessions
	@mkdir -p conf public/emails public/app/plugins/datasource public/app/plugins/panel
	@[ -f conf/defaults.ini ] || cp /usr/share/grafana/conf/defaults.ini conf/
	@touch public/emails/template.html public/emails/template.txt
	grafana-server --config=grafana/grafana.ini --homepath=.

loki:
	@mkdir -p $(LOKI_DATA_DIR)
	loki --config.file=./loki/loki.yml

clean:
	@rm -rf ./data/* conf public

status:
	@ps aux | grep -E "(prometheus|grafana|loki)" | grep -v grep || echo "No services running"

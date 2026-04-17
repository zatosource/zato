use std::collections::HashMap;
use std::sync::RwLock;

use pyo3::prelude::*;

use crate::model::*;
use super::store::ConfigStore;
use super::util::lock_err;

fn load_into<T>(
    store: &RwLock<HashMap<String, T>>,
    items: Vec<T>,
    key_fn: impl Fn(&T) -> String,
) -> PyResult<()> {
    let mut guard = store.write().map_err(lock_err)?;
    for item in items {
        let k = key_fn(&item);
        guard.insert(k, item);
    }
    Ok(())
}

#[pymethods]
impl ConfigStore {

    #[pyo3(signature = (path,))]
    fn load_yaml(&self, py: Python<'_>, path: &str) -> PyResult<()> {
        let contents = std::fs::read_to_string(path)
            .map_err(|e| pyo3::exceptions::PyIOError::new_err(format!("{}: {}", path, e)))?;
        let config: EnmasseConfig = serde_yaml::from_str(&contents)
            .map_err(|e| pyo3::exceptions::PyValueError::new_err(format!("YAML parse: {}", e)))?;
        self.apply_enmasse_config(py, config)
    }

    #[pyo3(signature = (yaml_str,))]
    fn load_yaml_string(&self, py: Python<'_>, yaml_str: &str) -> PyResult<()> {
        let config: EnmasseConfig = serde_yaml::from_str(yaml_str)
            .map_err(|e| pyo3::exceptions::PyValueError::new_err(format!("YAML parse: {}", e)))?;
        self.apply_enmasse_config(py, config)
    }
}

impl ConfigStore {

    fn apply_enmasse_config(&self, _py: Python<'_>, config: EnmasseConfig) -> PyResult<()> {

        {
            let mut store = self.security.write().map_err(lock_err)?;
            for sec in config.security {
                store.insert(sec.name().to_string(), sec);
            }
        }

        load_into(&self.groups, config.groups, |g| g.name.clone())?;
        load_into(&self.channel_rest, config.channel_rest, |c| c.name.clone())?;
        load_into(&self.outgoing_rest, config.outgoing_rest, |o| o.name.clone())?;

        {
            let mut store = self.outgoing_soap.write().map_err(lock_err)?;
            for out in config.outgoing_soap {
                store.insert(out.name.clone(), out);
            }
            for out in config.outgoing_soap_alias {
                store.insert(out.name.clone(), out);
            }
        }

        load_into(&self.scheduler, config.scheduler, |j| j.name.clone())?;
        load_into(&self.holiday_calendar, config.holiday_calendar, |c| c.name.clone())?;
        load_into(&self.outgoing_sql, config.sql, |s| s.name.clone())?;

        {
            let mut store = self.generic_connection.write().map_err(lock_err)?;

            let mut insert_with_type = |mut conn: GenericConnection, default_type: &str| {
                if conn.type_.is_empty() {
                    conn.type_ = default_type.to_string();
                }
                store.insert(conn.name.clone(), conn);
            };

            for conn in config.ldap {
                insert_with_type(conn, "outconn-ldap");
            }
            for conn in config.confluence {
                insert_with_type(conn, "cloud-confluence");
            }
            for conn in config.jira {
                insert_with_type(conn, "cloud-jira");
            }
            for conn in config.microsoft_365 {
                insert_with_type(conn, "cloud-microsoft-365");
            }
            for conn in config.zato_generic_connection {
                store.insert(conn.name.clone(), conn);
            }
        }

        load_into(&self.cache_builtin, config.cache, |c| c.name.clone())?;
        load_into(&self.email_smtp, config.email_smtp, |e| e.name.clone())?;
        load_into(&self.email_imap, config.email_imap, |e| e.name.clone())?;
        load_into(&self.outgoing_odoo, config.odoo, |o| o.name.clone())?;
        load_into(&self.elastic_search, config.elastic_search, |e| e.name.clone())?;
        load_into(&self.pubsub_topic, config.pubsub_topic, |t| t.name.clone())?;
        load_into(&self.pubsub_permission, config.pubsub_permission, |p| p.id.clone())?;
        load_into(&self.pubsub_subscription, config.pubsub_subscription, |s| s.id.clone())?;
        load_into(&self.channel_openapi, config.channel_openapi, |c| c.name.clone())?;

        Ok(())
    }
}

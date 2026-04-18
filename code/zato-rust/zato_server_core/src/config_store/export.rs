use pyo3::prelude::*;
use pyo3::types::{PyDict, PyList};

use super::store::ConfigStore;
use super::util::{struct_to_pydict, lock_err};

#[pymethods]
impl ConfigStore {

    #[pyo3(signature = ())]
    fn export_to_dict<'py>(&self, py: Python<'py>) -> PyResult<Py<PyDict>> {
        let out = PyDict::new(py);

        macro_rules! export_section {
            ($key:expr, $field:ident) => {{
                let store = self.$field.read().map_err(lock_err)?;
                if !store.is_empty() {
                    let list = PyList::empty(py);
                    for item in store.values() {
                        let d = struct_to_pydict(py, item)?;
                        let _ = list.append(d.bind(py));
                    }
                    let _ = out.set_item($key, list);
                }
            }};
        }

        export_section!("security", security);
        export_section!("groups", groups);
        export_section!("channel_rest", channel_rest);
        export_section!("outgoing_rest", outgoing_rest);
        export_section!("outgoing_soap", outgoing_soap);
        export_section!("scheduler", scheduler);
        export_section!("holiday_calendar", holiday_calendar);
        export_section!("sql", outgoing_sql);
        export_section!("cache", cache_builtin);
        export_section!("email_smtp", email_smtp);
        export_section!("email_imap", email_imap);
        export_section!("odoo", outgoing_odoo);
        export_section!("elastic_search", elastic_search);
        export_section!("pubsub_topic", pubsub_topic);

        {
            let store = self.pubsub_permission.read().map_err(lock_err)?;
            if !store.is_empty() {
                let list = PyList::empty(py);
                for item in store.values() {
                    let d = struct_to_pydict(py, item)?;
                    let bound = d.bind(py);
                    if let Some(val) = bound.get_item("pub_topics")? {
                        let _ = bound.del_item("pub_topics");
                        let _ = bound.set_item("pub", val);
                    }
                    if let Some(val) = bound.get_item("sub_topics")? {
                        let _ = bound.del_item("sub_topics");
                        let _ = bound.set_item("sub", val);
                    }
                    let _ = list.append(bound);
                }
                let _ = out.set_item("pubsub_permission", list);
            }
        }

        export_section!("pubsub_subscription", pubsub_subscription);
        export_section!("channel_openapi", channel_openapi);

        {
            let store = self.generic_connection.read().map_err(lock_err)?;
            let type_map: &[(&str, &str)] = &[
                ("ldap", "outconn-ldap"),
                ("confluence", "cloud-confluence"),
                ("jira", "cloud-jira"),
                ("microsoft_365", "cloud-microsoft-365"),
            ];
            for &(section_key, type_prefix) in type_map {
                let list = PyList::empty(py);
                let mut has_items = false;
                for item in store.values() {
                    if item.type_ == type_prefix {
                        let d = struct_to_pydict(py, item)?;
                        let _ = list.append(d.bind(py));
                        has_items = true;
                    }
                }
                if has_items {
                    let _ = out.set_item(section_key, list);
                }
            }
        }

        Ok(out.unbind())
    }

    fn get_scheduler_jobs_json(&self) -> PyResult<String> {
        let store = self.scheduler.read().map_err(lock_err)?;
        Ok(serde_json::to_string(&*store).unwrap_or_else(|_| "{}".to_string()))
    }

    fn get_holiday_calendars_json(&self) -> PyResult<String> {
        let store = self.holiday_calendar.read().map_err(lock_err)?;
        Ok(serde_json::to_string(&*store).unwrap_or_else(|_| "{}".to_string()))
    }
}

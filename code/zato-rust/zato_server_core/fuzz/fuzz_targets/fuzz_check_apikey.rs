#![no_main]
use libfuzzer_sys::fuzz_target;
use zato_server_core::config_store::ConfigStore;
use zato_server_core::model::{SecurityDef, ApiKeyDef};

fuzz_target!(|data: &[u8]| {
    let header_value = String::from_utf8_lossy(data).to_string();

    let cs = ConfigStore::default();
    cs.set_security_direct("ak1", SecurityDef::ApiKey(ApiKeyDef {
        id: "id-ak1".to_string(),
        name: "ak1".to_string(),
        is_active: true,
        username: String::new(),
        password: "testkey".to_string(),
    })).unwrap();

    let _ = cs.check_apikey_inner(&header_value);
});

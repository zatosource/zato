#![no_main]
use libfuzzer_sys::fuzz_target;
use zato_server_core::config_store::ConfigStore;
use zato_server_core::model::{SecurityDef, BasicAuthDef};

fuzz_target!(|data: &[u8]| {
    if data.len() < 2 {
        return;
    }
    let split = data[0] as usize % data.len().max(1);
    let username = String::from_utf8_lossy(&data[1..=split.min(data.len() - 1)]).to_string();
    let password = String::from_utf8_lossy(&data[split.min(data.len() - 1)..]).to_string();

    let cs = ConfigStore::default();
    cs.set_security_direct("ba1", SecurityDef::BasicAuth(BasicAuthDef {
        id: "id-ba1".to_string(),
        name: "ba1".to_string(),
        is_active: true,
        username: "testuser".to_string(),
        password: "testpass".to_string(),
        realm: String::new(),
    })).unwrap();

    let _ = cs.check_basic_auth_inner(&username, &password);
});

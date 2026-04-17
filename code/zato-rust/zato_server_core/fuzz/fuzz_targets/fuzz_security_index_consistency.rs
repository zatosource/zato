#![no_main]
use libfuzzer_sys::fuzz_target;
use zato_server_core::config_store::ConfigStore;
use zato_server_core::model::{SecurityDef, BasicAuthDef, ApiKeyDef};

fuzz_target!(|data: &[u8]| {
    let cs = ConfigStore::default();

    for chunk in data.chunks(4) {
        if chunk.is_empty() {
            continue;
        }
        let op = chunk[0] % 3;
        let name_byte = if chunk.len() > 1 { chunk[1] % 8 } else { 0 };
        let name = format!("s{name_byte}");
        let val_byte = if chunk.len() > 2 { chunk[2] } else { 0 };
        let val = format!("v{val_byte}");

        match op {
            0 => {
                let sec = SecurityDef::BasicAuth(BasicAuthDef {
                    id: format!("id-{name}"),
                    name: name.clone(),
                    is_active: true,
                    username: val,
                    password: "p".to_string(),
                    realm: String::new(),
                });
                let _ = cs.set_security_direct(&name, sec);
            }
            1 => {
                let sec = SecurityDef::ApiKey(ApiKeyDef {
                    id: format!("id-{name}"),
                    name: name.clone(),
                    is_active: true,
                    username: String::new(),
                    password: val,
                });
                let _ = cs.set_security_direct(&name, sec);
            }
            _ => {
                let _ = cs.delete_security_direct(&name);
            }
        }

        let idx_user = cs.get_username_index_snapshot().unwrap();
        let idx_key = cs.get_apikey_index_snapshot().unwrap();
        let store = cs.get_security_snapshot().unwrap();

        for (username, sec_name) in &idx_user {
            let sec = store.get(sec_name).expect("dangling username index entry");
            if let SecurityDef::BasicAuth(d) = sec {
                assert_eq!(&d.username, username);
            } else {
                panic!("username index points to non-BasicAuth");
            }
        }

        for (key_val, sec_name) in &idx_key {
            let sec = store.get(sec_name).expect("dangling apikey index entry");
            if let SecurityDef::ApiKey(d) = sec {
                assert_eq!(&d.password, key_val);
            } else {
                panic!("apikey index points to non-ApiKey");
            }
        }
    }
});

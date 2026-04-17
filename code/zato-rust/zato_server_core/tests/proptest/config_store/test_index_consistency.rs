use proptest::prelude::*;
use zato_server_core::config_store::ConfigStore;
use zato_server_core::model::{SecurityDef, BasicAuthDef, ApiKeyDef};

#[derive(Debug, Clone)]
enum Op {
    SetBasicAuth { name: String, username: String },
    SetApiKey { name: String, key_value: String },
    Delete { name: String },
}

fn arb_op() -> impl Strategy<Value = Op> {
    prop_oneof![
        ("[a-z]{1,8}", "[a-zA-Z0-9]{1,16}").prop_map(|(name, username)| Op::SetBasicAuth { name, username }),
        ("[a-z]{1,8}", "[a-zA-Z0-9]{1,16}").prop_map(|(name, key_value)| Op::SetApiKey { name, key_value }),
        "[a-z]{1,8}".prop_map(|name| Op::Delete { name }),
    ]
}

fn verify_index_consistent(cs: &ConfigStore) {
    let idx_user = cs.get_username_index_snapshot().unwrap();
    let idx_key = cs.get_apikey_index_snapshot().unwrap();
    let store = cs.get_security_snapshot().unwrap();

    // Every username index entry must point to a valid BasicAuth def with that username
    for (username, sec_name) in &idx_user {
        let sec = store.get(sec_name).unwrap_or_else(|| panic!("index points to missing def: {sec_name}"));
        match sec {
            SecurityDef::BasicAuth(d) => {
                assert_eq!(&d.username, username, "index username mismatch for {sec_name}");
            }
            _ => panic!("username index points to non-BasicAuth def: {sec_name}"),
        }
    }

    // Every BasicAuth def with a non-empty username must have an index entry
    for (name, sec) in &store {
        if let SecurityDef::BasicAuth(d) = sec {
            if !d.username.is_empty() {
                assert!(idx_user.contains_key(&d.username),
                    "BasicAuth {name} with username {:?} not in index", d.username);
            }
        }
    }

    // Every apikey index entry must point to a valid ApiKey def with that key value
    for (key_val, sec_name) in &idx_key {
        let sec = store.get(sec_name).unwrap_or_else(|| panic!("index points to missing def: {sec_name}"));
        match sec {
            SecurityDef::ApiKey(d) => {
                assert_eq!(&d.password, key_val, "index apikey mismatch for {sec_name}");
            }
            _ => panic!("apikey index points to non-ApiKey def: {sec_name}"),
        }
    }

    // Every ApiKey def with a non-empty password must have an index entry
    for (name, sec) in &store {
        if let SecurityDef::ApiKey(d) = sec {
            if !d.password.is_empty() {
                assert!(idx_key.contains_key(&d.password),
                    "ApiKey {name} with key {:?} not in index", d.password);
            }
        }
    }
}

proptest! {
    #[test]
    fn index_consistent_after_arbitrary_ops(ops in proptest::collection::vec(arb_op(), 1..100)) {
        let cs = ConfigStore::default();
        for op in &ops {
            match op {
                Op::SetBasicAuth { name, username } => {
                    let sec = SecurityDef::BasicAuth(BasicAuthDef {
                        id: format!("id-{name}"),
                        name: name.clone(),
                        is_active: true,
                        username: username.clone(),
                        password: "pass".to_string(),
                        realm: String::new(),
                    });
                    cs.set_security_direct(name, sec).unwrap();
                }
                Op::SetApiKey { name, key_value } => {
                    let sec = SecurityDef::ApiKey(ApiKeyDef {
                        id: format!("id-{name}"),
                        name: name.clone(),
                        is_active: true,
                        username: String::new(),
                        password: key_value.clone(),
                    });
                    cs.set_security_direct(name, sec).unwrap();
                }
                Op::Delete { name } => {
                    let _ = cs.delete_security_direct(name);
                }
            }
            verify_index_consistent(&cs);
        }
    }
}

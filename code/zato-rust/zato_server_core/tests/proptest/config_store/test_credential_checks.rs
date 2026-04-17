use proptest::prelude::*;
use zato_server_core::config_store::ConfigStore;
use zato_server_core::model::{SecurityDef, BasicAuthDef, ApiKeyDef};

fn arb_ba(name: &str, username: String, password: String) -> SecurityDef {
    SecurityDef::BasicAuth(BasicAuthDef {
        id: format!("id-{name}"),
        name: name.to_string(),
        is_active: true,
        username,
        password,
        realm: String::new(),
    })
}

fn arb_ak(name: &str, key_value: String) -> SecurityDef {
    SecurityDef::ApiKey(ApiKeyDef {
        id: format!("id-{name}"),
        name: name.to_string(),
        is_active: true,
        username: String::new(),
        password: key_value,
    })
}

proptest! {
    #[test]
    fn basic_auth_correct_creds_always_succeed(
        username in "[a-zA-Z0-9_]{1,64}",
        password in ".{0,256}",
    ) {
        let cs = ConfigStore::default();
        cs.set_security_direct("ba1", arb_ba("ba1", username.clone(), password.clone())).unwrap();
        let result = cs.check_basic_auth_inner(&username, &password).unwrap();
        prop_assert!(result.is_some(), "expected Some, got None for user={username:?} pass={password:?}");
    }

    #[test]
    fn basic_auth_wrong_password_always_fails(
        username in "[a-zA-Z0-9_]{1,64}",
        password in ".{1,256}",
        wrong in ".{1,256}",
    ) {
        prop_assume!(password != wrong);
        let cs = ConfigStore::default();
        cs.set_security_direct("ba1", arb_ba("ba1", username.clone(), password)).unwrap();
        let result = cs.check_basic_auth_inner(&username, &wrong).unwrap();
        prop_assert_eq!(result, None);
    }

    #[test]
    fn apikey_correct_key_always_succeeds(
        key_value in ".{1,256}",
    ) {
        let cs = ConfigStore::default();
        cs.set_security_direct("ak1", arb_ak("ak1", key_value.clone())).unwrap();
        let result = cs.check_apikey_inner(&key_value).unwrap();
        prop_assert!(result.is_some());
    }

    #[test]
    fn apikey_wrong_key_always_fails(
        key_value in ".{1,256}",
        wrong in ".{1,256}",
    ) {
        prop_assume!(key_value != wrong);
        let cs = ConfigStore::default();
        cs.set_security_direct("ak1", arb_ak("ak1", key_value)).unwrap();
        let result = cs.check_apikey_inner(&wrong).unwrap();
        prop_assert_eq!(result, None);
    }
}

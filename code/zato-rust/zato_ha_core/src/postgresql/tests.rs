// -*- coding: utf-8 -*-

// Copyright (C) 2026, Zato Source s.r.o. https://zato.io
// Licensed under AGPLv3, see LICENSE.txt for terms and conditions.

//! The tests of the database probe against a `PostgreSQL` test container.

use super::*;
use crate::test_support::LOOPBACK;
use std::process::Command;
use std::thread;
use std::time::Instant;

/// The image of the test container, which the live SQL tests of the Zato server use too.
const POSTGRESQL_IMAGE: &str = "postgres:16";

/// The port of `PostgreSQL` inside the container.
const POSTGRESQL_PORT: &str = "5432/tcp";

/// The password of the test container.
const PASSWORD: &str = "Test password";

/// The user name and the database name of the test container.
const USERNAME: &str = "zato";

/// How long the container may take to accept connections.
const STARTUP_TIMEOUT: Duration = Duration::from_mins(1);

/// How long to wait between two checks of the container.
const STARTUP_POLL: Duration = Duration::from_millis(250);

/// A port on the loopback that nothing listens on.
const CLOSED_PORT: u16 = 1;

/// The table of the generation guard with its one row, as the Zato server creates it.
const CREATE_GUARD: &str = "CREATE TABLE pubsub_active (id INTEGER PRIMARY KEY, generation BIGINT NOT NULL, owner TEXT NOT NULL);
    INSERT INTO pubsub_active (id, generation, owner) VALUES (1, 1, 'zato-a')";

/// A `PostgreSQL` server in a container removed on drop.
struct PostgreSqlContainer {
    /// The name of the container.
    name: String,

    /// The port of `PostgreSQL` on the host.
    port: u16,
}

impl PostgreSqlContainer {
    /// Starts the container and waits until it accepts connections.
    fn start() -> Self {
        let name = format!("zato-ha-probe-test-{}", std::process::id());
        let publish = format!("{LOOPBACK}::5432");
        let password = format!("POSTGRES_PASSWORD={PASSWORD}");
        let user = format!("POSTGRES_USER={USERNAME}");
        docker(&[
            "run",
            "--detach",
            "--rm",
            "--name",
            &name,
            "--publish",
            &publish,
            "--env",
            &password,
            "--env",
            &user,
            POSTGRESQL_IMAGE,
        ]);
        let mapping = docker(&["port", &name, POSTGRESQL_PORT]);
        let port = mapping.lines().next().unwrap().trim().rsplit(':').next().unwrap().parse().unwrap();
        let container = Self { name, port };
        container.wait_until_ready();
        container
    }

    /// Waits until the server accepts connections over TCP, which it does only after its initialization.
    fn wait_until_ready(&self) {
        let deadline = Instant::now() + STARTUP_TIMEOUT;
        while Instant::now() < deadline {
            let ready = Command::new("docker")
                .args(["exec", &self.name, "pg_isready", "--host", LOOPBACK, "--username", USERNAME])
                .output()
                .unwrap();
            if ready.status.success() {
                return;
            }
            thread::sleep(STARTUP_POLL);
        }
        panic!("PostgreSQL in {} did not accept connections within {STARTUP_TIMEOUT:?}", self.name);
    }

    /// Runs SQL statements in the database of the tests.
    fn execute(&self, statements: &str) {
        docker(&["exec", &self.name, "psql", "--username", USERNAME, "--command", statements]);
    }

    /// Returns the settings of the database of the tests.
    fn settings(&self) -> PostgreSqlConfig {
        settings(self.port)
    }
}

impl Drop for PostgreSqlContainer {
    fn drop(&mut self) {
        let _ = Command::new("docker").args(["rm", "--force", &self.name]).output();
    }
}

/// Runs the `docker` command and returns its standard output, failing the test if it fails.
fn docker(args: &[&str]) -> String {
    let output = Command::new("docker").args(args).output().unwrap();
    assert!(
        output.status.success(),
        "docker {}: {}",
        args.join(" "),
        String::from_utf8_lossy(&output.stderr)
    );
    String::from_utf8(output.stdout).unwrap()
}

/// Returns the settings of a database of the tests on the loopback at `port`.
fn settings(port: u16) -> PostgreSqlConfig {
    PostgreSqlConfig {
        host: LOOPBACK.to_owned(),
        port,
        username: USERNAME.to_owned(),
        password: PostgreSqlPassword::Value(PASSWORD.to_owned()),
        database: USERNAME.to_owned(),
        tls: None,
    }
}

#[test]
fn the_probe_succeeds_only_while_the_generation_guard_is_reachable() {
    let container = PostgreSqlContainer::start();
    let probe = PostgreSqlProbe::new(&container.settings()).unwrap();

    // A database in which no Zato server created the generation guard yet fails the probe ..
    assert!(probe.probe().is_err());

    // .. a database with the generation guard passes it ..
    container.execute(CREATE_GUARD);
    probe.probe().unwrap();
    probe.probe().unwrap();

    // .. and a database that does not answer fails it within the request timeout.
    docker(&["pause", &container.name]);
    let started = Instant::now();
    assert!(probe.probe().is_err());
    assert!(started.elapsed() < REQUEST_TIMEOUT + STARTUP_POLL);
    docker(&["unpause", &container.name]);
    probe.probe().unwrap();
}

#[test]
fn a_database_that_does_not_answer_is_an_error() {
    let probe = PostgreSqlProbe::new(&settings(CLOSED_PORT)).unwrap();
    assert!(probe.probe().is_err());
}

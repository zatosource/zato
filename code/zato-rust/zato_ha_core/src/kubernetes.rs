// -*- coding: utf-8 -*-

// Copyright (C) 2026, Zato Source s.r.o. https://zato.io
// Licensed under AGPLv3, see LICENSE.txt for terms and conditions.

//! The Kubernetes API server as the referee of the pair and as the target of the role label of the active pod.

pub mod client;
pub mod label;
pub mod lease;

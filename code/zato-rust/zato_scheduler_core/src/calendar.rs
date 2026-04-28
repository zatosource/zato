// -*- coding: utf-8 -*-

// Copyright (C) 2026, Zato Source s.r.o. https://zato.io
// Licensed under AGPLv3, see LICENSE.txt for terms and conditions.

use std::collections::HashSet;

use chrono::{Datelike, NaiveDate};
use serde::Serialize;

/// Holds calendar exclusion data - specific dates and weekdays that should be skipped.
#[derive(Debug, Clone, Serialize)]
pub struct CalendarData {
    /// Human-readable name of the calendar.
    pub name: String,
    /// Set of specific dates to exclude.
    pub dates: HashSet<NaiveDate>,
    /// Weekday numbers to exclude (0 = Monday, 6 = Sunday).
    pub weekdays: Vec<u8>,
    /// Optional description of the calendar.
    pub description: Option<String>,
}

impl CalendarData {
    /// Creates a new calendar with the given name and no exclusions.
    #[must_use]
    pub fn new(name: String) -> Self {
        Self {
            name,
            dates: HashSet::new(),
            weekdays: Vec::new(),
            description: None,
        }
    }

    /// Returns `true` if the given date is excluded by this calendar,
    /// either by an explicit date entry or by weekday.
    #[must_use]
    pub fn is_excluded(&self, date: NaiveDate) -> bool {
        if self.dates.contains(&date) {
            return true;
        }
        u8::try_from(date.weekday().num_days_from_monday()).is_ok_and(|weekday_num| self.weekdays.contains(&weekday_num))
    }
}

#[cfg(test)]
mod tests {
    use super::*;

    /// Error type alias for test results.
    type TestResult = Result<(), Box<dyn std::error::Error>>;

    #[test]
    fn test_date_exclusion() -> TestResult {
        let mut cal = CalendarData::new("test".into());
        let christmas = NaiveDate::from_ymd_opt(2026, 12, 25).ok_or("invalid date: 2026-12-25")?;
        cal.dates.insert(christmas);
        assert!(cal.is_excluded(christmas));
        let day_after = NaiveDate::from_ymd_opt(2026, 12, 26).ok_or("invalid date: 2026-12-26")?;
        assert!(!cal.is_excluded(day_after));
        Ok(())
    }

    #[test]
    fn test_weekday_exclusion() -> TestResult {
        let mut cal = CalendarData::new("test".into());
        cal.weekdays.push(5); // Saturday
        cal.weekdays.push(6); // Sunday
        let sat = NaiveDate::from_ymd_opt(2026, 4, 11).ok_or("invalid date: 2026-04-11")?;
        let sun = NaiveDate::from_ymd_opt(2026, 4, 12).ok_or("invalid date: 2026-04-12")?;
        let mon = NaiveDate::from_ymd_opt(2026, 4, 13).ok_or("invalid date: 2026-04-13")?;
        assert!(cal.is_excluded(sat));
        assert!(cal.is_excluded(sun));
        assert!(!cal.is_excluded(mon));
        Ok(())
    }
}

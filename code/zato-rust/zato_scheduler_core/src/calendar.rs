use std::collections::HashSet;

use chrono::{Datelike, NaiveDate};

#[derive(Debug, Clone)]
pub struct CalendarData {
    pub name: String,
    pub dates: HashSet<NaiveDate>,
    pub weekdays: Vec<u8>,
    pub description: Option<String>,
}

impl CalendarData {
    pub fn new(name: String) -> Self {
        CalendarData {
            name,
            dates: HashSet::new(),
            weekdays: Vec::new(),
            description: None,
        }
    }

    pub fn is_excluded(&self, date: NaiveDate) -> bool {
        if self.dates.contains(&date) {
            return true;
        }
        let wd = date.weekday().num_days_from_monday() as u8;
        self.weekdays.contains(&wd)
    }
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn test_date_exclusion() {
        let mut cal = CalendarData::new("test".into());
        let d = NaiveDate::from_ymd_opt(2026, 12, 25).unwrap();
        cal.dates.insert(d);
        assert!(cal.is_excluded(d));
        assert!(!cal.is_excluded(NaiveDate::from_ymd_opt(2026, 12, 26).unwrap()));
    }

    #[test]
    fn test_weekday_exclusion() {
        let mut cal = CalendarData::new("test".into());
        cal.weekdays.push(5); // Saturday
        cal.weekdays.push(6); // Sunday
        let sat = NaiveDate::from_ymd_opt(2026, 4, 11).unwrap(); // Saturday
        let sun = NaiveDate::from_ymd_opt(2026, 4, 12).unwrap(); // Sunday
        let mon = NaiveDate::from_ymd_opt(2026, 4, 13).unwrap(); // Monday
        assert!(cal.is_excluded(sat));
        assert!(cal.is_excluded(sun));
        assert!(!cal.is_excluded(mon));
    }
}

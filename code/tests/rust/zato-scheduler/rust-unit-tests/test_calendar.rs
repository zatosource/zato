use chrono::NaiveDate;

use zato_scheduler_core::calendar::CalendarData;

#[test]
fn test_empty_calendar_excludes_nothing() {
    let cal = CalendarData::new("empty".into());
    let d = NaiveDate::from_ymd_opt(2026, 6, 15).unwrap();
    assert!(!cal.is_excluded(d));
}

#[test]
fn test_specific_date_exclusion() {
    let mut cal = CalendarData::new("christmas".into());
    cal.dates.insert(NaiveDate::from_ymd_opt(2026, 12, 25).unwrap());

    assert!(cal.is_excluded(NaiveDate::from_ymd_opt(2026, 12, 25).unwrap()));
    assert!(!cal.is_excluded(NaiveDate::from_ymd_opt(2026, 12, 24).unwrap()));
    assert!(!cal.is_excluded(NaiveDate::from_ymd_opt(2026, 12, 26).unwrap()));
}

#[test]
fn test_multiple_dates_exclusion() {
    let mut cal = CalendarData::new("us-holidays".into());
    cal.dates.insert(NaiveDate::from_ymd_opt(2026, 1, 1).unwrap());
    cal.dates.insert(NaiveDate::from_ymd_opt(2026, 7, 4).unwrap());
    cal.dates.insert(NaiveDate::from_ymd_opt(2026, 12, 25).unwrap());

    assert!(cal.is_excluded(NaiveDate::from_ymd_opt(2026, 1, 1).unwrap()));
    assert!(cal.is_excluded(NaiveDate::from_ymd_opt(2026, 7, 4).unwrap()));
    assert!(cal.is_excluded(NaiveDate::from_ymd_opt(2026, 12, 25).unwrap()));
    assert!(!cal.is_excluded(NaiveDate::from_ymd_opt(2026, 3, 15).unwrap()));
}

#[test]
fn test_weekday_exclusion_saturday_sunday() {
    let mut cal = CalendarData::new("weekends".into());
    cal.weekdays.push(5); // Saturday
    cal.weekdays.push(6); // Sunday

    // 2026-04-11 is Saturday, 2026-04-12 is Sunday, 2026-04-13 is Monday
    assert!(cal.is_excluded(NaiveDate::from_ymd_opt(2026, 4, 11).unwrap()));
    assert!(cal.is_excluded(NaiveDate::from_ymd_opt(2026, 4, 12).unwrap()));
    assert!(!cal.is_excluded(NaiveDate::from_ymd_opt(2026, 4, 13).unwrap()));
    assert!(!cal.is_excluded(NaiveDate::from_ymd_opt(2026, 4, 14).unwrap()));
    assert!(!cal.is_excluded(NaiveDate::from_ymd_opt(2026, 4, 15).unwrap()));
}

#[test]
fn test_weekday_exclusion_monday_wednesday_friday() {
    let mut cal = CalendarData::new("mwf".into());
    cal.weekdays.push(0); // Monday
    cal.weekdays.push(2); // Wednesday
    cal.weekdays.push(4); // Friday

    // 2026-04-13=Mon, 14=Tue, 15=Wed, 16=Thu, 17=Fri
    assert!(cal.is_excluded(NaiveDate::from_ymd_opt(2026, 4, 13).unwrap()));
    assert!(!cal.is_excluded(NaiveDate::from_ymd_opt(2026, 4, 14).unwrap()));
    assert!(cal.is_excluded(NaiveDate::from_ymd_opt(2026, 4, 15).unwrap()));
    assert!(!cal.is_excluded(NaiveDate::from_ymd_opt(2026, 4, 16).unwrap()));
    assert!(cal.is_excluded(NaiveDate::from_ymd_opt(2026, 4, 17).unwrap()));
}

#[test]
fn test_combined_dates_and_weekdays() {
    let mut cal = CalendarData::new("combined".into());
    cal.weekdays.push(5); // Saturday
    cal.weekdays.push(6); // Sunday
    cal.dates.insert(NaiveDate::from_ymd_opt(2026, 4, 15).unwrap()); // Wednesday

    // Wednesday is excluded by date
    assert!(cal.is_excluded(NaiveDate::from_ymd_opt(2026, 4, 15).unwrap()));
    // Saturday excluded by weekday
    assert!(cal.is_excluded(NaiveDate::from_ymd_opt(2026, 4, 11).unwrap()));
    // Thursday not excluded
    assert!(!cal.is_excluded(NaiveDate::from_ymd_opt(2026, 4, 16).unwrap()));
}

#[test]
fn test_same_date_different_years() {
    let mut cal = CalendarData::new("yearly".into());
    cal.dates.insert(NaiveDate::from_ymd_opt(2026, 12, 25).unwrap());

    assert!(cal.is_excluded(NaiveDate::from_ymd_opt(2026, 12, 25).unwrap()));
    assert!(!cal.is_excluded(NaiveDate::from_ymd_opt(2027, 12, 25).unwrap()));
}

#[test]
fn test_leap_year_date() {
    let mut cal = CalendarData::new("leap".into());
    cal.dates.insert(NaiveDate::from_ymd_opt(2028, 2, 29).unwrap());

    assert!(cal.is_excluded(NaiveDate::from_ymd_opt(2028, 2, 29).unwrap()));
    assert!(!cal.is_excluded(NaiveDate::from_ymd_opt(2028, 2, 28).unwrap()));
}

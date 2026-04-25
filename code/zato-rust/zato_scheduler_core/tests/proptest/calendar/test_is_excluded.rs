use proptest::prelude::*;
use proptest::collection::hash_set;
use chrono::NaiveDate;
use zato_scheduler_core::calendar::CalendarData;

fn arb_naive_date() -> impl Strategy<Value = NaiveDate> {
    (2000i32..2100, 1u32..13, 1u32..29).prop_filter_map(
        "year/month/day must form a valid date",
        |(year, month, day)| NaiveDate::from_ymd_opt(year, month, day),
    )
}

proptest! {

    #[test]
    fn empty_calendar_excludes_nothing(date in arb_naive_date()) {
        let cal = CalendarData::new("empty".into());
        prop_assert!(!cal.is_excluded(date));
    }

    #[test]
    fn date_in_set_is_excluded(
        dates in hash_set(arb_naive_date(), 1..10),
    ) {
        let mut cal = CalendarData::new("test".into());
        for date in &dates {
            cal.dates.insert(*date);
        }
        for date in &dates {
            prop_assert!(cal.is_excluded(*date));
        }
    }

    #[test]
    fn weekday_in_list_is_excluded(
        weekdays in hash_set(0u8..7, 1..4),
        date in arb_naive_date(),
    ) {
        use chrono::Datelike;
        let mut cal = CalendarData::new("test".into());
        cal.weekdays = weekdays.iter().copied().collect();
        let weekday_num = u8::try_from(date.weekday().num_days_from_monday()).unwrap();
        if weekdays.contains(&weekday_num) {
            prop_assert!(cal.is_excluded(date));
        }
    }

    #[test]
    fn full_weekday_set_excludes_everything(date in arb_naive_date()) {
        let mut cal = CalendarData::new("full".into());
        cal.weekdays = vec![0, 1, 2, 3, 4, 5, 6];
        prop_assert!(cal.is_excluded(date));
    }

    #[test]
    fn date_not_in_set_and_weekday_not_in_list(
        date in arb_naive_date(),
    ) {
        use chrono::Datelike;
        let mut cal = CalendarData::new("test".into());
        let other_date = NaiveDate::from_ymd_opt(1999, 1, 1).unwrap();
        cal.dates.insert(other_date);
        let weekday_num = u8::try_from(date.weekday().num_days_from_monday()).unwrap();
        let excluded_weekday = (weekday_num + 1) % 7;
        cal.weekdays = vec![excluded_weekday];
        if date != other_date && weekday_num != excluded_weekday {
            prop_assert!(!cal.is_excluded(date));
        }
    }
}

#![no_main]
use libfuzzer_sys::fuzz_target;
use chrono::NaiveDate;
use zato_scheduler_core::calendar::CalendarData;

fuzz_target!(|data: &[u8]| {
    if data.len() < 5 {
        return;
    }

    let year = 2000i32 + i32::from(data[0]) % 100;
    let month = u32::from(data[1]) % 12 + 1;
    let day = u32::from(data[2]) % 28 + 1;

    let Some(date) = NaiveDate::from_ymd_opt(year, month, day) else {
        return;
    };

    let mut cal = CalendarData::new("fuzz".into());

    for &b in &data[3..] {
        let wd = b % 7;
        if !cal.weekdays.contains(&wd) {
            cal.weekdays.push(wd);
        }
    }

    let _ = cal.is_excluded(date);
});

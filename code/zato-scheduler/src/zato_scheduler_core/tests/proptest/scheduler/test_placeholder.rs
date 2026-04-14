use proptest::prelude::*;

proptest! {

    #[test]
    fn placeholder(_n in 0u32..100) {
        prop_assert!(true);
    }
}

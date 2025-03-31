#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Script to generate performance test rule files with varying numbers of rules and conditions.
"""

# stdlib
import os
from pathlib import Path

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from zato.common.typing_ import any_, anydict, dict_, strdict, strlist

# ################################################################################################################################
# ################################################################################################################################

# Define the template for a rule
RULE_TEMPLATE = """
rule
    TELCO_BSS_{rule_num:03d}
docs
    {rule_description}
    Used for {rule_purpose} in the BSS system.
defaults
    {defaults}
when
{conditions}
then
{actions}
"""

# Define common conditions that can be reused across rules
COMMON_CONDITIONS = [
    'account_status == \'active\'',                      # Condition 001
    'customer_id =~ \'[A-Z]{{2}}\\d{{6}}\'',             # Condition 002
    'customer_type == \'business\'',                     # Condition 003
    'is_contract_signed == true',                        # Condition 004
    'monthly_spend > 500',                               # Condition 005
    'region in high_priority_regions',                   # Condition 006
    'service_level == \'premium\'',                      # Condition 007
    'subscription_months > min_subscription_months',     # Condition 008
    'usage_percentage > 75',                             # Condition 009
    'customer_segment == \'enterprise\'',                # Condition 010
]

# Define unique conditions that can be used to create variety
UNIQUE_CONDITIONS = [
    'support_tickets_open < 5',                        # Condition 101
    'usage_decline_months >= high_risk_threshold',     # Condition 102
    'upgrade_eligibility_score > 7',                   # Condition 103
    'peak_usage_percentage > capacity_threshold',      # Condition 104
    'outage_duration_minutes > min_outage_minutes',    # Condition 105
    'services_subscribed < 3',                         # Condition 106
    'equipment_age_months > 24',                       # Condition 107
    'current_platform in legacy_platforms',            # Condition 108
    'contract_end_days < 90',                          # Condition 109
    'customer_industry in iot_compatible_industries',  # Condition 110
    'billing_complaints > 0',                          # Condition 111
    'churn_prediction_score > 0.7',                    # Condition 112
    'bandwidth_utilization > 80',                      # Condition 113
    'credit_score > 700',                              # Condition 114
    'business_customers_affected > 50',                # Condition 115
    'network_segment_congestion == true',              # Condition 116
    'projected_growth_rate > 5',                       # Condition 117
    'business_impact_level > 2',                       # Condition 118
    'fault_responsibility == \'provider\'',            # Condition 119
    'sla_breach == true',                              # Condition 120
    'cross_sell_propensity > 0.6',                     # Condition 121
    'last_upsell_attempt_days > 90',                   # Condition 122
    'service_usage_complementary == true',             # Condition 123
    'hardware_compatibility_new_features == false',    # Condition 124
    'service_calls_equipment > 1',                     # Condition 125
    'has_custom_integrations == false',                # Condition 126
    'migration_complexity_score < 7',                  # Condition 127
    'competitive_pressure_score > 3',                  # Condition 128
    'customer_lifetime_value > 50000',                 # Condition 129
    'data_service_subscribed == true',                 # Condition 130
    'digital_transformation_score > 6',                # Condition 131
    'monthly_data_usage > 500',                        # Condition 132
    'technology_adoption_score > 7',                   # Condition 133
    'priority_support_eligible == true',               # Condition 134
    'critical_business_process == true',               # Condition 135
    'dedicated_support_eligible == true',              # Condition 136
    'satisfaction_score < 7',                          # Condition 137
    'retention_score < 6',                             # Condition 138
    'competitor_mentions_support > 0',                 # Condition 139
    'payment_method == \'auto\'',                      # Condition 140
    'growth_trajectory_positive == true',              # Condition 141
    'payment_history_months > 12',                     # Condition 142
    'customer_complaints_capacity > 10',               # Condition 143
    'last_upgrade_months > 12',                        # Condition 144
    'customer_reported_issue == true',                 # Condition 145
    'multiple_services_affected == true',              # Condition 146
    'service_affected == \'critical\'',                # Condition 147
    'customer_growth_phase == \'expansion\'',          # Condition 148
    'contract_remaining_months > 12',                  # Condition 149
    'current_equipment_model_discontinued == true',    # Condition 150
    'monthly_spend > 2000',                            # Condition 151
    'upgrade_program_eligible == true',                # Condition 152
    'platform_support_end_months < 12',                # Condition 153
    'service_compatibility_new_platform == true',      # Condition 154
    'technology_refresh_budget_approved == true',      # Condition 155
    'market_share_strategic_account == true',          # Condition 156
    'price_sensitivity_score > 7',                     # Condition 157
    'renewal_propensity_score < 0.7',                  # Condition 158
    'subscription_type in premium_subscription_types', # Condition 159
    'competitor_iot_mentions > 0',                     # Condition 160
    'iot_inquiries > 0',                               # Condition 161
]

# Define rule descriptions and purposes
RULE_DESCRIPTIONS = [
    "Determines if a customer is eligible for premium support based on subscription type and history.",
    "Identifies customers at risk of churn based on usage patterns and billing history.",
    "Determines eligibility for service upgrade offers based on usage patterns and account status.",
    "Identifies network capacity planning needs based on regional usage patterns.",
    "Determines billing adjustments for service outages based on SLA terms and outage impact.",
    "Identifies opportunities for service bundling based on customer usage patterns.",
    "Determines eligibility for early equipment upgrade based on account history and usage.",
    "Identifies customers for migration to new service platforms based on technology compatibility.",
    "Determines pricing adjustments for contract renewals based on customer value and market conditions.",
    "Identifies opportunities for IoT service expansion based on customer industry and usage patterns.",
    "Evaluates customer satisfaction metrics to trigger proactive outreach.",
    "Determines eligibility for special pricing based on competitive landscape.",
    "Identifies cross-selling opportunities based on current service utilization.",
    "Evaluates technical support escalation needs based on issue complexity.",
    "Determines promotional campaign targeting based on customer segments.",
    "Identifies potential network bottlenecks based on usage trends.",
    "Determines eligibility for beta program participation based on customer profile.",
    "Identifies opportunities for service plan optimization.",
    "Evaluates security compliance requirements based on customer industry.",
    "Determines data usage pattern anomalies for fraud detection.",
]

RULE_PURPOSES = [
    "prioritizing customer support tickets",
    "proactive retention campaigns",
    "targeted upselling",
    "infrastructure investment planning",
    "automated credit processing",
    "cross-selling campaigns",
    "hardware refresh programs",
    "technology transition planning",
    "retention and revenue management",
    "targeted IoT solution selling",
    "customer experience improvement",
    "competitive response management",
    "revenue optimization",
    "support resource allocation",
    "marketing campaign targeting",
    "capacity planning",
    "product development feedback",
    "customer cost optimization",
    "regulatory compliance management",
    "fraud prevention",
]

# Define default values that can be used in rules
DEFAULT_VALUES = [
    "min_subscription_months = 6\n    premium_subscription_types = ['platinum', 'gold', 'enterprise']\n    high_priority_regions = ['EMEA', 'APAC', 'NA']",
    "high_risk_threshold = 3\n    premium_subscription_types = ['platinum', 'gold', 'enterprise']\n    min_subscription_months = 6",
    "capacity_threshold = 75\n    high_priority_regions = ['EMEA', 'APAC', 'NA']",
    "min_outage_minutes = 30\n    premium_subscription_types = ['platinum', 'gold', 'enterprise']",
    "min_subscription_months = 6\n    high_priority_regions = ['EMEA', 'APAC', 'NA']",
    "premium_subscription_types = ['platinum', 'gold', 'enterprise']\n    min_subscription_months = 6",
    "high_priority_regions = ['EMEA', 'APAC', 'NA']\n    legacy_platforms = ['TDM', 'PSTN', 'ISDN']",
    "premium_subscription_types = ['platinum', 'gold', 'enterprise']\n    high_priority_regions = ['EMEA', 'APAC', 'NA']\n    min_subscription_months = 6",
    "iot_compatible_industries = ['manufacturing', 'healthcare', 'logistics', 'retail', 'utilities']\n    high_priority_regions = ['EMEA', 'APAC', 'NA']",
    "support_tiers = ['standard', 'premium', 'platinum']\n    response_time_thresholds = {'standard': 24, 'premium': 8, 'platinum': 4}",
]

# Define actions that can be used in rules
ACTIONS = [
    "support_priority = 'high'\n    response_time_hours = 2\n    dedicated_agent = true",
    "churn_risk = 'high'\n    retention_action = 'executive_outreach'\n    offer_discount = 15",
    "upgrade_offer = 'bandwidth_increase'\n    discount_percentage = 10\n    offer_duration_months = 6",
    "capacity_planning_priority = 'high'\n    budget_allocation_percentage = 15\n    implementation_timeline_months = 3",
    "credit_percentage = 15\n    apology_communication = true\n    follow_up_survey = true",
    "bundle_offer = 'voice_data_cloud'\n    discount_percentage = 12\n    promotion_duration_months = 12",
    "equipment_upgrade_offer = true\n    upgrade_fee_discount = 50\n    contract_extension_months = 12",
    "migration_priority = 'high'\n    incentive_offer = 'free_installation'\n    dedicated_migration_support = true",
    "renewal_discount_percentage = 8\n    extended_payment_terms = true\n    value_added_services_free = 2",
    "iot_solution_offer = 'industry_specific'\n    pilot_program_eligible = true\n    consultation_scheduling = 'priority'",
    "customer_outreach = 'proactive'\n    satisfaction_survey = true\n    special_offer = 'loyalty_discount'",
    "competitive_response = 'price_match'\n    sales_team_notification = true\n    executive_briefing = true",
    "cross_sell_package = 'complementary_services'\n    marketing_campaign = 'targeted'\n    discount_offer = 10",
    "support_escalation = true\n    specialist_assignment = 'immediate'\n    case_priority = 'high'",
    "campaign_inclusion = true\n    personalized_messaging = true\n    offer_type = 'segment_specific'",
    "network_analysis = 'detailed'\n    capacity_increase_recommendation = true\n    monitoring_frequency = 'daily'",
    "beta_program_invitation = true\n    feedback_priority = 'high'\n    early_access_features = ['feature_a', 'feature_b']",
    "plan_optimization_recommendation = 'cost_saving'\n    usage_analysis = true\n    alternative_plans = ['plan_a', 'plan_b']",
    "compliance_review = 'required'\n    documentation_update = true\n    regulatory_notification = true",
    "fraud_alert = true\n    account_review = 'immediate'\n    security_team_notification = true",
]

def generate_rule_file(num_rules:'int', total_conditions:'int', common_conditions_count:'int', output_file:'str') -> 'None':
    """Generate a rule file with the specified parameters."""
    
    # Validate inputs
    if common_conditions_count > total_conditions:
        raise ValueError('Number of common conditions cannot exceed total conditions')
    
    if common_conditions_count > len(COMMON_CONDITIONS):
        raise ValueError(f'Not enough common conditions defined. Need {common_conditions_count}, have {len(COMMON_CONDITIONS)}')
    
    unique_conditions_count = total_conditions - common_conditions_count
    
    # Create the file content
    content = '# ################################################################################################################################'
    
    for rule_num in range(1, num_rules + 1):
        # Select conditions for this rule
        rule_common_conditions = COMMON_CONDITIONS[:common_conditions_count]
        
        # Calculate the starting index for unique conditions to ensure they don't overlap between rules
        unique_start_idx = (rule_num - 1) * unique_conditions_count % (len(UNIQUE_CONDITIONS) - unique_conditions_count)
        rule_unique_conditions = UNIQUE_CONDITIONS[unique_start_idx:unique_start_idx + unique_conditions_count]
        
        # Combine all conditions
        all_conditions = rule_common_conditions + rule_unique_conditions
        
        # Format the conditions with proper comments
        conditions_text = ''
        for i, cond in enumerate(all_conditions):
            # Determine the actual condition number based on the condition's position in the original lists
            if i < common_conditions_count:
                # For common conditions, use the original index + 1 (1-based indexing)
                condition_num = i + 1
            else:
                # For unique conditions, use the original index + 101 (to start at 101)
                unique_idx = unique_start_idx + (i - common_conditions_count)
                condition_num = unique_idx + 101
            
            if i == len(all_conditions) - 1:
                # Last condition should not have 'and'
                conditions_text += f'    {cond}                            # Condition {condition_num:03d}'
            else:
                conditions_text += f'    {cond} and                      # Condition {condition_num:03d}\n'
        
        # Select description, purpose, defaults, and actions
        description = RULE_DESCRIPTIONS[rule_num % len(RULE_DESCRIPTIONS)]
        purpose = RULE_PURPOSES[rule_num % len(RULE_PURPOSES)]
        defaults = DEFAULT_VALUES[rule_num % len(DEFAULT_VALUES)]
        action = ACTIONS[rule_num % len(ACTIONS)]
        
        # Format the rule
        rule = RULE_TEMPLATE.format(
            rule_num=rule_num,
            rule_description=description,
            rule_purpose=purpose,
            defaults=defaults,
            conditions=conditions_text,
            actions=action
        )
        
        content += rule
        content += '\n# ################################################################################################################################'
    
    # Write the file
    with open(output_file, 'w') as f:
        f.write(content)
    
    print(f'Generated {output_file} with {num_rules} rules, {total_conditions} conditions per rule, {common_conditions_count} common')

def main() -> 'None':
    """Generate all the requested rule files."""
    
    # Define the configurations for the files to generate
    configs = [
        # 10 rules files with 10 conditions
        (10, 10, 1, 'perf_010_rules_010_conditions_001_common.zrules'),
        (10, 10, 3, 'perf_010_rules_010_conditions_003_common.zrules'),
        (10, 10, 5, 'perf_010_rules_010_conditions_005_common.zrules'),
        (10, 10, 7, 'perf_010_rules_010_conditions_007_common.zrules'),
        (10, 10, 9, 'perf_010_rules_010_conditions_009_common.zrules'),
        
        # 10 rules files with 5 conditions
        (10, 5, 1, 'perf_010_rules_005_conditions_001_common.zrules'),
        (10, 5, 3, 'perf_010_rules_005_conditions_003_common.zrules'),
        
        # 30 rules files with 10 conditions
        (30, 10, 1, 'perf_030_rules_010_conditions_001_common.zrules'),
        (30, 10, 3, 'perf_030_rules_010_conditions_003_common.zrules'),
        (30, 10, 5, 'perf_030_rules_010_conditions_005_common.zrules'),
        (30, 10, 7, 'perf_030_rules_010_conditions_007_common.zrules'),
        (30, 10, 9, 'perf_030_rules_010_conditions_009_common.zrules'),
        
        # 30 rules files with 5 conditions
        (30, 5, 1, 'perf_030_rules_005_conditions_001_common.zrules'),
        (30, 5, 3, 'perf_030_rules_005_conditions_003_common.zrules'),
        
        # 60 rules files with 10 conditions
        (60, 10, 1, 'perf_060_rules_010_conditions_001_common.zrules'),
        (60, 10, 3, 'perf_060_rules_010_conditions_003_common.zrules'),
        (60, 10, 5, 'perf_060_rules_010_conditions_005_common.zrules'),
        (60, 10, 7, 'perf_060_rules_010_conditions_007_common.zrules'),
        (60, 10, 9, 'perf_060_rules_010_conditions_009_common.zrules'),
        
        # 60 rules files with 5 conditions
        (60, 5, 1, 'perf_060_rules_005_conditions_001_common.zrules'),
        (60, 5, 3, 'perf_060_rules_005_conditions_003_common.zrules'),
        (60, 5, 5, 'perf_060_rules_005_conditions_005_common.zrules'),
        
        # 100 rules files with 10 conditions
        (100, 10, 1, 'perf_100_rules_010_conditions_001_common.zrules'),
        (100, 10, 3, 'perf_100_rules_010_conditions_003_common.zrules'),
        (100, 10, 5, 'perf_100_rules_010_conditions_005_common.zrules'),
        (100, 10, 7, 'perf_100_rules_010_conditions_007_common.zrules'),
        (100, 10, 9, 'perf_100_rules_010_conditions_009_common.zrules'),
        
        # 100 rules files with 5 conditions
        (100, 5, 1, 'perf_100_rules_005_conditions_001_common.zrules'),
        (100, 5, 3, 'perf_100_rules_005_conditions_003_common.zrules'),
        (100, 5, 5, 'perf_100_rules_005_conditions_005_common.zrules'),
        
        # 500 rules files with 10 conditions
        (500, 10, 1, 'perf_500_rules_010_conditions_001_common.zrules'),
        (500, 10, 3, 'perf_500_rules_010_conditions_003_common.zrules'),
        (500, 10, 5, 'perf_500_rules_010_conditions_005_common.zrules'),
        (500, 10, 7, 'perf_500_rules_010_conditions_007_common.zrules'),
        (500, 10, 9, 'perf_500_rules_010_conditions_009_common.zrules'),
        
        # 500 rules files with 5 conditions
        (500, 5, 1, 'perf_500_rules_005_conditions_001_common.zrules'),
        (500, 5, 3, 'perf_500_rules_005_conditions_003_common.zrules'),
        (500, 5, 5, 'perf_500_rules_005_conditions_005_common.zrules'),
    ]
    
    # Get the current directory
    current_dir = Path(os.path.dirname(os.path.abspath(__file__)))
    
    # Create the perf directory if it doesn't exist
    perf_dir = current_dir / 'perf'
    perf_dir.mkdir(exist_ok=True)
    
    # Generate each file
    for num_rules, total_conditions, common_conditions_count, filename in configs:
        output_path = perf_dir / filename
        generate_rule_file(num_rules, total_conditions, common_conditions_count, output_path)

if __name__ == '__main__':
    main()

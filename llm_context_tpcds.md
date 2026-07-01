# TPC-DS Data Warehouse Context

This document provides the metadata and schema definitions for the TPC-DS 10GB Data Warehouse generated for the Retail project. It is intended to be used as context for Large Language Models (LLMs) to automatically generate accurate Spark SQL / Hive queries.

## Storage Configuration
All tables are stored in **Parquet** format in an AWS S3 bucket.
- **Base Warehouse Path**: `s3://onpe-datalake-mx/warehouse/tpcds-10gb/`

## Optimizations & Partitioning
To ensure performant queries, the large fact tables have been optimized using Date-based Partitioning. **When generating queries filtering by date or time, always try to use the partition columns in the `WHERE` clause.**

| Table Name | Partition Column | Description |
|---|---|---|
| `store_sales` | `ss_sold_date_sk` | Partitioned by the date the item was sold. |
| `store_returns` | `sr_returned_date_sk` | Partitioned by the date the item was returned. |
| `catalog_sales` | `cs_sold_date_sk` | Partitioned by the date the catalog item was sold. |
| `web_sales` | `ws_sold_date_sk` | Partitioned by the date the web item was sold. |

---

## Schemas

### 1. Fact Tables

#### `store_sales`
Path: `s3://onpe-datalake-mx/warehouse/tpcds-10gb/store_sales/`
- `ss_sold_date_sk` (Integer) - **[PARTITION KEY]**
- `ss_sold_time_sk` (Integer)
- `ss_item_sk` (Integer) - Foreign Key to `item`
- `ss_customer_sk` (Integer) - Foreign Key to `customer`
- `ss_cdemo_sk` (Integer) - Foreign Key to `customer_demographics`
- `ss_hdemo_sk` (Integer) - Foreign Key to `household_demographics`
- `ss_addr_sk` (Integer) - Foreign Key to `customer_address`
- `ss_store_sk` (Integer) - Foreign Key to `store`
- `ss_promo_sk` (Integer) - Foreign Key to `promotion`
- `ss_ticket_number` (Integer)
- `ss_quantity` (Integer)
- `ss_wholesale_cost` (Double)
- `ss_list_price` (Double)
- `ss_sales_price` (Double)
- `ss_ext_discount_amt` (Double)
- `ss_ext_sales_price` (Double)
- `ss_ext_wholesale_cost` (Double)
- `ss_ext_list_price` (Double)
- `ss_ext_tax` (Double)
- `ss_coupon_amt` (Double)
- `ss_net_paid` (Double)
- `ss_net_paid_inc_tax` (Double)
- `ss_net_profit` (Double)

#### `store_returns`
Path: `s3://onpe-datalake-mx/warehouse/tpcds-10gb/store_returns/`
- `sr_returned_date_sk` (Integer) - **[PARTITION KEY]**
- `sr_return_time_sk` (Integer)
- `sr_item_sk` (Integer)
- `sr_customer_sk` (Integer)
- `sr_cdemo_sk` (Integer)
- `sr_hdemo_sk` (Integer)
- `sr_addr_sk` (Integer)
- `sr_store_sk` (Integer)
- `sr_reason_sk` (Integer)
- `sr_ticket_number` (Integer)
- `sr_return_quantity` (Integer)
- `sr_return_amt` (Double)
- `sr_return_tax` (Double)
- `sr_return_amt_inc_tax` (Double)
- `sr_fee` (Double)
- `sr_return_ship_cost` (Double)
- `sr_refunded_cash` (Double)
- `sr_reversed_charge` (Double)
- `sr_store_credit` (Double)
- `sr_net_loss` (Double)

#### `catalog_sales`
Path: `s3://onpe-datalake-mx/warehouse/tpcds-10gb/catalog_sales/`
- `cs_sold_date_sk` (Integer) - **[PARTITION KEY]**
- `cs_sold_time_sk` (Integer)
- `cs_ship_date_sk` (Integer)
- `cs_bill_customer_sk` (Integer)
- `cs_bill_cdemo_sk` (Integer)
- `cs_bill_hdemo_sk` (Integer)
- `cs_bill_addr_sk` (Integer)
- `cs_ship_customer_sk` (Integer)
- `cs_ship_cdemo_sk` (Integer)
- `cs_ship_hdemo_sk` (Integer)
- `cs_ship_addr_sk` (Integer)
- `cs_call_center_sk` (Integer)
- `cs_catalog_page_sk` (Integer)
- `cs_ship_mode_sk` (Integer)
- `cs_warehouse_sk` (Integer)
- `cs_item_sk` (Integer)
- `cs_promo_sk` (Integer)
- `cs_order_number` (Integer)
- `cs_quantity` (Integer)
- `cs_wholesale_cost` (Double)
- `cs_list_price` (Double)
- `cs_sales_price` (Double)
- `cs_ext_discount_amt` (Double)
- `cs_ext_sales_price` (Double)
- `cs_ext_wholesale_cost` (Double)
- `cs_ext_list_price` (Double)
- `cs_ext_tax` (Double)
- `cs_coupon_amt` (Double)
- `cs_ext_ship_cost` (Double)
- `cs_net_paid` (Double)
- `cs_net_paid_inc_tax` (Double)
- `cs_net_paid_inc_ship` (Double)
- `cs_net_paid_inc_ship_tax` (Double)
- `cs_net_profit` (Double)

#### `web_sales`
Path: `s3://onpe-datalake-mx/warehouse/tpcds-10gb/web_sales/`
- `ws_sold_date_sk` (Integer) - **[PARTITION KEY]**
- `ws_sold_time_sk` (Integer)
- `ws_ship_date_sk` (Integer)
- `ws_item_sk` (Integer)
- `ws_bill_customer_sk` (Integer)
- `ws_bill_cdemo_sk` (Integer)
- `ws_bill_hdemo_sk` (Integer)
- `ws_bill_addr_sk` (Integer)
- `ws_ship_customer_sk` (Integer)
- `ws_ship_cdemo_sk` (Integer)
- `ws_ship_hdemo_sk` (Integer)
- `ws_ship_addr_sk` (Integer)
- `ws_web_page_sk` (Integer)
- `ws_web_site_sk` (Integer)
- `ws_ship_mode_sk` (Integer)
- `ws_warehouse_sk` (Integer)
- `ws_promo_sk` (Integer)
- `ws_order_number` (Integer)
- `ws_quantity` (Integer)
- `ws_wholesale_cost` (Double)
- `ws_list_price` (Double)
- `ws_sales_price` (Double)
- `ws_ext_discount_amt` (Double)
- `ws_ext_sales_price` (Double)
- `ws_ext_wholesale_cost` (Double)
- `ws_ext_list_price` (Double)
- `ws_ext_tax` (Double)
- `ws_coupon_amt` (Double)
- `ws_ext_ship_cost` (Double)
- `ws_net_paid` (Double)
- `ws_net_paid_inc_tax` (Double)
- `ws_net_paid_inc_ship` (Double)
- `ws_net_paid_inc_ship_tax` (Double)
- `ws_net_profit` (Double)

---

### 2. Dimension Tables

#### `date_dim`
Path: `s3://onpe-datalake-mx/warehouse/tpcds-10gb/date_dim/`
- `d_date_sk` (Integer) - Primary Key. Joins with fact partition keys.
- `d_date_id` (String)
- `d_date` (String) - e.g. "2023-01-15"
- `d_month_seq` (Integer)
- `d_week_seq` (Integer)
- `d_quarter_seq` (Integer)
- `d_year` (Integer)
- `d_dow` (Integer)
- `d_moy` (Integer)
- `d_dom` (Integer)
- `d_qoy` (Integer)
- `d_fy_year` (Integer)
- `d_fy_quarter_seq` (Integer)
- `d_fy_week_seq` (Integer)
- `d_day_name` (String) - e.g. "Monday"
- `d_quarter_name` (String)
- `d_holiday` (String)
- `d_weekend` (String)
- `d_following_holiday` (String)
- `d_first_dom` (Integer)
- `d_last_dom` (Integer)
- `d_same_day_ly` (Integer)
- `d_same_day_lq` (Integer)
- `d_current_day` (String)
- `d_current_week` (String)
- `d_current_month` (String)
- `d_current_quarter` (String)
- `d_current_year` (String)

#### `store`
Path: `s3://onpe-datalake-mx/warehouse/tpcds-10gb/store/`
- `s_store_sk` (Integer) - Primary Key
- `s_store_id` (String)
- `s_rec_start_date` (String)
- `s_rec_end_date` (String)
- `s_closed_date_sk` (Integer)
- `s_store_name` (String)
- `s_number_employees` (Integer)
- `s_floor_space` (Integer)
- `s_hours` (String)
- `s_manager` (String)
- `s_market_id` (Integer)
- `s_geography_class` (String)
- `s_market_desc` (String)
- `s_market_manager` (String)
- `s_division_id` (Integer)
- `s_division_name` (String)
- `s_company_id` (Integer)
- `s_company_name` (String)
- `s_street_number` (String)
- `s_street_name` (String)
- `s_street_type` (String)
- `s_suite_number` (String)
- `s_city` (String)
- `s_county` (String)
- `s_state` (String)
- `s_zip` (String)
- `s_country` (String)
- `s_gmt_offset` (Double)
- `s_tax_precentage` (Double)

#### `item`
Path: `s3://onpe-datalake-mx/warehouse/tpcds-10gb/item/`
- `i_item_sk` (Integer) - Primary Key
- `i_item_id` (String)
- `i_rec_start_date` (String)
- `i_rec_end_date` (String)
- `i_item_desc` (String)
- `i_current_price` (Double)
- `i_wholesale_cost` (Double)
- `i_brand_id` (Integer)
- `i_brand` (String)
- `i_class_id` (Integer)
- `i_class` (String)
- `i_category_id` (Integer)
- `i_category` (String)
- `i_manufact_id` (Integer)
- `i_manufact` (String)
- `i_size` (String)
- `i_formulation` (String)
- `i_color` (String)
- `i_units` (String)
- `i_container` (String)
- `i_manager_id` (Integer)
- `i_product_name` (String)

#### `customer`
Path: `s3://onpe-datalake-mx/warehouse/tpcds-10gb/customer/`
- `c_customer_sk` (Integer) - Primary Key
- `c_customer_id` (String)
- `c_current_cdemo_sk` (Integer)
- `c_current_hdemo_sk` (Integer)
- `c_current_addr_sk` (Integer)
- `c_first_shipto_date_sk` (Integer)
- `c_first_sales_date_sk` (Integer)
- `c_salutation` (String)
- `c_first_name` (String)
- `c_last_name` (String)
- `c_preferred_cust_flag` (String)
- `c_birth_day` (Integer)
- `c_birth_month` (Integer)
- `c_birth_year` (Integer)
- `c_birth_country` (String)
- `c_login` (String)
- `c_email_address` (String)
- `c_last_review_date` (String)
- `c_last_review_date_sk` (Integer)

#### `customer_demographics`
Path: `s3://onpe-datalake-mx/warehouse/tpcds-10gb/customer_demographics/`
- `cd_demo_sk` (Integer) - Primary Key
- `cd_gender` (String)
- `cd_marital_status` (String)
- `cd_education_status` (String)
- `cd_purchase_estimate` (Integer)
- `cd_credit_rating` (String)
- `cd_dep_count` (Integer)
- `cd_dep_employed_count` (Integer)
- `cd_dep_college_count` (Integer)

#### `customer_address`
Path: `s3://onpe-datalake-mx/warehouse/tpcds-10gb/customer_address/`
- `ca_address_sk` (Integer) - Primary Key
- `ca_address_id` (String)
- `ca_street_number` (String)
- `ca_street_name` (String)
- `ca_street_type` (String)
- `ca_suite_number` (String)
- `ca_city` (String)
- `ca_county` (String)
- `ca_state` (String)
- `ca_zip` (String)
- `ca_country` (String)
- `ca_gmt_offset` (Double)
- `ca_location_type` (String)

#### `promotion`
Path: `s3://onpe-datalake-mx/warehouse/tpcds-10gb/promotion/`
- `p_promo_sk` (Integer) - Primary Key
- `p_promo_id` (String)
- `p_start_date_sk` (Integer)
- `p_end_date_sk` (Integer)
- `p_item_sk` (Integer)
- `p_cost` (Double)
- `p_response_target` (Integer)
- `p_promo_name` (String)
- `p_channel_dmail` (String)
- `p_channel_email` (String)
- `p_channel_catalog` (String)
- `p_channel_tv` (String)
- `p_channel_radio` (String)
- `p_channel_press` (String)
- `p_channel_event` (String)
- `p_channel_demo` (String)
- `p_channel_details` (String)
- `p_purpose` (String)
- `p_discount_active` (String)

#### `household_demographics`
Path: `s3://onpe-datalake-mx/warehouse/tpcds-10gb/household_demographics/`
- `hd_demo_sk` (Integer) - Primary Key
- `hd_income_band_sk` (Integer)
- `hd_buy_potential` (String)
- `hd_dep_count` (Integer)
- `hd_vehicle_count` (Integer)

#### `income_band`
Path: `s3://onpe-datalake-mx/warehouse/tpcds-10gb/income_band/`
- `ib_income_band_sk` (Integer) - Primary Key
- `ib_lower_bound` (Integer)
- `ib_upper_bound` (Integer)

#### `time_dim`
Path: `s3://onpe-datalake-mx/warehouse/tpcds-10gb/time_dim/`
- `t_time_sk` (Integer) - Primary Key
- `t_time_id` (String)
- `t_time` (Integer)
- `t_hour` (Integer)
- `t_minute` (Integer)
- `t_second` (Integer)
- `t_am_pm` (String)
- `t_shift` (String)
- `t_sub_shift` (String)
- `t_meal_time` (String)

---

### 3. ML Derived Tables

#### `customer_segments`
Path: `s3://onpe-datalake-mx/warehouse/tpcds-10gb/customer_segments/`
- `recency` (Integer) - Days since last purchase
- `frequency` (Integer) - Number of unique transactions
- `monetary` (Double) - Total amount spent (`ss_net_paid`)
- `segment_id` (Integer) - The K-Means cluster ID (0 to 4) representing the customer segment.
- `c_customer_sk` (Integer)
- `c_customer_id` (String)
- `c_first_name` (String)
- `c_last_name` (String)
- `c_email_address` (String)
*(Note: Inherits all fields from `customer` dimension)*

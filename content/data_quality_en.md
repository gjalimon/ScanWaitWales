# Data Quality & Dataset Caveats

This page documents known reporting anomalies, administrative caveats, and data-cleaning rules affecting the NHS Wales diagnostic waiting times data used in **ScanWait Wales**.

---

## Dataset Source & Official Metadata

* **Dataset:** [Diagnostic services: pathway waiting times, August 2024 onwards (Dataset ID: `3c2720e6-95ae-4eeb-9e88-ed74bb40c6b9`)](https://stats.gov.wales/en-GB/3c2720e6-95ae-4eeb-9e88-ed74bb40c6b9/start#about)
* **Designation & Publisher:** Accredited official statistics published by the **Welsh Government** (`stats.healthinfo@gov.wales`).
* **Data Provider & Collection:** Compiled by **Digital Health and Care Wales (DHCW)** from the **Diagnostic and Therapy Services Waiting Times (DATS)** return, drawn directly from Local Health Board patient administrative systems.
* **Coverage & Release Schedule:** Covers monthly snapshots from **August 2024 to September 2026** (dataset first published **23 October 2025**; next scheduled update **23 December 2026**).
* **Related Official Quality Documentation:** [NHS activity and performance summary: quality report (Welsh Government)](https://www.gov.wales/nhs-activity-and-performance-summary-september-and-october-2026-html)
* **No Retrospective Revisions:** Per the [StatsWales dataset documentation](https://stats.gov.wales/en-GB/3c2720e6-95ae-4eeb-9e88-ed74bb40c6b9/start#about), because figures are extracted from live Local Health Board administrative systems, **revised figures cannot be produced** once published. Historical submission gaps and site-coding anomalies therefore remain permanently in the published time series.

---

## Chronological Log of Data Quality Issues & Anomalies

### November 2026 — Hospital Site Verification & "Ghost Scanner" Filtering (FOI 2026 148)
* **Unverified Equipment Mappings:** Cross-checking StatsWales hospital-level records against physical radiology infrastructure revealed smaller and community hospitals reported with active waiting lists for specialist scanners they do not operate on-site (for example, *Ruthin Community Hospital* recorded with patients waiting for Non-Cardiac Nuclear Medicine).
* **Non-Physical / Catch-All Site Labels:** The raw StatsWales dataset includes five non-hospital administrative buckets (`Community` under Betsi Cadwaladr UHB [Ref 19] and Aneurin Bevan UHB [Ref 22]; `Unallocated in Aneurin Bevan University LHB` [Ref 209]; `Unknown Sites in Cwm Taf Morgannwg` [Ref 193]; and `Trust` under Swansea Bay UHB [Ref 174]), as well as a duplicate site-board entry (`Royal Glamorgan` listed under both Cwm Taf Morgannwg UHB [Ref 164] and Cardiff and Vale UHB [Ref 97]).
* **Mitigation in ScanWait Wales:** Freedom of Information requests (**FOI 2026 148**) were submitted to all seven Local Health Boards and Velindre University NHS Trust to verify permanent and mobile scanner availability across 10 imaging modalities. ScanWait Wales filters all outputs through a verified reference table (`selected_hospitals_services_coordinates.csv`) so waiting times are only published for confirmed hospital–scanner pairs.

### September 2026 — Small-Denominator Volatility in Specialist Cardiac Scans
* **Issue:** Specialist cardiac modalities with very small queues (1 to 40 patients) exhibit large percentage swings from small headcount changes.
* **Examples:**
  * *Grange University Hospital* — **CT [Cardiac only]**: `1` patient waiting in August and September 2026 compared with `15` in April 2026 (**+1,400.0%** relative difference).
  * *Singleton Hospital* — **Nuclear Medicine [Cardiac]**: rose from `9` patients in May 2026 to `40` in September 2026 (**+344.4%**).

### July 2026 — Multi-Site Ultrasound & MRI Backlog Surges
* **Issue:** Simultaneous drops in monthly cohort clearance rates across high-volume modalities caused sharp single-month headcount increases.
* **Examples:**
  * *Aneurin Bevan UHB* recorded a **+48.7%** board-wide jump (+3,316 patients, from `6,812` to `10,128`), driven by concurrent Non-Obstetric Ultrasound surges at *Nevill Hall* (`775` to `1,636`, **+111.1%**), *Royal Gwent* (`1,118` to `1,638`, **+46.5%**), and *Ysbyty Ystrad Fawr* (`353` to `739`, **+109.3%**), alongside *Royal Gwent* MRI (`851` to `1,240`, **+45.7%**).
  * *Nevill Hall* — **CT [Cardiac only]** increased from `11` to `38` patients (**+245.5%** month-on-month).

### May – September 2026 — Intra-Board Queue Reallocations & Zero-Clearance Months
* **Intra-Board Reallocation (Cardiff and Vale UHB):** Between May and September 2026, queues at *University Hospital Llandough* fell sharply (Non-Obstetric Ultrasound dropped from `3,294` to `1,484`; CT dropped from `1,105` to `529`), while *University Hospital of Wales (UHW)* rose over the exact same window:
  * **UHW Non-Obstetric Ultrasound:** jumped **+66.2%** in June 2026 (`2,623` to `4,359`, peaking at `5,162` in August).
  * **UHW MRI:** jumped **+36.0%** in June 2026 (`1,898` to `2,581`, reaching `3,583` in September).
  * **UHW Fluoroscopy:** climbed from `20` in April 2026 to `112` in May, `420` in June (**+275.0%**), and `495` in September.
* **Zero-Clearance Months (June 2026):** Recorded monthly cohort outflow dropped to **0.0%** for Non-Obstetric Ultrasound at *Royal Glamorgan* (`1,130` to `1,723`, +593) and *Prince Charles Hospital* (`904` to `1,420`, +516), causing incoming referrals to accumulate directly onto the active waiting list.

### March – April 2026 — Missing Monthly Submission & Artificial Rebound (Cwm Taf Morgannwg UHB)
* **Issue:** In **March 2026**, 13 of Cwm Taf Morgannwg UHB's 19 active hospital–scan series were omitted from the monthly submission—specifically all 6 services at *Bridgend* (`3,079` patients in February 2026) and 7 of 8 services at *Royal Glamorgan* (`4,300` patients in February 2026).
* **Impact:** The Health Board's reported total fell **-77.0%** (`8,286` to `1,909`) in March 2026 and spiked **+300.7%** (+5,741 patients back to `7,650`) when both hospitals resumed reporting in **April 2026**. Because StatsWales does not issue retrospective revisions, this reporting gap remains in the historical series.

### December 2025 – April 2026 — Late Series Entry & Volatility (NW Cancer Treatment Centre)
* **Issue:** *NW Cancer Treatment Centre* (operated by Betsi Cadwaladr UHB) had no diagnostic waiting list entries between August 2024 and November 2025, first appearing in **December 2025** (`94` CT patients).
* **Impact:** Reported CT pathways dropped to `27` in **March 2026**, spiked **+1,044.4%** to `309` in **April 2026**, and declined to `42` by September 2026. *(Note: Velindre University NHS Trust has no diagnostic hospital sites reported in this StatsWales dataset.)*

### September – December 2025 — Autumn Backlog Accumulation (Betsi Cadwaladr UHB)
* **Issue:** Total waiting pathways across *Betsi Cadwaladr UHB* increased **+20.6%** (+3,590 patients) in September 2025 and **+11.9%** (+2,506 patients) in October 2025 across *Ysbyty Maelor*, *Ysbyty Gwynedd*, and *Ysbyty Glan Clwyd* (peaking at `24,949` in December 2025) while monthly clearance rates slowed to 18%–28%, before higher clearance rates (50%–70%) reduced backlogs in 2026.

### October 2024 – April 2025 — Single-Patient Median Band Jumps
* **Issue:** Because ScanWait Wales estimates typical wait times using the 50th-percentile (median) weekly band, small queues can jump sharply when a single patient remains in a long-wait band.
* **Examples:**
  * *Bridgend* — **CT [Cardiac only]** (October 2024): jumped from `1` week to `22` weeks when only 1 patient remained on the list (`Total_Waiting = 1`) in the 22-week band.
  * *Nevill Hall* — **Nuclear Medicine [Cardiac]** (April 2025): jumped from `4` weeks to `27` weeks (+23 weeks) following 0.0% monthly clearance on a 16-patient list.
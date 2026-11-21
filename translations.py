"""
This file stores every phrase used on the website in both English and Welsh.
When a user selects a language, the app reads the correct dictionary from here.

To add a new phrase:
    1. Add a new key (e.g. "welcome_title") to both "en" and "cy" sections.
    2. In the HTML template, replace the hardcoded text with:
       {{ translations['your_key_here'] }}

Language codes:
    "en" = English
    "cy" = Cymraeg (Welsh)
"""

TRANSLATIONS = {
    "en": {
        # ---------- Welcome Page ----------
        "page_title": "ScanWait Wales Welcome Page",

        # --- Navigation Bar ---
        "nav_brand": "ScanWait Wales",
        "nav_home": "Home",
        "nav_input": "Wait Times", # changed from "Calculation" to "Wait Times" 
        "nav_visualisations": "Explore Data",
        "nav_information": "More Information",

        # --- Main Content ---
        "welcome_subtitle": "<b>Welcome to ScanWait Wales</b> - <i>the unofficial site for finding out how long you might be waiting for your next scan.</i>",
        "welcome_description": "We take the data published monthly by NHS Wales, run our calculations, and (hopefully) give you an idea of how long you could be waiting until your scan happens. To find out more, please go to More Information.",
        "welcome_text": "ScanWait Wales is designed to help patients explore scanning wait times from NHS Wales and identify hospitals that may offer a selected scan. "
        "We are not affiliated with NHS Wales and we do not have access to NHS patient records, NHS numbers, clinical notes or individual appointment information. "
        "The estimated results do not represent an individual appointment. "
        "The application uses publicly available hospital information, postcode reference datasets and aggregated waiting-time statistics. No information is stored when using this service.",

        # ---------- Input Page ----------
        "page_title_input": "Wait Times - ScanWait Wales",
        "input_heading": "Hospital and Scan Type Selection",
        "input_instruction": "Please select a hospital and scan type from the drop-down menus provided.",
        "input_label_service": "Select a scan type",
        "input_label_location": "Select a hospital:",
        "calculate_button": "Calculate",

        # ---------- Input Postcode ----------
        "heading_postcode": "Check the estimated wait times for your scan",
        "info_disclaimer": "None of the information you provide will be stored.",
        "selection_process": "Scan -> Hospital -> Results",
        "input_postcode": "Enter a Postcode in Wales:",
        "input_placeholder": "For example, CF10 1EP",
        "input_nearest": "Check Nearest",
        "input_all_hospitals": "All Welsh hospitals that offer this scan",
        "input_three_hospitals": "Three nearest hospitals",
        "ranked_postcode": "Hospitals are ranked by straight-line distance from",
        "input_health_board": "Health board:",

        # ---------- Health Board Name Translations ----------
        "health_board_Aneurin_Bevan": "Aneurin Bevan",
        "health_board_Betsi_Cadwaladr": "Betsi Cadwaladr",
        "health_board_Cardiff_and_Vale": "Cardiff and Vale",
        "health_board_Cwm_Taf_Morgannwg": "Cwm Taf Morgannwg",
        "health_board_Hywel_Dda": "Hywel Dda",
        "health_board_Swansea_Bay": "Swansea Bay",

        "all_hospitals": "All hospitals offering",
        "label_select_hospital": "Select a hospital:",
        "option_choose_hospital": "Choose a hospital",
        "drive_label": "Drive:",
        "walk_label": "Walk:",
        "unavailable": "Unavailable",

        # ---------- Hospital Card Labels ----------
        "label_hospital": "Hospital:",
        "label_distance": "Distance:",
        "label_healthboard": "Health Board:",
        "miles_away": "miles away from postcode",
        "view_wait_time_button": "View estimated wait time",
        "view_all_hospitals_button": "View all hospitals offering this scan",
        "nearby_alternatives_heading": "Nearby Alternatives",

        # ---------- Output Page ----------
        "page_title_output": "Calculated Wait Time - ScanWait Wales",

        # The output sentences are split into chunks around the variables.
        # This lets English and Welsh have their own natural word order.
        # Example: "The current calculated wait time for [scan] at [hospital] is [X] weeks"
        #   chunk 1  = "The current calculated wait time for"
        #   variable = scan_choice
        #   chunk 2  = "at"
        #   variable = hospital_choice
        #   chunk 3  = "is"
        #   variable = typical_wait
        #   chunk 4  = "weeks"
        "output_wait_prefix": "The current estimated wait time for",
        "output_wait_at": "at",
        "output_wait_is": "is",
        "output_wait_around": "around",
        "output_weeks": "weeks",
        "output_source_prefix": "This is based on the",
        "output_source_suffix": "data provided by StatsWales. The estimated results do not represent an individual appointment.",
        "output_more_info": "To find out more about the dataset and how this calculation is made and its limitations, please visit",
        "output_more_info_link": "More Information",
        "output_bottom_disclaimer": "Based on the",
        "output_bottom_disclaimer_link": "data provided by StatsWales. To find out more, please visit",

        # ---------- Scan Type Translations ----------
        "scan_type_CT": "CT",
        "scan_type_MRI": "MRI",
        "scan_type_Ultrasound": "Ultrasound",
        "scan_type_Nuclear_Medicine": "Nuclear Medicine",
        "scan_type_Fluoroscopy": "Fluoroscopy",
        "scan_type_Diagnostic_Angiography": "Diagnostic Angiography",
        "scan_type_Cardiac_CT": "CT [Cardiac only]",
        "scan_type_Cardiac_MRI": "MRI [Cardiac only]",
        "scan_type_Nuclear_Medicine_Cardiac": "Nuclear Medicine [Cardiac / Myocardial Perfusion]",

        # ---------- Month Translations ----------
        "month_January": "January",
        "month_February": "February",
        "month_March": "March",
        "month_April": "April",
        "month_May": "May",
        "month_June": "June",
        "month_July": "July",
        "month_August": "August",
        "month_September": "September",
        "month_October": "October",
        "month_November": "November",
        "month_December": "December",

        # ---------- Gauge / Speedometer ----------
        "gauge_label_0": "0 Weeks",
        "gauge_desc_0": "On target",
        "gauge_label_8": "8 Weeks",
        "gauge_desc_8": "Approaching limit",
        "gauge_label_15": "15+ Weeks",
        "gauge_desc_15": "Exceeded target",
        "gauge_unit": "Weeks",
        "gauge_unit_singular": "Week",
        "status_green": "On track — within the 8-week target",
        "status_orange": "Over target — 8 weeks or longer",
        "status_red": "Significantly delayed — longer than 8 weeks",

                # --- Visualisations Page (menu) ---
        "vis_page_title": "Visualisations - ScanWait Wales",
        "vis_welcome_heading": "Welcome to the visualisations page",
        "vis_instruction": "Use this page to navigate to the various visualisations on offer. Our goal here is to make the data interactive and accessible to the public. Click an image to open a visualisation.",
        "vis_card_heatmap_title": "Heat map of wait times across Wales",
        "vis_card_heatmap_desc": "An interactive heat map of scan wait times across wales.",
        "vis_card_heatmap_alt": "Icon: map of Wales",
        "vis_card_barchart_title": "Bar graph comparing hospitals",
        "vis_card_barchart_desc": "A stacked bar graph of wait times for all scans across all hospitals.",
        "vis_card_barchart_alt": "Icon: bar graph",
        "vis_card_linechart_title": "Time-series line graph",
        "vis_card_linechart_desc": "An interactive line graph of wait times since August 2024.",
        "vis_card_linechart_alt": "Icon: line graph",

                        # --- Heatmap Page ---
        "heat_page_title": "Waiting-Time Heatmap - ScanWait Wales",
        "heat_back_button": "← Back to visualisations",
        "heat_heading": "Waiting times across Wales",
        "heat_instruction": "Choose a scan type to see waiting times at hospitals across Wales.",
        "heat_colour_explain": "The lightest shade of red represents the shortest wait time of one week. The darkest shade of red represents the longest wait times of 15 weeks or more.",
        "heat_nhs_target": "The <strong>NHS Wales target</strong> for diagnostic scans is <strong>8 weeks</strong>.",
        "heat_label_scan": "Choose a scan type:",
        "heat_dropdown_placeholder": "Choose a scan",
        "heat_map_message_placeholder": "Please choose a scan type",
        "heat_map_message_no_coords": "No hospitals with coordinates were found for this scan type.",
        "heat_hospital_singular": "hospital",
        "heat_hospital_plural": "hospitals",
        "heat_shown_for": "shown for",
        "heat_colourbar_title": "Waiting time (weeks)",
        "heat_map_title_prefix": "Waiting times for ",
        "heat_hover_wait": "Waiting time",
        "heat_weeks_abbreviation": "w",

        # --- Stacked Bar Chart Page ---
        "stacked_page_title": "Stacked Bar Chart - ScanWait Wales",
        "stacked_back_button": "← Back to visualisations",
        "stacked_heading": "Compare waiting times across selected Welsh Hospitals",
        "stacked_nhs_target": "The NHS Wales target for diagnostic scans waiting times is 8 weeks.",

        # --- Line Graph Page ---
        "line_page_title": "Time-series line graph - ScanWait Wales",
        "line_back_button": "← Back to visualisations",
        "line_heading": "Compare waiting times across selected Welsh Hospitals",
        "line_nhs_target": "The NHS Wales target for diagnostic scans waiting times is 8 weeks.",
        "line_filter_label": "Filter by scan type:",
        "line_visualise_button": "Visualise",

        # --- Plotly Chart Text ---
        "chart_title_summary": "Summary of scan wait times across all hospitals",
        "chart_xaxis_hospital": "Hospital",
        "chart_yaxis_weeks": "Wait time (weeks)",
        "chart_legend_scan_type": "Scan type",
        "chart_hover_scan": "Scan",
        "chart_hover_wait": "Wait time",
        "chart_weeks": "weeks",
        "chart_week_singular": "week",
        "chart_week_plural": "weeks",
        "chart_line_title_prefix": "wait times across all hospitals",
        "chart_xaxis_date": "Date",
        "chart_yaxis_waittime": "Wait time (weeks)",

        #----------- Information Page ----------
        "page_title_information": "More Information - ScanWait Wales",
        "heading1": "About ScanWait Wales",
        "about_text": "ScanWait Wales was produced as an accessibility tool by a group of outstandingly smart, attractive, philanthropic, humble students studying for a Data Science and Analytics MSc at Cardiff University.",
        "about_text2": "ScanWait Wales is designed to help patients explore scanning wait times from NHS Wales and identify hospitals that may offer a selected scan. We are not affiliated with NHS Wales and we do not have access to NHS patient records, NHS numbers, clinical notes or individual appointment information. The estimated results do not represent an individual appointment. The application uses publicly available hospital information, postcode reference datasets and aggregated waiting-time statistics. No information is stored when using this service.",
        "about_text3": "Our goal is to make publicly available information easier to understand and navigate. It is an information tool and does not provide individual appointment advice or determine clinical priority.",
        "heading2": "The Team",
        "team_text": "Eleri Hayman - Welsh Language Developer<br>Charlie Hastings- User Interface & Experience Developer<br>Faith Hamelin - Backend Developer<br>Revée O'Neal-Allamby - User Interface Developer<br>Gerald Alimon - Backend Developer<br><br>",
        "team_sub": "Contact Us<br>",
        "team_text2": "If you have any concerns, questions or just want a general chat about this project, please contact us via haymane@cardiff.ac.uk",
        "heading3": "Data Privacy",
        "privacy_text": "The application only asks for the information necessary to perform the search: selected scan and, for the nearest hospital function, postcode.",
        "privacy_text2": "The postcode is used temporarily to obtain coordinates and is never stored by the application's database. The application does not store combinations of postcode, scan selection, IP address or other identifiers. This is in accordance with the",
        "privacy_text_link": "UK Data Protection Legislation Principles",
        "heading4": "Use of External Services",
        "external_text": "If you select to use the postcode distance tool, your postcode will then be sent to Postcodes.io. The services obtains approximate coordinates and sends them to the OpenStreetMap Routing Machine (OSRM) to calculate driving or walking information. We do not send any other data to external providers. We have used the ",
        "external_text_link": "UKSA data ethics checklists in the use of geospatial data",
        "external_text2": "to produce our postcode mapping feature.",
        "heading5": "Fairness and Inclusion",
        "fairness_text": "Ranking by straight-line distance does not always identify the hospital that is easiest to reach. Rural roads, public transport, mobility requirements and whether a user has access to a car may affect the real journey. Providing a nearest-three option with travel routing and an all-hospitals option helps users define what they think are their 'nearest' hospitals.",
        "heading6": "Accessability",
        "access_text": "The ScanWait Wales website has been designed and developed with the needs of individuals with visual and colour impairments or difficulty reading in mind.",
        "access_sub": "Visual and Colour Impairment",
        "access_text2": "The website's main font is Verdana - which was selected for its clarity. No text is smaller than 12pt, and the majority of it is a dark colour on a light (but not white) background to help with readability. The main site colours of white, red, and green were inspired by the Welsh flag. These colours have been adjusted in accordance with ",
        "access_link": "WCAG guidelines",
        "access_text3": "to provide sufficient contrast between text and the background. The primary background of the site is an off-white, which was selected to improve readability and reduce glare.",
        "access_text4": "Colours outside the main scheme (used in visualisations) were chosen as they are visually distinct from the main theme, but still maintain a minimum contrast to comply with WCAG AA standards.",
        "access_text5": "In addition to the above, we have chosen to avoid conveying important information exclusively through the use of colour. Hover text and varied opacity have been used in the visualisations where this is not possible.",
        "access_sub2": "Screen Readers",
        "access_text6": "For visitors using screen readers, the number of links per page have been kept to a minimum and are sufficiently descriptive without requiring the additional context of the surrounding text. We have also chosen to avoid using emojis throughout the website. These decisions have been made to comply with the ",
        "access_link2": "Equality Act 2010.",
        "access_text7": "Colour contrasts were checked using the ",
        "access_link3": "WebAIM contrast checker.",
        "access_text8": "Please note, our website has not been tested by blind or partially sighted users.",
        "heading7": "Language Options",
        "language_text": "Our application is available in both Welsh and English in line with the ",
        "language_link": "Welsh Language Measure 2011.",
        "language_text2": "We have provided Welsh and English versions that contain equivalent information.",
        "language_text3": "Please note, there may be fewer errors in the Welsh. ",
        "language_link2": "Cysill Ar-Lein",
        "language_text4": "was used to proof check the spelling and grammar but some errors may still have been missed. We are happy to take any feedback about improvements from users.",
        "heading8": "Licence",
        "licence_text": "This webapp is licensed under the ",
        "licence_link":"Government Licence v3.0.",
        "licence_text2": "The underlying git repository is under a ",
        "licence_link2": "MIT Licence.",
        "heading9": "Methodology",
        "method_sub": "What Data We Use<br>",
        "method_text": "The official",
        "method_link": "StatsWales dataset for all of our waiting-time records.",
        "method_text2": "We filter this data so that we only look at adult patients (18 years of age and over). Whenever you check a wait time, we calculate it using the most recent month",
        "method_sub2": "How We Work Out the Typical Wait<br>",
        "method_text3": "To find the typical (median) wait for a specific scan at your chosen hospital, we do the following:",
        "method_text4": "- We add up all the patients currently waiting for that specific scan to get the total list size. <br>"
        "- We find the exact halfway point (50%) of that patient queue <br>"
        "- We count up through the weekly waiting bands until we pass that halfway point.<br>"
        "- To give you a safe and conservative estimate, we report the upper end of that weekly band.<br>"
        "- If the halfway point lands in the highest band (40 weeks and over), we simply report it as 40 weeks.<br>",
        "method_text5": "This method is referred to as a <i>Cumulative Frequency Distribution</i>. It is a simple and robust way to estimate wait times and is commonly used within ",
        "method_link2": " healthcare.",
        "method_text6": "Its limitations lie in the fact that it is based on current trends rather than future predictions.",
        "heading10": "What the Wait Time Gauge Means",
        "gauge_text": "To make the wait times easy to read at a glance, we classify them into colour zones and use a visual speedometer: According to the ",
        "gauge_link": "Welsh government",
        "gauge_text2": "you should not be waiting more than 8 weeks for your scan.",
        "guage_text3": "- Green: A wait of 8 weeks or less. [within government targets]<br>"
        "- Orange: A wait between 9 and 12 weeks.<br>"
        "- Red: A wait of 13 weeks or longer.<br>",
        "heading11": "Validation",
        "validation_text": "New data is released towards the end of each month. Before we use that data, we inspect the data for any changes in its presentation and we calculate all possible outputs using a much slower but auditable method. These numbers are then checked against the output of our main calculator. We only use this new data when it passes all our checks.",
        "heading12": "Data Limitations",
        "limit_text": "The data published from StatsWales is aggregated from monthly reports from all the health boards in Wales which is then used to measure their performance.",
        "limit_sub": "Urgency",
        "limit_text2": "It does not categorize data on 'urgency' therefore some patients who might have been classified as urgent would expect a shorter wait time. Consequently, a large influx of 'urgent' patients in a single month might mean that 'routine' patients could expect longer waits.",
        "limit_sub2": "Incomplete Information on Scanning Locations",
        "limit_text3": "As of 2026, there is no publicly available database that contains information on what specific diagnostic services are offered in each and every hospital in Wales. Some hospitals mention it in their websites but the list is not comprehensive and most don't have that information readily available. We are working to request that information to be made public, as we believe that the public should know which services are available in their community.",
        "limit_sub3": "Ghost Scanners",
        "limit_text4": "The data published by StatsWales contains some hospital waiting lists for scans which are not offered in that hospital. For example, a rural community hospital offering MRI scans. We try our best to filter out these obvious mistakes, but without a comprehensive hospital-scanner database, we can never be certain.",

                # ---------- Age Group & Stock-and-Flow Trend ----------
        "input_label_age_group": "Select patient age group:",
        "age_group_adult": "Adult (18+)",
        "age_group_child": "Child (under-18)",
        "output_age_group_label": "Age group:",
        "output_predicted_wait_label": "Projected next-month wait:",
        "output_trend_rising": "Queue trend: Rising",
        "output_trend_falling": "Queue trend: Falling",
        "output_trend_stable": "Queue trend: Stable",

        # ---------- Language Switch ----------
        # This is the text on the button that switches to the other language.
        "language_switch_to": "Cymraeg",
    },

    "cy": {
        # ---------- Welcome Page ----------
        "page_title": "ScanWait Cymru Tudalen Groeso",

        # --- Navigation Bar ---
        "nav_brand": "ScanWait Cymru",
        "nav_home": "Hafan",
        "nav_input": "Amseroedd Aros", 
        "nav_visualisations": "Archwilio Data",
        "nav_information": "Mwy o Wybodaeth",

        # --- Main Content ---
        "welcome_subtitle": "<b>Croeso i ScanWait Cymru</b> - <i>y safle answyddogol i ganfod pa mor hir y gallai fod yn rhaid i chi aros am eich sgan nesaf.</i>",
        "welcome_description": "Rydyn ni'n cymryd y data a gyhoeddir yn fisol gan GIG Cymru, yn rhedeg ein cyfrifiadau, ac (yn gobeithio) yn rhoi syniad i chi o ba mor hir y gallwch chi fod yn aros am eich sgan i ddigwydd. I wybod mwy, ewch i Mwy o Wybodaeth.",
        "welcome_text": "Mae ScanWait Cymru wedi'i gynllunio i helpu cleifion i archwilio amseroedd aros sganio o GIG Cymru a nodi ysbytai a allai gynnig sgan dethol. Nid ydym yn gysylltiedig â GIG Cymru ac nid oes gennym fynediad at gofnodion cleifion y GIG, rhifau'r GIG, nodiadau clinigol na gwybodaeth am apwyntiadau unigol. Nid yw'r canlyniadau amcangyfrifed yn cynrychioli penodiad unigol. Mae'r cais yn defnyddio gwybodaeth ysbyty sydd ar gael i'r cyhoedd, setiau data cyfeirio cod post ac ystadegau amser aros agregedig. Ni chaiff unrhyw wybodaeth ei storio wrth ddefnyddio'r gwasanaeth hwn.",

        # ---------- Input Page ----------
        "page_title_input": "Amseroedd Aros - ScanWait Cymru",
        "input_heading": "Dewis Ysbyty a Math o Sgan",
        "input_instruction": "Dewiswch ysbyty a math o sgan o'r dewislenni isod.",
        "input_label_service": "Dewiswch fath o sgan",
        "input_label_location": "Dewiswch ysbyty:",
        "calculate_button": "Cyfrifo",

        #---------- Input Postcode ----------
        "heading_postcode": "Gwiriwch yr amseroedd aros amcangyfrifed ar gyfer eich sgan",
        "info_disclaimer": "Ni fydd unrhyw un o'r wybodaeth a ddarparwch yn cael ei storio.",
        "selection_process": "Sgan -> Ysbyty -> Canlyniad",
        "input_postcode": "Rhowch god post yng Nghymru:",
        "input_nearest": "Gwirio Agosaf",
        "input_all_hospitals": "Holl ysbytai Cymru sy'n cynnig y sgan hwn",
        "input_three_hospitals": "Tri ysbyty agosaf",
        "ranked_postcode": "Mae ysbytai yn cael eu rhestru yn ôl pellter llinell syth o",
        "input_health_board": "Bwrdd Iechyd",

        # ---------- Health Board Name Translations ----------
        "health_board_Aneurin_Bevan": "Aneurin Bevan",
        "health_board_Betsi_Cadwaladr": "Betsi Cadwaladr",
        "health_board_Cardiff_and_Vale": "Caerdydd a'r Fro",
        "health_board_Cwm_Taf_Morgannwg": "Cwm Taf Morgannwg",
        "health_board_Hywel_Dda": "Hywel Dda",
        "health_board_Swansea_Bay": "Bae Abertawe",

        "all_hospitals": "Pob ysbyty sy'n cynnig",
        "input_placeholder": "Er enghraifft, CF10 1EP",
        "label_select_hospital": "Dewiswch ysbyty:",
        "option_choose_hospital": "Dewiswch ysbyty",
        "drive_label": "Gyrru:",
        "walk_label": "Cerdded:",
        "unavailable": "Ddim ar gael",

        # ---------- Hospital Card Labels ----------
        "label_hospital": "Ysbyty:",
        "label_distance": "Pellter:",
        "label_healthboard": "Bwrdd Iechyd:",
        "miles_away": "milltir i ffwrdd o'r cod post",
        "view_wait_time_button": "Gweld yr amser aros amcangyfrifedig",
        "view_all_hospitals_button": "Gweld pob ysbyty sy'n cynnig y sgan hwn",
        "nearby_alternatives_heading": "Dewisiadau Cyfagos",

        # ---------- Output Page ----------
        "page_title_output": "Amser Aros Cyfrifedig - ScanWait Cymru",
        "output_wait_prefix": "Yr amser aros amcangyfrifedig cyfredol ar gyfer",
        "output_wait_at": "yn",
        "output_wait_is": "yw",
        "output_wait_around": "o gwmpas",
        "output_weeks": "wythnos",
        "output_source_prefix": "Mae hyn yn seiliedig ar ddata",
        "output_source_suffix": "a ddarparwyd gan StatsWales. Nid yw'r canlyniadau amcangyfrifed yn cynrychioli penodiad unigol.",
        "output_more_info": "I ddarganfod mwy am y set ddata a sut mae'r cyfrifiad hwn yn cael ei wneud a'i gyfyngiadau, ewch i ",
        "output_more_info_link": "Mwy o Wybodaeth",
        "output_bottom_disclaimer": "Yn seiliedig ar ddata",
        "output_bottom_disclaimer_link": "a ddarparwyd gan StatsWales. I gael gwybod mwy, ewch i",

        # ---------- Scan Type Translations ----------
        "scan_type_CT": "CT",
        "scan_type_MRI": "MRI",
        "scan_type_Ultrasound": "Ultrawstŷn",
        "scan_type_Nuclear_Medicine": "Meddygaeth Niwclear",
        "scan_type_Fluoroscopy": "Fflworosgopi",
        "scan_type_Diagnostic_Angiography": "Angiograffeg Ddiagnostig",
        "scan_type_Cardiac_CT": "CT [Cardiag yn unig]",
        "scan_type_Cardiac_MRI": "MRI [Cardiag yn unig]",
        "scan_type_Nuclear_Medicine_Cardiac": "Meddygaeth Niwclear [Cardiag / Myocardial Perfusion]",

        # ---------- Month Translations ----------
        "month_January": "Ionawr",
        "month_February": "Chwefror",
        "month_March": "Mawrth",
        "month_April": "Ebrill",
        "month_May": "Mai",
        "month_June": "Mehefin",
        "month_July": "Gorffennaf",
        "month_August": "Awst",
        "month_September": "Medi",
        "month_October": "Hydref",
        "month_November": "Tachwedd",
        "month_December": "Rhagfyr",

        # ---------- Gauge / Speedometer ----------
        "gauge_label_0": "0 Wythnos",
        "gauge_desc_0": "Ar y targed",
        "gauge_label_8": "8 Wythnos",
        "gauge_desc_8": "Yn agosáu at y terfyn",
        "gauge_label_15": "15+ Wythnos",
        "gauge_desc_15": "Wedi rhagori ar y targed",
        "gauge_unit": "Wythnos",
        "gauge_unit_singular": "Wythnos",
        "status_green": "Ar y trywydd cywir — o fewn y targed 8 wythnos",
        "status_orange": "Dros y targed — 8 wythnos neu fwy",
        "status_red": "Oedi sylweddol — mwy nag 8 wythnos",

        # --- Visualisations Page (menu) ---
        "vis_page_title": "Graffiau - ScanWait Cymru",
        "vis_welcome_heading": "Croeso i'r Tudalen Graffiau",
        "vis_instruction": "Defnyddiwch y dudalen hon i lywio i'r gwahanol raffiau sydd ar gael. Ein nod yma yw gwneud y data yn rhyngweithiol ac yn hygyrch i'r cyhoedd. Cliciwch y ddelwedd i weld graff.",
        "vis_card_heatmap_title": "Map gwres o amseroedd aros dros Gymru",
        "vis_card_heatmap_desc": "Map gwres rhyngweithiol o amseroedd aros sganio dros Gymru.",
        "vis_card_heatmap_alt": "Eicon: map o Gymru",
        "vis_card_barchart_title": "Graff bar sy'n cymharu ysbytai",
        "vis_card_barchart_desc": "Graff bar pentyrru o amseroedd aros ar gyfer pob sgan ar draws pob ysbyty.",
        "vis_card_barchart_alt": "Eicon: graff bar",
        "vis_card_linechart_title": "Graff llinell cyfresi cyfnod",
        "vis_card_linechart_desc": "Graff llinell ryngweithiol o amseroedd aros ers Awst 2024.",
        "vis_card_linechart_alt": "Eicon: graff llinell",

                # --- Heatmap Page ---
        "heat_page_title": "Map Gwres Amseroedd Aros - ScanWait Cymru",
        "heat_back_button": "← Nôl i graffiau",
        "heat_heading": "Amser aros dros Gymru",
        "heat_instruction": "Dewiswch fath o sgan i weld amser aros am ysbytai dros Gymru.",
        "heat_colour_explain": "Mae'r cysgod ysgafnaf o goch yn cynrychioli'r amser aros byrraf o wythnos. Mae'r cysgod tywyllaf o goch yn cynrychioli'r amseroedd aros hiraf o 15 wythnos neu fwy.",
        "heat_nhs_target": "<br><br>Y <strong>targed GIG Cymru</strong> an sganiau diagnostig yw <strong>8 wythnos</strong>.",
        "heat_label_scan": "Dewiswch fath o sgan:",
        "heat_dropdown_placeholder": "Dewiswch sgan",
        "heat_map_message_placeholder": "Dewiswch fath o sgan plîs",
        "heat_map_message_no_coords": "Ni ddarganfuwyd unrhyw ysbytai gyda chyfesurynnau ar gyfer y math o sgan hwn.",
        "heat_hospital_singular": "ysbyty",
        "heat_hospital_plural": "ysbytai",
        "heat_shown_for": "dangos am",
        "heat_colourbar_title": "Amser aros (wythnos)",
        "heat_map_title_prefix": "Amser aros am ",
        "heat_hover_wait": "Amser aros",
        "heat_weeks_abbreviation": "w",

        # --- Stacked Bar Chart Page ---
        "stacked_page_title": "Siart Bar Pentyrru - ScanWait Cymru",
        "stacked_back_button": "← Nôl i graffiau",
        "stacked_heading": "Cymharu amseroedd aros dros ysbytai dethol yng Nghymru",
        "stacked_nhs_target": "Y targed GIG Cymru am amser aros am sganiau diagnostig yw 8 wythnos.",

        # --- Line Graph Page ---
        "line_page_title": "Graff llinell cyfresi cyfnod - ScanWait Cymru",
        "line_back_button": "← Nôl i graffiau",
        "line_heading": "Cymharu amseroedd aros dros ysbytai dethol yng Nghymru",
        "line_nhs_target": "Y targed GIG Cymru am amser aros am sganiau diagnostig yw 8 wythnos.",
        "line_filter_label": "Hidlo gan fath o sgan:",
        "line_visualise_button": "Gweld",

        # --- Plotly Chart Text ---
        "chart_title_summary": "Crynodeb o amser aros am sgan dros holl ysbytai",
        "chart_xaxis_hospital": "Ysbyty",
        "chart_yaxis_weeks": "Amser aros (wythnos)",
        "chart_legend_scan_type": "Fath o sgan",
        "chart_hover_scan": "Sgan",
        "chart_hover_wait": "Amser aros",
        "chart_weeks": "wythnos",
        "chart_week_singular": "wythnos",
        "chart_week_plural": "wythnosau",
        "chart_line_title_prefix": "amser aros dros holl ysbytai",
        "chart_xaxis_date": "Dyddiad",
        "chart_yaxis_waittime": "Amser aros (wythnis)",

        #----------- Information Page ----------
        "page_title_information": "Mwy o Wybodaeth - ScanWait Cymru",
        "heading1": "Amdan ScanWait Cymru",
        "about_text": "Cynhyrchwyd ScanWait Wales fel offeryn hygyrchedd gan grŵp o fyfyrwyr eithriadol o glyfar, deniadol, dyngarol a gostyngedig sy'n astudio ar gyfer gradd Meistr Gwyddor Data a Dadansoddet ym Mhrifysgol Caerdydd.",
        "about_text2": "Mae ScanWait Wales wedi'i gynllunio i helpu cleifion i archwilio amseroedd aros sganio o GIG Cymru a nodi ysbytai a allai gynnig sgan dethol. Nid ydym yn gysylltiedig â GIG Cymru ac nid oes gennym fynediad at gofnodion cleifion y GIG, Rhifau'r GIG, nodiadau clinigol neu wybodaeth am apwyntiadau unigol. Nid yw'r canlyniadau amcangyfrifed yn cynrychioli penodiad unigol. Mae'r cais yn defnyddio gwybodaeth ysbyty sydd ar gael i'r cyhoedd, setiau data cyfeirio cod post ac ystadegau amser aros agregedig. Ni chaiff unrhyw wybodaeth ei storio wrth ddefnyddio'r gwasanaeth hwn.",
        "about_text3": "Ein nod yw gwneud gwybodaeth sydd ar gael i'r cyhoedd yn haws i'w deall a'i llywio. Mae'n offeryn gwybodaeth ac nid yw'n darparu cyngor apwyntiad unigol nac yn pennu blaenoriaeth glinigol.",
        "heading2": "Y Tîm",
        "team_text": "Eleri Hayman- Datblygwr Iaith Gymraeg<br>Charlie Hastings- Datblygwr Rhyngwyneb & Phrofiad Defnyddiwr<br>Faith Hamelin - Datblygwr Cefn<br>Revée O'Neal-Allamby - Datblygwr Rhyngwyneb Defnyddiwr<br>Gerald Alimon - Datblygwr Cefn<br><br>",
        "team_sub": "Cysylltu â Ni<br>",
        "team_text2": "Os oes gennych chi unrhyw bryderon, cwestiynau neu eisiau sgwrs gyffredinol am y prosiect hwn, cysylltwch â ni drwy haymane@cardiff.ac.uk",
        "heading3": "Preifatrwydd Data",
        "privacy_text": "Mae'r cais yn gofyn am y wybodaeth sy'n angenrheidiol i berfformio'r chwiliad yn unig: sgan dethol ac, ar gyfer y swyddogaeth ysbyty agosaf, cod post.",
        "privacy_text2": "Mae'r cod post yn cael ei ddefnyddio dros dro i gael cyfesurynnau ac nid yw byth yn cael ei storio gan gronfa ddata y cais. Nid yw'r cais yn storio cyfuniadau o god post, dewis sganio, cyfeiriad IP neu ddynodwyr eraill. Mae hyn yn unol ag",
        "privacy_text_link": "Egwyddorion Deddfwriaeth Diogelu Data'r Prydain.",
        "heading4": "Defnyddio Gwasanaethau Allanol",
        "external_text": "Os byddwch yn dewis defnyddio'r offeryn pellter cod post, bydd eich cod post wedyn yn cael ei anfon at Postcodes.io. Mae'r gwasanaethau yn cael cyfesurynnau bras ac yn eu hanfon i OpenStreetMap Routing Machine (OSRM) i gyfrifo gwybodaeth gyrru neu gerdded. Nid ydym yn anfon unrhyw ddata arall at ddarparwyr allanol. Rydyn ni wedi defnyddio ",
        "external_text_link": "rhestrau gwirio moeseg data USKA wrth ddefnyddio data gofodol",
        "external_text2": "i gynhyrchu ein nodwedd mapio cod post.",
        "heading5": "Tegwch a Chynhwysiant",
        "fairness_text": "Nid yw graddio yn ôl pellter llinell syth bob amser yn nodi'r ysbyty sy'n hawsaf i'w gyrraedd. Gall ffyrdd gwledig, trafnidiaeth gyhoeddus, gofynion symudedd ac a oes gan ddefnyddiwr fynediad at gar effeithio ar y daith go iawn. Mae darparu opsiwn tri agosaf gyda llwybro teithio ac opsiwn pob ysbyty yn helpu defnyddwyr i ddiffinio beth maen nhw'n meddwl yw eu hysbytai 'agosaf'",
        "heading6": "Hygyrchedd",
        "access_text": "Mae gwefan ScanWait Cymru wedi'i dylunio a'i datblygu gan ystyried anghenion unigolion â nam ar eu golwg a lliw neu anhawster darllen.",
        "access_sub": "Amhariad ar y golwg a lliw",
        "access_text2": "Prif ffont y wefan yw Verdana - a ddewiswyd am ei eglurder. Nid oes unrhyw destun yn llai na 12pt, ac mae'r mwyafrif ohonyn nhw yn lliw tywyll ar gefndir golau (ond nid gwyn) i helpu gyda darllenodd. Ysbrydolwyd prif liwiau'r safle gwyn, coch a gwyrdd gan faner Cymru. Mae'r lliwiau hyn wedi'u haddasu yn unol â ",
        "access_link": "chanllawiau WCAG ",
        "access_text3": "i ddarparu digon o gyferbyniad rhwng y testun a'r cefndir. Prif gefndir y wefan yw gwyn oddi ar y gwefan a ddewiswyd i wella darllenodd a lleihau disgleirdeb.",
        "access_text4":"Dewiswyd lliwiau y tu allan i'r brif thema (a ddefnyddir mewn graffiau) gan eu bod yn weledol wahanol i'r brif thema, ond yn dal i gynnal cyferbyniad lleiaf i gydymffurfio â safonau WCAG AA.",
        "access_text5": "Yn ogystal â'r uchod, rydyn ni wedi dewis osgoi dangos gwybodaeth bwysig trwy ddefnyddio lliw yn unig. Defnyddiwyd testun hofran a thryloywder amrywiol yn y graffiau lle nad yw hyn yn bosibl.",
        "access_sub2": "Darllenwyr Sgrin",
        "access_text6": "Ar gyfer ymwelwyr sy'n defnyddio darllenwyr sgrin, mae nifer y dolenni fesul tudalen wedi'u cadw i'r lleiafswm ac maent yn ddigon disgrifiadol heb fod angen cyd-destun ychwanegol y testun amgylchynol. Rydym hefyd wedi dewis osgoi defnyddio emojis ledled y wefan. Mae'r penderfyniadau hyn wedi'u gwneud i gydymffurfio â ",
        "access_link2": "Deddf Cydraddoldeb 2010.",
        "access_text7": "Gwiriwyd cyferbyniadau lliw gan ddefnyddio'r ", 
        "access_link3": "gwiriwr cyferbyniad WebAIM.", 
        "access_text8": "Sylwer, nid yw ein gwefan wedi'i phrofi gan ddefnyddwyr dall neu rannol olwg.",
        "heading7": "Dewisiadau Iaith",
        "language_text": "Mae ein cais ar gael yn Gymraeg a Saesneg yn unol â ",
        "language_link": "Mesur y Gymraeg 2011.",
        "language_text2": "Rydyn ni wedi darparu fersiynau Cymraeg a Saesneg sy'n cynnwys gwybodaeth gyfatebol.",
        "language_text3": "Nodwch, efallai y bydd llai o wallau yn y Gymraeg. Defnyddiwyd ",
        "language_link2": "Cysill Ar-lein",
        "language_text4": " i wirio'r sillafu a'r gramadeg ond efallai bod rhai gwallau wedi'u colli o hyd. Rydyn ni'n hapus i gymryd unrhyw adborth am welliannau gan ddefnyddwyr.",
        "heading8": "Trwydded",
        "licence_text": "Mae'r ap gwe hwn wedi'i drwyddedu o ",
        "licence_link": "Drwydded y Llywodraeth v3.0. ",
        "licence_text2": "Mae'r storfa git sylfaenol o dan ",
        "licence_link2": "drwydded MIT.",
        "heading9": "Methodoleg",
        "method_sub": "Pa Ddata Rydyn Ni'n Ddefnyddio",
        "method_text": "Set ddata swyddogol ",
        "method_link": "StatsCymru ar gyfer ein holl gofnodion amser aros.",
        "method_text2": "Rydyn ni'n hidlo'r data hwn fel ein bod yn edrych ar gleifion sy'n oedolion (18 oed a hŷn) yn unig. Pryd bynnag y byddwch chi'n gwirio amser aros, rydym yn ei gyfrifo gan ddefnyddio'r mis diweddaraf a gyhoeddwyd yn y set ddata.",
        "method_sub2": "Sut Rydyn Ni'n Gweithio Allan yr Aros Nodweddiadol ",
        "method_text3": "Ddod o hyd i'r aros nodweddiadol (canolrif) am sgan penodol yn eich ysbyty dewisol, rydyn ni'n gwneud y canlynol:",
        "method_text4": "- Rydyn ni'n adio'r holl gleifion sy'n aros am y sgan penodol hwnnw ar hyn o bryd i gael cyfanswm maint y rhestr.<br>"
        "- Rydyn ni'n dod o hyd i'r union bwynt hanner ffordd (50%) o'r ciw claf hwnnw.<br>"
        "- Rydyn ni'n cyfrif i fyny trwy'r bandiau aros wythnosol nes i ni basio'r pwynt hanner ffordd hwnnw.<br>"
        "- I roi amcangyfrif diogel a cheidwadol i chi, rydyn ni'n adrodd pen uchaf y band wythnosol hwnnw.<br>"
        "- Os yw'r pwynt hanner ffordd yn glanio yn y band uchaf (40 wythnos a throsodd),  rydyn ni'n syml yn ei adrodd fel 40 wythnos.<br>",
        "method_text5": "Cyfeirir at y dull hwn fel Dosbarthiad Amledd Cronnus. Mae'n ffordd syml a chadarn o amcangyfrif amseroedd aros ac fe'i defnyddir yn gyffredin o fewn ",
        "method_link2": "gofal iechyd.",
        "method_text6": "Mae ei gyfyngiadau yn gorwedd yn y ffaith ei fod yn seiliedig ar dueddiadau cyfredol yn hytrach na rhagfynegiadau yn y dyfodol.",
        "heading10": "Beth Mae'r Mesurydd Amser Aros yn ei Olygu",
        "gauge_text": "Er mwyn gwneud yr amseroedd aros yn hawdd i'w darllen ar yr olwg, rydym yn eu dosbarthu'n barthau lliw ac yn defnyddio cyflymder gweledol: Yn ôl ",
        "gauge_link": "Llywodraeth Cymru,",
        "gauge_text2": "ni ddylech fod yn aros mwy nag 8 wythnos am eich sgan.",
        "guage_text3": "-	Gwyrdd: Aros o 8 wythnos neu lai. [o fewn targedau'r llywodraeth]<br>"
        "- Oren: Aros rhwng 9 a 12 wythnos.<br>"
        "- Coch: Aros o 13 wythnos neu fwy.<br>",
        "heading11": "Dilysu",
        "validation_text": "Mae data newydd yn cael ei ryddhau tua diwedd pob mis. Cyn i ni ddefnyddio'r data hwnnw, rydym yn archwilio'r data am unrhyw newidiadau yn ei gyflwyniad ac rydym yn cyfrifo'r holl allbynnau posibl gan ddefnyddio dull archwilio sy’n arafach. Yna mae'r rhifau hyn yn cael eu gwirio yn erbyn allbwn ein prif gyfrifiannell. Dim ond pan fydd yn pasio ein holl wiriadau rydyn ni'n defnyddio'r data newydd hwn.",
        "heading12": "Cyfyngiadau Data",
        "limit_text": "Mae'r data a gyhoeddir gan StatsCymru yn cael ei agregu o adroddiadau misol gan yr holl fyrddau iechyd yng Nghymru sydd wedyn yn cael eu defnyddio i fesur eu perfformiad.",
        "limit_sub": "Brys",
        "limit_text2": "Nid yw yn categoreiddio data ar 'frys', felly byddai rhai cleifion a allai fod wedi'u dosbarthu fel brys yn disgwyl amser aros byrrach. O ganlyniad, gallai mewnlifiad mawr o gleifion 'brys' mewn un mis olygu y gallai cleifion 'arferol' ddisgwyl aros hirach.",
        "limit_sub2": "Gwybodaeth Anghyflawn am Leoliadau Sganio",
        "limit_text3": "O 2026 ymlaen, nid oes cronfa ddata sydd ar gael i'r cyhoedd, sy'n cynnwys gwybodaeth am ba wasanaethau diagnostig penodol sy'n cael eu cynnig ym mhob ysbyty yng Nghymru. Mae rhai ysbytai yn sôn amdano yn eu gwefannau ond nid yw'r rhestr yn gynhwysfawr ac nid oes gan y mwyafrif y wybodaeth honno ar gael yn rhwydd. Rydym yn gweithio i ofyn i'r wybodaeth honno gael ei gwneud yn gyhoeddus, gan ein bod yn credu y dylai'r cyhoedd wybod pa wasanaethau sydd ar gael yn eu cymuned.",
        "limit_sub3": "Sganwyr Ysbrydion",
        "limit_text4": "Mae'r data a gyhoeddwyd gan StatsCymru yn cynnwys rhai rhestrau aros ysbytai ar gyfer sganiau nad ydynt yn cael eu cynnig yn yr ysbyty hwnnw. Er enghraifft, ysbyty cymunedol gwledig sy'n cynnig sganiau MRI. Rydym yn ceisio ein gorau i hidlo'r camgymeriadau amlwg hyn, ond heb gronfa ddata cynhwysfawr o sganwyr ysbyty, ni allwn byth fod yn sicr.",       



                # ---------- Age Group & Stock-and-Flow Trend ----------
        "input_label_age_group": "Dewiswch grŵp oedran y claf:",
        "age_group_adult": "Oedolyn (18+)",
        "age_group_child": "Plentyn (dan 18)",
        "output_age_group_label": "Grŵp oedran:",
        "output_predicted_wait_label": "Amser aros rhagamcanol y mis nesaf:",
        "output_trend_rising": "Tuedd y ciw: Yn codi",
        "output_trend_falling": "Tuedd y ciw: Yn gostwng",
        "output_trend_stable": "Tuedd y ciw: Sefydlog",

        # ---------- Language Switch ----------
        "language_switch_to": "English",
    },
}

# This function allows other files to import the text in the correct language depending on the user's choice.
# English is the default language if no choise is made or if the language code is not recognised.
def get_translations(language_code):
    if language_code not in TRANSLATIONS:
        language_code = "en"

    return TRANSLATIONS[language_code]

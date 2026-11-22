# Ansawdd Data a Chafeatau'r Set Ddata

Mae'r dudalen hon yn dogfennu anghysondebau adrodd hysbys, cafeatau gweinyddol, a rheolau glanhau data sy'n effeithio ar ddata amseroedd aros diagnostig GIG Cymru a ddefnyddir yn **ScanWait Wales**.

---

## Ffynhonnell y Set Ddata a Metadata Swyddogol

* **Set Ddata:** [Gwasanaethau diagnostig: amseroedd aros llwybrau, Awst 2024 ymlaen (ID y Set Ddata: `3c2720e6-95ae-4eeb-9e88-ed74bb40c6b9`)](https://stats.gov.wales/en-GB/3c2720e6-95ae-4eeb-9e88-ed74bb40c6b9/start#about)
* **Dynodiad a Chyhoeddwr:** Ystadegau swyddogol achrededig a gyhoeddir gan **Lywodraeth Cymru** (`stats.healthinfo@gov.wales`).
* **Darparwr Data a Chasglu:** Wedi'i lunio gan **Iechyd a Gofal Digidol Cymru (DHCW)** o'r ffurflen **Amseroedd Aros Gwasanaethau Diagnostig a Therapi (DATS)**, a dynnir yn uniongyrchol o systemau gweinyddol cleifion Byrddau Iechyd Lleol.
* **Cwmpas ac Amserlen Gyhoeddi:** Yn cwmpasu cipluniau misol o **Awst 2024 i Fedi 2026** (cyhoeddwyd y set ddata gyntaf ar **23 Hydref 2025**; y diweddariad nesaf wedi'i drefnu ar gyfer **23 Rhagfyr 2026**).
* **Dogfennaeth Ansawdd Swyddogol Gysylltiedig:** [Crynodeb o weithgarwch a pherfformiad y GIG: adroddiad ansawdd (Llywodraeth Cymru)](https://www.gov.wales/nhs-activity-and-performance-summary-september-and-october-2026-html)
* **Dim Diwygiadau Ôl-weithredol:** Yn unol â [dogfennaeth set ddata StatsCymru](https://stats.gov.wales/en-GB/3c2720e6-95ae-4eeb-9e88-ed74bb40c6b9/start#about), gan fod y ffigurau'n cael eu tynnu o systemau gweinyddol byw Byrddau Iechyd Lleol, **ni ellir cynhyrchu ffigurau diwygiedig** ar ôl eu cyhoeddi. Mae bylchau cyflwyno hanesyddol ac anghysondebau codio safleoedd felly'n aros yn barhaol yn y gyfres amser gyhoeddedig.

---

## Cofnod Cronolegol o Faterion ac Anghysondebau Ansawdd Data

### Tachwedd 2026 — Dilysu Safleoedd Ysbytai a Hidlo "Sganwyr Ysbryd" (FOI 2026 148)
* **Mapio Offer Heb ei Ddilysu:** Datgelodd croeswirio cofnodion lefel ysbyty StatsCymru yn erbyn seilwaith radioleg ffisegol fod ysbytai llai ac ysbytai cymunedol yn cael eu hadrodd gyda rhestrau aros gweithredol ar gyfer sganwyr arbenigol nad ydynt yn eu gweithredu ar y safle (er enghraifft, cofnodwyd *Ysbyty Cymunedol Rhuthun* gyda chleifion yn aros am Feddygaeth Niwclear Heb fod yn Gardiaidd).
* **Labeli Safleoedd Anffisegol / Cyffredinol:** Mae set ddata crai StatsCymru yn cynnwys pum bwced gweinyddol nad ydynt yn ysbytai (`Community` o dan BIP Betsi Cadwaladr [Cyf 19] a BIP Aneurin Bevan [Cyf 22]; `Unallocated in Aneurin Bevan University LHB` [Cyf 209]; `Unknown Sites in Cwm Taf Morgannwg` [Cyf 193]; a `Trust` o dan BIP Bae Abertawe [Cyf 174]), yn ogystal â chofnod dyblyg o safle-bwrdd (`Royal Glamorgan` wedi'i restru o dan BIP Cwm Taf Morgannwg [Cyf 164] a BIP Caerdydd a'r Fro [Cyf 97]).
* **Lliniaru yn ScanWait Wales:** Cyflwynwyd ceisiadau Rhyddid Gwybodaeth (**FOI 2026 148**) i bob un o'r saith Bwrdd Iechyd Lleol ac Ymddiriedolaeth GIG Prifysgol Felindre i ddilysu argaeledd sganwyr parhaol a symudol ar draws 10 dull delweddu. Mae ScanWait Wales yn hidlo pob allbwn trwy dabl cyfeirio wedi'i ddilysu (`selected_hospitals_services_coordinates.csv`) fel mai dim ond ar gyfer parau ysbyty–sganiwr wedi'u cadarnhau y cyhoeddir amseroedd aros.

### Medi 2026 — Anwadalrwydd Enwadur Bach mewn Sganiau Cardiaidd Arbenigol
* **Mater:** Mae dulliau cardiaidd arbenigol gyda chiwiau bach iawn (1 i 40 o gleifion) yn dangos newidiadau canrannol mawr o ganlyniad i newidiadau bach yn nifer y cleifion.
* **Enghreifftiau:**
  * *Ysbyty Athrofaol y Faenor (Grange)* — **CT [Cardiaidd yn unig]**: `1` claf yn aros ym mis Awst a mis Medi 2026 o'i gymharu â `15` ym mis Ebrill 2026 (gwahaniaeth cymharol o **+1,400.0%**).
  * *Ysbyty Singleton* — **Meddygaeth Niwclear [Cardiaidd]**: cododd o `9` claf ym mis Mai 2026 i `40` ym mis Medi 2026 (**+344.4%**).

### Gorffennaf 2026 — Ymchwyddiadau mewn Ôl-groniadau Uwchsain ac MRI ar Draws Sawl Safle
* **Mater:** Achosodd gostyngiadau cydamserol mewn cyfraddau clirio carfanau misol ar draws dulliau cyfaint uchel gynnydd sydyn mewn niferoedd mewn un mis.
* **Enghreifftiau:**
  * Cofnododd *BIP Aneurin Bevan* naid o **+48.7%** ar draws y bwrdd (+3,316 o gleifion, o `6,812` i `10,128`), wedi'i gyrru gan ymchwyddiadau cydamserol mewn Uwchsain Heb fod yn Obstetrig yn *Nevill Hall* (`775` i `1,636`, **+111.1%**), *Ysbyty Brenhinol Gwent* (`1,118` i `1,638`, **+46.5%**), ac *Ysbyty Ystrad Fawr* (`353` i `739`, **+109.3%**), ochr yn ochr ag MRI *Ysbyty Brenhinol Gwent* (`851` i `1,240`, **+45.7%**).
  * *Nevill Hall* — cynyddodd **CT [Cardiaidd yn unig]** o `11` i `38` o gleifion (**+245.5%** o fis i fis).

### Mai – Medi 2026 — Ailddyrannu Ciwiau o Fewn Bwrdd a Misoedd Dim-Clirio
* **Ailddyrannu o Fewn Bwrdd (BIP Caerdydd a'r Fro):** Rhwng mis Mai a mis Medi 2026, gostyngodd ciwiau yn *Ysbyty Athrofaol Llandochau* yn sydyn (gostyngodd Uwchsain Heb fod yn Obstetrig o `3,294` i `1,484`; gostyngodd CT o `1,105` i `529`), tra cododd *Ysbyty Athrofaol Cymru (UHW)* dros yr un cyfnod yn union:
  * **Uwchsain Heb fod yn Obstetrig UHW:** neidiodd **+66.2%** ym mis Mehefin 2026 (`2,623` i `4,359`, gan gyrraedd uchafbwynt o `5,162` ym mis Awst).
  * **MRI UHW:** neidiodd **+36.0%** ym mis Mehefin 2026 (`1,898` i `2,581`, gan gyrraedd `3,583` ym mis Medi).
  * **Fflworosgopi UHW:** dringodd o `20` ym mis Ebrill 2026 i `112` ym mis Mai, `420` ym mis Mehefin (**+275.0%**), a `495` ym mis Medi.
* **Misoedd Dim-Clirio (Mehefin 2026):** Gostyngodd all-lif carfan misol a gofnodwyd i **0.0%** ar gyfer Uwchsain Heb fod yn Obstetrig yn *Ysbyty Brenhinol Morgannwg* (`1,130` i `1,723`, +593) ac *Ysbyty'r Tywysog Siarl* (`904` i `1,420`, +516), gan achosi i atgyfeiriadau newydd gronni'n uniongyrchol ar y rhestr aros weithredol.

### Mawrth – Ebrill 2026 — Cyflwyniad Misol Coll ac Adlam Artiffisial (BIP Cwm Taf Morgannwg)
* **Mater:** Ym mis **Mawrth 2026**, hepgorwyd 13 o 19 cyfres ysbyty–sgan gweithredol BIP Cwm Taf Morgannwg o'r cyflwyniad misol—yn benodol pob un o'r 6 gwasanaeth ym *Mhen-y-bont ar Ogwr* (`3,079` o gleifion ym mis Chwefror 2026) a 7 o 8 gwasanaeth yn *Ysbyty Brenhinol Morgannwg* (`4,300` o gleifion ym mis Chwefror 2026).
* **Effaith:** Gostyngodd cyfanswm adroddedig y Bwrdd Iechyd **-77.0%** (`8,286` i `1,909`) ym mis Mawrth 2026 a neidiodd **+300.7%** (+5,741 o gleifion yn ôl i `7,650`) pan ailddechreuodd y ddau ysbyty adrodd ym mis **Ebrill 2026**. Gan nad yw StatsCymru yn cyhoeddi diwygiadau ôl-weithredol, mae'r bwlch adrodd hwn yn aros yn y gyfres hanesyddol.

### Rhagfyr 2025 – Ebrill 2026 — Mynediad Hwyr i'r Gyfres ac Anwadalrwydd (Canolfan Trin Canser Gogledd Cymru)
* **Mater:** Nid oedd gan *Ganolfan Trin Canser Gogledd Cymru* (a weithredir gan BIP Betsi Cadwaladr) unrhyw gofnodion rhestr aros diagnostig rhwng mis Awst 2024 a mis Tachwedd 2025, gan ymddangos gyntaf ym mis **Rhagfyr 2025** (`94` o gleifion CT).
* **Effaith:** Gostyngodd llwybrau CT a adroddwyd i `27` ym mis **Mawrth 2026**, neidiodd **+1,044.4%** i `309` ym mis **Ebrill 2026**, a gostyngodd i `42` erbyn mis Medi 2026. *(Noder: Nid oes gan Ymddiriedolaeth GIG Prifysgol Felindre unrhyw safleoedd ysbyty diagnostig wedi'u hadrodd yn y set ddata hon gan StatsCymru.)*

### Medi – Rhagfyr 2025 — Cronni Ôl-groniadau'r Hydref (BIP Betsi Cadwaladr)
* **Mater:** Cynyddodd cyfanswm y llwybrau aros ar draws *BIP Betsi Cadwaladr* **+20.6%** (+3,590 o gleifion) ym mis Medi 2025 a **+11.9%** (+2,506 o gleifion) ym mis Hydref 2025 ar draws *Ysbyty Maelor*, *Ysbyty Gwynedd*, ac *Ysbyty Glan Clwyd* (gan gyrraedd uchafbwynt o `24,949` ym mis Rhagfyr 2025) tra arafodd cyfraddau clirio misol i 18%–28%, cyn i gyfraddau clirio uwch (50%–70%) leihau ôl-groniadau yn 2026.

### Hydref 2024 – Ebrill 2025 — Neidiadau Band Canolrifol Un Claf
* **Mater:** Gan fod ScanWait Wales yn amcangyfrif amseroedd aros nodweddiadol gan ddefnyddio'r band wythnosol 50fed ganradd (canolrif), gall ciwiau bach neidio'n sydyn pan fydd un claf yn aros mewn band aros hir.
* **Enghreifftiau:**
  * *Pen-y-bont ar Ogwr* — **CT [Cardiaidd yn unig]** (Hydref 2024): neidiodd o `1` wythnos i `22` wythnos pan nad oedd ond 1 claf yn weddill ar y rhestr (`Total_Waiting = 1`) yn y band 22 wythnos.
  * *Nevill Hall* — **Meddygaeth Niwclear [Cardiaidd]** (Ebrill 2025): neidiodd o `4` wythnos i `27` wythnos (+23 wythnos) yn dilyn cyfradd glirio fisol o 0.0% ar restr o 16 claf.
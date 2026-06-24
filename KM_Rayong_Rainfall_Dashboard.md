# KM: Rayong Rainfall Dashboard

ไฟล์นี้สรุปสิ่งที่ทำไว้ทั้งหมดสำหรับโปรเจกต์ `Water Rainfall RY Dashboard` เพื่อให้กลับมาแก้ไข ใช้งาน หรือส่งต่อได้ในอนาคต

## Project Location

- Local folder: `/Users/puschark/Documents/Forecasting water/rayong-rainfall-dashboard-pages`
- GitHub repository: `https://github.com/pabank10-png/rayong-rainfall-dashboard`
- GitHub Pages URL: `https://pabank10-png.github.io/rayong-rainfall-dashboard/`
- Main dashboard file: `index.html`
- Data updater script: `scripts/update_dashboard.py`
- GitHub Actions workflow: `.github/workflows/update-dashboard.yml`

## Main Output

Dashboard เป็นไฟล์ HTML หลักชื่อ `index.html` ใช้ GitHub Pages เปิดเป็นเว็บสาธารณะ โดยข้อมูลหลักถูกฝังเป็น JavaScript object ในไฟล์เดียวกัน และมี workflow สำหรับดึงข้อมูลใหม่อัตโนมัติ

หน้าเว็บปัจจุบันมี 3 ส่วนหลัก:

1. `ข้อมูลฝนเปรียบเทียบรายปี`
2. `ข้อมูลฝนทุกปี`
3. `ฝนรายวัน`

## Design / Mood and Tone

ปรับหน้าตาให้สอดคล้องกับ Web Reference `Water Reservoir Dashboard`

สิ่งที่ปรับแล้ว:

- Header สี teal แบบเดียวกับ reference
- ชื่อหน้า: `Water Rainfall RY Dashboard`
- Subtitle: `Rayong Rainfall · Historical Rainfall & Scenario Analysis`
- ปุ่มบน header:
  - Dark mode toggle
  - Live pill
  - Date chip
  - Download all Data
- พื้นหลัง mint/teal อ่อน พร้อม dotted pattern
- Cards เป็นสีขาว ขอบบาง เงานุ่ม
- Dark mode ยังใช้งานได้
- Infographic และ chart cards ปรับ mood/tone ให้เข้ากับ reference

## Data Sources

### Monthly / Historical Rainfall

ใช้ข้อมูลจาก HII/TISERVICE ผ่าน Power BI public query endpoint:

- Entity: `mRainAmp_TISERVICE`
- Field หลัก:
  - `PROV_T`
  - `AMPHOE_T`
  - `yearBE`
  - `MONTH`
  - `MEAN_OBS`
- Script ที่ดึงข้อมูล: `scripts/update_dashboard.py`
- เริ่มดึงข้อมูลตั้งแต่ พ.ศ. 2513 จนถึงปีปัจจุบัน

Mapping ปัจจุบัน:

| Dashboard Group | Reservoir | Province | District Used |
|---|---|---|---|
| 3 อ่าง | ดอกกราย | ระยอง | ปลวกแดง |
| 3 อ่าง | คลองใหญ่ | ระยอง | ปลวกแดง |
| 3 อ่าง | หนองปลาไหล | ระยอง | ปลวกแดง |
| อ่างประแสร์ | ประแสร์ | ชลบุรี | บ่อทอง |

หมายเหตุสำคัญ: `อ่างประแสร์` ใช้ `บ่อทอง` เท่านั้น ไม่ใช้ `หนองใหญ่`

### Daily Rainfall

หน้า `ฝนรายวัน` ใช้ API:

```text
https://api-v3.thaiwater.net/api/v1/thaiwater30/public/rain_monthly_graph
```

สถานีที่ใช้อยู่ใน `index.html`:

| Province | Station ID | Station |
|---|---:|---|
| ชลบุรี | 111 | อบต.บ่อทอง |
| ระยอง | 1109580 | อบต.ปลวกแดง |
| จันทบุรี | 129 | อบต.ขุนซ่อง |
| จันทบุรี | 128 | แก่งหางแมว |

หน้า daily มีการแสดง badge `ข้อมูลล่าสุดถึงวันที่ ...` จากวันที่ล่าสุดที่ API ส่งข้อมูลจริงมา โดยตัดวันที่อนาคตที่ยังไม่ถึงออก ไม่ให้เข้าใจผิดว่าเป็นข้อมูลจริง

## Calculation Logic

### Year Format

- ใน `DATA` object ใช้ปี ค.ศ. เป็น key เช่น `2026`
- ใน UI แสดงเป็น พ.ศ. โดยบวก 543
- ตัวอย่าง: `2026` แสดงเป็น `2569`

### Complete Year

ปีที่ถือว่า complete ต้องมีข้อมูลครบ 12 เดือน

ใช้กับ:

- ค่าเฉลี่ยย้อนหลัง 5 ปี
- ค่าเฉลี่ยย้อนหลัง 10 ปี
- ค่าเฉลี่ยย้อนหลัง 15 ปี
- ปีฝนมากสุด/น้อยสุดใน tab `ข้อมูลฝนทุกปี`

### Header Summary Cards

ตอนนี้แสดงทีละอ่าง โดยมี tab:

- Default: `3 อ่างฯ`
- เลือกเปลี่ยนเป็น `อ่างประแสร์`

แต่ละอ่างแสดง 4 card:

1. เฉลี่ย 5 ปี / 10 ปี
2. สูงสุด 5 ปี / ทั้งหมด
3. ต่ำสุด 5 ปี / ทั้งหมด
4. ช่วงข้อมูล

### Tab: ข้อมูลฝนเปรียบเทียบรายปี

- เลือกอ่างได้
- เลือกปีเปรียบเทียบได้สูงสุด 3 slot
- มี option ค่าเฉลี่ย 5 ปี และ 10 ปี
- Current partial year:
  - เดือนที่มีข้อมูลแสดงจริง
  - เดือนอนาคตแสดงเป็น `—` ในตาราง
  - กราฟใช้ค่าว่าง/ศูนย์ตาม logic ที่กำหนดไว้เดิม

### Tab: ข้อมูลฝนทุกปี

มี checkbox เลือกชุดข้อมูลในกราฟ:

- ข้อมูลทั้งหมด
- ข้อมูลฝนมากสุด
- ข้อมูลฝนน้อยสุด
- ฝนย้อนหลัง 5 ปี
- ฝนย้อนหลัง 10 ปี
- ฝนย้อนหลัง 15 ปี

เส้น Actual ล่าสุดถูกดึงขึ้นด้านบนสุดของกราฟเพื่อไม่ให้โดนเส้นอื่นทับ และใช้สีสว่างให้เห็นชัดบนธีมปัจจุบัน

### Tab: ฝนรายวัน

- เลือกจังหวัด
- เลือกปีเปรียบเทียบได้สูงสุด 3 ปี
- แสดงแผนที่สถานี
- กราฟภาพรวมรายเดือนคลิกแท่งเพื่อ drill down เป็นรายวันได้
- วันที่ที่ API ยังไม่มีข้อมูลจริงจะแสดงเป็นช่องว่าง ไม่ใส่ 0
- ตารางใช้ `—` สำหรับวันที่/เดือนที่ยังไม่มีข้อมูล

## GitHub Actions

Workflow file:

```text
.github/workflows/update-dashboard.yml
```

Trigger:

- Manual run ผ่าน GitHub Actions (`Run workflow`)
- Schedule ทุกวันเวลา `01:00 UTC`
- เวลาไทยคือประมาณ `08:00 น.`

Workflow ทำงานดังนี้:

1. Checkout repo
2. Setup Python 3.12
3. Run `python scripts/update_dashboard.py`
4. Commit เฉพาะ `index.html` ถ้ามีข้อมูลเปลี่ยน

## How to Update Data Manually

ผ่าน GitHub:

1. เข้า repo `rayong-rainfall-dashboard`
2. ไปที่ tab `Actions`
3. เลือก workflow `Update Rainfall Dashboard`
4. กด `Run workflow`
5. รอให้ run สำเร็จ
6. เปิด GitHub Pages URL แล้ว refresh

ผ่านเครื่อง local:

```bash
cd "/Users/puschark/Documents/Forecasting water/rayong-rainfall-dashboard-pages"
python3 scripts/update_dashboard.py
git add index.html
git commit -m "Update rainfall dashboard data"
git push origin main
```

## How to Edit Web Design

แก้ในไฟล์:

```text
index.html
```

ส่วนที่ควรระวัง:

- `DATA` block ถูก update โดย script อัตโนมัติ
- ถ้าแก้โครง `const DATA={...};` หรือ constants เหล่านี้ ต้องระวัง regex ใน `scripts/update_dashboard.py`
  - `CURRENT_YEAR_CE`
  - `LAST_FULL_YEAR_CE`
  - `CURRENT_MONTH_IDX`
  - `ALL_CE_YEARS`
- CSS/HTML/JS อยู่ในไฟล์เดียวกัน
- มี fallback Chart.js ฝังอยู่ใน `index.html` ด้วย ทำให้ไฟล์ใหญ่

## Important Files

| File | Purpose |
|---|---|
| `index.html` | Dashboard UI, embedded data, charts, daily rainfall page |
| `scripts/update_dashboard.py` | Fetch monthly historical data and update `index.html` |
| `.github/workflows/update-dashboard.yml` | GitHub Action for automatic/manual update |
| `static/libraries/chart.js/4.5.1/chart.umd.js` | Local Chart.js library for GitHub Pages |

## Current Known Notes

- `.DS_Store` อาจโผล่ใน local repo จาก macOS แต่ไม่ได้จำเป็นต้อง commit
- ถ้า `git push` ถูก reject เพราะ remote มี commit ใหม่ ให้ใช้:

```bash
git pull --rebase origin main
git push origin main
```

- ถ้าต้องใช้ vi ตอน rebase:
  - กด `Esc`
  - พิมพ์ `:wq`
  - กด Enter

## Recent Completed Changes

- ย้าย dashboard ขึ้น GitHub Pages แยกจาก project earthquake
- เพิ่ม workflow สำหรับ update data อัตโนมัติ
- ปรับ design ให้ mood/tone ใกล้ `Water Reservoir Dashboard`
- เพิ่ม comma separator ในตัวเลขฝน
- ปรับ mobile layout ของกราฟ iPhone
- ปรับ header summary ให้เลือกแสดงทีละอ่าง
- เพิ่ม daily data latest-date badge
- ปรับ `อ่างประแสร์` ให้ใช้เฉพาะ `บ่อทอง`

## Practical Checklist Before Future Changes

ก่อนแก้:

1. เช็กสถานะ git

```bash
git status --short
```

2. แก้เฉพาะไฟล์ที่เกี่ยวข้อง
3. ทดสอบ local

```bash
python3 -m http.server 8787
```

เปิด:

```text
http://127.0.0.1:8787/
```

4. ตรวจว่ากราฟขึ้น ไม่มี error สำคัญ
5. Commit และ push

```bash
git add index.html
git commit -m "Describe change"
git push origin main
```

## Future Improvement Ideas

- แยก CSS/JS ออกจาก `index.html` เพื่อลดความเสี่ยงเวลาแก้
- เพิ่ม README หน้า GitHub
- เพิ่ม `.gitignore` สำหรับ `.DS_Store`
- เพิ่ม version/date ของ dashboard ใน footer
- เพิ่ม note อธิบาย data source แบบ user-friendly ในหน้าเว็บ

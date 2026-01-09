# NamoFoundry

NamoFoundry คือศูนย์กลางสำหรับจัดการ Flow การทำงานตั้งแต่ Blueprint (ต้นร่าง) ไปจนถึง Solution (แนวทางแก้ไข) และ Implementation (การนำไปใช้จริง)

## 🔄 Concept (แนวคิดหลัก)

- **จัดการข้อมูล:** จัดการไฟล์งานดิบ (raw files), blueprint, และ solution ภายใต้ framework ที่มีโครงสร้างชัดเจน (Data hygiene + Knowledge architecture)
- **Visualize:** ใช้ **Knowledge Framework App** (เว็บแอปพลิเคชันในโฟลเดอร์ `/app`) เพื่อแสดงผลข้อมูลในมุมมองต่างๆ เช่น Matrix, Kanban, หรือ Mindmap
- **จัดเก็บไฟล์ใหญ่:** ไฟล์ขนาดใหญ่เช่น datasets, PDF, หรือ media จะถูกเก็บไว้ใน Google Drive และมีการทำลิงก์เชื่อมโยงไว้ในไฟล์ `drive_links.md`

---

## 🛠️ Setup and Installation (การติดตั้ง)

ในการใช้งานสคริปต์แปลงไฟล์อัตโนมัติของโปรเจกต์นี้ คุณจำเป็นต้องติดตั้ง Python และ library ที่เกี่ยวข้องก่อน

1. **Clone a repository:**

    ```bash
    git clone https://github.com/your-username/namo-foundry.git
    cd namo-foundry
    ```

2. **สร้าง Virtual Environment (แนะนำ):**

    ```bash
    python -m venv venv
    source venv/bin/activate  # On Windows, use `venv\Scripts\activate`
    ```

3. **ติดตั้ง Dependencies:**
    ติดตั้ง library ที่จำเป็นทั้งหมดจากไฟล์ `requirements.txt`

    ```bash
    pip install -r requirements.txt
    ```

---

## 🚀 Workflows & Usage (การใช้งาน)

โปรเจกต์นี้มี 2 workflow หลักในการสร้าง Blueprint JSON.

### 1. Manual Conversion (แปลงไฟล์ด้วยตนเอง)

เป็นวิธีที่ง่ายที่สุดในการแปลงไฟล์ `.txt` หรือ `.md` ให้เป็น JSON สำหรับนำไปใช้ในแอปพลิเคชัน

- **Input:** นำไฟล์ `.txt` หรือ `.md` ของคุณไปวางไว้ในโฟลเดอร์ `Workflows/`
- **Run script:** สั่งรันสคริปต์ `convert_raw_to_json.py`

  ```bash
  python scripts/convert_raw_to_json.py
  ```

- **Output:** สคริปต์จะสร้างไฟล์ `import.json` ขึ้นมาในโฟลเดอร์ `Workflows/` ซึ่งรวมข้อมูลจากทุกไฟล์ที่คุณใส่เข้าไป

### 2. Full Pipeline (ไปป์ไลน์อัตโนมัติเต็มรูปแบบ)

ไปป์ไลน์นี้รองรับไฟล์ได้หลายชนิด (.txt, .md, .pdf, .docx) และมีความสามารถสูงกว่า เช่น การ sanitizing เนื้อหา, การสร้างโครงสร้าง blueprint ที่ซับซ้อน, และการ enrich ข้อมูลผ่าน API (ถ้ามี)

- **Input:** นำไฟล์ `.txt`, `.md`, `.pdf`, หรือ `.docx` ไปวางในโฟลเดอร์ `framework/`
- **Run script:** สั่งรันสคริปต์ `auto_blueprint_full.py`

  ```bash
  python tools/auto_blueprint_full.py
  ```

- **Output:** สคริปต์จะสร้างไฟล์ JSON แยกสำหรับแต่ละ Input ออกมาในโฟลเดอร์ `blueprints/`
  - รองรับการแยกหลายชุดในไฟล์เดียว (ถ้ามีหัวข้อชุด/Part/Section)
  - สามารถจัด output ตามประเภทเอกสารด้วย `--output-layout by-type`
  - สามารถแยก output ตามบทบาทด้วย `--output-mode role-split`
  - สามารถส่งออกเป็น Markdown ได้ด้วย `--output-format md` หรือ `--output-format both`
  - ค่าเริ่มต้นจะ **redact PII** และ **anonymize source** เพื่อความปลอดภัย
  - LLM enrichment จะปิดไว้ตามค่าเริ่มต้น ใช้ `--enable-llm` เมื่อต้องการ

---

## ✨ Example (ตัวอย่าง Input/Output)

### Input ตัวอย่าง (`/framework/my_idea.txt`)

```text
This is a simple idea for a new project.
It's about creating a tool to manage knowledge graphs.
The main features should be:
- Node creation
- Link editing
- Visualization
```

### Output ตัวอย่าง (`/blueprints/my_idea.json`)

```json
{
  "id": "BP-20231027-a1b2c3",
  "brand": "NamoNexus",
  "title": "my idea",
  "slogan": "Elevate your existence with NamoNexus.",
  "meta_definition": "This Blueprint is designed as an entity beyond AI — a self-evolving, meta-intelligent framework that grows infinitely across dimensions.",
  "sections": {
    "executive_summary": "This is a simple idea for a new project.\nIt's about creating a tool to manage knowledge graphs.\nThe main features should be:\n- Node creation\n- Link editing\n- Visualization",
    "value_proposition": "Universal adaptability, modular architecture, AI-agnostic integration, and self-evolving design.",
    "system_overview": "A layered framework transforming raw data into commercial blueprints with metadata and validation.",
    "quick_start_guide": "1) Place raw files into /framework  2) Run the pipeline  3) Review JSON in /blueprints  4) Deploy to your ecosystem.",
    "template_instructions": "Follow the schema. Keep sections concise. Use neutral, professional English. Avoid personal names.",
    "examples": "Education curricula, healthcare protocols, financial decision flows, brand guidelines.",
    "license_and_notes": "Licensed under NamoVerse Creative Framework License (NCFL-1.0). Provide attribution for redistribution.",
    "marketing_pack": "Target: builders, strategists, educators. Pain: unstructured data. USP: chaos-to-commerce via meta-intelligence. Pricing: Base/Pro tiers. GTM: ProductHunt + LinkedIn."
  },
  "status": "complete",
  "version": "0.1",
  "metadata": {
    "author": "NamoVerse Engine",
    "language": "en",
    "source_file": "framework/my_idea.txt",
    "last_updated": "2023-10-27",
    "pipeline": "auto-blueprint-full"
  }
}
```

*(หมายเหตุ: `id` และ `last_updated` จะถูก generate ตามวันและเวลาที่รันสคริปต์)*

---

## 🌐 Using the Web App (การใช้งานเว็บแอป)

1. **เปิด `app/index.html`** ใน browser เพื่อเริ่มใช้งาน (local)
2. **Import JSON:** ใช้ปุ่ม "Import JSON" เพื่อนำเข้าไฟล์ `import.json` (จาก Manual Conversion) หรือไฟล์อื่นๆ จากโฟลเดอร์ `blueprints/`
3. **Visualize:** ข้อมูลจะถูกแสดงผลในรูปแบบต่างๆ ให้คุณจัดการและวิเคราะห์ต่อได้
4. **(Optional) Deploy:** คุณสามารถ deploy เว็บแอปนี้ขึ้น GitHub Pages ได้โดยใช้ workflow ที่อยู่ใน `.github/workflows/deploy.yml`

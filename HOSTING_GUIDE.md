# 🌐 ការណែនាំអំពីរបៀប Host Bot ឱ្យដំណើរការ ២៤ម៉ោង/៧ថ្ងៃ (24/7)

ដើម្បីឱ្យ **RB Drama Bot** ដំណើរការរហូត ២៤ម៉ោង/៧ថ្ងៃ ទោះបីជាអ្នកបិទកុំព្យូទ័រផ្ទាល់ខ្លួនក៏ដោយ អ្នកមានជម្រើសល្អៗចំនួន ២ ៖

---

## ⭐️ ជម្រើសទី 1 ៖ ឥតគិតថ្លៃ (Free Cloud Hosting) តាម Render.com ឬ Koyeb

នេះជាជម្រើសឥតគិតថ្លៃ និងងាយស្រួលដោយមិនចាំបាច់មានចំណេះដឹងខាង Server Linux ឡើយ។

### ជំហានអនុវត្តតាម Render.com ៖
1. **បង្កើត GitHub Repository**៖
   - បង្កើតគណនី [GitHub.com](https://github.com) (ប្រសិនបើមិនទាន់មាន)
   - បង្កើត New Repository ថ្មីមួយ (កំណត់ជា **Private**)
   - Upload ឯកសារទាំងអស់ក្នុង Folder `rb_drama_bot` ចូលទៅ (លើកលែងឯកសារ `.env` កុំ Upload ឱ្យសោះដើម្បីសុវត្ថិភាព Token)

2. **ចុះឈ្មោះចូល Render.com**៖
   - ចូលទៅកាន់ [Render.com](https://render.com) ហើយចុះឈ្មោះដោយភ្ជាប់ជាមួយគណនី GitHub
   - ចុចប៊ូតុង **New +** រួចជ្រើសរើស **Background Worker** (ឬ Web Service)
   - ជ្រើសរើស Repository `rb_drama_bot` របស់អ្នកពី GitHub

3. **កំណត់ការ Run**៖
   - **Environment**: `Python 3`
   - **Build Command**: `pip install -r requirements.txt`
   - **Start Command**: `python main.py`

4. **កំណត់ Environment Variables (បញ្ចូល Token)**៖
   - ចូលទៅកាន់ផ្នែក **Environment Variables** លើ Render រួចបញ្ចូល៖
     - `BOT_TOKEN` = `8250321325:AAGvoZK4ZhCvCtxFu4PLeOw39uxkdsLOMyE`
     - `ADMIN_IDS` = `1379913959`
   - ចុច **Deploy**! នោះ Bot នឹងចាប់ផ្តើមដំណើរការ ២៤ម៉ោងភ្លាមៗ។

---

## 🚀 ជម្រើសទី 2 ៖ ប្រើប្រាស់ Linux VPS (ស្ថិរភាពខ្ពស់បំផុត និងណែនាំសម្រាប់ Movie/Drama Bot)

ប្រសិនបើអ្នកចង់បានភាពរលូនបំផុត រក្សាទិន្នន័យរឿង និងភាគរឿងជាប់រហូតមិនបាត់បង់ ការជួល **Cloud VPS** (តម្លៃប្រហែល $3 - $5/ខែ នៅ [DigitalOcean](https://digitalocean.com), [Hetzner](https://hetzner.com), ឬ [Vultr](https://vultr.com)) គឺជាជម្រើសលេខ ១។

### ជំហានរៀបចំលើ Linux VPS (Ubuntu/Debian) ៖

1. **ចូលទៅកាន់ Server តាម Terminal/SSH**៖
   ```bash
   ssh root@ip_address_server_របស់លោកអ្នក
   ```

2. **តម្លើង Python និង Git**៖
   ```bash
   apt update && apt upgrade -y
   apt install python3 python3-pip python3-venv git -y
   ```

3. **ចម្លងគម្រោងចូល Server**៖
   ```bash
   cd /root
   git clone <link_github_របស់លោកអ្នក> rb_drama_bot
   cd rb_drama_bot
   pip3 install -r requirements.txt
   ```

4. **បង្កើតឯកសារ `.env` លើ Server**៖
   ```bash
   nano .env
   ```
   (ចម្លង Token និង Admin ID ដាក់ចូល រួចចុច `Ctrl + O` -> `Enter` -> `Ctrl + X` ដើម្បី Save)

5. **កំណត់ឱ្យ Bot ដើរ ២៤/៧ ដោយស្វ័យប្រវត្តិតាមរយៈ Systemd Service**៖
   ចម្លងឯកសារ `rb_drama.service` ទៅកាន់ system folder៖
   ```bash
   cp rb_drama.service /etc/systemd/system/
   systemctl daemon-reload
   systemctl enable rb_drama
   systemctl start rb_drama
   ```

6. **ពិនិត្យស្ថានភាព Bot**៖
   ```bash
   systemctl status rb_drama
   ```
   (ប្រសិនបើឃើញពណ៌បៃតង `active (running)` មានន័យថា Bot កំពុងដើរ ២៤ម៉ោង/៧ថ្ងៃហើយ ទោះបី Server restart ក៏វានឹងដំណើរការឡើងវិញដោយស្វ័យប្រវត្តិដែរ)

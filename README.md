# 🎬 RB Drama - Telegram Bot

Telegram Bot សម្រាប់ចាក់ផ្សាយ និងចែករំលែករឿងភាគ (Drama) ជាមួយ **Admin Panel** ពេញលេញ សម្រាប់បង្ហោះរឿងថ្មីៗ និងផ្ញើសារប្រកាសដំណឹង (Broadcast) ទៅកាន់សមាជិកទាំងអស់។

---

## 🌟 មុខងារចម្បង (Key Features)

### 👥 សម្រាប់អ្នកទស្សនា (Users)
- 🎬 **មើលបញ្ជីរឿងទាំងអស់ (Catalog & Pagination)**៖ បង្ហាញរឿងភាគតាមទំព័រ ងាយស្រួលរកមើល
- 🔍 **ស្វែងរករឿងតាមឈ្មោះ (Search)**៖ គ្រាន់តែវាយឈ្មោះរឿងផ្ញើចូលក្នុង Bot វានឹងស្វែងរកភ្លាមៗ
- ⭐️ **រឿងថ្មីៗ (Recent Dramas)**៖ រកមើលរឿងដែលទើបតែដាក់បញ្ចូល
- 🎞 **ទស្សនាភាគរឿង**៖ មើលវីដេអូតាមរយៈតំណភ្ជាប់ (Links) ឬវីដេអូ Telegram ដោយផ្ទាល់
- 📢 **Force Channel Subscription**៖ (Optional) តម្រូវឱ្យចូលរួម Channel របស់អ្នកជាមុនសិនទើបអាចទស្សនាបាន

### 👑 សម្រាប់ Admin (Admin Panel)
- ➕ **បង្ហោះរឿងថ្មី (Add Drama)**៖ បញ្ចូលចំណងជើង, ប្រភេទរឿង, សង្ខេបដំណើររឿង, រូប Poster, និងស្ថានភាព (Ongoing/Completed)
- 🎬 **គ្រប់គ្រងភាគរឿង (Add Episodes)**៖ បន្ថែមភាគថ្មីៗដោយគ្រាន់តែផ្ញើ Link (Google Drive, YouTube, Stream) ឬ Upload វីដេអូ Telegram ផ្ទាល់
- 📢 **ផ្ញើសារ Broadcast**៖ ផ្ញើសារប្រកាសដំណឹង (សារអក្សរ រូបភាព ឬ Forward) ទៅកាន់គ្រប់សមាជិកទាំងអស់របស់ Bot
- 📊 **ស្ថិតិ Bot (Statistics)**៖ មើលចំនួនសមាជិក, ចំនួនរឿង, និងចំនួនភាគសរុប
- 🗑 **លុបរឿងចេញ (Delete Drama)**៖ លុបរឿង និងភាគទាំងអស់ចេញពីប្រព័ន្ធ

---

## 🛠 របៀបដំឡើង និងដំណើរការ (Setup & Installation)

### ជំហានទី 1 ៖ បង្កើត Bot និងយក Token ពី @BotFather
1. បើកកម្មវិធី Telegram ហើយស្វែងរក **[@BotFather](https://t.me/BotFather)**
2. ចុច **Start** រួចផ្ញើពាក្យបញ្ជា `/newbot`
3. វាយបញ្ចូលឈ្មោះ Bot៖ `RB Drama`
4. វាយបញ្ចូល Username សម្រាប់ Bot (ត្រូវតែបញ្ចប់ដោយពាក្យ `bot` ឧ. `rb_drama_kh_bot` ឬ `rbdrama_official_bot`)
5. BotFather នឹងផ្ញើ **API Token** មកឱ្យអ្នក (ឧ. `7123456789:AAFxxx_xxxxxx...`) -> សូមចម្លង (Copy) Token នេះទុក។

### ជំហានទី 2 ៖ យក Telegram User ID របស់អ្នក (Admin ID)
1. ស្វែងរក Bot ឈ្មោះ **[@userinfobot](https://t.me/userinfobot)** នៅលើ Telegram
2. ចុច **Start** វានឹងបង្ហាញព័ត៌មានរបស់អ្នក រួមទាំង **`Id: 123456789`**
3. ចម្លងលេខសម្គាល់ (ID) នោះទុក។

### ជំហានទី 3 ៖ កំណត់រចនាសម្ព័ន្ធឯកសារ `.env`
បើកឯកសារ `.env` ក្នុង Folder `rb_drama_bot` រួចបំពេញព័ត៌មាន៖
```env
# បញ្ចូល Bot Token ទទួលបានពី @BotFather
BOT_TOKEN=7123456789:AAFxxx_xxxxxx...

# បញ្ចូល Telegram ID របស់អ្នក (Admin)
ADMIN_IDS=123456789

# បើចង់ឱ្យ User Join Channel ជាមុន សូមដាក់ឈ្មោះ Channel ដោយមិនបាច់ដាក់ @ (បើមិនចង់ ទុកនៅទំនេរ)
FORCE_SUB_CHANNEL=

# Link ឆានែលរបស់អ្នក (ឧ. https://t.me/your_channel)
CHANNEL_LINK=
```

### ជំហានទី 4 ៖ ដំណើរការ Bot
បើក Terminal ឬ PowerShell នៅក្នុង Folder `rb_drama_bot` រួចដំណើរការ៖
```bash
python main.py
```

នៅពេល Bot ដំណើរការជោគជ័យ អ្នកនឹងឃើញសារ៖
```text
🚀 កំពុងដំណើរការ RB Drama Telegram Bot...
✅ Bot បានចាប់ផ្តើមដំណើរការ Polling ដោយជោគជ័យ!
```

---

## 📱 របៀបប្រើប្រាស់ Admin Panel លើ Telegram

1. ចូលទៅកាន់ Bot របស់អ្នកលើ Telegram (គណនីដែលបានដាក់ ID ក្នុង `ADMIN_IDS`)
2. វាយពាក្យបញ្ជា `/admin`
3. ផ្ទាំង Admin Panel នឹងបង្ហាញប៊ូតុងមុខងារនីមួយៗ ៖
   - ចុច **➕ បង្ហោះរឿងថ្មី** ដើម្បីចាប់ផ្តើមដាក់រឿង
   - ចុច **🎬 គ្រប់គ្រង និងបន្ថែមភាគរឿង** ដើម្បីបញ្ចូលភាគទី 1, 2, 3...
   - ចុច **📢 ផ្ញើសារ Broadcast** ដើម្បីផ្ញើសារទៅកាន់អ្នកប្រើទាំងអស់
   - ចុច **📊 ស្ថិតិទូទៅ** ដើម្បីមើលទិន្នន័យ

---

## 📁 រចនាសម្ព័ន្ធគម្រោង (Project Structure)

```text
rb_drama_bot/
├── .env                  # កន្លែងរក្សាទុក Token និង Admin ID
├── .env.example          # គំរូ configuration
├── requirements.txt      # បញ្ជី library ដែលត្រូវប្រើ (python-telegram-bot, python-dotenv)
├── config.py             # គ្រប់គ្រង environment variables
├── database.py           # ប្រព័ន្ធរក្សាទុកទិន្នន័យ SQLite (users, dramas, episodes)
├── keyboards.py          # ប៊ូតុង និងមឺនុយ Telegram Inline Keyboards
├── handlers/
│   ├── __init__.py
│   ├── user_handlers.py  # មុខងារសម្រាប់អ្នកទស្សនា (/start, search, watch, catalog)
│   └── admin_handlers.py # មុខងារ Admin Panel (add drama, add episodes, broadcast, stats)
├── main.py               # ឯកសារចម្បងសម្រាប់ដំណើរការ Bot
├── test_bot.py           # ឯកសារសម្រាប់តេស្តប្រព័ន្ធ
└── README.md             # សៀវភៅណែនាំ
```

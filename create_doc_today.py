import json
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build

TOKEN_PATH = "/home/satyaaditech/.hermes/google_token.json"
FOLDER_ID = "1Bh9ZIizra0I-3hmlqcHjhLJi3-eTAI4U" # Materi Olahrasa folder

with open(TOKEN_PATH) as f:
    creds_data = json.load(f)
creds = Credentials.from_authorized_user_info(creds_data)

docs_service = build("docs", "v1", credentials=creds)
drive_service = build("drive", "v3", credentials=creds)

doc_title = "RENUNGAN PENYISWAAN - Waspada Perangkap Keserakahan (2026-10-22)"
print(f"Creating Google Doc: {doc_title}...")
doc = docs_service.documents().create(body={"title": doc_title}).execute()
doc_id = doc.get("documentId")
doc_url = f"https://docs.google.com/document/d/{doc_id}/edit"
print(f"Doc created: {doc_url}")

# Move to folder
try:
    file = drive_service.files().get(fileId=doc_id, fields="parents").execute()
    prev_parents = ",".join(file.get("parents", []))
    drive_service.files().update(
        fileId=doc_id,
        addParents=FOLDER_ID,
        removeParents=prev_parents,
        fields="id, parents"
    ).execute()
    print(f"Moved doc to folder {FOLDER_ID}")
except Exception as e:
    print("Folder move notice:", e)

# Set permission reader/anyone
try:
    drive_service.permissions().create(
        fileId=doc_id,
        body={"type": "anyone", "role": "reader"}
    ).execute()
    print("Shared doc with anyone as reader")
except Exception as e:
    print("Permission notice:", e)

body_text = """RENUNGAN PENYISWAAN
Kamis Pahing, 22 Oktober 2026

Waspada Perangkap Keserakahan: Mengapa Otak Tak Pernah Puas Mengejar Kepemilikan? ⚖️

Salam Karahayon 🙏

========================================
I. KUTIPAN TUNTUNAN (KANONIKAL VERBATIM)
========================================
Rujukan: [SSJ] Serat Sasangka Jati — Kitab I: Hasta Sila (Panca Sila: 2. Narima)

"Narima iku akeh lerege marang tentreming ati, dadi dudu wong kang lumuh ing gawe, nanging kang narima ing sapandum. Apa kang wus cinekel ana ing tangane, digarap kanthi senenging ati, ora murka lan ora ngangsa-angsa. Narima iku ora mengini darbeking liyan, sarta ora meri marang kabegjane liyan, mulane wong kang narima iku kena den arani wong kang sokur ing Pangeran. Panarima iku sawijining bandha kang ora bisa entek, mulane sing sapa golek sugih upayanen aneng jroning panarima. Wong kang narima iku begja ing sajroning uripe, amarga dheweke menang karo owah gingsiring kahanan."

(Terjemahan Resmi):
Menerima (narima) itu banyak bermuara pada ketenteraman hati, jadi bukanlah orang yang malas bekerja, melainkan orang yang menerima apa yang menjadi bagiannya. Apa yang telah berada di tangannya, dikerjakan dengan senang hati, tidak serakah dan tidak berambisi membabi buta. Narima itu tidak menginginkan milik orang lain, serta tidak iri terhadap keberuntungan orang lain, maka orang yang narima dapat disebut orang yang bersyukur kepada Tuhan. Rasa penerimaan itu adalah suatu harta kekayaan yang tidak bisa habis, karena itu barang siapa mencari kekayaan, carilah di dalam rasa penerimaan. Orang yang narima itu beruntung di dalam hidupnya, karena ia menang terhadap perubahan keadaan.

========================================
II. PANGILON RASA (KONTEMPLASI BATIN)
========================================
Pernahkah kita mengamati sebuah keganjilan halus di dalam batin kita sendiri? Ketika sebuah target materi yang dulu kita impikan akhirnya tercapai—entah saldo tabungan tertentu, kendaraan baru, atau pencapaian karier—rasa lega dan bahagia yang muncul ternyata hanya bertahan beberapa hari. Tak lama kemudian, rongga dada kembali terasa kosong, lalu kepala kita otomatis menyusun target baru yang lebih besar. Kita mengira rasa aman akan tiba jika sudah memiliki "sedikit lagi", padahal kata "cukup" tak pernah kunjung datang.

Sains modern menyebut siklus ini sebagai hedonic treadmill—mekanisme biologis di mana otak kita lekas terbiasa pada perolehan baru dan segera menuntut lonjakan kepuasan berikutnya agar tidak cemas. Namun jauh sebelum sains membedah biologi saraf, kearifan batin telah memperingatkan kita: nafsu jasmani adalah wadah tanpa dasar. Semakin rakus kita mengisinya dengan materi dan perbandingan sosial, semakin bocor batin kita, menuntut kita terus berlari dalam kepanikan otopilot tanpa tahu di mana garis akhirnya.

Di titik kelelahan inilah, Sang Guru Sejati membukakan rahasia adiluhung tentang Narima. Selama ini, banyak orang keliru mengira bahwa narima adalah sikap pasrah yang lemah, apatis, atau dalih orang yang malas berikhtiar (lumuh ing gawe). Padahal sabda menegaskan sebaliknya: raga kita tetap tekun dan terampil menggarap apa yang ada di genggaman (digarap kanthi senenging ati), namun batin kita merdeka dari racun ketamakan (ora murka lan ora ngangsa-angsa) serta bebas dari perihnya iri dengki melihat rezeki orang lain (ora mengini darbeking liyan).

Mengapa penerimaan batin disebut sebagai harta yang tak pernah bisa habis (bandha kang ora bisa entek)? Karena orang yang batinnya telah narima tidak bisa lagi disandera oleh pasang-surutnya roda dunia (menang karo owah gingsiring kahanan). Saat orang lain panik mencari rasa aman dari angka-angka fana yang selalu bisa lenyap, jiwa yang narima telah kaya dari dalam. Ia berhenti menjadi pengemis kepuasan materi, sebab ia tahu: kekayaan sejati bukanlah memiliki segala hal yang ada di dunia, melainkan ketidakterikatan jiwa yang telah berlabuh tenang di haribaan Sang Hyang Suksma.

========================================
III. LAKU PANYISWAN (MIKRO-PRAKTIK 30 DETIK)
========================================
1. Eling ing Pamikir (Detik 0–10):
Tarik satu napas dalam secara hening. Sadari kepanikan pikiran yang sedang berbisik "aku masih kurang, aku harus punya itu". Katakan perlahan ke dalam sanubari: "Iki mung hawa nepsu jasmani kang golek rasa aman palsu. Uripatiku wus cukup lan kapengku ing Gusti."

2. Hayati Harta Panarima (Detik 11–20):
Buka kedua telapak tangan di atas pangkuan. Arahkan perhatian penuh pada hal paling mendasar yang kita miliki detik ini: napas yang masih mengalir, tubuh yang sehat, dan tugas yang masih bisa digarap. Syukuri apa yang ada di tangan tanpa membandingkannya dengan milik orang lain.

3. Pasrah Sumarah ing Kahanan (Detik 21–30):
Kendurkan ketegangan di pundak, rahang, dan kening. Lepaskan ambisi mengontrol hari esok. Kembalikan seluruh perburuan materi ke dalam pangkuan Sang Guru Sejati: "Gusti, kawula pasrah narima ing sapandum, nyenyadhang tentreming ati wonten ing telenging sanubari." Rasakan kesejukan (lerem) mengendap di rongga dada.

========================================
IV. JANGKAR BATIN
========================================
Mutiara Rasa:
"Keserakahan lahir bukan karena dunia ini kekurangan, melainkan karena batin yang lupa pada Sang Urip takkan pernah mengenal kata cukup. Orang yang paling kaya di muka bumi bukanlah yang menggenggam segalanya, melainkan yang batinnya merdeka karena telah 'narima ing sapandum'."

Pertanyaan Refleksi:
"Di sudut hidupmu hari ini, pencapaian atau kepemilikan apa yang terus kamu kejar hingga merampas kedamaian batinmu—dan beranikah engkau berhenti sejenak untuk mensyukuri apa yang telah ada di tanganmu?"

========================================
Semoga kita semua senantiasa berlimpah dengan sih, tuntunan, pepadang, dan pangayoman dari Sang Guru Sejati. Satuhu. 🙏🌿
"""

# Insert text
docs_service.documents().batchUpdate(
    documentId=doc_id,
    body={"requests": [{"insertText": {"location": {"index": 1}, "text": body_text}}]}
).execute()

print("Doc body inserted successfully!")
print("FINAL_GDOC_URL:", doc_url)

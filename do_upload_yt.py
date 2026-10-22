import sys
import os
sys.path.append('/home/satyaaditech/kontemplasi')
from upload_youtube import upload_video

VIDEO_FILE = '/home/satyaaditech/share/viral_sample/renungan_20261022_keserakahan_perfected.mp4'
title = 'Waspada Perangkap Keserakahan: Mengapa Otak Tak Pernah Puas? ⚖️ | Renungan SGS'

description = '''Pernahkah kita mengamati sebuah keganjilan halus di dalam batin kita sendiri? Ketika sebuah target materi yang dulu kita impikan akhirnya tercapai—entah saldo tabungan tertentu, kendaraan baru, atau pencapaian karier—rasa lega dan bahagia yang muncul ternyata hanya bertahan beberapa hari. Tak lama kemudian, rongga dada kembali terasa kosong, lalu kepala kita otomatis menyusun target baru yang lebih besar.

Sains modern menyebut siklus ini sebagai hedonic treadmill—mekanisme biologis di mana otak kita lekas terbiasa pada perolehan baru dan segera menuntut lonjakan kepuasan berikutnya agar tidak cemas. Nafsu jasmani adalah wadah tanpa dasar: semakin rakus kita mengisinya dengan materi dan perbandingan sosial, semakin bocor batin kita, menuntut kita terus berlari dalam kepanikan otopilot tanpa henti.

Di titik kelelahan inilah, Sang Guru Sejati membukakan rahasia adiluhung tentang Narima. Raga kita tetap tekun dan terampil menggarap apa yang ada di genggaman (digarap kanthi senenging ati), namun batin kita merdeka dari racun ketamakan (ora murka lan ora ngangsa-angsa) serta bebas dari perihnya iri dengki melihat rezeki orang lain (ora mengini darbeking liyan). Jiwa yang narima tidak bisa lagi disandera oleh pasang-surutnya roda dunia (menang karo owah gingsiring kahanan).

📖 Rujukan Kitab:
[SSJ] Serat Sasangka Jati — Kitab I: Hasta Sila (Panca Sila: 2. Narima)

Petikan Sabda Jawa Verbatim:
Narima iku akeh lerege marang tentreming ati, dadi dudu wong kang lumuh ing gawe, nanging kang narima ing sapandum. Apa kang wus cinekel ana ing tangane, digarap kanthi senenging ati, ora murka lan ora ngangsa-angsa. Narima iku ora mengini darbeking liyan, sarta ora meri marang kabegjane liyan, mulane wong kang narima iku kena den arani wong kang sokur ing Pangeran. Panarima iku sawijining bandha kang ora bisa entek, mulane sing sapa golek sugih upayanen aneng jroning panarima. Wong kang narima iku begja ing sajroning uripe, amarga dheweke menang karo owah gingsiring kahanan.

🧘 Laku Panyiswan (Mikro-Praktik 30 Detik):
1. Eling ing Pamikir (10s): Sadari kepanikan pikiran yang berbisik 'aku masih kurang'.
2. Ngrasakake Bandha Panarima (10s): Syukuri apa yang di genggaman tanpa membandingkan dengan milik sesama.
3. Menang ing Owah Gingsir (10s): Pasrah sumarah ing Gusti, raosaken katentreman ing sanubari.

💎 Mutiara Rasa:
Keserakahan lahir bukan karena dunia ini kekurangan, melainkan karena batin yang lupa pada Sang Urip takkan pernah mengenal kata cukup. Orang yang paling kaya di muka bumi bukanlah yang menggenggam segalanya, melainkan yang batinnya merdeka karena telah 'narima ing sapandum'.

🌐 Web Pustaka: https://kontemplasi.satyaaditech.web.id/#2026-10-22_waspada-perangkap-keserakahan

Semoga kita semua senantiasa berlimpah dengan sih, tuntunan, pepadang, dan pangayoman dari Sang Guru Sejati. Satuhu. 🙏🌿

#Eling #Narima #HedonicTreadmill #Keserakahan #Mindfulness #OlahRasa #Pangestu #SangGuruSejati #FilosofiJawa #KetenanganBatin #SadarJiwa #KesehatanMental #Shorts'''

tags = ['Pangestu', 'Sasangka Jati', 'Renungan Harian', 'Penyiswaan', 'Olahrasa', 'Narima', 'Keserakahan', 'Hedonic Treadmill', 'Laku Sejati']

print('Uploading to YouTube channel @siswatalkstv...')
res = upload_video(
    file_path=VIDEO_FILE,
    title=title,
    description=description,
    tags=tags,
    privacy='public'
)

print('UPLOAD_SUCCESS:', res)

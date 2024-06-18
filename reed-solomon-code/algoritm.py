from ff import GF256int
from polynomial import Polynomial

"""Modul ini mengimplementasikan Pengkodean Reed-Solomon.
Ini mendukung konfigurasi arbitrer untuk n dan k, panjang kata kode dan
panjang pesan. Ini dapat digunakan untuk menyesuaikan kekuatan koreksi kesalahan dari
kode.

Peringatan: Karena cara saya mengimplementasikannya, byte nol awal dalam sebuah
pesan akan dijatuhkan. Hati-hati jika mengkodekan data biner, tambahkan padding data Anda sendiri
ke k byte per blok untuk menghindari masalah. Lihat juga opsi nostrip untuk
decode().

Ketika dipanggil sebagai skrip, file ini mengkodekan data dari standar masukan dan mengeluarkannya
ke standar keluaran, menggunakan kode RS standar 255,223. Ini cocok untuk
mengkodekan teks dan mencobanya, tetapi jangan coba untuk mengkodekan data biner dengan itu!

Saat mengkodekan, ini mengeluarkan blok 255 byte, 223 di antaranya adalah data (dipad
dengan byte nol awal jika perlu) dan kemudian 32 byte data paritas.

Gunakan flag -d untuk mendekode data pada standar masukan ke standar keluaran. Ini membaca dalam
blok 255 byte, dan mengeluarkan data yang didekode dari mereka. Jika ada kurang dari
16 kesalahan per blok, data Anda akan dipulihkan.
"""

class RSCoder(object):
    def __init__(self, n, k):
        """Membuat objek Pengkode/Pendekode Reed-Solomon baru yang dikonfigurasi dengan
        nilai n dan k yang diberikan.
        n adalah panjang kata kode, harus kurang dari 256
        k adalah panjang pesan, harus kurang dari n

        Kode akan memiliki kekuatan koreksi kesalahan s di mana 2s = n - k

        RSCoder tipikal adalah RSCoder(255, 223)
        """
        if n < 0 or k < 0:
            raise ValueError("n dan k harus positif")
        if not n < 256:
            raise ValueError("n harus paling banyak 255")
        if not k < n:
            raise ValueError("Panjang kata kode n harus lebih besar dari panjang pesan k")
        self.n = n
        self.k = k

        # Hasilkan polinomial generator untuk kode RS
        # g(x) = (x-α^1)(x-α^2)...(x-α^(n-k))
        # α adalah 3, generator untuk GF(2^8)
        g = Polynomial((GF256int(1),))
        for alpha in range(1, n - k + 1):
            p = Polynomial((GF256int(1), GF256int(3) ** alpha))
            g = g * p
        self.g = g

        # h(x) = (x-α^(n-k+1))...(x-α^n)
        h = Polynomial((GF256int(1),))
        for alpha in range(n - k + 1, n + 1):
            p = Polynomial((GF256int(1), GF256int(3) ** alpha))
            h = h * p
        self.h = h

        # g*h digunakan dalam verifikasi, dan selalu x^n-1
        # TODO: Ini di-hardcode untuk (255, 223)
        # Tapi tidak masalah karena metode verifikasi saya tidak menggunakannya
        self.gtimesh = Polynomial(x255=GF256int(1), x0=GF256int(1))

    def encode(self, message, poly=False):
        """Mengkodekan string yang diberikan dengan pengkodean reed-solomon. Mengembalikan byte
        string dengan k byte pesan dan n-k byte paritas di akhir.
        
        Jika pesan < k byte panjangnya, diasumsikan telah dipad di depan
        dengan byte nol.

        Urutan yang dikembalikan selalu n byte panjang.

        Jika poly bukan False, mengembalikan objek Polynomial yang dikodekan sebagai gantinya
        dari polinomial yang diterjemahkan kembali ke string (berguna untuk debugging)
        """
        n = self.n
        k = self.k

        if len(message) > k:
            raise ValueError("Panjang pesan maksimal %d. Pesan adalah %d" % (k, len(message)))

        # Kodekan pesan sebagai polinomial:
        m = Polynomial(GF256int(b) for b in message)

        # Geser polinomial ke atas dengan n-k dengan mengalikan dengan x^(n-k)
        mprime = m * Polynomial((GF256int(1),) + (GF256int(0),) * (n - k))

        # mprime = q*g + b untuk beberapa q
        # jadi mari kita temukan b:
        b = mprime % self.g

        # Kurangi b, jadi sekarang c = q*g
        c = mprime - b
        # Karena c adalah kelipatan dari g, itu memiliki (setidaknya) n-k akar: α^1 hingga α^(n-k)

        if poly:
            return c

        # Ubah polinomial c kembali menjadi string byte
        return bytes(c.coefficients).rjust(n, b"\0")

    def verify(self, code):
        """Memverifikasi kode valid dengan menguji bahwa kode sebagai polinomial
        kode membagi g
        mengembalikan True/False
        """
        c = Polynomial(GF256int(b) for b in code)

        # Ini juga berfungsi, tetapi memakan waktu lebih lama. Kedua pemeriksaan sama validnya.
        # return (c * self.h) % self.gtimesh == Polynomial(x0=0)

        # Karena semua kata kode adalah kelipatan dari g, memeriksa bahwa kode membagi g
        # cukup untuk memvalidasi kata kode.
        return c % self.g == Polynomial(x0=0)

    def decode(self, r, nostrip=False):
        """Diberikan string atau array byte yang diterima r, mencoba untuk mendekodenya. Jika
        itu adalah kata kode yang valid, atau jika tidak lebih dari (n-k)/2 kesalahan, pesan
        dikembalikan.

        Pesan selalu memiliki k byte, jika pesan berisi kurang itu dibiarkan dengan padding byte nol di depan. Saat didekode, byte nol awal ini dihilangkan, tetapi itu dapat menyebabkan masalah jika mendekode data biner. Ketika nostrip adalah True, pesan yang dikembalikan selalu sepanjang k byte. Ini berguna untuk memastikan tidak ada data yang hilang saat mendekode data biner.
        """
        n = self.n
        k = self.k

        if self.verify(r):
            # n-k byte terakhir adalah paritas
            if nostrip:
                return r[:-(n - k)]
            else:
                return r[:-(n - k)].lstrip(b"\0")

        # Ubah r menjadi polinomial
        r = Polynomial(GF256int(b) for b in r)

        # Hitung sindrom:
        sz = self._syndromes(r)

        # Temukan polinomial lokator kesalahan dan polinomial evaluator kesalahan
        # menggunakan algoritma Berlekamp-Massey
        sigma, omega = self._berlekamp_massey(sz)

        # Sekarang gunakan prosedur Chien untuk menemukan lokasi kesalahan
        # j adalah array integer yang mewakili posisi kesalahan, 0
        # menjadi byte paling kanan
        # X adalah array yang sesuai dari nilai GF(2^8) di mana X_i = alpha^(j_i)
        X, j = self._chien_search(sigma)

        # Dan akhirnya, temukan besaran kesalahan dengan Formula Forney
        # Y adalah array nilai GF(2^8) yang sesuai dengan besaran kesalahan
        # di posisi yang diberikan oleh array j
        Y = self._forney(omega, X)

        # Gabungkan kesalahan dan lokasi bersama-sama untuk membentuk polinomial kesalahan
        Elist = []
        for i in range(255):
            if i in j:
                Elist.append(Y[j.index(i)])
            else:
                Elist.append(GF256int(0))
        E = Polynomial(reversed(Elist))

        # Dan kita mendapatkan kata kode sebenarnya!
        c = r - E

        # Bentuk kembali menjadi string dan kembalikan semua kecuali n-k byte terakhir
        ret = bytes(c.coefficients[:-(n - k)])

        if nostrip:
            # Objek Polynomial tidak menyimpan koefisien 0 awal, jadi kita
            # sebenarnya perlu menambahkan padding ini ke k byte
            return ret.rjust(k, b"\0")
        else:
            return ret

    def _syndromes(self, r):
        """Diberikan kata kode yang diterima r dalam bentuk objek Polynomial,
        menghitung sindrom dan mengembalikan polinomial sindrom
        """
        n = self.n
        k = self.k

        # s[l] adalah kata kode yang diterima dievaluasi pada α^l untuk 1 <= l <= s
        # α dalam implementasi ini adalah 3
        s = [GF256int(0)]  # s[0] adalah 0 (koefisien dari z^0)
        for l in range(1, n - k + 1):
            s.append(r.evaluate(GF256int(3) ** l))

        # Sekarang bangun polinomial dari semua nilai s[l] kita
        # s(z) = sum(s_i * z^i, i=1..inf)
        sz = Polynomial(reversed(s))

        return sz

    def _berlekamp_massey(self, s):
        """Menghitung dan mengembalikan polinomial lokator kesalahan (sigma) dan polinomial
        evaluator kesalahan (omega)
        Parameter s adalah polinomial sindrom (sindrom dikodekan dalam fungsi
        generator) seperti yang dikembalikan oleh _syndromes. Jangan bingung dengan
        s lainnya = (n-k)/2

        Catatan:
        Polinomial kesalahan:
        E(x) = E_0 + E_1 x + ... + E_(n-1) x^(n-1)

        j_1, j_2, ..., j_s adalah posisi kesalahan. (Ada paling banyak s
        kesalahan)

        Lokasi kesalahan X_i didefinisikan: X_i = α^(j_i)
        yaitu, pangkat α yang sesuai dengan lokasi kesalahan

        Besaran kesalahan Y_i didefinisikan: E_(j_i)
        yaitu, koefisien dalam polinomial kesalahan di posisi j_i

        Polinomial lokator kesalahan:
        sigma(z) = Produk( 1 - X_i * z, i=1..s )
        akar adalah kebalikan dari lokasi kesalahan
        ( 1/X_1, 1/X_2, ...)

        Polinomial evaluator kesalahan omega(z) tidak ditulis di sini
        """
        n = self.n
        k = self.k

        # Inisialisasi:
        sigma = [Polynomial((GF256int(1),))]
        omega = [Polynomial((GF256int(1),))]
        tao = [Polynomial((GF256int(1),))]
        gamma = [Polynomial((GF256int(0),))]
        D = [0]
        B = [0]

        # Konstanta polinomial:
        ONE = Polynomial(z0=GF256int(1))
        ZERO = Polynomial(z0=GF256int(0))
        Z = Polynomial(z1=GF256int(1))
        
        # Secara iteratif menghitung polinomial 2s kali. Yang terakhir akan benar
        for l in range(0, n - k):
            # Tujuan untuk setiap iterasi: Menghitung sigma[l+1] dan omega[l+1] sehingga
            # (1 + s)*sigma[l] == omega[l] dalam mod z^(l+1)

            # Untuk iterasi loop ini, kita memiliki sigma[l] dan omega[l],
            # dan sedang menghitung sigma[l+1] dan omega[l+1]
            
            # Pertama temukan Delta, koefisien non-nol dari z^(l+1) dalam
            # (1 + s) * sigma[l]
                        # Delta ini valid untuk l (iterasi ini) saja
            Delta = ((ONE + s) * sigma[l]).get_coefficient(l + 1)
            # Jadikan itu polinomial derajat 0
            Delta = Polynomial(x0=Delta)

            # Sekarang hitung sigma[l+1] dan omega[l+1] dari
            # sigma[l], omega[l], tao[l], gamma[l], dan Delta
            sigma.append(sigma[l] - Delta * Z * tao[l])
            omega.append(omega[l] - Delta * Z * gamma[l])

            # Sekarang hitung tao dan gamma berikutnya
            # Ada dua cara untuk melakukan ini
            if Delta == ZERO or 2 * D[l] > (l + 1):
                # Aturan A
                D.append(D[l])
                B.append(B[l])
                tao.append(Z * tao[l])
                gamma.append(Z * gamma[l])

            elif Delta != ZERO and 2 * D[l] < (l + 1):
                # Aturan B
                D.append(l + 1 - D[l])
                B.append(1 - B[l])
                tao.append(sigma[l] // Delta)
                gamma.append(omega[l] // Delta)
            elif 2 * D[l] == (l + 1):
                if B[l] == 0:
                    # Aturan A (sama seperti di atas)
                    D.append(D[l])
                    B.append(B[l])
                    tao.append(Z * tao[l])
                    gamma.append(Z * gamma[l])

                else:
                    # Aturan B (sama seperti di atas)
                    D.append(l + 1 - D[l])
                    B.append(1 - B[l])
                    tao.append(sigma[l] // Delta)
                    gamma.append(omega[l] // Delta)
            else:
                raise Exception("Kode tidak seharusnya sampai di sini")

        return sigma[-1], omega[-1]

    def _chien_search(self, sigma):
        """Ingat definisi sigma, itu memiliki s akar. Untuk menemukannya, fungsi ini
        mengevaluasi sigma di semua 255 titik non-nol untuk menemukan akarnya
        Kebalikan dari akar adalah X_i, lokasi kesalahan

        Mengembalikan daftar X lokasi kesalahan, dan daftar j yang sesuai dari
        posisi kesalahan (log diskrit dari nilai X yang sesuai) Daftar
        ini bisa besar hingga s elemen.

        Catatan teknis matematika penting: Implementasi ini sebenarnya bukan
        pencarian Chien. Pencarian Chien adalah cara untuk mengevaluasi polinomial
        sehingga setiap evaluasi hanya memakan waktu konstan. Di sini hanya
        melakukan 255 evaluasi langsung, yang jauh kurang efisien.
        """
        X = []
        j = []
        p = GF256int(3)
        for l in range(1, 256):
            # Evaluasi ini bisa lebih efisien, tetapi ya sudahlah
            if sigma.evaluate(p ** l) == 0:
                X.append(p ** (-l))
                # Ini berbeda dari catatan, saya pikir catatan itu salah
                # Catatan mengatakan nilai j hanya l, padahal sebenarnya 255 - l
                j.append(255 - l)

        return X, j

    def _forney(self, omega, X):
        """Menghitung besaran kesalahan"""
        s = (self.n - self.k) // 2

        Y = []

        for l, Xl in enumerate(X):
            # Hitung bagian pertama dari Yl
            Yl = Xl ** s
            Yl *= omega.evaluate(Xl.inverse())
            Yl *= Xl.inverse()

            # Hitung produk urutan dan kalikan kebalikannya
            prod = GF256int(1)
            for ji in range(s):
                if ji == l:
                    continue
                if ji < len(X):
                    Xj = X[ji]
                else:
                    Xj = GF256int(0)
                prod = prod * (Xl - Xj)
            Yl = Yl * prod.inverse()

            Y.append(Yl)
        return Y

if __name__ == "__main__":
    def test_rs_coder():
        print("\nREED SOLOMON ALGORITHM\n")

        # Inisialisasi RS Coder dengan parameter tipikal (255, 223)
        coder = RSCoder(255, 223)

        # Pesan uji
        message = b"Hello, world"
        print(f"Pesan asli: {message}\n")

        # Kodekan pesan
        print("====================ENCODE====================")
        encoded_message = coder.encode(message)
        print(f"Pesan ter-Encode: {encoded_message}")

        # Dekode pesan
        print("\n====================DECODE====================")
        decoded_message = coder.decode(encoded_message)
        print(f"Pesan ter-Decode: {decoded_message}")

        # Periksa apakah pesan terdekod cocok dengan pesan asli
        assert message == decoded_message, "Dekoding gagal!"
        print("Dekoding berhasil!")

        # Perkenalkan beberapa kesalahan ke pesan terkode
        encoded_message_with_errors = bytearray(encoded_message)
        encoded_message_with_errors[0] ^= 0xFF  # Balikkan byte pertama
        encoded_message_with_errors[10] ^= 0xFF  # Balikkan byte ke-11

        # Dekode pesan yang rusak
        print("\n====================DECODE WITH ERRORS====================")
        try:
            corrected_message = coder.decode(encoded_message_with_errors)
            print(f"Pesan yang dikoreksi: {corrected_message}")
            assert message == corrected_message, "Koreksi kesalahan gagal!"
            print("Koreksi kesalahan berhasil!")
        except Exception as e:
            print(f"Koreksi kesalahan gagal: {e}")

    test_rs_coder()

    print("All test Completed!")

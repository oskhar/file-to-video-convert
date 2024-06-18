from ff import GF256int
from polynomial import Polynomial

"""
Modul ini mengimplementasikan Pengkodean Reed-Solomon.
Ini mendukung konfigurasi sembarang untuk n dan k, panjang kode kata dan
panjang pesan. Ini dapat digunakan untuk menyesuaikan daya koreksi kesalahan kode.

Peringatan: Karena cara saya mengimplementasikan ini, byte nol terdepan dalam pesan akan dihapus.
Hati-hati jika mengkodekan data biner, bantallah data sendiri hingga k byte per blok untuk menghindari masalah. Juga lihat opsi nostrip pada
decode().

Ketika dipanggil sebagai skrip, file ini mengkodekan data dari standar input dan mengeluarkannya
ke standar output, menggunakan kode RS standar 255,223. Ini cocok untuk
mengkodekan teks dan mencobanya, tetapi jangan mencoba mengkodekan data biner dengan itu!

Saat mengkodekan, ia mengeluarkan blok 255 byte, 223 di antaranya adalah data (dipadatkan
dengan byte nol terdepan jika perlu) dan kemudian 32 byte data paritas.

Gunakan bendera -d untuk mendekode data pada standar input ke standar output. Ini membaca dalam
blok 255 byte, dan mengeluarkan data yang didekodekan dari mereka. Jika ada kurang dari
16 kesalahan per blok, data Anda akan dipulihkan.
"""

class RSCoder(object):
    def __init__(self, n, k):
        """
        Membuat objek Pengkode/Pendekode Reed-Solomon baru yang dikonfigurasi dengan
        nilai n dan k yang diberikan.
        n adalah panjang kode kata, harus kurang dari 256
        k adalah panjang pesan, harus kurang dari n

        Kode akan memiliki daya koreksi kesalahan s di mana 2s = n - k

        RSCoder yang khas adalah RSCoder(255, 223)
        """
        if n < 0 or k < 0:
            raise ValueError("n dan k harus positif")
        if not n < 256:
            raise ValueError("n harus paling banyak 255")
        if not k < n:
            raise ValueError("Panjang kode kata n harus lebih besar dari panjang pesan k")
        self.n = n
        self.k = k

        # Menghasilkan polinomial generator untuk kode RS
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
        # TODO: Ini dikodekan keras untuk (255, 223)
        # Tetapi tidak masalah karena metode verifikasi saya tidak menggunakannya
        self.gtimesh = Polynomial(x255=GF256int(1), x0=GF256int(1))

    def encode(self, pesan, poly=False):
        """
        Mengkodekan string yang diberikan dengan pengkodean reed-solomon. Mengembalikan byte
        string dengan k byte pesan dan n-k byte paritas di akhir.
        
        Jika pesan kurang dari k byte panjangnya, diasumsikan dipadatkan di depan
        dengan byte nol.

        Urutan yang dikembalikan selalu n byte panjangnya.

        Jika poly tidak False, mengembalikan objek Polynomial yang dikodekan sebagai ganti
        polinomial diterjemahkan kembali ke string (berguna untuk debugging)
        """
        n = self.n
        k = self.k

        if len(pesan) > k:
            raise ValueError("Panjang pesan maksimal adalah %d. Pesan ini %d" % (k, len(pesan)))

        # Encode pesan sebagai polinomial:
        m = Polynomial(GF256int(b) for b in pesan)

        # Geser polinomial ke atas dengan n-k dengan mengalikan dengan x^(n-k)
        mprime = m * Polynomial((GF256int(1),) + (GF256int(0),) * (n - k))

        # mprime = q*g + b untuk beberapa q
        # jadi mari kita temukan b:
        b = mprime % self.g

        # Kurangkan b, jadi sekarang c = q*g
        c = mprime - b
        # Karena c adalah kelipatan dari g, ia memiliki (setidaknya) n-k akar: α^1 hingga α^(n-k)

        if poly:
            return c

        # Ubah polinomial c kembali menjadi byte string
        return bytes(c.coefficients).rjust(n, b"\0")

    def verify(self, code):
        """
        Memverifikasi kode valid dengan menguji bahwa kode sebagai polinomial
        membagi g
        mengembalikan True/False
        """
        c = Polynomial(GF256int(b) for b in code)

        # Ini juga berfungsi, tetapi memakan waktu lebih lama. Kedua pengecekan sama-sama valid.
        # return (c * self.h) % self.gtimesh == Polynomial(x0=0)

        # Karena semua kode kata adalah kelipatan dari g, memeriksa bahwa kode membagi g
        # cukup untuk memvalidasi kode kata.
        return c % self.g == Polynomial(x0=0)

    def decode(self, r, nostrip=False):
        """
        Diberi string yang diterima atau array byte r, berusaha untuk mendekodekannya. Jika
        itu adalah kode kata yang valid, atau jika ada tidak lebih dari (n-k)/2 kesalahan,
        pesan dikembalikan.

        Sebuah pesan selalu memiliki k byte, jika pesan berisi lebih sedikit, itu akan
        dipadatkan dengan byte nol. Saat didekodekan, byte nol terdepan ini
        dihapus, tetapi itu bisa menyebabkan masalah jika mendekodekan data biner. Saat
        nostrip adalah True, pesan yang dikembalikan selalu k byte panjangnya. Ini berguna untuk memastikan tidak ada data yang hilang saat mendekodekan data biner.
        """
        n = self.n
        k = self.k

        if self.verify(r):
            # Byte terakhir n-k adalah paritas
            if nostrip:
                return r[:-(n - k)]
            else:
                return r[:-(n - k)].lstrip(b"\0")

        # Ubah r menjadi polinomial
        r = Polynomial(GF256int(b) for b in r)

        # Hitung sindrom:
        sz = self._syndromes(r)

        # Temukan polinomial penemu kesalahan dan polinomial penilai kesalahan
        # menggunakan algoritma Berlekamp-Massey
        sigma, omega = self._berlekamp_massey(sz)

        # Sekarang gunakan prosedur Chien untuk menemukan lokasi kesalahan
        # j adalah array integer yang mewakili posisi kesalahan, 0
        # adalah byte paling kanan
        # X adalah array nilai GF(2^8) yang sesuai di mana X_i = alpha^(j_i)
        X, j = self._chien_search(sigma)

        # Dan akhirnya, temukan magnitudo kesalahan dengan Rumus Forney
        # Y adalah array nilai GF(2^8) yang sesuai dengan magnitudo kesalahan
        # pada posisi yang diberikan oleh array j
        Y = self._forney(omega, X)

        # Gabungkan kesalahan dan lokasi untuk membentuk polinomial kesalahan
        Elist = []
        for i in range(255):
            if i in j:
                Elist.append(Y[j.index(i)])
            else:
                Elist.append(GF256int(0))
        E = Polynomial(reversed(Elist))

        # Dan kita mendapatkan kode kata nyata kita!
        c = r - E

        # Bentuknya kembali menjadi string dan kembalikan semua kecuali byte terakhir n-k
        ret = bytes(c.coefficients[:-(n - k)])

        if nostrip:
            # Objek Polynomial tidak menyimpan koefisien 0 terdepan, jadi kita
            # sebenarnya perlu menambahkannya hingga k byte
            return ret.rjust(k, b"\0")
        else:
            return ret

    def _syndromes(self, r):
        """
        Diberi kode kata yang diterima r dalam bentuk objek Polynomial,
        menghitung sindrom dan mengembalikan polinomial sindrom
        """
        n = self.n
        k = self.k

        # s[l] adalah kode kata yang diterima dievaluasi pada α^l untuk 1 <= l <= s
        # α dalam implementasi ini adalah 3
        s = [GF256int(0)]  # s[0] adalah 0 (koefisien dari z^0)
        for l in range(1, n - k + 1):
            s.append(r.evaluate(GF256int(3) ** l))

        # Sekarang bangun polinomial dari semua nilai s[l] kita
        # s(z) = sum(s_i * z^i, i=1..inf)
        sz = Polynomial(reversed(s))

        return sz

    def _berlekamp_massey(self, s):
        """
        Menghitung dan mengembalikan polinomial penemu kesalahan (sigma) dan
        polinomial penilai kesalahan (omega)
        Parameter s adalah polinomial sindrom (sindrom yang dikodekan dalam
        fungsi generator) seperti yang dikembalikan oleh _syndromes. Jangan bingung dengan
        s lainnya = (n-k)/2

        Catatan:
        Polinomial kesalahan:
        E(x) = E_0 + E_1 x + ... + E_(n-1) x^(n-1)

        j_1, j_2, ..., j_s adalah posisi kesalahan. (Ada paling banyak s
        kesalahan)

        Lokasi kesalahan X_i didefinisikan: X_i = α^(j_i)
        yaitu, pangkat dari α yang sesuai dengan lokasi kesalahan

        Magnitudo kesalahan Y_i didefinisikan: E_(j_i)
        yaitu, koefisien dalam polinomial kesalahan pada posisi j_i

        Polinomial penemu kesalahan:
        sigma(z) = Product( 1 - X_i * z, i=1..s )
        akar adalah kebalikan dari lokasi kesalahan
        ( 1/X_1, 1/X_2, ...)

        Polinomial penilai kesalahan omega(z) tidak ditulis di sini
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
        
        # Menghitung polinomial secara iteratif 2s kali. Yang terakhir akan benar
        for l in range(0, n - k):
            # Tujuan untuk setiap iterasi: Hitung sigma[l+1] dan omega[l+1] sedemikian rupa sehingga
            # (1 + s)*sigma[l] == omega[l] dalam mod z^(l+1)

            # Untuk iterasi loop tertentu ini, kita memiliki sigma[l] dan omega[l],
            # dan sedang menghitung sigma[l+1] dan omega[l+1]
            
            # Pertama temukan Delta, koefisien tidak nol dari z^(l+1) dalam
            # (1 + s) * sigma[l]
            # Delta ini valid untuk l (iterasi ini) saja
            Delta = ((ONE + s) * sigma[l]).get_coefficient(l + 1)
            # Jadikan itu polinomial derajat 0
            Delta = Polynomial(x0=Delta)

            # Sekarang dapat menghitung sigma[l+1] dan omega[l+1] dari
            # sigma[l], omega[l], tao[l], gamma[l], dan Delta
            sigma.append(sigma[l] - Delta * Z * tao[l])
            omega.append(omega[l] - Delta * Z * gamma[l])

            # Sekarang hitung tao dan gamma berikutnya
            # Ada dua cara untuk melakukannya
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
                raise Exception("Kode seharusnya tidak sampai di sini")

        return sigma[-1], omega[-1]

    def _chien_search(self, sigma):
        """
        Ingat definisi sigma, ia memiliki s akar. Untuk menemukannya, fungsi ini mengevaluasi sigma pada semua 255 titik non-nol untuk menemukan akar
        Kebalikan dari akar adalah X_i, lokasi kesalahan

        Mengembalikan daftar X dari lokasi kesalahan, dan daftar j yang sesuai dari
        posisi kesalahan (log diskrit dari nilai X yang sesuai) Daftar
        maksimal s elemen besar.

        Catatan teknis penting: Implementasi ini sebenarnya bukan
        Pencarian Chien. Pencarian Chien adalah cara mengevaluasi polinomial
        sehingga setiap evaluasi hanya memakan waktu konstan. Ini di sini hanya
        melakukan 255 evaluasi secara langsung, yang jauh kurang efisien.
        """
        X = []
        j = []
        p = GF256int(3)
        for l in range(1, 256):
            # Evaluasi ini bisa lebih efisien, tetapi oh well
            if sigma.evaluate(p ** l) == 0:
                X.append(p ** (-l))
                # Ini berbeda dari catatan, saya pikir catatan itu salah
                # Catatan mengatakan nilai j hanya l, padahal sebenarnya 255 - l
                j.append(255 - l)

        return X, j

    def _forney(self, omega, X):
        """Menghitung magnitudo kesalahan"""
        s = (self.n - self.k) // 2

        Y = []

        for l, Xl in enumerate(X):
            # Hitung bagian pertama dari Yl
            Yl = Xl ** s
            Yl *= omega.evaluate(Xl.inverse())
            Yl *= Xl.inverse()

            # Hitung urutan produk dan kalikan kebalikannya
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
    def uji_pengkode_rs():
        print("Mengujicoba Pengkode RS...")

        # Inisialisasi Pengkode RS dengan parameter tipikal (255, 223)
        Code = RSCoder(255, 223)

        # Pesan uji
        pesan = b"Hello, Reed-Solomon!"
        print(f"Pesan asli: {pesan}")

        # Mengkodekan pesan
        pesan_terkode = Code.encode(pesan)
        print(f"Pesan terkode: {pesan_terkode}")

        # Mendekodekan pesan
        pesan_didekode = Code.decode(pesan_terkode)
        print(f"Pesan didekode: {pesan_didekode}")

        # Memeriksa apakah pesan yang didekodekan sesuai dengan pesan asli
        assert pesan == pesan_didekode, "Dekode gagal!"
        print("Dekode berhasil!")

        # Memperkenalkan beberapa kesalahan pada pesan terkode
        pesan_terkode_dengan_kesalahan = bytearray(pesan_terkode)
        pesan_terkode_dengan_kesalahan[0] ^= 0xFF  # Balikkan byte pertama
        pesan_terkode_dengan_kesalahan[10] ^= 0xFF  # Balikkan byte ke-11

        # Mendekodekan pesan yang rusak
        try:
            pesan_terkoreksi = Code.decode(pesan_terkode_dengan_kesalahan)
            print(f"Pesan terkoreksi: {pesan_terkoreksi}")
            assert pesan == pesan_terkoreksi, "Koreksi kesalahan gagal!"
            print("Koreksi kesalahan berhasil!")
        except Exception as e:
            print(f"Koreksi kesalahan gagal: {e}")

    uji_pengkode_rs()

    print("Semua uji selesai.")

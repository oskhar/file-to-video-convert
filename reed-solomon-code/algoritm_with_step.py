from ff import GF256int
from polynomial import Polynomial

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
        print(f"Starting encoding process for message: {pesan}")

        n = self.n
        k = self.k

        if len(pesan) > k:
            raise ValueError("Panjang pesan maksimal adalah %d. Pesan ini %d" % (k, len(pesan)))

        # Encode pesan sebagai polinomial:
        m = Polynomial(GF256int(b) for b in pesan)
        print(f"Message as polynomial: {m}")

        # Geser polinomial ke atas dengan n-k dengan mengalikan dengan x^(n-k)
        mprime = m * Polynomial((GF256int(1),) + (GF256int(0),) * (n - k))
        print(f"Shifted polynomial mprime: {mprime}")

        # mprime = q*g + b untuk beberapa q
        # jadi mari kita temukan b:
        b = mprime % self.g
        print(f"Remainder polynomial b: {b}")

        # Kurangkan b, jadi sekarang c = q*g
        c = mprime - b
        print(f"Codeword polynomial c: {c}")

        if poly:
            return c

        # Ubah polinomial c kembali menjadi byte string
        encoded_message = bytes(c.coefficients).rjust(n, b"\0")
        print(f"Encoded message: {encoded_message}")
        return encoded_message

    def verify(self, code):
        """
        Memverifikasi kode valid dengan menguji bahwa kode sebagai polinomial
        membagi g
        mengembalikan True/False
        """
        c = Polynomial(GF256int(b) for b in code)
        print(f"Verifying code: {c}")

        # Ini juga berfungsi, tetapi memakan waktu lebih lama. Kedua pengecekan sama-sama valid.
        # return (c * self.h) % self.gtimesh == Polynomial(x0=0)

        # Karena semua kode kata adalah kelipatan dari g, memeriksa bahwa kode membagi g
        # cukup untuk memvalidasi kode kata.
        is_valid = c % self.g == Polynomial(x0=0)
        print(f"Verification result: {is_valid}")
        return is_valid

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
        print(f"Starting decoding process for received code: {r}")

        n = self.n
        k = self.k

        if self.verify(r):
            # Byte terakhir n-k adalah paritas
            if nostrip:
                decoded_message = r[:-(n - k)]
                print(f"Decoded message (nostrip): {decoded_message}")
                return decoded_message
            else:
                decoded_message = r[:-(n - k)].lstrip(b"\0")
                print(f"Decoded message: {decoded_message}")
                return decoded_message

        # Ubah r menjadi polinomial
        r = Polynomial(GF256int(b) for b in r)
        print(f"Received code as polynomial: {r}")

        # Hitung sindrom:
        sz = self._syndromes(r)
        print(f"Syndromes polynomial: {sz}")

        # Temukan polinomial penemu kesalahan dan polinomial penilai kesalahan
        # menggunakan algoritma Berlekamp-Massey
        sigma, omega = self._berlekamp_massey(sz)
        print(f"Error locator polynomial sigma: {sigma}")
        print(f"Error evaluator polynomial omega: {omega}")

        # Sekarang gunakan prosedur Chien untuk menemukan lokasi kesalahan
        # j adalah array integer yang mewakili posisi kesalahan, 0
        # adalah byte paling kanan
        # X adalah array nilai GF(2^8) yang sesuai di mana X_i = alpha^(j_i)
        X, j = self._chien_search(sigma)
        print(f"Error locations X: {X}")
        print(f"Error positions j: {j}")

        # Dan akhirnya, temukan magnitudo kesalahan dengan Rumus Forney
        # Y adalah array nilai GF(2^8) yang sesuai dengan magnitudo kesalahan
        # pada posisi yang diberikan oleh array j
        Y = self._forney(omega, X)
        print(f"Error magnitudes Y: {Y}")

        # Gabungkan kesalahan dan lokasi untuk membentuk polinomial kesalahan
        Elist = []
        for i in range(255):
            if i in j:
                Elist.append(Y[j.index(i)])
            else:
                Elist.append(GF256int(0))
        E = Polynomial(reversed(Elist))
        print(f"Error polynomial E: {E}")

        # Dan kita mendapatkan kode kata nyata kita!
        c = r - E
        print(f"Corrected codeword polynomial c: {c}")

        # Bentuknya kembali menjadi string dan kembalikan semua kecuali byte terakhir n-k
        ret = bytes(c.coefficients[:-(n - k)])

        if nostrip:
            # Objek Polynomial tidak menyimpan koefisien 0 terdepan, jadi kita
            # sebenarnya perlu menambahkannya hingga k byte
            decoded_message = ret.rjust(k, b"\0")
            print(f"Decoded message (nostrip): {decoded_message}")
            return decoded_message
        else:
            decoded_message = ret
            print(f"Decoded message: {decoded_message}")
            return decoded_message

    def _syndromes(self, r):
        """
        Diberi kode kata yang diterima r dalam bentuk objek Polynomial,
        menghitung sindrom dan mengembalikan polinomial sindrom
        """
        n = self.n
        k = self.k

        # s[l] adalah kode kata yang diterima dievaluasi pada α^l untuk 1 <= l <= s
        # α dalam implementasi ini adalah 3
        s = [GF256int(0)]  # s[0] adalah tempat kosong, diindeks dari 1
        for l in range(1, n - k + 1):
            s.append(r(GF256int(3) ** l))

        # Bentuknya menjadi polinomial
        sz = Polynomial((GF256int(0),) + tuple(s))
        print(f"Syndromes: {s}")
        print(f"Syndromes polynomial sz: {sz}")
        return sz

    def _berlekamp_massey(self, sz):
        """
        Menggunakan sindrom sz, gunakan algoritma Berlekamp-Massey untuk menemukan
        polinomial penemu kesalahan sigma dan polinomial penilai kesalahan omega

        Mengembalikan sigma, omega dalam bentuk objek Polynomial
        """
        n = self.n
        k = self.k

        s = sz.coefficients[1:]
        print(f"Syndromes coefficients: {s}")

        # Implementasi algoritma Berlekamp-Massey dari pseudocode Wikipedia
        C = [GF256int(0)] * (n - k + 1)
        B = [GF256int(0)] * (n - k + 1)
        C[0] = GF256int(1)
        B[0] = GF256int(1)

        L = 0
        m = 1
        b = GF256int(1)

        for n in range(len(s)):
            # Hitung disparitas
            d = s[n]
            for i in range(1, L + 1):
                d += C[i] * s[n - i]

            if d != GF256int(0):
                T = C[:]
                factor = d / b
                for i in range(m, n - L + m):
                    C[i] -= factor * B[i - m]
                if L <= n / 2:
                    L = n + 1 - L
                    B = T
                    b = d
                    m = 0

            m += 1

        sigma = Polynomial(C)
        omega = Polynomial(s[:len(sigma.coefficients) - 1] + (GF256int(0),))
        print(f"Error locator polynomial sigma: {sigma}")
        print(f"Error evaluator polynomial omega: {omega}")
        return sigma, omega

    def _chien_search(self, sigma):
        """
        Menggunakan prosedur Chien untuk menemukan akar dari polinomial penemu kesalahan sigma

        Mengembalikan array X dan array j. X adalah nilai GF(2^8) di mana
        akar sigma(X[i]) = 0 ditemukan. j adalah posisi dalam kode kata yang
        kesalahan terjadi, dimulai dengan 0 untuk byte paling kanan
        """
        X = []
        j = []
        alpha = GF256int(3)

        for i in range(256):
            if sigma(alpha ** i) == GF256int(0):
                X.append(alpha ** i)
                j.append(255 - i)

        print(f"Chien search results, error locations X: {X}")
        print(f"Chien search results, error positions j: {j}")
        return X, j

    def _forney(self, omega, X):
        """
        Menggunakan Rumus Forney untuk menghitung magnitudo kesalahan Y_i dari X_i

        Mengembalikan array Y, nilai GF(2^8) dari magnitudo kesalahan
        """
        Y = []
        for X_i in X:
            denominator = GF256int(1)
            for X_j in X:
                if X_i != X_j:
                    denominator *= X_i + X_j
            Y.append(-omega(X_i) / denominator)

        print(f"Forney error magnitudes Y: {Y}")
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

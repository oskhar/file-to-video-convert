# Penjelasan tentang Step "Analyze Unicode Characters"

#### 0. **Analisis Karakter Unicode**

Dalam proses pembuatan QR Code, langkah pertama adalah menganalisis karakter Unicode dalam teks input untuk menentukan mode encoding yang paling sesuai.

QR Code mendukung beberapa mode encoding, yaitu Numeric, Alphanumeric, Byte, dan Kanji, masing-masing dengan kapasitas dan tujuan yang berbeda.

#### Rincian Karakter

Tabel berikut menunjukkan detail dari setiap karakter dalam teks "Hello, world! 123":

| Index | Char | CP hex | NM (Numeric Mode) | AM (Alphanumeric Mode) | BM (Byte Mode) | KM (Kanji Mode) |
| ----- | ---- | ------ | ----------------- | ---------------------- | -------------- | --------------- |
| 0     | H    | U+0048 | No                | Yes                    | Yes            | No              |
| 1     | e    | U+0065 | No                | No                     | Yes            | No              |
| 2     | l    | U+006C | No                | No                     | Yes            | No              |
| 3     | l    | U+006C | No                | No                     | Yes            | No              |
| 4     | o    | U+006F | No                | No                     | Yes            | No              |
| 5     | ,    | U+002C | No                | No                     | Yes            | No              |
| 6     |      | U+0020 | No                | Yes                    | Yes            | No              |
| 7     | w    | U+0077 | No                | No                     | Yes            | No              |
| 8     | o    | U+006F | No                | No                     | Yes            | No              |
| 9     | r    | U+0072 | No                | No                     | Yes            | No              |
| 10    | l    | U+006C | No                | No                     | Yes            | No              |
| 11    | d    | U+0064 | No                | No                     | Yes            | No              |
| 12    | !    | U+0021 | No                | No                     | Yes            | No              |
| 13    |      | U+0020 | No                | Yes                    | Yes            | No              |
| 14    | 1    | U+0031 | Yes               | Yes                    | Yes            | No              |
| 15    | 2    | U+0032 | Yes               | Yes                    | Yes            | No              |
| 16    | 3    | U+0033 | Yes               | Yes                    | Yes            | No              |

#### Keterangan:

- **CP hex**: Kode titik (code point) dalam format hexadecimal.
- **NM**: Apakah karakter bisa di-encode dalam Mode Numerik?
- **AM**: Apakah karakter bisa di-encode dalam Mode Alfanumerik?
- **BM**: Apakah karakter bisa di-encode dalam Mode Byte?
- **KM**: Apakah karakter bisa di-encode dalam Mode Kanji?

#### Hasil Analisis

- **Numeric Mode (NM)**: Hanya karakter '1', '2', dan '3' yang bisa di-encode dalam mode ini.
- **Alphanumeric Mode (AM)**: Tidak semua karakter bisa di-encode dalam mode ini.
- **Byte Mode (BM)**: Semua karakter bisa di-encode dalam mode ini.
- **Kanji Mode (KM)**: Tidak ada karakter yang bisa di-encode dalam mode ini.

### Mode yang Dipilih

**Byte Mode** dipilih karena semua karakter dalam teks input bisa di-encode dalam mode ini.

### Di mana letak step ini dalam kode?

Bagian kode yang melakukan analisis karakter Unicode dan memilih mode encoding adalah sebagai berikut:

```python
class QrSegment:
    # ... Kode lainnya

	_mode: QrSegment.Mode

	def __init__(self, mode: QrSegment.Mode, numch: int, bitdata: Sequence[int]) -> None:
		if numch < 0:
			raise ValueError()
		self._mode = mode
		self._numchars = numch
		self._bitdata = list(bitdata)

    def get_mode(self) -> QrSegment.Mode:
        return self._mode

	class Mode:

		_modebits: int
		_charcounts: tuple[int,int,int]

		def __init__(self, modebits: int, charcounts: tuple[int,int,int]):
			self._modebits = modebits
			self._charcounts = charcounts

		def get_mode_bits(self) -> int:
			return self._modebits

		def num_char_count_bits(self, ver: int) -> int:
			return self._charcounts[(ver + 7) // 17]

		NUMERIC     : QrSegment.Mode
		ALPHANUMERIC: QrSegment.Mode
		BYTE        : QrSegment.Mode
		KANJI       : QrSegment.Mode
		ECI         : QrSegment.Mode

	Mode.NUMERIC      = Mode(0x1, (10, 12, 14))
	Mode.ALPHANUMERIC = Mode(0x2, ( 9, 11, 13))
	Mode.BYTE         = Mode(0x4, ( 8, 16, 16))
	Mode.KANJI        = Mode(0x8, ( 8, 10, 12))
	Mode.ECI          = Mode(0x7, ( 0,  0,  0))
    # ... Kode lainnya
```

Output akan menunjukkan bahwa mode Byte dipilih, dengan jumlah byte dan panjang data dalam bit, sesuai dengan hasil analisis.

# Penjelasan tentang Step "Membuat Data Segmen"

#### 1. Konversi Karakter ke Bit

Dalam proses pembuatan segmen data untuk QR Code, setiap karakter dalam teks diubah menjadi representasi biner (bit). Tabel berikut menunjukkan bagaimana setiap karakter dalam teks "Hello, world! 123" dikonversi menjadi bit:

| Index | Char | Values (hex) | Bits     |
| ----- | ---- | ------------ | -------- |
| 0     | H    | 48           | 01001000 |
| 1     | e    | 65           | 01100101 |
| 2     | l    | 6C           | 01101100 |
| 3     | l    | 6C           | 01101100 |
| 4     | o    | 6F           | 01101111 |
| 5     | ,    | 2C           | 00101100 |
| 6     |      | 20           | 00100000 |
| 7     | w    | 77           | 01110111 |
| 8     | o    | 6F           | 01101111 |
| 9     | r    | 72           | 01110010 |
| 10    | l    | 6C           | 01101100 |
| 11    | d    | 64           | 01100100 |
| 12    | !    | 21           | 00100001 |
| 13    |      | 20           | 00100000 |
| 14    | 1    | 31           | 00110001 |
| 15    | 2    | 32           | 00110010 |
| 16    | 3    | 33           | 00110011 |

#### 2. Segmen yang Dibuat

Segmen yang dihasilkan dari konversi di atas adalah sebagai berikut:

- **Mode:** Byte
- **Count:** 17 bytes (jumlah total karakter)
- **Data:** 136 bits (17 bytes \* 8 bits per byte)

#### Kenapa Harus Dijadikan Biner?

1. Standar QR Code:

   - QR Code memiliki standar encoding yang ditentukan oleh ISO/IEC 18004. Standar ini mengharuskan data dalam QR Code untuk diubah menjadi format biner agar dapat di-encode dan dibaca oleh scanner.

2. Kompresi dan Efisiensi:

   - Representasi biner memungkinkan data untuk di-encode dalam bentuk yang paling padat dan efisien. Mode byte, misalnya, menggunakan 8 bit per karakter, yang memungkinkan penggunaan memori yang efisien.

3. Koreksi Kesalahan:

   - Sistem koreksi kesalahan QR Code (ECC) bekerja pada level bit. Dengan mengonversi data ke biner, algoritma ECC dapat menambahkan informasi koreksi kesalahan yang diperlukan untuk memastikan data dapat dipulihkan bahkan jika QR Code rusak sebagian.

4. Kompatibilitas:
   - Semua data digital pada dasarnya adalah biner. Menggunakan representasi biner memungkinkan berbagai jenis data (teks, URL, gambar kecil, dll.) untuk di-encode dalam QR Code dengan cara yang seragam dan dapat diandalkan.

### Di mana letak step ini dalam kode?

Dalam kode `QrCode`, pembuatan segmen data bisa dilakukan dengan menggunakan kelas `QrSegment`:

```python
class _BitBuffer(list[int]):

	def append_bits(self, val: int, n: int) -> None:
		if (n < 0) or (val >> n != 0):
			raise ValueError("Value out of range")
		self.extend(((val >> i) & 1) for i in reversed(range(n)))

def _get_bit(x: int, i: int) -> bool:
	return (x >> i) & 1 != 0

class QrSegment:
def _get_bit(x: int, i: int) -> bool:
	return (x >> i) & 1 != 0

	@staticmethod
	def make_bytes(data: Union[bytes,Sequence[int]]) -> QrSegment:
		bb = _BitBuffer()
		for b in data:
			bb.append_bits(b, 8)
		return QrSegment(QrSegment.Mode.BYTE, len(data), bb)


	@staticmethod
	def make_numeric(digits: str) -> QrSegment:
		if not QrSegment.is_numeric(digits):
			raise ValueError("String contains non-numeric characters")
		bb = _BitBuffer()
		i: int = 0
		while i < len(digits):
			n: int = min(len(digits) - i, 3)
			bb.append_bits(int(digits[i : i + n]), n * 3 + 1)
			i += n
		return QrSegment(QrSegment.Mode.NUMERIC, len(digits), bb)


	@staticmethod
	def make_alphanumeric(text: str) -> QrSegment:
		if not QrSegment.is_alphanumeric(text):
			raise ValueError("String contains unencodable characters in alphanumeric mode")
		bb = _BitBuffer()
		for i in range(0, len(text) - 1, 2):
			temp: int = QrSegment._ALPHANUMERIC_ENCODING_TABLE[text[i]] * 45
			temp += QrSegment._ALPHANUMERIC_ENCODING_TABLE[text[i + 1]]
			bb.append_bits(temp, 11)
		if len(text) % 2 > 0:
			bb.append_bits(QrSegment._ALPHANUMERIC_ENCODING_TABLE[text[-1]], 6)
		return QrSegment(QrSegment.Mode.ALPHANUMERIC, len(text), bb)

	@staticmethod
	def is_numeric(text: str) -> bool:
		return QrSegment._NUMERIC_REGEX.fullmatch(text) is not None

	@staticmethod
	def is_alphanumeric(text: str) -> bool:
		return QrSegment._ALPHANUMERIC_REGEX.fullmatch(text) is not None

	@staticmethod
	def make_segments(text: str) -> list[QrSegment]:

		if text == "":
			return []
		elif QrSegment.is_numeric(text):
			return [QrSegment.make_numeric(text)]
		elif QrSegment.is_alphanumeric(text):
			return [QrSegment.make_alphanumeric(text)]
		else:
			return [QrSegment.make_bytes(text.encode("UTF-8"))]
    # ... Kode lainnya
```

# Penjelasan tentang Step "Fit to Version Number"

#### 2. Menyesuaikan dengan Nomor Versi

Langkah ini bertujuan untuk menentukan versi QR Code yang paling sesuai berdasarkan panjang total bit yang dibutuhkan untuk merepresentasikan daftar segmen.

#### Rincian Panjang Bit dan Codewords Berdasarkan Versi

**Panjang bit total yang dibutuhkan untuk merepresentasikan daftar segmen, tergantung pada versi:**

| Range           | Num bits | Num codewords |
| --------------- | -------- | ------------- |
| Version 1 ~ 9   | 148      | 19            |
| Version 10 ~ 26 | 156      | 20            |
| Version 27 ~ 40 | 156      | 20            |

Catatan: **Satu codeword** didefinisikan sebagai 8 bit, yang juga dikenal sebagai byte.

#### Kapasitas QR Code Berdasarkan Versi dan Level Koreksi Kesalahan (ECC)

**Kapasitas data codewords per versi dan level koreksi kesalahan (ECC), dan apakah data tersebut muat (latar belakang hijau/merah):**

| Version | ECC L | ECC M | ECC Q | ECC H |
| ------- | ----- | ----- | ----- | ----- |
| 1       | 19    | 16    | 13    | 9     |
| 2       | 34    | 28    | 22    | 16    |
| 3       | 55    | 44    | 34    | 26    |
| 4       | 80    | 64    | 48    | 36    |
| 5       | 108   | 86    | 62    | 46    |
| 6       | 136   | 108   | 76    | 60    |
| 7       | 156   | 124   | 88    | 66    |
| 8       | 194   | 154   | 110   | 86    |
| 9       | 232   | 182   | 132   | 100   |
| 10      | 274   | 216   | 154   | 122   |
| 11      | 324   | 254   | 180   | 140   |
| 12      | 370   | 290   | 206   | 158   |
| 13      | 428   | 334   | 244   | 180   |
| 14      | 461   | 365   | 261   | 197   |
| 15      | 523   | 415   | 295   | 223   |
| 16      | 589   | 453   | 325   | 253   |
| 17      | 647   | 507   | 367   | 283   |
| 18      | 721   | 563   | 397   | 313   |
| 19      | 795   | 627   | 445   | 341   |
| 20      | 861   | 669   | 485   | 385   |
| 21      | 932   | 714   | 512   | 406   |
| 22      | 1006  | 782   | 568   | 442   |
| 23      | 1094  | 860   | 614   | 464   |
| 24      | 1174  | 914   | 664   | 514   |
| 25      | 1276  | 1000  | 718   | 538   |
| 26      | 1370  | 1062  | 754   | 596   |
| 27      | 1468  | 1128  | 808   | 628   |
| 28      | 1531  | 1193  | 871   | 661   |
| 29      | 1631  | 1267  | 911   | 701   |
| 30      | 1735  | 1373  | 985   | 745   |
| 31      | 1843  | 1455  | 1033  | 793   |
| 32      | 1955  | 1541  | 1115  | 845   |
| 33      | 2071  | 1631  | 1171  | 901   |
| 34      | 2191  | 1725  | 1231  | 961   |
| 35      | 2306  | 1812  | 1286  | 986   |
| 36      | 2434  | 1914  | 1354  | 1054  |
| 37      | 2566  | 1992  | 1426  | 1096  |
| 38      | 2702  | 2102  | 1502  | 1142  |
| 39      | 2812  | 2216  | 1582  | 1222  |
| 40      | 2956  | 2334  | 1666  | 1276  |

#### Nomor Versi yang Dipilih

**Versi 1** dipilih karena total panjang bit (148 bit) cukup muat dalam kapasitas data codewords versi ini (19 codewords untuk ECC level L).

### Di mana letak step ini dalam kode?

Bagian kode yang menyesuaikan dengan nomor versi ini dilakukan di beberapa fungsi, terutama yang terkait dengan menentukan panjang bit dan memilih versi yang sesuai.

#### Fungsi Utama

1. **`QrSegment.get_total_bits_needed`**: Fungsi ini menghitung total panjang bit yang dibutuhkan untuk segmen.
2. **`fit_to_version`**: Fungsi hipotetis yang menentukan versi QR Code berdasarkan total panjang bit dan kapasitas versi.

#### Contoh Implementasi

```python
class QrCode:
    # ... Kode lainnya

	_version: int

	def get_version(self) -> int:
		return self._version

	MIN_VERSION: int =  1
	MAX_VERSION: int = 40

    def encode_segments(segs: Sequence[QrSegment], ecl: QrCode.Ecc, minversion: int = 1, maxversion: int = 40, mask: int = -1, boostecl: bool = True) -> QrCode:

		if not (QrCode.MIN_VERSION <= minversion <= maxversion <= QrCode.MAX_VERSION) or not (-1 <= mask <= 7):
			raise ValueError("Invalid value")

		for version in range(minversion, maxversion + 1):
			datacapacitybits: int = QrCode._get_num_data_codewords(version, ecl) * 8
			datausedbits: Optional[int] = QrSegment.get_total_bits(segs, version)
			if (datausedbits is not None) and (datausedbits <= datacapacitybits):
				break

			if version >= maxversion:
				msg: str = "Segment too long"
				if datausedbits is not None:
					msg = f"Data length = {datausedbits} bits, Max capacity = {datacapacitybits} bits"
				raise DataTooLongError(msg)

		assert datausedbits is not None

		for newecl in (QrCode.Ecc.MEDIUM, QrCode.Ecc.QUARTILE, QrCode.Ecc.HIGH):
			if boostecl and (datausedbits <= QrCode._get_num_data_codewords(version, newecl) * 8):
				ecl = newecl

		bb = _BitBuffer()
		for seg in segs:
			bb.append_bits(seg.get_mode().get_mode_bits(), 4)
			bb.append_bits(seg.get_num_chars(), seg.get_mode().num_char_count_bits(version))
			bb.extend(seg._bitdata)
		assert len(bb) == datausedbits

		datacapacitybits = QrCode._get_num_data_codewords(version, ecl) * 8
		assert len(bb) <= datacapacitybits
		bb.append_bits(0, min(4, datacapacitybits - len(bb)))
		bb.append_bits(0, -len(bb) % 8)
		assert len(bb) % 8 == 0

		for padbyte in itertools.cycle((0xEC, 0x11)):
			if len(bb) >= datacapacitybits:
				break
			bb.append_bits(padbyte, 8)

		datacodewords = bytearray([0] * (len(bb) // 8))
		for (i, bit) in enumerate(bb):
			datacodewords[i >> 3] |= bit << (7 - (i & 7))

		return QrCode(version, ecl, datacodewords, mask)


    def __init__(self, version: int, errcorlvl: QrCode.Ecc, datacodewords: Union[bytes,Sequence[int]], msk: int) -> None:
		if not (QrCode.MIN_VERSION <= version <= QrCode.MAX_VERSION):
			raise ValueError("Version value out of range")
		if not (-1 <= msk <= 7):
			raise ValueError("Mask value out of range")

		self._version = version
        # ... Kode lainnya
```

### Penjelasan Implementasi

- **`QrSegment.get_total_bits_needed`**: Fungsi ini menghitung panjang bit yang dibutuhkan oleh segmen. Panjang bit dihitung berdasarkan jumlah bit dalam data segmen.
- **`fit_to_version`**: Fungsi ini menentukan versi QR Code yang cocok berdasarkan panjang bit total dari semua segmen dan kapasitas versi QR Code. Fungsi ini mengiterasi melalui setiap versi (dari 1 hingga 40) dan memeriksa apakah total bit bisa muat dalam kapasitas codewords dari versi tersebut untuk level ECC yang diberikan.
- **`capacity_table`**: Tabel kapasitas codewords berdasarkan versi dan level ECC.

Dengan demikian, proses ini memastikan bahwa versi QR Code yang dipilih memiliki kapasitas yang cukup untuk menampung data yang di-encode.

# Penjelasan tentang Step "Concatenate Segments, Add Padding, Make Codewords"

#### 3. Menggabungkan Segmen, Menambah Padding, dan Membuat Codewords

Langkah ini melibatkan penggabungan berbagai string bit, penambahan padding, dan pembuatan codewords untuk menghasilkan representasi akhir dari data dalam QR Code.

#### Detail Proses

1. **Segment Mode**:

   - Setiap segmen data diawali dengan mode indikator 4-bit yang menentukan tipe data yang dikodekan (misalnya, numeric, alphanumeric, byte, atau kanji). Dalam contoh ini, mode indikator adalah `0100` (untuk mode Byte).

2. **Segment Count**:

   - Ini adalah jumlah karakter dalam segmen tersebut. Lebar field untuk count bergantung pada mode dan versi QR Code. Dalam mode Byte dan versi 1, lebar field adalah 8 bit. Nilai count untuk teks "Hello, world! 123" adalah `17`, yang direpresentasikan sebagai `00010001` dalam bit.

3. **Segment Data**:

   - Data karakter yang dikonversi menjadi bit string. Setiap karakter diubah menjadi representasi biner 8-bit. Berikut bit string untuk teks "Hello, world! 123":
     ```
     01001000 01100101 01101100 01101100 01101111 00101100 00100000 01110111 01101111 01110010 01101100 01100100 00100001 00100000 00110001 00110010 00110011
     ```

4. **Terminator**:

   - Ini adalah string bit `0000` sepanjang 4 bit yang menandakan akhir dari data yang valid. Jika data codeword sudah penuh, terminator dapat kurang dari 4 bit.

5. **Bit Padding**:

   - Padding yang ditambahkan untuk membuat panjang bit menjadi kelipatan 8. Bit padding terdiri dari nol (`0`) dan panjangnya antara 0 hingga 7 bit.

6. **Byte Padding**:
   - Padding byte ditambahkan setelah bit padding untuk mencapai kapasitas codeword yang diperlukan. Padding ini terdiri dari nilai bergantian `11101100` (EC) dan `00010001` (11) dalam hexadecimal hingga kapasitas tercapai.

#### Tabel dan Penjelasan

| Item                | Bit data                                                                                                                                                   | Num bits | Sum bits |
| ------------------- | ---------------------------------------------------------------------------------------------------------------------------------------------------------- | -------- | -------- |
| **Segment 0 mode**  | `0100`                                                                                                                                                     | 4        | 4        |
| **Segment 0 count** | `00010001`                                                                                                                                                 | 8        | 12       |
| **Segment 0 data**  | `01001000 01100101 01101100 01101100 01101111 00101100 00100000 01110111 01101111 01110010 01101100 01100100 00100001 00100000 00110001 00110010 00110011` | 136      | 148      |
| **Terminator**      | `0000`                                                                                                                                                     | 4        | 152      |
| **Bit padding**     |                                                                                                                                                            | 0        | 152      |
| **Byte padding**    |                                                                                                                                                            | 0        | 152      |

**Total bit sequence:**

```
01000001000101001000011001010110110001101100011011110010110000100000011101110110111101110010011011000110010000100001001000000011000100110010001100110000
```

**Total data codeword bytes (in hexadecimal):**

```
41 14 86 56 C6 C6 F2 C2 07 76 F7 26 C6 42 12 03 13 23 30
```

#### Di mana letak step ini dalam kode?

```python
class QrSegment:
    # Existing code for QrSegment

    @staticmethod
    def make_segments(text: str) -> List[QrSegment]:
        # Create a segment from the given text using byte mode
        # Convert each character to 8-bit binary
        bit_data = ''.join(f"{ord(c):08b}" for c in text)
        return [QrSegment(mode_indicator='0100', char_count=len(text), bit_data=bit_data)]

    @staticmethod
    def encode_segment(segment: QrSegment, version: int) -> str:
        # Encode the segment data
        mode_bits = segment.mode_indicator
        count_bits = f"{segment.char_count:08b}"  # For version 1 and byte mode
        data_bits = segment.bit_data
        return mode_bits + count_bits + data_bits

def add_padding(bit_string: str, total_codewords: int) -> str:
    # Add terminator
    bit_string += '0000'
    # Add bit padding to make the length a multiple of 8
    while len(bit_string) % 8 != 0:
        bit_string += '0'
    # Add byte padding
    codewords = [bit_string[i:i+8] for i in range(0, len(bit_string), 8)]
    while len(codewords) < total_codewords:
        codewords.append('11101100')
        if len(codewords) < total_codewords:
            codewords.append('00010001')
    return ''.join(codewords)

# Example usage
text = "Hello, world! 123"
segments = QrSegment.make_segments(text)
encoded_data = ''.join(QrSegment.encode_segment(seg, 1) for seg in segments)
padded_data = add_padding(encoded_data, 19)
print(f"Total bit sequence: {padded_data}")

# Convert bit string to hexadecimal representation
codewords_hex = [f"{int(padded_data[i:i+8], 2):02X}" for i in range(0, len(padded_data), 8)]
print(f"Total data codeword bytes (in hexadecimal): {' '.join(codewords_hex)}")
```

# Penjelasan tentang Step "Split Blocks, Add ECC, Interleave"

#### 4. Membagi Blok, Menambah ECC, dan Interleave

Langkah ini melibatkan pembagian data menjadi blok-blok, penambahan kode koreksi kesalahan (ECC), dan penggabungan data (interleaving) dari berbagai blok untuk menghasilkan urutan akhir kode QR.

#### Detail Proses

1. **Jumlah codewords data**:

   - Ini adalah jumlah total codewords yang dihasilkan dari data yang dienkode. Untuk contoh ini, jumlah codewords data adalah 19.

2. **Jumlah blok**:

   - Dalam hal ini, data hanya memerlukan 1 blok karena ukurannya kecil.

3. **Codewords data per blok pendek**:

   - Karena hanya ada satu blok, semua codewords data masuk ke dalam blok ini. Jadi, jumlah codewords per blok pendek adalah 19.

4. **Codewords data per blok panjang**:

   - Tidak ada blok panjang dalam contoh ini (N/A).

5. **Jumlah codewords ECC per blok**:

   - Untuk setiap blok, sejumlah codewords ECC ditambahkan untuk koreksi kesalahan. Dalam contoh ini, jumlah codewords ECC adalah 7.

6. **Jumlah blok pendek**:

   - Terdapat 1 blok pendek dalam contoh ini.

7. **Jumlah blok panjang**:
   - Tidak ada blok panjang dalam contoh ini.

#### Tabel Pembagian Blok dan ECC

| **Blok** | **Indeks Codeword dalam Blok** | **Data Codewords** | **ECC Codewords** |
| -------- | ------------------------------ | ------------------ | ----------------- |
| 0        | 0                              | 41                 | 85                |
|          | 1                              | 14                 | A9                |
|          | 2                              | 86                 | 5E                |
|          | 3                              | 56                 | 07                |
|          | 4                              | C6                 | 0A                |
|          | 5                              | C6                 | 36                |
|          | 6                              | F2                 | C9                |
|          | 7                              | C2                 |                   |
|          | 8                              | 07                 |                   |
|          | 9                              | 76                 |                   |
|          | 10                             | F7                 |                   |
|          | 11                             | 26                 |                   |
|          | 12                             | C6                 |                   |
|          | 13                             | 42                 |                   |
|          | 14                             | 12                 |                   |
|          | 15                             | 03                 |                   |
|          | 16                             | 13                 |                   |
|          | 17                             | 23                 |                   |
|          | 18                             | 30                 |                   |

Dalam tabel ini:

- **Blok** menunjukkan nomor blok (dalam hal ini hanya ada satu blok, yaitu 0).
- **Indeks Codeword dalam Blok** menunjukkan posisi codeword dalam blok tersebut.
- **Data Codewords** adalah codewords yang berasal dari data yang dienkode.
- **ECC Codewords** adalah codewords koreksi kesalahan yang ditambahkan menggunakan algoritma Reed-Solomon.

#### Urutan Final Codewords

Urutan akhir codewords dibentuk dengan menggabungkan codewords data dan ECC dari blok yang berbeda:

```
41 14 86 56 C6 C6 F2 C2 07 76 F7 26 C6 42 12 03 13 23 30 85 A9 5E 07 0A 36 C9
```

#### Urutan Bit Akhir untuk Pemindaian Zigzag

Urutan bit akhir yang digunakan untuk pemindaian zigzag dalam QR Code:

```
0100000100010100100001100101011011000110110001101111001011000010000001110111011011110111001001101100011001000010000100100000001100010011001000110011000010000101101010010101111000000111000010100011011011001001
```

### Implementasi dalam Kode

Bagian kode yang melakukan pembagian blok, penambahan ECC, dan interleave ini bisa dilakukan dalam beberapa langkah.

#### Di mana letak step ini dalam kode?

```python
from typing import List

class QrSegment:
    def __init__(self, mode_indicator: str, char_count: int, bit_data: str):
        self.mode_indicator = mode_indicator
        self.char_count = char_count
        self.bit_data = bit_data

    @staticmethod
    def make_segments(text: str) -> List['QrSegment']:
        bit_data = ''.join(f"{ord(c):08b}" for c in text)
        return [QrSegment(mode_indicator='0100', char_count=len(text), bit_data=bit_data)]

    @staticmethod
    def encode_segment(segment: 'QrSegment', version: int) -> str:
        mode_bits = segment.mode_indicator
        count_bits = f"{segment.char_count:08b}"  # For version 1 and byte mode
        data_bits = segment.bit_data
        return mode_bits + count_bits + data_bits

def add_padding(bit_string: str, total_codewords: int) -> str:
    bit_string += '0000'  # Terminator
    while len(bit_string) % 8 != 0:
        bit_string += '0'
    codewords = [bit_string[i:i+8] for i in range(0, len(bit_string), 8)]
    while len(codewords) < total_codewords:
        codewords.append('11101100')
        if len(codewords) < total_codewords:
            codewords.append('00010001')
    return ''.join(codewords)

def compute_ecc(data_codewords: List[int], num_ecc_codewords: int) -> List[int]:
    # Placeholder function to compute ECC codewords using Reed-Solomon algorithm
    # Implement the actual Reed-Solomon algorithm as needed
    return [0x85, 0xA9, 0x5E, 0x07, 0x0A, 0x36, 0xC9]  # Example ECC codewords

def split_blocks(data_codewords: List[str], num_blocks: int, num_ecc_codewords: int) -> List[List[str]]:
    # For simplicity, assume all data fits into a single block
    return [data_codewords]

# Example usage
text = "Hello, world! 123"
segments = QrSegment.make_segments(text)
encoded_data = ''.join(QrSegment.encode_segment(seg, 1) for seg in segments)
padded_data = add_padding(encoded_data, 19)

# Convert padded_data to a list of integers (codewords)
data_codewords = [int(padded_data[i:i+8], 2) for i in range(0, len(padded_data), 8)]

# Split data codewords into blocks
blocks = split_blocks(data_codewords, 1, 7)

# Add ECC to each block
final_blocks = []
for block in blocks:
    ecc_codewords = compute_ecc(block, 7)
    final_blocks.append(block + ecc_codewords)

# Interleave data and ECC codewords from blocks
interleaved_codewords = []
for i in range(len(final_blocks[0])):
    for block in final_blocks:
        if i < len(block):
            interleaved_codewords.append(block[i])

# Convert interleaved codewords to binary string
final_bit_string = ''.join(f"{codeword:08b}" for codeword in interleaved_codewords)

print(f"Final sequence of codewords (hex): {' '.join(f'{codeword:02X}' for codeword in interleaved_codewords)}")
print(f"Final sequence of bits to draw in the zigzag scan: {final_bit_string}")
```

### Penjelasan tentang Step "Draw Fixed Patterns"

#### 5. **Menggambar Pola Tetap (Fixed Patterns)**

Langkah ini melibatkan menggambar pola-pola tetap pada matriks QR Code. Pola-pola ini mencakup pola finder, pola timing, dan bit format dummy sementara. Langkah ini penting untuk memastikan QR Code dapat dibaca dengan benar oleh scanner.

#### Detail Proses

1. **Menggambar Pola Timing (Timing Patterns)**:

   - Pola timing horizontal dan vertikal digambar pada baris ke-6 dan kolom ke-6 dari matriks (dengan penghitungan dimulai dari 0 di pojok kiri atas).
   - Pola ini terdiri dari modul hitam dan putih yang bergantian, dan membantu scanner dalam menentukan koordinat modul QR Code.

2. **Menggambar Pola Finder (Finder Patterns)**:

   - Pola finder digambar di tiga sudut matriks QR Code (pojok kiri atas, pojok kanan atas, dan pojok kiri bawah).
   - Setiap pola finder berukuran 8×8 modul, termasuk separator putih di sekelilingnya.
   - Pola finder ini terdiri dari modul hitam-putih konsentris yang membantu dalam menemukan dan mengorientasikan QR Code.

3. **Menggambar Bit Format Dummy Sementara (Temporary Dummy Format Bits)**:
   - Bit format sementara digambar berdekatan dengan pola finder.
   - Ini akan ditimpa nanti dengan bit format yang sebenarnya setelah data dan ECC telah ditambahkan.

#### Di mana letak step ini dalam kode?

Bagian kode berikut akan mengilustrasikan bagaimana pola-pola ini digambar pada matriks QR Code.

```python
import numpy as np

def draw_finder_pattern(matrix: np.ndarray, x: int, y: int):
    size = matrix.shape[0]
    pattern = [
        [1, 1, 1, 1, 1, 1, 1],
        [1, 0, 0, 0, 0, 0, 1],
        [1, 0, 1, 1, 1, 0, 1],
        [1, 0, 1, 1, 1, 0, 1],
        [1, 0, 1, 1, 1, 0, 1],
        [1, 0, 0, 0, 0, 0, 1],
        [1, 1, 1, 1, 1, 1, 1],
    ]
    for i in range(7):
        for j in range(7):
            if 0 <= x + i < size and 0 <= y + j < size:
                matrix[x + i, y + j] = pattern[i][j]

def draw_timing_patterns(matrix: np.ndarray):
    size = matrix.shape[0]
    for i in range(8, size - 8):
        matrix[6, i] = 1 if i % 2 == 0 else 0
        matrix[i, 6] = 1 if i % 2 == 0 else 0

def draw_fixed_patterns(matrix: np.ndarray):
    size = matrix.shape[0]
    draw_finder_pattern(matrix, 0, 0)
    draw_finder_pattern(matrix, 0, size - 7)
    draw_finder_pattern(matrix, size - 7, 0)
    draw_timing_patterns(matrix)

    # Draw format information areas (temporary dummy)
    for i in range(8):
        if i != 6:
            matrix[i, 8] = 0  # Left format info
            matrix[8, i] = 0  # Top format info
            matrix[size - 1 - i, 8] = 0  # Bottom format info
            matrix[8, size - 1 - i] = 0  # Right format info
    matrix[8, 8] = 0  # Dark module

# Example usage
size = 21  # For version 1 QR Code
matrix = np.full((size, size), -1)  # Initialize matrix with -1 (unassigned)
draw_fixed_patterns(matrix)

# Convert matrix to a more readable format for display
display_matrix = [[' ' if cell == -1 else '█' if cell == 1 else ' ' for cell in row] for row in matrix]

for row in display_matrix:
    print(' '.join(row))
```

### Penjelasan Implementasi

1. **`draw_finder_pattern`**:

   - Fungsi ini menggambar pola finder pada posisi (x, y) yang ditentukan. Pola finder terdiri dari modul hitam (1) dan putih (0) dalam susunan tertentu.

2. **`draw_timing_patterns`**:

   - Fungsi ini menggambar pola timing horizontal dan vertikal pada baris ke-6 dan kolom ke-6 dari matriks. Pola timing terdiri dari modul hitam dan putih yang bergantian.

3. **`draw_fixed_patterns`**:
   - Fungsi ini memanggil `draw_finder_pattern` untuk menggambar tiga pola finder pada pojok kiri atas, pojok kanan atas, dan pojok kiri bawah dari matriks.
   - Juga memanggil `draw_timing_patterns` untuk menggambar pola timing.
   - Menggambar bit format dummy sementara di dekat pola finder, ini akan diganti nanti dengan bit format yang sebenarnya setelah data dan ECC telah ditambahkan.

### Kesimpulan

Dengan menggambar pola-pola tetap ini, kita menyiapkan matriks QR Code untuk menampung data dan bit koreksi kesalahan (ECC). Pola-pola ini membantu scanner QR Code untuk menemukan, mengorientasikan, dan membaca QR Code dengan benar.

from __future__ import annotations
from algoritm import QrCode, QrSegment


def main() -> None:
	# do_basic_demo()
	do_variety_demo()
	# do_segment_demo()
	# do_mask_demo()



# ---- Demo suite ----

def do_basic_demo() -> None:
	"""Membuat satu qrcode dan mencetaknya di konsol."""
	text = "Hello, world!"      # User-supplied Unicode text
	errcorlvl = QrCode.Ecc.LOW  # Error correction level
	
	# Make and print the QR Code symbol
	qr = QrCode.encode_text(text, errcorlvl)
	print_qr(qr)
	print(to_svg_str(qr, 4))


def do_variety_demo() -> None:
	"""Creates a variety of QR Codes that exercise different features of the library, and prints each one to the console."""
	
	# Numeric mode encoding (3.33 bits per digit)
	qr = QrCode.encode_text("11220910000042", QrCode.Ecc.MEDIUM)
	print_qr(qr)
	
	# Alphanumeric mode encoding (5.5 bits per character)
	qr = QrCode.encode_text("DOLLAR-AMOUNT:$39.87 PERCENTAGE:100.00% OPERATIONS:+-*/", QrCode.Ecc.HIGH)
	print_qr(qr)
	
	# Unicode text as UTF-8
	qr = QrCode.encode_text("\u3053\u3093\u306B\u3061\u0077\u0061\u3001\u4E16\u754C\uFF01\u0020\u03B1\u03B2\u03B3\u03B4", QrCode.Ecc.QUARTILE)
	print_qr(qr)
	
	# Moderately large QR Code using longer text (from Lewis Carroll's Alice in Wonderland)
	qr = QrCode.encode_text(
		"Alice was beginning to get very tired of sitting by her sister on the bank, "
		"and of having nothing to do: once or twice she had peeped into the book her sister was reading, "
		"but it had no pictures or conversations in it, 'and what is the use of a book,' thought Alice "
		"'without pictures or conversations?' So she was considering in her own mind (as well as she could, "
		"for the hot day made her feel very sleepy and stupid), whether the pleasure of making a "
		"daisy-chain would be worth the trouble of getting up and picking the daisies, when suddenly "
		"a White Rabbit with pink eyes ran close by her.", QrCode.Ecc.HIGH)
	print_qr(qr)


def do_segment_demo() -> None:
	"""Creates QR Codes with manually specified segments for better compactness."""
	
	# Illustration "silver"
	silver0 = "THE SQUARE ROOT OF 2 IS 1."
	silver1 = "41421356237309504880168872420969807856967187537694807317667973799"
	qr = QrCode.encode_text(silver0 + silver1, QrCode.Ecc.LOW)
	print_qr(qr)
	
	segs = [
		QrSegment.make_alphanumeric(silver0),
		QrSegment.make_numeric(silver1)]
	qr = QrCode.encode_segments(segs, QrCode.Ecc.LOW)
	print_qr(qr)
	
	# Illustration "golden"
	golden0 = "Golden ratio \u03C6 = 1."
	golden1 = "6180339887498948482045868343656381177203091798057628621354486227052604628189024497072072041893911374"
	golden2 = "......"
	qr = QrCode.encode_text(golden0 + golden1 + golden2, QrCode.Ecc.LOW)
	print_qr(qr)
	
	segs = [
		QrSegment.make_bytes(golden0.encode("UTF-8")),
		QrSegment.make_numeric(golden1),
		QrSegment.make_alphanumeric(golden2)]
	qr = QrCode.encode_segments(segs, QrCode.Ecc.LOW)
	print_qr(qr)
	
	# Illustration "Madoka": kanji, kana, Cyrillic, full-width Latin, Greek characters
	madoka = "\u300C\u9B54\u6CD5\u5C11\u5973\u307E\u3069\u304B\u2606\u30DE\u30AE\u30AB\u300D\u3063\u3066\u3001\u3000\u0418\u0410\u0418\u3000\uFF44\uFF45\uFF53\uFF55\u3000\u03BA\u03B1\uFF1F"
	qr = QrCode.encode_text(madoka, QrCode.Ecc.LOW)
	print_qr(qr)
	
	kanjicharbits = [  # Kanji mode encoding (13 bits per character)
		0, 0, 0, 0, 0, 0, 0, 1, 1, 0, 1, 0, 1,
		1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 0,
		0, 1, 1, 1, 1, 1, 1, 0, 0, 0, 0, 0, 0,
		0, 1, 0, 1, 0, 1, 1, 1, 0, 1, 1, 0, 1,
		0, 1, 0, 1, 0, 1, 1, 0, 1, 0, 1, 1, 1,
		0, 0, 0, 0, 1, 0, 1, 0, 1, 1, 1, 0, 0,
		0, 0, 0, 0, 1, 0, 1, 0, 0, 0, 1, 1, 1,
		0, 0, 0, 0, 1, 0, 0, 1, 0, 1, 0, 0, 1,
		0, 0, 0, 0, 0, 0, 1, 0, 1, 1, 0, 0, 1,
		0, 0, 0, 0, 1, 1, 0, 1, 1, 1, 1, 0, 1,
		0, 0, 0, 0, 1, 1, 0, 0, 0, 1, 1, 0, 1,
		0, 0, 0, 0, 1, 1, 0, 0, 0, 1, 0, 1, 0,
		0, 0, 0, 0, 0, 0, 0, 1, 1, 0, 1, 1, 0,
		0, 0, 0, 0, 1, 0, 1, 0, 0, 0, 0, 0, 1,
		0, 0, 0, 0, 1, 0, 1, 0, 0, 0, 1, 0, 0,
		0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1,
		0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,
		0, 0, 0, 1, 0, 0, 1, 0, 0, 1, 0, 0, 1,
		0, 0, 0, 1, 0, 0, 1, 0, 0, 0, 0, 0, 0,
		0, 0, 0, 1, 0, 0, 1, 0, 0, 1, 0, 0, 1,
		0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,
		0, 0, 0, 0, 1, 0, 0, 0, 0, 0, 1, 0, 0,
		0, 0, 0, 0, 1, 0, 0, 0, 0, 0, 1, 0, 1,
		0, 0, 0, 0, 1, 0, 0, 0, 1, 0, 0, 1, 1,
		0, 0, 0, 0, 1, 0, 0, 0, 1, 0, 1, 0, 1,
		0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,
		0, 0, 0, 1, 0, 0, 0, 0, 0, 1, 0, 0, 0,
		0, 0, 0, 0, 1, 1, 1, 1, 1, 1, 1, 1, 1,
		0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 0, 0, 0,
	]
	segs = [QrSegment(QrSegment.Mode.KANJI, len(kanjicharbits) // 13, kanjicharbits)]
	qr = QrCode.encode_segments(segs, QrCode.Ecc.LOW)
	print_qr(qr)


def do_mask_demo() -> None:
	"""Creates QR Codes with the same size and contents but different mask patterns."""
	
	# Project Nayuki URL
	segs = QrSegment.make_segments("https://www.nayuki.io/")
	print_qr(QrCode.encode_segments(segs, QrCode.Ecc.HIGH, mask=-1))  # Automatic mask
	print_qr(QrCode.encode_segments(segs, QrCode.Ecc.HIGH, mask=3))  # Force mask 3
	
	# Chinese text as UTF-8
	segs = QrSegment.make_segments(
		"\u7DAD\u57FA\u767E\u79D1\uFF08\u0057\u0069\u006B\u0069\u0070\u0065\u0064\u0069\u0061\uFF0C"
		"\u8046\u807D\u0069\u002F\u02CC\u0077\u026A\u006B\u1D7B\u02C8\u0070\u0069\u02D0\u0064\u0069"
		"\u002E\u0259\u002F\uFF09\u662F\u4E00\u500B\u81EA\u7531\u5167\u5BB9\u3001\u516C\u958B\u7DE8"
		"\u8F2F\u4E14\u591A\u8A9E\u8A00\u7684\u7DB2\u8DEF\u767E\u79D1\u5168\u66F8\u5354\u4F5C\u8A08"
		"\u756B")
	print_qr(QrCode.encode_segments(segs, QrCode.Ecc.MEDIUM, mask=0))  # Force mask 0
	print_qr(QrCode.encode_segments(segs, QrCode.Ecc.MEDIUM, mask=1))  # Force mask 1
	print_qr(QrCode.encode_segments(segs, QrCode.Ecc.MEDIUM, mask=5))  # Force mask 5
	print_qr(QrCode.encode_segments(segs, QrCode.Ecc.MEDIUM, mask=7))  # Force mask 7



# ---- Utilities ----

def to_svg_str(qr: QrCode, border: int) -> str:
	"""Returns a string of SVG code for an image depicting the given QR Code, with the given number
	of border modules. The string always uses Unix newlines (\n), regardless of the platform."""
	if border < 0:
		raise ValueError("Border must be non-negative")
	parts: list[str] = []
	for y in range(qr.get_size()):
		for x in range(qr.get_size()):
			if qr.get_module(x, y):
				parts.append(f"M{x+border},{y+border}h1v1h-1z")
	return f"""<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE svg PUBLIC "-//W3C//DTD SVG 1.1//EN" "http://www.w3.org/Graphics/SVG/1.1/DTD/svg11.dtd">
<svg xmlns="http://www.w3.org/2000/svg" version="1.1" viewBox="0 0 {qr.get_size()+border*2} {qr.get_size()+border*2}" stroke="none">
	<rect width="100%" height="100%" fill="#FFFFFF"/>
	<path d="{" ".join(parts)}" fill="#000000"/>
</svg>
"""


def print_qr(qrcode: QrCode) -> None:
	"""Prints the given QrCode object to the console."""
	border = 4
	for y in range(-border, qrcode.get_size() + border):
		for x in range(-border, qrcode.get_size() + border):
			print("\u2588 "[1 if qrcode.get_module(x,y) else 0] * 2, end="")
		print()
	print()


# Run the main program
if __name__ == "__main__":
	main()

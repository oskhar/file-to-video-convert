Draw finder

```python
    def _draw_finder_pattern(self, x: int, y: int) -> None:
		for dy in range(-4, 5):
			for dx in range(-4, 5):
				xx, yy = x + dx, y + dy
				if (0 <= xx < self._size) and (0 <= yy < self._size):
					self._set_function_module(xx, yy, max(abs(dx), abs(dy)) not in (2, 4))
    def _draw_function_patterns(self) -> None:
		for i in range(self._size):
			self._set_function_module(6, i, i % 2 == 0)
			self._set_function_module(i, 6, i % 2 == 0)

		self._draw_finder_pattern(3, 3)
		self._draw_finder_pattern(self._size - 4, 3)
		self._draw_finder_pattern(3, self._size - 4)

		alignpatpos: list[int] = self._get_alignment_pattern_positions()
		numalign: int = len(alignpatpos)
		skips: Sequence[tuple[int,int]] = ((0, 0), (0, numalign - 1), (numalign - 1, 0))
		for i in range(numalign):
			for j in range(numalign):
				if (i, j) not in skips:
					self._draw_alignment_pattern(alignpatpos[i], alignpatpos[j])

		self._draw_format_bits(0)
		self._draw_version()
```

Draw version

```python

	def _draw_version(self) -> None:
		if self._version < 7:
			return

		rem: int = self._version
		for _ in range(12):
			rem = (rem << 1) ^ ((rem >> 11) * 0x1F25)
		bits: int = self._version << 12 | rem
		assert bits >> 18 == 0

		for i in range(18):
			bit: bool = _get_bit(bits, i)
			a: int = self._size - 11 + i % 3
			b: int = i // 3
			self._set_function_module(a, b, bit)
			self._set_function_module(b, a, bit)
```

Mask pattern

```python
	_mask: int
	_MASK_PATTERNS: Sequence[collections.abc.Callable[[int,int],int]] = (
		(lambda x, y:  (x + y) % 2                  ),
		(lambda x, y:  y % 2                        ),
		(lambda x, y:  x % 3                        ),
		(lambda x, y:  (x + y) % 3                  ),
		(lambda x, y:  (x // 3 + y // 2) % 2        ),
		(lambda x, y:  x * y % 2 + x * y % 3        ),
		(lambda x, y:  (x * y % 2 + x * y % 3) % 2  ),
		(lambda x, y:  ((x + y) % 2 + x * y % 3) % 2),
	)
	def get_mask(self) -> int:
			return self._mask

	def _apply_mask(self, mask: int) -> None:
		if not (0 <= mask <= 7):
			raise ValueError("Mask value out of range")
		masker: collections.abc.Callable[[int,int],int] = QrCode._MASK_PATTERNS[mask]
		for y in range(self._size):
			for x in range(self._size):
				self._modules[y][x] ^= (masker(x, y) == 0) and (not self._isfunction[y][x])
```

Draw format

```python
	def _draw_format_bits(self, mask: int) -> None:
			data: int = self._errcorlvl.formatbits << 3 | mask
			rem: int = data
			for _ in range(10):
				rem = (rem << 1) ^ ((rem >> 9) * 0x537)
			bits: int = (data << 10 | rem) ^ 0x5412
			assert bits >> 15 == 0

			for i in range(0, 6):
				self._set_function_module(8, i, _get_bit(bits, i))
			self._set_function_module(8, 7, _get_bit(bits, 6))
			self._set_function_module(8, 8, _get_bit(bits, 7))
			self._set_function_module(7, 8, _get_bit(bits, 8))
			for i in range(9, 15):
				self._set_function_module(14 - i, 8, _get_bit(bits, i))

			for i in range(0, 8):
				self._set_function_module(self._size - 1 - i, 8, _get_bit(bits, i))
			for i in range(8, 15):
				self._set_function_module(8, self._size - 15 + i, _get_bit(bits, i))
			self._set_function_module(8, self._size - 8, True)
```

Draw isi pesannya

```python
	def _draw_codewords(self, data: bytes) -> None:
		assert len(data) == QrCode._get_num_raw_data_modules(self._version) // 8

		i: int = 0
		for right in range(self._size - 1, 0, -2):
			if right <= 6:
				right -= 1
			for vert in range(self._size):
				for j in range(2):
					x: int = right - j
					upward: bool = (right + 1) & 2 == 0
					y: int = (self._size - 1 - vert) if upward else vert
					if (not self._isfunction[y][x]) and (i < len(data) * 8):
						self._modules[y][x] = _get_bit(data[i >> 3], 7 - (i & 7))
						i += 1
		assert i == len(data) * 8

	@staticmethod
	def _get_num_data_codewords(ver: int, ecl: QrCode.Ecc) -> int:
		return QrCode._get_num_raw_data_modules(ver) // 8 \
			- QrCode._ECC_CODEWORDS_PER_BLOCK    [ecl.ordinal][ver] \
			* QrCode._NUM_ERROR_CORRECTION_BLOCKS[ecl.ordinal][ver]
```

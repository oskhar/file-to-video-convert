import unittest
import itertools
import algoritm

class TestRSverify(unittest.TestCase):
    def setUp(self):
        self.coder = algoritm.RSCoder(255, 223)

    def test_one(self):
        """Tests a codeword without errors validates"""
        code = self.coder.encode(b"Hello, world!")
        print(f"Encoded 'Hello, world!': {code}")
        self.assertTrue(self.coder.verify(code))
        print("Codeword is valid\n")

    def test_two(self):
        """Verifies that changing any single character will invalidate the codeword"""
        message = b"Hello, world! This is a test message, to be encoded, and verified."
        code = self.coder.encode(message)
        print(f"Encoded message: {code}")

        for i in range(len(code)):
            # Change the value at position i and verify that the code is not valid
            bad_code = bytearray(code)
            bad_code[i] ^= 0xFF  # Invert the byte
            print(f"Modified code at position {i}: {bad_code}")
            self.assertFalse(self.coder.verify(bad_code))
        print("All modified codewords are invalid\n")

class TestRSdecoding(unittest.TestCase):
    def setUp(self):
        self.coder = algoritm.RSCoder(255, 223)
        self.string = b"Hello, world! This is a long string"

        self.code = self.coder.encode(self.string)
        print(f"Setup encoded string: {self.code}")

    def test_strip(self):
        """Tests that the nostrip feature works"""
        otherstr = self.string.rjust(223, b"\0")
        codestr = self.coder.encode(otherstr)
        print(f"Encoded padded string: {codestr}")

        self.assertEqual(255, len(codestr))

        # Decode with default behavior: stripping of leading null bytes
        decode = self.coder.decode(codestr)
        decode2 = self.coder.decode(codestr[:5] + b"\x50" + codestr[6:])
        print(f"Decoded string: {decode}, Altered decoded string: {decode2}")

        self.assertEqual(self.string, decode)
        self.assertEqual(self.string, decode2)

        # Decode with nostrip
        decode = self.coder.decode(codestr, nostrip=True)
        decode2 = self.coder.decode(codestr[:5] + b"\x50" + codestr[6:], nostrip=True)
        print(f"Decoded string with nostrip: {decode}, Altered decoded string with nostrip: {decode2}")

        self.assertEqual(otherstr, decode)
        self.assertEqual(otherstr, decode2)

    def test_noerr(self):
        """Make sure a codeword with no errors decodes"""
        decode = self.coder.decode(self.code)
        print(f"Decoded codeword with no errors: {decode}")
        self.assertEqual(self.string, decode)

    def test_oneerr(self):
        """Change just one byte and make sure it decodes"""
        for i in range(len(self.code)):
            newch = (self.code[i] + 50) % 256
            r = bytearray(self.code)
            r[i] = newch
            decode = self.coder.decode(r)
            print(f"Modified code at position {i}: {r}, Decoded: {decode}")
            self.assertEqual(self.string, decode)

    def disabled_test_twoerr(self):
        """Test that changing every combination of 2 bytes still decodes.
        This test is long and probably unnecessary."""
        # Test disabled, it takes too long
        for i1, i2 in itertools.combinations(range(len(self.code)), 2):
            r = list(self.code)

            # increment the byte by 50
            r[i1] = (r[i1] + 50) % 256
            r[i2] = (r[i2] + 50) % 256

            r = bytes(r)
            decode = self.coder.decode(r)
            print(f"Modified code at positions {i1} and {i2}: {r}, Decoded: {decode}")
            self.assertEqual(self.string, decode)

    def test_16err(self):
        """Tests if 16 byte errors still decodes"""
        errors = [5, 6, 12, 13, 38, 40, 42, 47, 50, 57, 58, 59, 60, 61, 62, 65]
        r = list(self.code)

        for e in errors:
            r[e] = (r[e] + 50) % 256

        r = bytes(r)
        decode = self.coder.decode(r)
        print(f"Code with 16 errors: {r}, Decoded: {decode}")
        self.assertEqual(self.string, decode)

    def test_17err(self):
        """Kinda pointless, checks that 17 errors doesn't decode.
        Actually, this could still decode by coincidence on some inputs, so this test shouldn't be here at all."""
        errors = [5, 6, 12, 13, 22, 38, 40, 42, 47, 50, 57, 58, 59, 60, 61, 62, 65]
        r = list(self.code)

        for e in errors:
            r[e] = (r[e] + 50) % 256

        r = bytes(r)
        decode = self.coder.decode(r)
        print(f"Code with 17 errors: {r}, Decoded: {decode}")
        self.assertNotEqual(self.string, decode)

class TestOtherConfig(unittest.TestCase):
    """Tests a configuration of the coder other than RS(255,223)"""

    def test255_13(self):
        coder = algoritm.RSCoder(255, 13)
        m = b"Hello, world!"
        code = coder.encode(m)
        print(f"RS(255,13) encoded 'Hello, world!': {code}")

        self.assertTrue(coder.verify(code))
        self.assertEqual(m, coder.decode(code))

        self.assertEqual(255, len(code))

        # Change 121 bytes. This code should tolerate up to 121 bytes changed
        changes = [1, 4, 5, 6, 9, 10, 14, 15, 19, 20, 21, 24, 26, 30, 32, 34,
                   38, 39, 40, 42, 43, 44, 45, 47, 49, 50, 53, 59, 60, 62, 65, 67,
                   68, 69, 71, 73, 74, 79, 80, 81, 85, 89, 90, 93, 94, 95, 100,
                   101, 105, 106, 107, 110, 112, 117, 120, 121, 123, 126, 127,
                   132, 133, 135, 136, 138, 143, 149, 150, 152, 154, 158, 159,
                   161, 162, 163, 165, 166, 168, 169, 170, 174, 176, 177, 178,
                   179, 182, 186, 191, 192, 193, 196, 197, 198, 200, 203, 206,
                   208, 209, 210, 211, 212, 216, 219, 222, 224, 225, 226, 228,
                   230, 232, 234, 235, 237, 238, 240, 242, 244, 245, 248, 249,
                   250, 253]
        c = list(code)
        for pos in changes:
            c[pos] = (c[pos] + 50) % 255

        c = bytes(c)
        decode = coder.decode(c)
        print(f"Modified RS(255,13) code: {c}, Decoded: {decode}")
        self.assertEqual(m, decode)

    def test30_10(self):
        """Tests the RS(30,10) code"""
        coder = algoritm.RSCoder(30, 10)
        m = b"Hello, wor"
        code = coder.encode(m)
        print(f"RS(30,10) encoded 'Hello, wor': {code}")

        self.assertTrue(coder.verify(code))
        self.assertEqual(m, coder.decode(code))
        self.assertEqual(30, len(code))

        # Change 10 bytes. This code should tolerate up to 10 bytes changed
        changes = [0, 1, 2, 4, 7, 10, 14, 18, 22, 27]
        c = list(code)
        for pos in changes:
            c[pos] = (c[pos] + 50) % 255

        c = bytes(c)
        decode = coder.decode(c)
        print(f"Modified RS(30,10) code: {c}, Decoded: {decode}")
        self.assertEqual(m, decode)

if __name__ == "__main__":
    unittest.main()

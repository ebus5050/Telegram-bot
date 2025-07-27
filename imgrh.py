# imgrh.py — acts like imghdr

__all__ = ['what']

def what(file, h=None):
    if h is None:
        if isinstance(file, str):
            with open(file, 'rb') as f:
                h = f.read(32)
        else:
            h = file.read(32)

    for test in tests:
        res = test(h, file)
        if res:
            return res
    return None

def test_jpeg(h, f): return h[6:10] in (b'JFIF', b'Exif') and 'jpeg'
def test_png(h, f):  return h[:8] == b'\211PNG\r\n\032\n' and 'png'
def test_gif(h, f):  return h[:6] in (b'GIF87a', b'GIF89a') and 'gif'
def test_bmp(h, f):  return h[:2] == b'BM' and 'bmp'
def test_webp(h, f): return h[:4] == b'RIFF' and h[8:12] == b'WEBP' and 'webp'

tests = [test_jpeg, test_png, test_gif, test_bmp, test_webp]

import sys, hashlib, os
img, outdir = sys.argv[1], sys.argv[2]
os.makedirs(outdir, exist_ok=True)
JPEG = [53277184,53375488,53793280,54206976,54473216,54481408,171561472]
GIF = [54714880,54727168]
d = open(img,'rb').read()

def jpeg_end(o):
    if d[o:o+2] != b'\xff\xd8': return None
    i = o+2
    while i < len(d):
        if d[i] != 0xFF: return None
        while d[i] == 0xFF: i += 1
        m = d[i]; i += 1
        if m == 0xD9: return i
        if m == 0x01 or 0xD0 <= m <= 0xD7: continue
        ln = int.from_bytes(d[i:i+2],'big'); i += ln
        if m == 0xDA:
            while i < len(d):
                j = d.find(b'\xff', i)
                if j < 0: return None
                n = d[j+1]
                if n == 0x00 or 0xD0 <= n <= 0xD7: i = j+2; continue
                i = j; break
    return None

def gif_end(o):
    i = o+6
    flags = d[i+4]; i += 7
    if flags & 0x80: i += 3*(2**((flags&7)+1))
    while i < len(d):
        b = d[i]; i += 1
        if b == 0x3B: return i
        if b == 0x21:
            i += 1
            while d[i]: i += d[i]+1
            i += 1
        elif b == 0x2C:
            fl = d[i+8]; i += 9
            if fl & 0x80: i += 3*(2**((fl&7)+1))
            i += 1
            while d[i]: i += d[i]+1
            i += 1
        else: return None
    return None

for kind, offs, fn in (('jpg',JPEG,jpeg_end),('gif',GIF,gif_end)):
    for o in offs:
        e = fn(o)
        if e is None:
            print(o, kind, 'NO VALID END FOUND'); continue
        data = d[o:e]
        name = f"carved_{o}.{kind}"
        open(os.path.join(outdir,name),'wb').write(data)
        print(o, kind, len(data), hashlib.sha256(data).hexdigest(), name, sep='\t')

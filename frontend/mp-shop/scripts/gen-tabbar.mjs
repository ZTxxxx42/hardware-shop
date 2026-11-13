import { deflateSync } from 'node:zlib'
import { writeFileSync } from 'node:fs'
import { fileURLToPath } from 'node:url'
import { dirname, join } from 'node:path'

const outDir = join(dirname(fileURLToPath(import.meta.url)), '..', 'src', 'static', 'tabbar')

// ---------- PNG encoder ----------
const crcTable = new Int32Array(256)
for (let n = 0; n < 256; n++) {
  let c = n
  for (let k = 0; k < 8; k++) c = c & 1 ? 0xedb88320 ^ (c >>> 1) : c >>> 1
  crcTable[n] = c
}
function crc32(buf) {
  let c = 0xffffffff
  for (let i = 0; i < buf.length; i++) c = crcTable[(c ^ buf[i]) & 0xff] ^ (c >>> 8)
  return (c ^ 0xffffffff) >>> 0
}
function chunk(type, data) {
  const len = Buffer.alloc(4)
  len.writeUInt32BE(data.length, 0)
  const typeBuf = Buffer.from(type, 'ascii')
  const crc = Buffer.alloc(4)
  crc.writeUInt32BE(crc32(Buffer.concat([typeBuf, data])), 0)
  return Buffer.concat([len, typeBuf, data, crc])
}
function encodePNG(size, rgba) {
  const sig = Buffer.from([137, 80, 78, 71, 13, 10, 26, 10])
  const ihdr = Buffer.alloc(13)
  ihdr.writeUInt32BE(size, 0)
  ihdr.writeUInt32BE(size, 4)
  ihdr[8] = 8
  ihdr[9] = 6
  const stride = size * 4 + 1
  const raw = Buffer.alloc(stride * size)
  for (let y = 0; y < size; y++) {
    raw[y * stride] = 0
    rgba.copy(raw, y * stride + 1, y * size * 4, (y + 1) * size * 4)
  }
  return Buffer.concat([sig, chunk('IHDR', ihdr), chunk('IDAT', deflateSync(raw)), chunk('IEND', Buffer.alloc(0))])
}

// ---------- SDF shapes ----------
function rr(px, py, x, y, w, h, r) {
  const cx = x + w / 2
  const cy = y + h / 2
  const qx = Math.max(Math.abs(px - cx) - (w / 2 - r), 0)
  const qy = Math.max(Math.abs(py - cy) - (h / 2 - r), 0)
  return qx * qx + qy * qy <= r * r
}
function circ(px, py, cx, cy, r) {
  const dx = px - cx
  const dy = py - cy
  return dx * dx + dy * dy <= r * r
}
function sign(px, py, ax, ay, bx, by) {
  return (px - bx) * (ay - by) - (ax - bx) * (py - by)
}
function tri(px, py, ax, ay, bx, by, cx, cy) {
  const d1 = sign(px, py, ax, ay, bx, by)
  const d2 = sign(px, py, bx, by, cx, cy)
  const d3 = sign(px, py, cx, cy, ax, ay)
  const neg = d1 < 0 || d2 < 0 || d3 < 0
  const pos = d1 > 0 || d2 > 0 || d3 > 0
  return !(neg && pos)
}

const icons = {
  home: (x, y) => (tri(x, y, 40.5, 6, 6, 42, 75, 42) || rr(x, y, 15, 42, 51, 32, 2)) && !rr(x, y, 35, 52, 11, 22, 2),
  category: (x, y) => rr(x, y, 17, 17, 22, 22, 5) || rr(x, y, 42, 17, 22, 22, 5) || rr(x, y, 17, 42, 22, 22, 5) || rr(x, y, 42, 42, 22, 22, 5),
  cart: (x, y) => rr(x, y, 13, 18, 55, 28, 6) || rr(x, y, 19, 7, 43, 5, 2.5) || circ(x, y, 27, 59, 6.5) || circ(x, y, 54, 59, 6.5),
  user: (x, y) => circ(x, y, 40.5, 23, 14) || rr(x, y, 15, 45, 51, 27, 13),
}

const colors = {
  gray: [147, 160, 173],
  blue: [200, 82, 31],
}

function render(pred, color) {
  const size = 81
  const ss = 3
  const rgba = Buffer.alloc(size * size * 4)
  const [r, g, b] = color
  for (let y = 0; y < size; y++) {
    for (let x = 0; x < size; x++) {
      let hit = 0
      for (let sy = 0; sy < ss; sy++) {
        for (let sx = 0; sx < ss; sx++) {
          if (pred(x + (sx + 0.5) / ss, y + (sy + 0.5) / ss)) hit++
        }
      }
      const alpha = Math.round((hit / (ss * ss)) * 255)
      const i = (y * size + x) * 4
      rgba[i] = r
      rgba[i + 1] = g
      rgba[i + 2] = b
      rgba[i + 3] = alpha
    }
  }
  return encodePNG(size, rgba)
}

for (const [name, pred] of Object.entries(icons)) {
  writeFileSync(join(outDir, `${name}.png`), render(pred, colors.gray))
  writeFileSync(join(outDir, `${name}-active.png`), render(pred, colors.blue))
}

console.log('tabbar icons written to', outDir)

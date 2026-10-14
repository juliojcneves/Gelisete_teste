"""Monta o vídeo do Episódio 1 a partir dos arquivos do repositório.

Uso: python3 video/make_video.py  (gera video/Episodio1_Triangulo_amoroso.mp4)
"""
import os
import subprocess
import tempfile

from PIL import Image, ImageDraw, ImageFilter, ImageFont

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
W, H, FPS = 1280, 720, 24
FONT_BOLD = "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"
FONT = "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"
ACCENT = (196, 86, 44)  # tom do blazer laranja
NAVY = (36, 70, 128)    # azul do selo "Episódio 1"

ABERTURA = os.path.join(ROOT, "Abertura_2.mp4")
FUNDO = os.path.join(ROOT, "Fundo_Gelisete.png")
CARD = os.path.join(ROOT, "1. Triangulo amoroso.jpg")
OUT = os.path.join(ROOT, "video", "Episodio1_Triangulo_amoroso.mp4")

ABERTURA_DUR, TITULO_DUR, CARD_DUR, XF = 8.0, 6.0, 5.0, 1.0


def titulo_png(path):
    """Fundo Gelisete com o título nos espaços brancos laterais."""
    img = Image.open(FUNDO).convert("RGB")
    img = img.resize((round(img.width * H / img.height), H), Image.LANCZOS)
    left = (img.width - W) // 2
    canvas = img.crop((left, 0, left + W, H))
    d = ImageDraw.Draw(canvas)
    # Selo "Episódio 1" à esquerda
    f_ep = ImageFont.truetype(FONT_BOLD, 34)
    d.rounded_rectangle((60, 230, 300, 290), radius=30, fill=NAVY)
    d.text((180, 260), "Episódio 1", font=f_ep, fill="white", anchor="mm")
    # Título
    f_t = ImageFont.truetype(FONT_BOLD, 54)
    d.text((60, 320), "Triângulo", font=f_t, fill=(30, 30, 30))
    d.text((60, 385), "amoroso", font=f_t, fill=ACCENT)
    d.rectangle((62, 465, 182, 471), fill=ACCENT)
    # Assinatura à direita
    f_s = ImageFont.truetype(FONT, 28)
    d.text((W - 60, 300), "com", font=f_s, fill=(110, 110, 110), anchor="ra")
    d.text((W - 60, 340), "Gelisete", font=ImageFont.truetype(FONT_BOLD, 44),
           fill=(30, 30, 30), anchor="ra")
    canvas.save(path)


def card_png(path):
    """Card do episódio sobre uma versão desfocada dele mesmo."""
    card = Image.open(CARD).convert("RGB")
    bg = card.resize((W, H)).filter(ImageFilter.GaussianBlur(30))
    bg = Image.blend(bg, Image.new("RGB", (W, H), "black"), 0.45)
    scale = 560 / card.height
    fg = card.resize((int(card.width * scale), 560), Image.LANCZOS)
    shadow = Image.new("RGBA", (fg.width + 60, fg.height + 60), (0, 0, 0, 0))
    ImageDraw.Draw(shadow).rounded_rectangle((30, 40, fg.width + 30, fg.height + 40),
                                             radius=24, fill=(0, 0, 0, 160))
    shadow = shadow.filter(ImageFilter.GaussianBlur(14))
    x, y = (W - fg.width) // 2, (H - fg.height) // 2
    bg.paste(shadow, (x - 30, y - 30), shadow)
    bg.paste(fg, (x, y))
    bg.save(path)


def main():
    tmp = tempfile.mkdtemp()
    t_png, c_png = os.path.join(tmp, "titulo.png"), os.path.join(tmp, "card.png")
    titulo_png(t_png)
    card_png(c_png)

    zoom = (f"zoompan=z='min(zoom+0.0006,1.06)':x='iw/2-(iw/zoom/2)':"
            f"y='ih/2-(ih/zoom/2)':d=1:s={W}x{H}:fps={FPS}")
    off1 = ABERTURA_DUR - XF
    off2 = off1 + TITULO_DUR - XF
    total = off2 + CARD_DUR
    fc = (
        f"[0:v]scale={W}:{H},fps={FPS},format=yuv420p,setsar=1[a];"
        f"[1:v]{zoom},trim=duration={TITULO_DUR},format=yuv420p,setsar=1[t];"
        f"[2:v]{zoom},trim=duration={CARD_DUR},format=yuv420p,setsar=1[c];"
        f"[a][t]xfade=transition=fade:duration={XF}:offset={off1}[at];"
        f"[at][c]xfade=transition=fade:duration={XF}:offset={off2},"
        f"fade=t=out:st={total - 1}:d=1[v];"
        f"[0:a]apad,atrim=duration={total},afade=t=out:st={ABERTURA_DUR - 1.5}:d=1.5[aout]"
    )
    subprocess.run([
        "ffmpeg", "-v", "error", "-y",
        "-i", ABERTURA,
        "-loop", "1", "-t", str(TITULO_DUR), "-i", t_png,
        "-loop", "1", "-t", str(CARD_DUR), "-i", c_png,
        "-filter_complex", fc, "-map", "[v]", "-map", "[aout]",
        "-c:v", "libx264", "-crf", "20", "-preset", "medium", "-pix_fmt", "yuv420p",
        "-c:a", "aac", "-b:a", "160k", "-movflags", "+faststart", OUT,
    ], check=True)
    print("Gerado:", OUT)


if __name__ == "__main__":
    main()
